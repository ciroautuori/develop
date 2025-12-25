"""
Dashboard Stats Service - Metriche reali per admin dashboard.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.domain.portfolio.models import Project, Service, ContactRequest
from app.domain.booking.models import Booking


class DashboardStatsService:
    """Servizio per calcolo statistiche dashboard."""
    
    @staticmethod
    def get_overview_stats(db: Session) -> Dict[str, Any]:
        """
        Statistiche overview dashboard.
        
        Returns:
            Dict con total_projects, total_bookings, total_contacts, etc.
        """
        # Projects count
        total_projects = db.query(Project).filter(
            Project.is_public == True
        ).count()
        
        active_projects = db.query(Project).filter(
            Project.status == "active",
            Project.is_public == True
        ).count()
        
        # Bookings count
        total_bookings = db.query(Booking).count()
        
        pending_bookings = db.query(Booking).filter(
            Booking.status == "pending"
        ).count()
        
        # Contacts count
        total_contacts = db.query(ContactRequest).count()
        
        unread_contacts = db.query(ContactRequest).filter(
            ContactRequest.status == "new"
        ).count()
        
        # Services count
        total_services = db.query(Service).filter(
            Service.is_active == True
        ).count()
        
        # Growth calculations (last 30 days vs previous 30 days)
        now = datetime.utcnow()
        last_30 = now - timedelta(days=30)
        previous_60 = now - timedelta(days=60)
        
        projects_last_30 = db.query(Project).filter(
            Project.created_at >= last_30
        ).count()
        
        projects_previous_30 = db.query(Project).filter(
            Project.created_at >= previous_60,
            Project.created_at < last_30
        ).count()
        
        projects_growth = DashboardStatsService._calculate_growth(
            projects_last_30, 
            projects_previous_30
        )
        
        bookings_last_30 = db.query(Booking).filter(
            Booking.created_at >= last_30
        ).count()
        
        bookings_previous_30 = db.query(Booking).filter(
            Booking.created_at >= previous_60,
            Booking.created_at < last_30
        ).count()
        
        bookings_growth = DashboardStatsService._calculate_growth(
            bookings_last_30,
            bookings_previous_30
        )
        
        contacts_last_30 = db.query(ContactRequest).filter(
            ContactRequest.created_at >= last_30
        ).count()
        
        contacts_previous_30 = db.query(ContactRequest).filter(
            ContactRequest.created_at >= previous_60,
            ContactRequest.created_at < last_30
        ).count()
        
        contacts_growth = DashboardStatsService._calculate_growth(
            contacts_last_30,
            contacts_previous_30
        )
        
        return {
            "projects": {
                "total": total_projects,
                "active": active_projects,
                "growth_percentage": projects_growth
            },
            "bookings": {
                "total": total_bookings,
                "pending": pending_bookings,
                "growth_percentage": bookings_growth
            },
            "contacts": {
                "total": total_contacts,
                "unread": unread_contacts,
                "growth_percentage": contacts_growth
            },
            "services": {
                "total": total_services
            }
        }
    
    @staticmethod
    def get_recent_activity(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recent activity feed.
        
        Returns:
            Lista di attività recenti (bookings, contacts, projects)
        """
        activities = []
        
        # Recent bookings
        recent_bookings = db.query(Booking).order_by(
            desc(Booking.created_at)
        ).limit(limit).all()
        
        for booking in recent_bookings:
            activities.append({
                "type": "booking",
                "id": booking.id,
                "title": f"New booking from {booking.name}",
                "description": f"{booking.service_type} - {booking.budget_range}",
                "timestamp": booking.created_at.isoformat(),
                "status": booking.status
            })
        
        # Recent contacts
        recent_contacts = db.query(ContactRequest).order_by(
            desc(ContactRequest.created_at)
        ).limit(limit).all()
        
        for contact in recent_contacts:
            activities.append({
                "type": "contact",
                "id": contact.id,
                "title": f"New contact from {contact.name}",
                "description": contact.subject,
                "timestamp": contact.created_at.isoformat(),
                "status": contact.status
            })
        
        # Recent projects
        recent_projects = db.query(Project).order_by(
            desc(Project.created_at)
        ).limit(limit).all()
        
        for project in recent_projects:
            activities.append({
                "type": "project",
                "id": project.id,
                "title": f"Project updated: {project.title}",
                "description": project.category,
                "timestamp": project.updated_at.isoformat(),
                "status": project.status
            })
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]
    
    @staticmethod
    def get_projects_by_status(db: Session) -> Dict[str, int]:
        """Distribuzione progetti per status."""
        results = db.query(
            Project.status,
            func.count(Project.id).label("count")
        ).group_by(Project.status).all()
        
        return {status: count for status, count in results}
    
    @staticmethod
    def get_bookings_by_status(db: Session) -> Dict[str, int]:
        """Distribuzione bookings per status."""
        results = db.query(
            Booking.status,
            func.count(Booking.id).label("count")
        ).group_by(Booking.status).all()
        
        return {status: count for status, count in results}
    
    @staticmethod
    def get_contacts_by_type(db: Session) -> Dict[str, int]:
        """Distribuzione contatti per tipo."""
        results = db.query(
            ContactRequest.request_type,
            func.count(ContactRequest.id).label("count")
        ).group_by(ContactRequest.request_type).all()
        
        return {req_type: count for req_type, count in results}
    
    @staticmethod
    def get_monthly_stats(db: Session, months: int = 6) -> Dict[str, List[Dict]]:
        """
        Stats mensili per grafici.
        
        Returns ultimi N mesi di dati per projects, bookings, contacts.
        """
        now = datetime.utcnow()
        monthly_data = {
            "projects": [],
            "bookings": [],
            "contacts": []
        }
        
        for i in range(months):
            month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            # Projects this month
            projects_count = db.query(Project).filter(
                Project.created_at >= month_start,
                Project.created_at <= month_end
            ).count()
            
            # Bookings this month
            bookings_count = db.query(Booking).filter(
                Booking.created_at >= month_start,
                Booking.created_at <= month_end
            ).count()
            
            # Contacts this month
            contacts_count = db.query(ContactRequest).filter(
                ContactRequest.created_at >= month_start,
                ContactRequest.created_at <= month_end
            ).count()
            
            month_label = month_start.strftime("%b %Y")
            
            monthly_data["projects"].insert(0, {
                "month": month_label,
                "count": projects_count
            })
            monthly_data["bookings"].insert(0, {
                "month": month_label,
                "count": bookings_count
            })
            monthly_data["contacts"].insert(0, {
                "month": month_label,
                "count": contacts_count
            })
        
        return monthly_data
    
    @staticmethod
    def _calculate_growth(current: int, previous: int) -> float:
        """
        Calcola percentuale crescita.
        
        Returns:
            Percentuale crescita (es. 25.5 per +25.5%)
        """
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        
        growth = ((current - previous) / previous) * 100
        return round(growth, 1)
