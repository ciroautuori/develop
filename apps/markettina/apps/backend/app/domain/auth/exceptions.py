"""Auth Domain Exceptions
Custom exceptions for authentication and authorization business logic.
"""

from app.core.exceptions import (
    AlreadyExistsException,
    AuthenticationException,
    AuthorizationException,
    BaseAppException,
    BusinessRuleViolationException,
    NotFoundException,
    ValidationException,
)

# ============================================================================
# USER EXCEPTIONS
# ============================================================================

class UserNotFoundError(NotFoundException):
    """User not found exception."""

    def __init__(self, identifier: str | int):
        super().__init__(resource="User", identifier=identifier)
        self.identifier = identifier


class UserAlreadyExistsError(AlreadyExistsException):
    """User already exists exception (duplicate email)."""

    def __init__(self, email: str):
        super().__init__(resource="User", field=f"email '{email}'")
        self.details["email"] = email


class UserInactiveError(AuthorizationException):
    """User account is inactive/disabled."""

    def __init__(self, user_id: int):
        super().__init__(message="User account is inactive")
        self.error_code = "USER_INACTIVE"
        self.details["user_id"] = user_id


class UserSuspendedError(AuthorizationException):
    """User account is suspended."""

    def __init__(self, user_id: int, reason: str | None = None):
        message = "User account is suspended"
        if reason:
            message += f": {reason}"
        super().__init__(message=message)
        self.error_code = "USER_SUSPENDED"
        self.details.update({
            "user_id": user_id,
            "reason": reason
        })


# ============================================================================
# AUTHENTICATION EXCEPTIONS
# ============================================================================

class InvalidCredentialsError(AuthenticationException):
    """Invalid email/password combination."""

    def __init__(self):
        super().__init__(message="Invalid email or password")
        self.error_code = "INVALID_CREDENTIALS"


class InvalidPasswordError(ValidationException):
    """Password does not meet requirements."""

    def __init__(self, requirements: list[str]):
        super().__init__(
            message="Password does not meet requirements",
            errors={"password": requirements}
        )


class PasswordTooWeakError(ValidationException):
    """Password is too weak."""

    def __init__(self, min_length: int = 8):
        super().__init__(
            message=f"Password must be at least {min_length} characters",
            errors={"password": f"Minimum length: {min_length} characters"}
        )
        self.details["min_length"] = min_length


class EmailNotVerifiedError(AuthenticationException):
    """Email address not verified."""

    def __init__(self, email: str):
        super().__init__(message=f"Email '{email}' is not verified")
        self.error_code = "EMAIL_NOT_VERIFIED"
        self.details["email"] = email


class AccountLockedError(AuthenticationException):
    """Account locked due to too many failed login attempts."""

    def __init__(self, locked_until: str | None = None):
        message = "Account locked due to too many failed login attempts"
        if locked_until:
            message += f" until {locked_until}"
        super().__init__(message=message)
        self.error_code = "ACCOUNT_LOCKED"
        if locked_until:
            self.details["locked_until"] = locked_until


# ============================================================================
# TOKEN EXCEPTIONS
# ============================================================================

class RefreshTokenExpiredError(AuthenticationException):
    """Refresh token has expired."""

    def __init__(self):
        super().__init__(message="Refresh token has expired")
        self.error_code = "REFRESH_TOKEN_EXPIRED"


class RefreshTokenRevokedError(AuthenticationException):
    """Refresh token has been revoked."""

    def __init__(self):
        super().__init__(message="Refresh token has been revoked")
        self.error_code = "REFRESH_TOKEN_REVOKED"


class InvalidRefreshTokenError(AuthenticationException):
    """Invalid refresh token."""

    def __init__(self):
        super().__init__(message="Invalid refresh token")
        self.error_code = "INVALID_REFRESH_TOKEN"


class MissingTokenError(AuthenticationException):
    """Authentication token is missing."""

    def __init__(self):
        super().__init__(message="Authentication token is required")
        self.error_code = "MISSING_TOKEN"


# ============================================================================
# PASSWORD RESET EXCEPTIONS
# ============================================================================

class PasswordResetTokenInvalidError(ValidationException):
    """Password reset token is invalid or expired."""

    def __init__(self):
        super().__init__(
            message="Password reset token is invalid or expired",
            errors={"token": "Token is invalid or has expired"}
        )


class PasswordResetTokenExpiredError(ValidationException):
    """Password reset token has expired."""

    def __init__(self, expires_in_minutes: int = 60):
        super().__init__(
            message=f"Password reset token has expired (valid for {expires_in_minutes} minutes)",
            errors={"token": f"Token expired (valid for {expires_in_minutes} min)"}
        )
        self.details["expires_in_minutes"] = expires_in_minutes


class TooManyPasswordResetRequestsError(BusinessRuleViolationException):
    """Too many password reset requests in short time."""

    def __init__(self, retry_after_seconds: int = 300):
        super().__init__(
            message=f"Too many password reset requests. Try again in {retry_after_seconds} seconds",
            rule="password_reset_rate_limit"
        )
        self.details["retry_after_seconds"] = retry_after_seconds


# ============================================================================
# MFA EXCEPTIONS
# ============================================================================

class MFARequiredError(AuthenticationException):
    """Multi-factor authentication is required."""

    def __init__(self):
        super().__init__(message="Multi-factor authentication is required")
        self.error_code = "MFA_REQUIRED"


class InvalidMFACodeError(AuthenticationException):
    """Invalid MFA verification code."""

    def __init__(self):
        super().__init__(message="Invalid MFA verification code")
        self.error_code = "INVALID_MFA_CODE"


class MFANotEnabledError(BusinessRuleViolationException):
    """MFA is not enabled for this user."""

    def __init__(self):
        super().__init__(
            message="Multi-factor authentication is not enabled for this account",
            rule="mfa_not_enabled"
        )


class MFAAlreadyEnabledError(BusinessRuleViolationException):
    """MFA is already enabled for this user."""

    def __init__(self):
        super().__init__(
            message="Multi-factor authentication is already enabled",
            rule="mfa_already_enabled"
        )


# ============================================================================
# OAUTH EXCEPTIONS
# ============================================================================

class OAuthProviderError(BaseAppException):
    """OAuth provider error."""

    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"OAuth error from {provider}: {message}",
            status_code=400,
            error_code="OAUTH_PROVIDER_ERROR"
        )
        self.details["provider"] = provider


class OAuthStateMismatchError(AuthenticationException):
    """OAuth state parameter mismatch (CSRF protection)."""

    def __init__(self):
        super().__init__(message="OAuth state mismatch - possible CSRF attack")
        self.error_code = "OAUTH_STATE_MISMATCH"


class OAuthAccountNotLinkedError(NotFoundException):
    """No account linked to this OAuth provider."""

    def __init__(self, provider: str, provider_user_id: str):
        super().__init__(
            resource=f"{provider} account",
            identifier=provider_user_id
        )
        self.details.update({
            "provider": provider,
            "provider_user_id": provider_user_id
        })


# ============================================================================
# PERMISSION EXCEPTIONS
# ============================================================================

class InsufficientPermissionsError(AuthorizationException):
    """User lacks required permissions for this action."""

    def __init__(self, required_permission: str):
        super().__init__(
            message=f"Insufficient permissions. Required: {required_permission}"
        )
        self.error_code = "INSUFFICIENT_PERMISSIONS"
        self.details["required_permission"] = required_permission


class AdminAccessRequiredError(AuthorizationException):
    """Admin access is required for this action."""

    def __init__(self):
        super().__init__(message="Admin access required")
        self.error_code = "ADMIN_ACCESS_REQUIRED"


# ============================================================================
# AUTH DOMAIN EXCEPTIONS (GENERAL)
# ============================================================================

class AuthDomainError(BaseAppException):
    """Base exception for auth domain."""

    def __init__(self, message: str = "Authentication domain error"):
        super().__init__(message=message, status_code=400, error_code="AUTH_DOMAIN_ERROR")
