from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database.database import get_sync_db
from app.core.security import (
    security,
    create_user_tokens,
    verify_token,
    get_current_user
)
from app.crud.user import user_crud
from app.models.user import User, UserStatus
from app.schemas.user import (
    UserLogin,
    UserCreate,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    UserResponse
)

router = APIRouter()


# ========== REGISTRATION ==========

@router.post("/register", response_model=UserResponse)
def register_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_sync_db)
):
    """Registrazione nuovo utente"""
    # Verifica email non esistente
    existing_user = user_crud.get_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verifica username non esistente (se fornito)
    if user_in.username:
        existing_username = user_crud.get_by_username(db, user_in.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Crea utente
    user = user_crud.create(db, user_in)
    
    # TODO: Invia email di verifica in background
    # background_tasks.add_task(send_verification_email, user.email, user.email_verification_token)
    
    return user


# ========== LOGIN ==========

@router.post("/login", response_model=TokenResponse)
def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_sync_db)
):
    """Login utente"""
    user = user_crud.authenticate(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != UserStatus.ACTIVE:
        if user.status == UserStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not verified. Please check your email."
            )
        elif user.status == UserStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account suspended. Contact support."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not active"
            )
    
    # Crea tokens
    tokens = create_user_tokens(user)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
        user=user
    )


# ========== TOKEN REFRESH ==========

@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_sync_db)
):
    """Refresh access token"""
    payload = verify_token(refresh_request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = user_crud.get(db, user_id)
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Crea nuovi tokens
    tokens = create_user_tokens(user)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
        user=user
    )


# ========== LOGOUT ==========

@router.post("/logout")
def logout_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Logout utente"""
    # TODO: Implementare blacklist token o invalidazione sessione
    # Per ora solo messaggio di successo
    return {"message": "Successfully logged out"}


# ========== EMAIL VERIFICATION ==========

@router.post("/verify-email")
def verify_email(
    verification: EmailVerificationConfirm,
    db: Session = Depends(get_sync_db)
):
    """Verifica email con token"""
    success = user_crud.verify_email(db, verification.token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
def resend_verification_email(
    request: EmailVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_sync_db)
):
    """Reinvia email di verifica"""
    token = user_crud.resend_verification(db, request.email)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found or already verified"
        )
    
    # TODO: Invia email in background
    # background_tasks.add_task(send_verification_email, request.email, token)
    
    return {"message": "Verification email sent"}


# ========== PASSWORD RESET ==========

@router.post("/reset-password")
def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_sync_db)
):
    """Richiesta reset password"""
    token = user_crud.reset_password_request(db, request.email)
    
    if token:
        # TODO: Invia email reset in background
        # background_tasks.add_task(send_password_reset_email, request.email, token)
        pass
    
    # Sempre successo per sicurezza (non rivelare se email esiste)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password/confirm")
def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_sync_db)
):
    """Conferma reset password"""
    success = user_crud.reset_password_confirm(db, reset_data.token, reset_data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password reset successfully"}


# ========== USER INFO ==========

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Informazioni utente corrente"""
    return current_user


# ========== HEALTH CHECK ==========

@router.get("/health")
def auth_health_check():
    """Health check per sistema auth"""
    return {
        "status": "healthy",
        "service": "authentication",
        "features": [
            "registration",
            "login",
            "token_refresh", 
            "email_verification",
            "password_reset",
            "role_based_access",
            "accessibility_support"
        ]
    }
