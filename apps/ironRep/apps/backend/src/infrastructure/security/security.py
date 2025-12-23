from datetime import datetime, timedelta
from typing import Optional, Annotated
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.infrastructure.config.settings import settings
from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.models import UserModel

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """Decode JWT token and return email (sub claim)."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Dependency to get current authenticated user from JWT token.

    Usage in endpoints:
        @router.get("/endpoint")
        async def endpoint(current_user: UserModel = Depends(get_current_user)):
            user_id = current_user.id
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token non valido o scaduto",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    user = db.query(UserModel).filter(UserModel.email == email).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utente disattivato"
        )

    return user


async def get_current_user_optional(
    token: Annotated[Optional[str], Depends(oauth2_scheme)] = None,
    db: Session = Depends(get_db)
) -> Optional[UserModel]:
    """
    Optional auth - returns None if no token provided.
    Useful for endpoints that work with or without auth.
    """
    if token is None:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


# Type alias for cleaner endpoint signatures
CurrentUser = Annotated[UserModel, Depends(get_current_user)]
