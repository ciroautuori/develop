"""
Analytics Router - Tracking and reporting endpoints
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.infrastructure.database.session import get_db
from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser

from .service import AnalyticsService

router = APIRouter(tags=["analytics"])


# ============================================================================
# SCHEMAS
# ============================================================================

class TrackEventRequest(BaseModel):
    """Schema per tracking evento."""
    event_type: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    session_id: str
    metadata: Optional[dict] = None


# ============================================================================
# PUBLIC ENDPOINTS (Tracking)
# ============================================================================

@router.post("/api/v1/analytics/track")
def track_event(
    data: TrackEventRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Traccia evento analytics (public endpoint).
    
    Chiamato dal frontend per trackare eventi utente.
    """
    # Get client info
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")
    
    event = AnalyticsService.track_event(
        db=db,
        event_type=data.event_type,
        session_id=data.session_id,
        ip_address=ip_address,
        resource_type=data.resource_type,
        resource_id=data.resource_id,
        user_agent=user_agent,
        referrer=referrer,
        metadata=data.metadata
    )
    
    return {"success": True, "event_id": event.id}


# ============================================================================
# ADMIN ENDPOINTS (Reporting)
# ============================================================================

@router.get("/api/v1/admin/analytics/overview")
def get_analytics_overview(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Overview analytics generale."""
    return AnalyticsService.get_overview(db, days)


@router.get("/api/v1/admin/analytics/projects/{project_id}")
def get_project_analytics(
    project_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Analytics per singolo progetto."""
    return AnalyticsService.get_project_analytics(db, project_id, days)


@router.get("/api/v1/admin/analytics/services/{service_id}")
def get_service_analytics(
    service_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Analytics per singolo servizio."""
    return AnalyticsService.get_service_analytics(db, service_id, days)


@router.get("/api/v1/admin/analytics/traffic")
def get_traffic_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Traffic over time."""
    return AnalyticsService.get_traffic_over_time(db, days)


@router.get("/api/v1/admin/analytics/top-projects")
def get_top_projects(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Top progetti per views."""
    return AnalyticsService.get_top_projects(db, days, limit)


@router.get("/api/v1/admin/analytics/top-services")
def get_top_services(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Top servizi per views."""
    return AnalyticsService.get_top_services(db, days, limit)
