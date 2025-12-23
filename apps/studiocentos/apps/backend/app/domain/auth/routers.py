"""Auth Router - Authentication Endpoints."""

import logging

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.core.api.dependencies.auth_deps import get_current_user
from app.core.api.middleware.rate_limit import rate_limit
from app.core.constants import AuthConstants, RateLimitConstants
from app.domain.auth.dependencies import get_auth_service
from app.domain.auth.models import User, UserRole
from app.domain.auth.refresh_token import RefreshTokenService, create_tokens_for_user
from app.domain.auth.schemas import UserCreate, UserRead
from app.domain.auth.services import AuthService
from app.infrastructure.database import get_db

class LoginRequest(BaseModel):
    email: str
    password: str

router = APIRouter()  # Tags specified in api/v1/__init__.py

@router.post("/login")
@rate_limit(
    max_requests=AuthConstants.MAX_LOGIN_ATTEMPTS,
    window_seconds=AuthConstants.LOGIN_RATE_LIMIT_WINDOW_SECONDS
)
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    db: Session = Depends(get_db),
):
    """Login endpoint - accepts JSON request with email and password.
    
    Returns access token, refresh token, and user data.
    """
    try:
        logger.debug(f"Login attempt for user: {login_data.email}")

        # Use service for authentication
        user = auth_service.authenticate_user(login_data.email, login_data.password)
        logger.debug(f"User authenticated: {bool(user)}")

        if not user:
            logger.debug("Authentication failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(f"Creating tokens for user: {user.email}")

        # SEC-03: Create access + refresh token
        tokens = create_tokens_for_user(db, user.id, user.email)
        logger.debug("Tokens created successfully")

        # Return simplified user data
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        logger.debug(f"User data prepared: {user_data}")

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
            "expires_in": tokens["expires_in"],
            "user": user_data,
        }
    except HTTPException:
        # Re-raise HTTPException (like 401 Unauthorized) without modification
        raise
    except Exception as e:
        logger.error(f"ERROR in login: {str(e)}")
        import traceback

        logger.error(f"TRACEBACK: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Operation failed. Please try again later.",
        )

@router.post("/register")
@rate_limit(
    max_requests=AuthConstants.MAX_REGISTRATION_PER_HOUR,
    window_seconds=3600
)
async def register(
    request: Request,
    user_data: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Free registration with 30-day trial.
    
    Customer acquisition strategy - no entry barriers.
    """
    from datetime import datetime, timedelta, timezone

    # Prepare registration data with trial role
    registration_data = {
        "email": user_data.email,
        "username": user_data.username,
        "password": user_data.password,
        "full_name": user_data.full_name,
        "role": UserRole.TRIAL,
    }

    # Register user via service (handles validation and password hashing)
    try:
        new_user = auth_service.register_user(registration_data)
        
        # Set trial expiration (service doesn't handle this yet)
        new_user.trial_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        auth_service.repository.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Operation failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Operation failed. Please try again later.",
        )

    return {
        "id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "role": new_user.role.value,
        "is_active": new_user.is_active,
        "trial_expires_at": new_user.trial_expires_at,
        "message": "User registered successfully with 30-day trial",
        "trial_benefits": [
            "🎁 30 giorni GRATUITI di accesso completo",
            "📊 Portfolio professionale illimitato",
            "🚀 Tutte le funzionalità Pro incluse",
        ],
    }

@router.get("/me", response_model=UserRead)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Get current user info."""
    return current_user

@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)
):
    """Logout endpoint con refresh token revocation.

    SEC-03: Revoca tutti i refresh token dell'utente per logout globale.
    """
    # Revoca tutti i refresh token
    revoked_count = RefreshTokenService.revoke_all_user_tokens(db, current_user.id)

    return {"message": "Successfully logged out", "tokens_revoked": revoked_count}

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
@rate_limit(
    max_requests=10,
    window_seconds=RateLimitConstants.RATE_LIMIT_WINDOW
)
async def refresh_access_token(
    request: Request, refresh_request: RefreshTokenRequest, db: Session = Depends(get_db)
):
    """Refresh access token usando refresh token.

    SEC-03: Implementa token rotation per security.

    Flow:
    1. Valida refresh token
    2. Genera nuovo access token
    3. Ruota refresh token (revoca vecchio, crea nuovo)

    Returns:
        New access_token + new refresh_token
    """
    # Valida refresh token
    refresh_token = RefreshTokenService.validate_refresh_token(db, refresh_request.refresh_token)

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
        )

    # Get user
    user = db.query(User).filter(User.id == refresh_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive"
        )

    # Token rotation: crea nuovi token e revoca vecchio
    new_refresh_token = RefreshTokenService.rotate_token(db, refresh_request.refresh_token, user.id)

    if not new_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to rotate refresh token"
        )

    # Genera nuovo access token
    access_token_expires = timedelta(hours=8)  # 8 hours for development
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token.token,
        "token_type": "bearer",
        "expires_in": 28800,  # 8 ore (8 * 60 * 60 = 28800 sec)
    }

@router.post("/revoke-token")
async def revoke_refresh_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Revoca specifico refresh token.
    Utile per logout da singolo device.
    """
    success = RefreshTokenService.revoke_token(db, refresh_request.refresh_token)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found")

    return {"message": "Refresh token revoked successfully"}
