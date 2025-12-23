"""Cache monitoring endpoints.

LOW-002: Cache statistics and monitoring endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.api.dependencies.auth_deps import get_current_user
from app.domain.auth.models import User
from app.infrastructure.cache.cache_monitor import get_cache_monitor

router = APIRouter(prefix="/cache", tags=["Cache"])


@router.get("/stats")
async def get_cache_stats(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get cache statistics (requires admin).

    Returns:
        Cache statistics including hit rate and performance metrics
    """
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    monitor = get_cache_monitor()
    stats = monitor.get_stats()

    return {
        "status": "success",
        "data": stats,
    }


@router.get("/hottest-keys")
async def get_hottest_keys(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
):
    """Get most frequently accessed cache keys.

    Args:
        limit: Maximum number of keys to return

    Returns:
        List of hottest keys with access statistics
    """
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    monitor = get_cache_monitor()
    keys = monitor.get_hottest_keys(limit=limit)

    return {
        "status": "success",
        "data": {
            "keys": keys,
            "count": len(keys),
        },
    }


@router.get("/coldest-keys")
async def get_coldest_keys(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
):
    """Get least frequently accessed cache keys (eviction candidates).

    Args:
        limit: Maximum number of keys to return

    Returns:
        List of coldest keys
    """
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    monitor = get_cache_monitor()
    keys = monitor.get_coldest_keys(limit=limit)

    return {
        "status": "success",
        "data": {
            "keys": keys,
            "count": len(keys),
        },
    }


@router.get("/miss-hotspots")
async def get_cache_miss_hotspots(
    current_user: Annotated[User, Depends(get_current_user)],
    threshold: int = 10,
):
    """Identify keys with high miss rates (optimization candidates).

    Args:
        threshold: Minimum number of accesses to consider

    Returns:
        List of keys with high miss rates
    """
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    monitor = get_cache_monitor()
    hotspots = monitor.identify_cache_misses_hotspots(threshold=threshold)

    return {
        "status": "success",
        "data": {
            "hotspots": hotspots,
            "count": len(hotspots),
            "message": "Keys with >50% miss rate that may need cache warming or longer TTL",
        },
    }


@router.post("/reset-stats")
async def reset_cache_stats(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Reset cache statistics (requires admin).

    Returns:
        Success message
    """
    if current_user.role != "ADMIN":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    monitor = get_cache_monitor()
    monitor.reset_stats()

    return {
        "status": "success",
        "message": "Cache statistics reset successfully",
    }
