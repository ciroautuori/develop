"""Notifications API Router."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.infrastructure.database.session import get_db
from app.domain.auth.admin_models import AdminUser
from app.core.api.dependencies.auth_deps import get_current_admin_user
from .models import Notification


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def get_notifications(
    unread_only: bool = False,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get admin notifications."""
    query = db.query(Notification).filter(
        Notification.admin_id == admin.id
    )

    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifications = query.order_by(
        desc(Notification.created_at)
    ).limit(limit).offset(offset).all()

    return {
        "success": True,
        "data": [
            {
                "id": n.id,
                "type": n.type,
                "priority": n.priority,
                "title": n.title,
                "message": n.message,
                "action_url": n.action_url,
                "action_text": n.action_text,
                "metadata": n.extra_data,
                "is_read": n.is_read,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "created_at": n.created_at.isoformat()
            }
            for n in notifications
        ]
    }


@router.get("/count")
def get_unread_count(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get unread notifications count."""
    count = db.query(Notification).filter(
        Notification.admin_id == admin.id,
        Notification.is_read == False
    ).count()

    return {"success": True, "data": {"unread_count": count}}


@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Mark notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.admin_id == admin.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()

    return {"success": True, "message": "Notification marked as read"}


@router.post("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Mark all notifications as read."""
    db.query(Notification).filter(
        Notification.admin_id == admin.id,
        Notification.is_read == False
    ).update({
        "is_read": True,
        "read_at": datetime.utcnow()
    })
    db.commit()

    return {"success": True, "message": "All notifications marked as read"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Delete notification."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.admin_id == admin.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {"success": True, "message": "Notification deleted"}


@router.post("/create")
def create_notification(
    type: str,
    title: str,
    message: str,
    priority: str = "medium",
    action_url: Optional[str] = None,
    action_text: Optional[str] = None,
    extra_data: Optional[dict] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Create new notification (for testing/system)."""
    notification = Notification(
        admin_id=admin.id,
        type=type,
        priority=priority,
        title=title,
        message=message,
        action_url=action_url,
        action_text=action_text,
        extra_data=extra_data or {}
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return {
        "success": True,
        "data": {
            "id": notification.id,
            "created_at": notification.created_at.isoformat()
        }
    }
