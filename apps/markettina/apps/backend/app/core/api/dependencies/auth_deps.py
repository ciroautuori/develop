"""Authentication Dependencies for FastAPI.

Provides dependency injection functions for authentication and authorization:
- get_current_user: Extract and validate JWT token
- get_current_admin_user: Extract and validate admin JWT token
- require_permission: Factory for permission-based access control
- get_password_hash: Hash passwords
- get_db: Database session (re-exported for convenience)
"""

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants.auth_constants import (
    Permission,
    ROLE_PERMISSIONS,
    has_permission,
)
from app.domain.auth.admin_models import AdminUser
from app.domain.auth.models import User
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

        # Verify token has admin role
        token_role: str = payload.get("role")
        if token_role not in ["admin", "editor", "viewer"]:
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
        logger.error(f"JWT decode error: {e!s}")
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


def require_permission(permission: Permission) -> Callable:
    """Factory to create dependencies that check for specific permissions.

    This implements RBAC (Role-Based Access Control) at the endpoint level.

    Args:
        permission: The Permission enum value required to access the endpoint

    Returns:
        A FastAPI dependency function that validates the permission

    Example:
        @router.get("/settings")
        async def get_settings(
            admin: AdminUser = Depends(require_permission(Permission.SETTINGS_READ))
        ):
            return {"settings": ...}

        @router.put("/settings")
        async def update_settings(
            admin: AdminUser = Depends(require_permission(Permission.SETTINGS_WRITE))
        ):
            ...
    """
    async def _check_permission(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        db: Annotated[Session, Depends(get_db)],
    ) -> AdminUser:
        # First, get the authenticated admin
        admin = await get_current_admin_user(credentials, db)

        # Get user's role (default to admin for backwards compatibility)
        role = getattr(admin, 'role', None) or "admin"

        # Check if user has the required permission
        if not has_permission(role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required. Your role: {role}"
            )

        return admin

    return _check_permission


def require_any_permission(*permissions: Permission) -> Callable:
    """Factory to create dependencies that check for ANY of the specified permissions.

    Args:
        permissions: Multiple Permission enum values (user needs at least one)

    Returns:
        A FastAPI dependency function

    Example:
        @router.get("/dashboard")
        async def get_dashboard(
            admin: AdminUser = Depends(require_any_permission(
                Permission.ADMIN_READ,
                Permission.ANALYTICS_READ
            ))
        ):
            ...
    """
    async def _check_any_permission(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        db: Annotated[Session, Depends(get_db)],
    ) -> AdminUser:
        admin = await get_current_admin_user(credentials, db)
        role = getattr(admin, 'role', None) or "admin"

        for perm in permissions:
            if has_permission(role, perm):
                return admin

        perm_list = ", ".join(p.value for p in permissions)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"One of these permissions required: {perm_list}. Your role: {role}"
        )

    return _check_any_permission


__all__ = [
    "get_current_active_user",
    "get_current_admin_user",
    "get_current_user",
    "get_db",
    "get_password_hash",
    "verify_password",
    "require_permission",
    "require_any_permission",
    "Permission",
]
