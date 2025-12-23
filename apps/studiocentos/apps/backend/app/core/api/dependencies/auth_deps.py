"""Authentication Dependencies for FastAPI.

Provides dependency injection functions for authentication and authorization:
- get_current_user: Extract and validate JWT token
- get_password_hash: Hash passwords
- get_db: Database session (re-exported for convenience)
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.auth.models import User
from app.domain.auth.admin_models import AdminUser
from app.infrastructure.database.session import get_db

# Security schemes
security = HTTPBearer()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
        
    Example:
        hashed = get_password_hash("mypassword123")
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Get current authenticated user from JWT token.
    
    Validates JWT token and returns the authenticated user.
    Raises HTTPException if token is invalid or user not found.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session
        
    Returns:
        Authenticated User object
        
    Raises:
        HTTPException: 401 if token invalid or user not found
        
    Example:
        @router.get("/me")
        async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
            return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract email from token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        # Verify token type
        token_type: str = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current active user (additional check).
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Active User object
        
    Raises:
        HTTPException: 403 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> AdminUser:
    """Get current authenticated admin user from JWT token.
    
    Validates JWT token and returns the authenticated admin.
    Raises HTTPException if token is invalid or admin not found.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session
        
    Returns:
        Authenticated AdminUser object
        
    Raises:
        HTTPException: 401 if token invalid or admin not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Verify token has admin role (type is always "access" from token_service)
        token_role: str = payload.get("role")
        if token_role != "admin":
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Admin role check failed. Role: {token_role}, Payload: {payload}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract admin ID from token
        admin_id: str = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
            
    except JWTError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception
    
    # Get admin from database
    admin = db.get(AdminUser, int(admin_id))
    
    if admin is None:
        raise credentials_exception
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive admin user"
        )
    
    return admin


__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "get_password_hash",
    "verify_password",
    "get_db",
]
