"""Centralized Exception Handling
Custom exceptions and error handling for the application.
"""

from typing import Any

from fastapi import status


class BaseAppException(Exception):
    """Base exception class for application-specific exceptions."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """Initialize the exception.

        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Application-specific error code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API response.

        Returns:
            Dictionary representation of the error
        """
        return {
            "error": {
                "message": self.message,
                "code": self.error_code,
                "status_code": self.status_code,
                "details": self.details,
            }
        }

# Authentication & Authorization Exceptions

class AuthenticationException(BaseAppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message, status_code=status.HTTP_401_UNAUTHORIZED, error_code="AUTH_FAILED"
        )

class AuthorizationException(BaseAppException):
    """Raised when user is not authorized to perform an action."""

    def __init__(self, message: str = "Not authorized"):
        super().__init__(
            message=message, status_code=status.HTTP_403_FORBIDDEN, error_code="NOT_AUTHORIZED"
        )

class TokenExpiredException(AuthenticationException):
    """Raised when JWT token has expired."""

    def __init__(self):
        super().__init__(message="Token has expired")
        self.error_code = "TOKEN_EXPIRED"

class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid."""

    def __init__(self):
        super().__init__(message="Invalid token")
        self.error_code = "INVALID_TOKEN"

# Resource Exceptions

class NotFoundException(BaseAppException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str = "Resource", identifier: Any | None = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(
            message=message, status_code=status.HTTP_404_NOT_FOUND, error_code="NOT_FOUND"
        )

class AlreadyExistsException(BaseAppException):
    """Raised when trying to create a resource that already exists."""

    def __init__(self, resource: str = "Resource", field: str | None = None):
        message = f"{resource} already exists"
        if field:
            message = f"{resource} with this {field} already exists"
        super().__init__(
            message=message, status_code=status.HTTP_409_CONFLICT, error_code="ALREADY_EXISTS"
        )

# Validation Exceptions

class ValidationException(BaseAppException):
    """Raised when validation fails."""

    def __init__(self, message: str = "Validation failed", errors: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=errors or {},
        )

class BusinessRuleViolationException(BaseAppException):
    """Raised when a business rule is violated."""

    def __init__(self, message: str, rule: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_RULE_VIOLATION",
            details={"rule": rule} if rule else {},
        )

# Database Exceptions

class DatabaseException(BaseAppException):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "Database operation failed", operation: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details={"operation": operation} if operation else {},
        )

class TransactionException(DatabaseException):
    """Raised when a database transaction fails."""

    def __init__(self, message: str = "Transaction failed"):
        super().__init__(message=message, operation="transaction")
        self.error_code = "TRANSACTION_ERROR"

# Multi-Tenancy Exceptions

class TenantException(BaseAppException):
    """Base exception for tenant-related errors."""

    def __init__(self, message: str = "Tenant error"):
        super().__init__(
            message=message, status_code=status.HTTP_400_BAD_REQUEST, error_code="TENANT_ERROR"
        )

class TenantNotFoundException(TenantException):
    """Raised when tenant is not found."""

    def __init__(self, tenant_id: str | None = None):
        message = "Tenant not found"
        if tenant_id:
            message = f"Tenant '{tenant_id}' not found"
        super().__init__(message=message)
        self.error_code = "TENANT_NOT_FOUND"
        self.status_code = status.HTTP_404_NOT_FOUND

class TenantAccessDeniedException(TenantException):
    """Raised when access to tenant resources is denied."""

    def __init__(self):
        super().__init__(message="Access to tenant resources denied")
        self.error_code = "TENANT_ACCESS_DENIED"
        self.status_code = status.HTTP_403_FORBIDDEN

# Rate Limiting Exceptions

class RateLimitExceededException(BaseAppException):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int | None = None):
        super().__init__(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after} if retry_after else {},
        )

# External Service Exceptions

class ExternalServiceException(BaseAppException):
    """Raised when an external service call fails."""

    def __init__(self, service: str, message: str | None = None):
        error_message = f"External service '{service}' error"
        if message:
            error_message = f"{error_message}: {message}"
        super().__init__(
            message=error_message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service},
        )

# Subscription & Billing Exceptions

class SubscriptionException(BaseAppException):
    """Base exception for subscription-related errors."""

    def __init__(self, message: str = "Subscription error"):
        super().__init__(
            message=message,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            error_code="SUBSCRIPTION_ERROR",
        )

class SubscriptionLimitExceededException(SubscriptionException):
    """Raised when subscription limit is exceeded."""

    def __init__(self, resource: str, limit: int):
        super().__init__(message=f"Subscription limit exceeded for {resource}. Limit: {limit}")
        self.error_code = "SUBSCRIPTION_LIMIT_EXCEEDED"
        self.details = {"resource": resource, "limit": limit}

class PaymentRequiredException(SubscriptionException):
    """Raised when payment is required for an action."""

    def __init__(self, message: str = "Payment required for this action"):
        super().__init__(message=message)
        self.error_code = "PAYMENT_REQUIRED"

# File Upload Exceptions

class FileUploadException(BaseAppException):
    """Raised when file upload fails."""

    def __init__(self, message: str = "File upload failed", reason: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="FILE_UPLOAD_ERROR",
            details={"reason": reason} if reason else {},
        )

class FileSizeExceededException(FileUploadException):
    """Raised when uploaded file size exceeds limit."""

    def __init__(self, max_size: int):
        super().__init__(
            message=f"File size exceeds maximum allowed size of {max_size} bytes",
            reason="file_too_large",
        )
        self.error_code = "FILE_SIZE_EXCEEDED"
        self.details["max_size"] = max_size

class InvalidFileTypeException(FileUploadException):
    """Raised when uploaded file type is not allowed."""

    def __init__(self, allowed_types: list):
        super().__init__(
            message=f"File type not allowed. Allowed types: {', '.join(allowed_types)}",
            reason="invalid_file_type",
        )
        self.error_code = "INVALID_FILE_TYPE"
        self.details["allowed_types"] = allowed_types
