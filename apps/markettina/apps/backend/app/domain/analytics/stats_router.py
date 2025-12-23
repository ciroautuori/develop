"""
Stats API Router - Dashboard statistics endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.domain.auth.admin_models import AdminUser
from app.domain.auth.dependencies import get_current_admin_user
from app.infrastructure.database.session import get_db

from .stats_service import DashboardStatsService

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview")
def get_overview_stats(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Get dashboard overview statistics.
    
    Returns counts and growth percentages for:
    - Projects
    - Bookings
    - Contacts
    - Services
    """
    stats = DashboardStatsService.get_overview_stats(db)
    return {"success": True, "data": stats}


@router.get("/activity")
def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get recent activity feed."""
    activities = DashboardStatsService.get_recent_activity(db, limit)
    return {"success": True, "data": activities}


@router.get("/projects/by-status")
def get_projects_by_status(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get projects distribution by status."""
    stats = DashboardStatsService.get_projects_by_status(db)
    return {"success": True, "data": stats}


@router.get("/bookings/by-status")
def get_bookings_by_status(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get bookings distribution by status."""
    stats = DashboardStatsService.get_bookings_by_status(db)
    return {"success": True, "data": stats}


@router.get("/contacts/by-type")
def get_contacts_by_type(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get contacts distribution by type."""
    stats = DashboardStatsService.get_contacts_by_type(db)
    return {"success": True, "data": stats}


@router.get("/monthly")
def get_monthly_stats(
    months: int = 6,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Get monthly statistics for charts.
    
    Args:
        months: Number of months to retrieve (default 6)
    """
    stats = DashboardStatsService.get_monthly_stats(db, months)
    return {"success": True, "data": stats}
