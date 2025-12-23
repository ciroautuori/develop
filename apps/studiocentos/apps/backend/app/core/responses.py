"""Standard API Response Envelopes
Response format uniforme per tutti gli endpoint.
"""

from datetime import datetime
from typing import Any, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

class APIResponse[T](BaseModel):
    """Standard API response envelope.

    STANDARDIZATION: Formato uniforme per tutti gli endpoint.
    Ispirato a JSON:API e best practices enterprise.

    Attributes:
        success: Indica se operazione è riuscita
        data: Payload della response
        message: Messaggio human-readable
        errors: Lista errori (se presenti)
        meta: Metadata aggiuntivi (pagination, etc.)
        timestamp: Timestamp ISO 8601
    """

    success: bool = True
    data: T | None = None
    message: str | None = None
    errors: list[dict] | None = None
    meta: dict | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": 1, "name": "Example"},
                "message": "Operation completed successfully",
                "meta": {"page": 1, "total": 100},
                "timestamp": "2025-09-30T15:00:00Z",
            }
        }

class PaginatedAPIResponse(APIResponse[list[T]]):
    """Response per endpoint paginati.
    Estende APIResponse aggiungendo metadata pagination.
    """

    def __init__(
        self,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
        message: str = "Success",
        **kwargs,
    ):
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        super().__init__(
            success=True,
            data=items,
            message=message,
            meta={
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                }
            },
            **kwargs,
        )

class ErrorDetail(BaseModel):
    """Dettaglio errore strutturato."""

    code: str
    message: str
    field: str | None = None
    details: dict | None = None

class ErrorResponse(APIResponse[None]):
    """Response per errori.
    success=False, data=None, errors popolato.
    """

    success: bool = False
    data: None = None
    errors: list[ErrorDetail]

    def __init__(self, message: str, errors: list[ErrorDetail], **kwargs):
        super().__init__(
            success=False,
            data=None,
            message=message,
            errors=[error.dict() for error in errors],
            **kwargs,
        )

# Helper functions per creare responses

def success_response(data: Any = None, message: str = "Success", meta: dict = None) -> APIResponse:
    """Crea success response standard.

    Example:
        ```python
        @router.get("/profile")
        async def get_profile(...):
            return success_response(
                data=profile,
                message="Profile retrieved successfully"
            )
        ```
    """
    return APIResponse(success=True, data=data, message=message, meta=meta)

def error_response(
    message: str, error_code: str = "ERROR", field: str = None, details: dict = None
) -> ErrorResponse:
    """Crea error response standard.

    Example:
        ```python
        if not profile:
            return error_response(
                message="Profile not found",
                error_code="PROFILE_NOT_FOUND",
                details={"user_id": user_id}
            )
        ```
    """
    return ErrorResponse(
        message=message,
        errors=[ErrorDetail(code=error_code, message=message, field=field, details=details)],
    )

def paginated_response(
    items: list[Any], total: int, page: int, page_size: int, message: str = "Success"
) -> PaginatedAPIResponse:
    """Crea paginated response standard.

    Example:
        ```python
        @router.get("/experiences")
        async def get_experiences(page: int = 1, page_size: int = 20):
            query = db.query(Experience).filter(...)
            total = query.count()
            items = query.offset((page-1)*page_size).limit(page_size).all()

            return paginated_response(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
                message="Experiences retrieved successfully"
            )
        ```
    """
    return PaginatedAPIResponse(
        items=items, total=total, page=page, page_size=page_size, message=message
    )
