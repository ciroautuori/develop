"""Auth Domain - Authentication & Authorization
Handles users, JWT authentication, OAuth, and registration.
"""

from app.core.api_key_rotation import APIKey  # noqa: F401

# Cross-domain model imports for relationships
# Profile model removed - merged into User  # noqa: F401

# Import only models to register with Base.metadata
# Routers are imported directly where needed to avoid circular imports
from .models import User, UserRole  # noqa: F401
from .models_mfa import MFAAttempt, MFASecret, TrustedDevice  # noqa: F401
from .password_reset import PasswordResetToken  # noqa: F401
from .refresh_token import RefreshToken  # noqa: F401

# Repository exports
from .repositories.user_repository import UserRepository  # noqa: F401

# Service exports (REFACTORED: MEDIUM-006)
from .services import AuthService  # noqa: F401
from .token_service import TokenService  # noqa: F401
from .session_service import SessionService  # noqa: F401

# Dependency injection exports
from .dependencies import get_auth_service, get_user_repository  # noqa: F401

# Exception exports
from .exceptions import (  # noqa: F401
    # User exceptions
    UserNotFoundError,
    UserAlreadyExistsError,
    UserInactiveError,
    UserSuspendedError,
    # Authentication exceptions
    InvalidCredentialsError,
    InvalidPasswordError,
    PasswordTooWeakError,
    EmailNotVerifiedError,
    AccountLockedError,
    # Token exceptions
    RefreshTokenExpiredError,
    RefreshTokenRevokedError,
    InvalidRefreshTokenError,
    MissingTokenError,
    # Password reset exceptions
    PasswordResetTokenInvalidError,
    PasswordResetTokenExpiredError,
    TooManyPasswordResetRequestsError,
    # MFA exceptions
    MFARequiredError,
    InvalidMFACodeError,
    MFANotEnabledError,
    MFAAlreadyEnabledError,
    # OAuth exceptions
    OAuthProviderError,
    OAuthStateMismatchError,
    OAuthAccountNotLinkedError,
    # Permission exceptions
    InsufficientPermissionsError,
    AdminAccessRequiredError,
    # General
    AuthDomainError,
)

__all__ = [
    # Models
    "User",
    "UserRole",
    "MFASecret",
    "MFAAttempt",
    "TrustedDevice",
    "PasswordResetToken",
    "RefreshToken",
    "APIKey",
    # Repositories
    "UserRepository",
    # Services (REFACTORED: MEDIUM-006)
    "AuthService",
    "TokenService",
    "SessionService",
    # Dependencies
    "get_user_repository",
    "get_auth_service",
    # Exceptions
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "UserInactiveError",
    "UserSuspendedError",
    "InvalidCredentialsError",
    "InvalidPasswordError",
    "PasswordTooWeakError",
    "EmailNotVerifiedError",
    "AccountLockedError",
    "RefreshTokenExpiredError",
    "RefreshTokenRevokedError",
    "InvalidRefreshTokenError",
    "MissingTokenError",
    "PasswordResetTokenInvalidError",
    "PasswordResetTokenExpiredError",
    "TooManyPasswordResetRequestsError",
    "MFARequiredError",
    "InvalidMFACodeError",
    "MFANotEnabledError",
    "MFAAlreadyEnabledError",
    "OAuthProviderError",
    "OAuthStateMismatchError",
    "OAuthAccountNotLinkedError",
    "InsufficientPermissionsError",
    "AdminAccessRequiredError",
    "AuthDomainError",
]


