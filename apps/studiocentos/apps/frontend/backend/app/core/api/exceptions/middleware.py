"""Global Exception Middleware - Last Line of Defense.

Catches all unhandled exceptions.
This should only catch exceptions not handled by endpoint decorators.
"""

import logging
import uuid

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    """
    Global middleware to catch all unhandled exceptions.
    
    This is the last line of defense - should only catch
    exceptions that weren't handled by endpoint decorators.
    """
    
    async def dispatch(self, request: Request, call_next):
        error_id = str(uuid.uuid4())
        
        try:
            response = await call_next(request)
            return response
        
        except Exception as e:
            # Log with full traceback
            logger.critical(
                f"Unhandled exception [{error_id}]: {str(e)}",
                exc_info=True,
                extra={
                    "error_id": error_id,
                    "path": request.url.path,
                    "method": request.method,
                    "client": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                }
            )
            
            # Return generic error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "An internal server error occurred",
                    "code": "INTERNAL_SERVER_ERROR",
                    "error_id": error_id,
                    "message": "Our team has been notified. Please contact support with this error ID."
                }
            )
