"""
Analytics Models - Event tracking
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class AnalyticsEvent(Base):
    """
    Eventi analytics per tracking.
    
    Traccia tutte le interazioni utente per analytics.
    """
    __tablename__ = "analytics_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Tipo evento
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # page_view, project_click, service_click, booking_created, contact_form_submit
    
    # Risorsa
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    # project, service, booking, user
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    
    # User info
    user_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    session_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    
    # Request info
    ip_address: Mapped[str] = mapped_column(String(50), nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    referrer: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Metadata aggiuntivo (renamed from metadata to avoid SQLAlchemy conflict)
    event_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )
    
    # Indexes per query performance
    __table_args__ = (
        Index('idx_event_resource', 'event_type', 'resource_type', 'resource_id'),
        Index('idx_event_date', 'event_type', 'created_at'),
        Index('idx_session_date', 'session_id', 'created_at'),
    )
