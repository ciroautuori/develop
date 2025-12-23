"""API Constants (Validation, Error Codes, HTTP Messages)"""

from typing import Final


class ValidationConstants:
    """Validation patterns and rules."""

    # Email
    EMAIL_MAX_LENGTH: Final[int] = 255
    EMAIL_PATTERN: Final[str] = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    # URL
    URL_MAX_LENGTH: Final[int] = 2048
    URL_PATTERN: Final[str] = r"^https?://.+"

    # Phone
    PHONE_PATTERN: Final[str] = r"^\+?[1-9]\d{1,14}$"


class ErrorCodes:
    """Standardized error codes for API responses."""

    # Generic
    INTERNAL_ERROR: Final[str] = "INTERNAL_ERROR"
    VALIDATION_ERROR: Final[str] = "VALIDATION_ERROR"
    NOT_FOUND: Final[str] = "NOT_FOUND"
    ALREADY_EXISTS: Final[str] = "ALREADY_EXISTS"

    # Auth
    INVALID_CREDENTIALS: Final[str] = "INVALID_CREDENTIALS"
    UNAUTHORIZED: Final[str] = "UNAUTHORIZED"
    FORBIDDEN: Final[str] = "FORBIDDEN"
    TOKEN_EXPIRED: Final[str] = "TOKEN_EXPIRED"

    # Subscription
    SUBSCRIPTION_EXPIRED: Final[str] = "SUBSCRIPTION_EXPIRED"
    USAGE_LIMIT_EXCEEDED: Final[str] = "USAGE_LIMIT_EXCEEDED"
    PAYMENT_REQUIRED: Final[str] = "PAYMENT_REQUIRED"

    # Rate limiting
    RATE_LIMIT_EXCEEDED: Final[str] = "RATE_LIMIT_EXCEEDED"


class HTTPMessages:
    """Standard HTTP response messages."""

    # Success
    SUCCESS: Final[str] = "Operation completed successfully"
    CREATED: Final[str] = "Resource created successfully"
    UPDATED: Final[str] = "Resource updated successfully"
    DELETED: Final[str] = "Resource deleted successfully"

    # Errors
    BAD_REQUEST: Final[str] = "Bad request"
    UNAUTHORIZED: Final[str] = "Authentication required"
    FORBIDDEN: Final[str] = "Access forbidden"
    NOT_FOUND: Final[str] = "Resource not found"
    CONFLICT: Final[str] = "Resource already exists"
    INTERNAL_ERROR: Final[str] = "Internal server error"
