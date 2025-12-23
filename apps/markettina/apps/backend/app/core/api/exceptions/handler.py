"""Exception Handler Decorator - Centralized Exception Management.

Converts domain exceptions to HTTP responses.
Logs all errors with unique error IDs.
Returns standardized error responses.
"""

import functools
import logging
import uuid
from collections.abc import Callable

from fastapi import HTTPException, status

from app.core.exceptions import BaseAppException

logger = logging.getLogger(__name__)


def handle_exceptions(func: Callable):
    """
    Decorator to handle exceptions in API endpoints.
    
    Converts domain exceptions to HTTP responses.
    Logs all errors with unique error IDs.
    Returns standardized error responses.
    
    Usage:
        @router.post("/endpoint")
        @handle_exceptions
        async def endpoint(...):
            ...
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        error_id = str(uuid.uuid4())

        try:
            return await func(*args, **kwargs)

        # Domain-specific exceptions (expected errors)
        except BaseAppException as e:
            logger.warning(
                f"Domain exception [{error_id}]: {e.message}",
                extra={
                    "error_id": error_id,
                    "error_code": e.error_code,
                    "status_code": e.status_code,
                    "details": e.details,
                    "endpoint": func.__name__
                }
            )

            raise HTTPException(
                status_code=e.status_code,
                detail={
                    "error": e.message,
                    "code": e.error_code,
                    "error_id": error_id,
                    "details": e.details
                }
            )

        # Unexpected errors (bugs)
        except Exception as e:
            logger.error(
                f"Unexpected exception [{error_id}]: {e!s}",
                exc_info=True,
                extra={
                    "error_id": error_id,
                    "error_type": type(e).__name__,
                    "endpoint": func.__name__
                }
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "An unexpected error occurred",
                    "error_id": error_id,
                    "message": "Please contact support with this error ID"
                }
            )

    return wrapper
