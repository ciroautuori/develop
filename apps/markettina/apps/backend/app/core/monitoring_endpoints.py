"""Monitoring endpoints for query performance and system metrics.

LOW-001: Endpoints to view query performance statistics.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.api.dependencies.auth_deps import get_current_user
from app.domain.auth.models import User
from app.infrastructure.database.query_logger import (
    get_query_performance_stats,
    reset_query_performance_stats,
)

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/query-performance")
async def get_query_performance(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get query performance statistics (requires authentication).

    Returns:
        Query performance metrics including slow queries
    """
    # Only admins can access monitoring endpoints
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    stats = get_query_performance_stats()
    return {
        "status": "success",
        "data": stats,
        "message": "Query performance statistics retrieved successfully",
    }


@router.post("/query-performance/reset")
async def reset_query_stats(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Reset query performance statistics (requires admin).

    Returns:
        Success message
    """
    # Only admins can reset stats
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    reset_query_performance_stats()
    return {
        "status": "success",
        "message": "Query performance statistics reset successfully",
    }
