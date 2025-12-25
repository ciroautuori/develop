"""API v1 Router - Main API Router Aggregation.

Aggregates all domain routers into a single API router with /api/v1 prefix.
"""

from fastapi import APIRouter

# StudiocentOS - Only essential domains
from app.domain.auth.api_key_router import router as api_key_router
from app.domain.auth.mfa_router import router as mfa_router
from app.domain.auth.password_reset_router import router as password_reset_router
from app.domain.auth.routers import router as auth_router
from app.domain.auth.username_router import router as username_router

# iModels - AI Models Management
from app.domain.imodels.router import router as imodels_router

# Marketing - Removed, registered directly in main.py to avoid double prefix

# Main API router with /api/v1 prefix
api_router = APIRouter(prefix="/api/v1")

# ============================================================================
# AUTH DOMAIN - Authentication & Authorization
# ============================================================================
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    mfa_router,
    prefix="/auth/mfa",
    tags=["Authentication - MFA"]
)

api_router.include_router(
    password_reset_router,
    prefix="/auth/password",
    tags=["Authentication - Password Reset"]
)

api_router.include_router(
    username_router,
    prefix="/auth/username",
    tags=["Authentication - Username"]
)

api_router.include_router(
    api_key_router,
    prefix="/auth/api-keys",
    tags=["Authentication - API Keys"]
)

# ============================================================================
# iMODELS DOMAIN - AI Models Management
# ============================================================================
api_router.include_router(
    imodels_router,
    tags=["iModels - AI Management"]
)

# ============================================================================
# MARKETING DOMAIN - Removed from here, registered directly in main.py
# ============================================================================
# NOTE: marketing_router is registered in main.py to avoid double prefix issue

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@api_router.get(
    "/health",
    tags=["Health"],
    summary="API Health Check",
    description="Check if the API v1 is running and healthy",
    response_description="Health status with service information"
)
async def api_health():
    """
    Health check endpoint for API v1.

    Returns service health status, version, and metadata.
    Use for monitoring, load balancers, and deployment verification.
    """
    from datetime import datetime, timezone
    from app.core.config import settings

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "studiocentos-api",
        "api_version": "v1"
    }

# Note: Portfolio, Support, Copilot, and Booking routers are included directly in main.py

__all__ = ["api_router"]
