"""Auth Domain - Authentication & Authorization
Handles users, JWT authentication, OAuth, and registration.
"""

from app.core.api_key_rotation import APIKey

# Dependency injection exports
from .dependencies import get_auth_service, get_user_repository

# Exception exports
from .exceptions import (
    AccountLockedError,
    AdminAccessRequiredError,
    # General
    AuthDomainError,
    EmailNotVerifiedError,
    # Permission exceptions
    InsufficientPermissionsError,
    # Authentication exceptions
    InvalidCredentialsError,
    InvalidMFACodeError,
    InvalidPasswordError,
    InvalidRefreshTokenError,
    MFAAlreadyEnabledError,
    MFANotEnabledError,
    # MFA exceptions
    MFARequiredError,
    MissingTokenError,
    OAuthAccountNotLinkedError,
    # OAuth exceptions
    OAuthProviderError,
    OAuthStateMismatchError,
    PasswordResetTokenExpiredError,
    # Password reset exceptions
    PasswordResetTokenInvalidError,
    PasswordTooWeakError,
    # Token exceptions
    RefreshTokenExpiredError,
    RefreshTokenRevokedError,
    TooManyPasswordResetRequestsError,
    UserAlreadyExistsError,
    UserInactiveError,
    # User exceptions
    UserNotFoundError,
    UserSuspendedError,
)

# Cross-domain model imports for relationships
# Profile model removed - merged into User
# Import only models to register with Base.metadata
# Routers are imported directly where needed to avoid circular imports
from .models import User, UserRole
from .models_mfa import MFAAttempt, MFASecret, TrustedDevice
from .oauth_tokens import OAuthToken  # Required for User.oauth_tokens relationship
from .admin_models import AdminUser, AdminSession, AdminAuditLog  # Admin models
from .settings_models import AdminSettings  # Required for AdminUser.settings relationship
from .password_reset import PasswordResetToken
from .refresh_token import RefreshToken

# Repository exports
from .repositories.user_repository import UserRepository

# Service exports (REFACTORED: MEDIUM-006)
from .services import AuthService
from .session_service import SessionService
from .token_service import TokenService

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
