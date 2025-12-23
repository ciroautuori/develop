from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, AuthResponse, RefreshTokenRequest, TokenResponse, UserInfo
from app.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    security,
    get_current_user
)
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Endpoint di login per admin"""
    result = await db.execute(select(User).where(User.username == login_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password incorretti"
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso negato: privilegi di amministratore richiesti"
        )
    
    # Aggiorna ultimo accesso
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Genera tokens
    access_token = create_access_token(subject=user.username)
    refresh_token = create_refresh_token(subject=user.username)
    
    user_info = UserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        created_at=user.created_at.isoformat()
    )
    
    return AuthResponse(
        user=user_info,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Rinnova access token usando refresh token"""
    payload = verify_token(refresh_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token non valido"
        )
    
    username = payload.get("sub")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non trovato o non autorizzato"
        )
    
    # Genera nuovo access token
    new_access_token = create_access_token(subject=user.username)
    new_refresh_token = create_refresh_token(subject=user.username)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout utente (invalidazione lato client)"""
    return {"message": "Logout effettuato con successo"}


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Ottieni informazioni utente corrente"""
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at.isoformat()
    )


@router.post("/verify")
async def verify_access_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica validità access token"""
    payload = verify_token(credentials.credentials)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido"
        )
    
    return {"valid": True, "username": payload.get("sub")}
