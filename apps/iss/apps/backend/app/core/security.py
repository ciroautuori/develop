from datetime import datetime, timedelta
from typing import Union, Any, Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.database import get_sync_db
from app.models.user import User, UserRole, UserStatus
import secrets
import hashlib

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)
security_optional = HTTPBearer(auto_error=False)


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    # Hash della password plain con salt
    salt = "iss_platform_salt_2024"  # Salt fisso per ora
    plain_hashed = hashlib.sha256((plain_password + salt).encode()).hexdigest()
    return plain_hashed == hashed_password


def get_password_hash(password: str) -> str:
    salt = "iss_platform_salt_2024"  # Salt fisso per ora
    return hashlib.sha256((password + salt).encode()).hexdigest()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_sync_db)) -> User:
    """Dependency per ottenere utente corrente da JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id = int(user_id)
    except ValueError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Verifica che l'utente sia attivo
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )

    # Aggiorna ultima attività
    user.last_activity = datetime.utcnow()
    db.commit()

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency per utente attivo verificato"""
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency per utente admin"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency per super admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


def get_current_aps_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency per utenti APS"""
    if not current_user.is_aps:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="APS membership required"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """Decorator per richiedere ruoli specifici"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


def require_accessibility_permissions(current_user: User = Depends(get_current_user)) -> User:
    """Dependency per utenti con esigenze di accessibilità - priorità supporto"""
    # Tutti gli utenti possono accedere, ma quelli con esigenze hanno priorità
    if current_user.needs_accessibility_support:
        # Logica per priorità o supporto aggiuntivo
        pass
    return current_user


# ========== UTILITY FUNCTIONS ==========

def generate_verification_token() -> str:
    """Genera token sicuro per verifica email"""
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """Genera token sicuro per reset password"""
    return secrets.token_urlsafe(32)


def create_user_tokens(user: User) -> dict:
    """Crea access e refresh token per utente"""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    return {
        "access_token": create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "refresh_token": create_refresh_token(subject=user.id),
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }
