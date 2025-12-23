from datetime import timedelta
import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.models import UserModel, GoogleAccountModel
from src.infrastructure.security.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from src.infrastructure.config.settings import settings
from src.infrastructure.external.google_oauth_service import google_oauth_service, get_all_scopes

router = APIRouter()
logger = logging.getLogger(__name__)

class Token(BaseModel):
    access_token: str
    token_type: str



class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_active: bool

    class Config:
        from_attributes = True


class GoogleAuthUrlResponse(BaseModel):
    authorization_url: str


class GoogleTokenExchangeRequest(BaseModel):
    code: str
    state: str | None = None






@router.get("/google/url", response_model=GoogleAuthUrlResponse)
def google_login_authorization_url() -> Any:
    try:
        url = google_oauth_service.get_authorization_url(scopes=get_all_scopes(), state="login")
        return {"authorization_url": url}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.post("/google/callback", response_model=Token)
def google_login_exchange_code(request: GoogleTokenExchangeRequest, db: Session = Depends(get_db)) -> Any:
    try:
        tokens = google_oauth_service.exchange_code_for_tokens(request.code)
        creds = google_oauth_service.get_credentials(
            tokens["access_token"],
            tokens.get("refresh_token"),
            datetime.fromisoformat(tokens["expires_at"]) if tokens.get("expires_at") else None,
        )
        user_info = google_oauth_service.get_user_info(creds)

        google_user_id = user_info.get("google_user_id")
        email = (user_info.get("email") or "").lower().strip()
        name = (user_info.get("name") or "Utente").strip()

        if not google_user_id or not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google user info incompleta")

        # 1) If this google_user_id is already linked, reuse that user
        existing_google = db.query(GoogleAccountModel).filter(GoogleAccountModel.google_user_id == google_user_id).first()
        if existing_google:
            user = db.query(UserModel).filter(UserModel.id == existing_google.user_id).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Link Google inconsistente")
        else:
            # 2) Otherwise map by email (create if missing)
            user = db.query(UserModel).filter(UserModel.email == email).first()
            if not user:
                user = UserModel(
                    id=str(uuid.uuid4()),
                    email=email,
                    password_hash=None,
                    name=name,
                    is_active=True,
                    is_onboarded=False,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    last_login_at=datetime.now(),
                )
                db.add(user)
                db.flush()
            else:
                user.last_login_at = datetime.now()
                if not user.name:
                    user.name = name

        # Upsert GoogleAccount for this user
        google_account = db.query(GoogleAccountModel).filter(GoogleAccountModel.user_id == user.id).first()
        if google_account:
            google_account.access_token = tokens["access_token"]
            google_account.refresh_token = tokens.get("refresh_token") or google_account.refresh_token
            google_account.token_expires_at = datetime.fromisoformat(tokens["expires_at"]) if tokens.get("expires_at") else None
            google_account.scopes = tokens.get("scopes")
            google_account.google_user_id = google_user_id
            google_account.google_email = email
            google_account.updated_at = datetime.now()
        else:
            google_account = GoogleAccountModel(
                id=str(uuid.uuid4()),
                user_id=user.id,
                google_user_id=google_user_id,
                google_email=email,
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),
                token_expires_at=datetime.fromisoformat(tokens["expires_at"]) if tokens.get("expires_at") else None,
                scopes=tokens.get("scopes"),
                fit_sync_enabled=True,
                calendar_sync_enabled=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(google_account)

        db.commit()

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Google login exchange failed")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Errore autorizzazione Google: {str(e)}")
