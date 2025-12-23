from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.database.session import get_db
from app.domain.newsletter.models import NewsletterSubscriber
from app.domain.newsletter.schemas import SubscriberCreate, SubscriberResponse
from app.core.api.dependencies.auth_deps import get_current_admin_user
from sqlalchemy import text

router = APIRouter(prefix="/newsletter", tags=["newsletter"])

@router.post("/subscribe", response_model=SubscriberResponse, status_code=status.HTTP_201_CREATED)
def subscribe_newsletter(
    data: SubscriberCreate,
    db: Session = Depends(get_db)
):
    """
    Public Endpoint: Subscribe to the newsletter.
    Idempotent: If email exists, returns existing record (200 OK ideally, but simpler to just return 201 or record).
    """
    # Check if exists
    existing = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == data.email).first()
    if existing:
        # If unsubscribed, reactivate? Or just return success.
        if existing.status == 'unsubscribed':
            existing.status = 'active'
            db.commit()
            db.refresh(existing)
        return existing

    new_subscriber = NewsletterSubscriber(
        email=data.email,
        source=data.source,
        status="active"
    )
    db.add(new_subscriber)
    db.commit()
    db.refresh(new_subscriber)
    return new_subscriber


@router.get("/subscribers", response_model=List[SubscriberResponse])
def list_subscribers(
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin_user)
):
    """
    Admin Endpoint: List all subscribers.
    """
    return db.query(NewsletterSubscriber).order_by(NewsletterSubscriber.created_at.desc()).all()
