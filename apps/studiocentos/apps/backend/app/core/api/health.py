"""Health Check and Monitoring Endpoints
Extracted from main.py for better modularity.
"""

import logging

from fastapi.responses import JSONResponse

from app.core.config import settings
from app.infrastructure.cache.manager import cache
from app.infrastructure.startup import startup_manager

logger = logging.getLogger("portfolio-backend")

def read_root() -> dict[str, str]:
    """Root endpoint for API.

    Returns:
        Welcome message
    """
    return {"message": "Welcome to the Portfolio API"}

def health_check() -> JSONResponse:
    """Enhanced health check with database pool monitoring.

    Returns:
        Health status with database and pool metrics
    """
    db_monitor = startup_manager.get_db_monitor()

    if db_monitor is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "initializing",
                "database": "not_initialized",
                "version": settings.APP_VERSION or "1.0.0",
                "message": "Database monitoring not yet initialized",
            },
        )

    health_status = db_monitor.health_check()
    status_code = 200 if health_status["status"] == "healthy" else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": health_status["status"],
            "database": health_status.get("connectivity", "unknown"),
            "version": settings.APP_VERSION or "1.0.0",
            "pool_metrics": health_status.get("pool_metrics", {}),
            "recommendations": health_status.get("recommendations", []),
        },
    )

def database_metrics() -> JSONResponse:
    """Database connection pool metrics endpoint.

    Returns:
        Database pool metrics and recommendations
    """
    try:
        db_monitor = startup_manager.get_db_monitor()

        if db_monitor is None:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Database monitor not initialized",
                    "detail": "Database monitoring is not available",
                },
            )

        pool_status = db_monitor.get_pool_status()
        db_monitor.log_pool_metrics()  # Log metrics for monitoring

        return JSONResponse(
            status_code=200,
            content={
                "pool_metrics": pool_status,
                "recommendations": db_monitor._get_recommendations(pool_status),
            },
        )
    except Exception as e:
        logger.error(f"Failed to retrieve database metrics: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to retrieve database metrics", "detail": str(e)},
        )

def cache_metrics() -> JSONResponse:
    """Redis cache metrics and statistics endpoint.

    Returns:
        Cache statistics and configuration
    """
    try:
        cache_stats = cache.get_stats()

        return JSONResponse(
            status_code=200,
            content={
                "cache_stats": cache_stats,
                "cache_config": {
                    "redis_host": (
                        cache.redis_client.connection_pool.connection_kwargs.get("host")
                        if cache.is_available
                        else "N/A"
                    ),
                    "redis_port": (
                        cache.redis_client.connection_pool.connection_kwargs.get("port")
                        if cache.is_available
                        else "N/A"
                    ),
                    "is_available": cache.is_available,
                    "default_ttl": 3600,
                },
            },
        )
    except Exception as e:
        logger.error(f"Failed to retrieve cache metrics: {e}")
        return JSONResponse(
            status_code=500, content={"error": "Failed to retrieve cache metrics", "detail": str(e)}
        )

def clear_user_cache(user_id: int) -> JSONResponse:
    """Clear all cache entries for a specific user.

    Args:
        user_id: User ID to clear cache for

    Returns:
        Success message with number of deleted entries
    """
    try:
        deleted_count = cache.clear_user_cache(user_id)
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Cache cleared for user {user_id}",
                "deleted_entries": deleted_count,
            },
        )
    except Exception as e:
        logger.error(f"Failed to clear user cache: {e}")
        return JSONResponse(
            status_code=500, content={"error": "Failed to clear user cache", "detail": str(e)}
        )
