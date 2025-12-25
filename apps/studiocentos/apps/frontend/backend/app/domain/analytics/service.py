"""
Analytics Service - Event tracking and aggregation
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from .models import AnalyticsEvent


class AnalyticsService:
    """Servizio per analytics e tracking."""
    
    @staticmethod
    def track_event(
        db: Session,
        event_type: str,
        session_id: str,
        ip_address: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        user_id: Optional[int] = None,
        user_agent: Optional[str] = None,
        referrer: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnalyticsEvent:
        """Traccia evento analytics."""
        event = AnalyticsEvent(
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            event_metadata=metadata or {}
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    
    @staticmethod
    def get_overview(db: Session, days: int = 30) -> Dict[str, Any]:
        """Ottieni overview analytics."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total events
        total_events = db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(AnalyticsEvent.created_at >= start_date)
        ).scalar()
        
        # Unique sessions
        unique_sessions = db.execute(
            select(func.count(func.distinct(AnalyticsEvent.session_id)))
            .where(AnalyticsEvent.created_at >= start_date)
        ).scalar()
        
        # Page views
        page_views = db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(
                and_(
                    AnalyticsEvent.event_type == 'page_view',
                    AnalyticsEvent.created_at >= start_date
                )
            )
        ).scalar()
        
        # Project clicks
        project_clicks = db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(
                and_(
                    AnalyticsEvent.event_type == 'project_click',
                    AnalyticsEvent.created_at >= start_date
                )
            )
        ).scalar()
        
        # Bookings created
        bookings_created = db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(
                and_(
                    AnalyticsEvent.event_type == 'booking_created',
                    AnalyticsEvent.created_at >= start_date
                )
            )
        ).scalar()
        
        # Conversion rate
        conversion_rate = (bookings_created / unique_sessions * 100) if unique_sessions > 0 else 0
        
        return {
            'period_days': days,
            'total_events': total_events,
            'unique_sessions': unique_sessions,
            'page_views': page_views,
            'project_clicks': project_clicks,
            'bookings_created': bookings_created,
            'conversion_rate': round(conversion_rate, 2)
        }
    
    @staticmethod
    def get_project_analytics(db: Session, project_id: int, days: int = 30) -> Dict[str, Any]:
        """Analytics per singolo progetto."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Views
        views = db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(
                and_(
                    AnalyticsEvent.event_type == 'project_view',
                    AnalyticsEvent.resource_type == 'project',
                    AnalyticsEvent.resource_id == project_id,
                    AnalyticsEvent.created_at >= start_date
                )
            )
        ).scalar()
        
        # Clicks
        clicks = db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(
                and_(
                    AnalyticsEvent.event_type == 'project_click',
                    AnalyticsEvent.resource_type == 'project',
                    AnalyticsEvent.resource_id == project_id,
                    AnalyticsEvent.created_at >= start_date
                )
            )
        ).scalar()
        
        # Unique visitors
        unique_visitors = db.execute(
            select(func.count(func.distinct(AnalyticsEvent.session_id)))
            .where(
                and_(
                    AnalyticsEvent.resource_type == 'project',
                    AnalyticsEvent.resource_id == project_id,
                    AnalyticsEvent.created_at >= start_date
                )
            )
        ).scalar()
        
        return {
            'project_id': project_id,
            'period_days': days,
            'views': views,
            'clicks': clicks,
            'unique_visitors': unique_visitors,
            'ctr': round((clicks / views * 100) if views > 0 else 0, 2)
        }
    
    @staticmethod
    def get_service_analytics(db: Session, service_id: int, days: int = 30) -> Dict[str, Any]:
        """Analytics per singolo servizio."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Views
        views = db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(
                and_(
                    AnalyticsEvent.event_type == 'service_view',
                    AnalyticsEvent.resource_type == 'service',
                    AnalyticsEvent.resource_id == service_id,
                    AnalyticsEvent.created_at >= start_date
                )
            )
        ).scalar()
        
        # Clicks
        clicks = db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(
                and_(
                    AnalyticsEvent.event_type == 'service_click',
                    AnalyticsEvent.resource_type == 'service',
                    AnalyticsEvent.resource_id == service_id,
                    AnalyticsEvent.created_at >= start_date
                )
            )
        ).scalar()
        
        return {
            'service_id': service_id,
            'period_days': days,
            'views': views,
            'clicks': clicks,
            'ctr': round((clicks / views * 100) if views > 0 else 0, 2)
        }
    
    @staticmethod
    def get_traffic_over_time(db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """Traffic giornaliero."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Group by date
        results = db.execute(
            select(
                func.date(AnalyticsEvent.created_at).label('date'),
                func.count(AnalyticsEvent.id).label('events'),
                func.count(func.distinct(AnalyticsEvent.session_id)).label('sessions')
            )
            .where(AnalyticsEvent.created_at >= start_date)
            .group_by(func.date(AnalyticsEvent.created_at))
            .order_by(func.date(AnalyticsEvent.created_at))
        ).all()
        
        return [
            {
                'date': str(row.date),
                'events': row.events,
                'sessions': row.sessions
            }
            for row in results
        ]
    
    @staticmethod
    def get_top_projects(db: Session, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """Top progetti per views."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.execute(
            select(
                AnalyticsEvent.resource_id,
                func.count(AnalyticsEvent.id).label('views')
            )
            .where(
                and_(
                    AnalyticsEvent.event_type == 'project_view',
                    AnalyticsEvent.resource_type == 'project',
                    AnalyticsEvent.created_at >= start_date
                )
            )
            .group_by(AnalyticsEvent.resource_id)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(limit)
        ).all()
        
        return [
            {'project_id': row.resource_id, 'views': row.views}
            for row in results
        ]
    
    @staticmethod
    def get_top_services(db: Session, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """Top servizi per views."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.execute(
            select(
                AnalyticsEvent.resource_id,
                func.count(AnalyticsEvent.id).label('views')
            )
            .where(
                and_(
                    AnalyticsEvent.event_type == 'service_view',
                    AnalyticsEvent.resource_type == 'service',
                    AnalyticsEvent.created_at >= start_date
                )
            )
            .group_by(AnalyticsEvent.resource_id)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(limit)
        ).all()
        
        return [
            {'service_id': row.resource_id, 'views': row.views}
            for row in results
        ]
