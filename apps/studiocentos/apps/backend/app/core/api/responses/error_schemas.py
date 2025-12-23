"""Error Response Schemas - Standardized Error Responses."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    type: Optional[str] = Field(None, description="Error type")


class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code (e.g., VALIDATION_ERROR)")
    error_id: str = Field(..., description="Unique error ID for tracking")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation failed",
                "code": "VALIDATION_ERROR",
                "error_id": "550e8400-e29b-41d4-a716-446655440000",
                "details": {
                    "field": "email",
                    "message": "Invalid email format"
                }
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """Validation error response."""
    code: str = "VALIDATION_ERROR"
    errors: list[ErrorDetail] = Field(default_factory=list)


class AuthenticationErrorResponse(ErrorResponse):
    """Authentication error response."""
    code: str = "AUTHENTICATION_ERROR"


class AuthorizationErrorResponse(ErrorResponse):
    """Authorization error response."""
    code: str = "AUTHORIZATION_ERROR"


class NotFoundErrorResponse(ErrorResponse):
    """Not found error response."""
    code: str = "NOT_FOUND"


class InternalServerErrorResponse(ErrorResponse):
    """Internal server error response."""
    code: str = "INTERNAL_SERVER_ERROR"
    message: str = "Please contact support with the error_id"
