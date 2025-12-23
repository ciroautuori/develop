"""
AnalyticsService - Servizio Analytics ISS
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import logging

from app.models.user import User
from app.models.evento import Evento, EventoIscrizione
from app.models.corso import Corso, CorsoIscrizione
from app.models.progetto import Progetto

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Servizio analytics ISS"""
    
    def get_dashboard_overview(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Dashboard overview con metriche principali"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Metriche base
            total_users = db.query(User).count()
            new_users = db.query(User).filter(User.created_at >= start_date).count()
            total_events = db.query(Evento).filter(Evento.data_inizio >= start_date).count()
            active_projects = db.query(Progetto).filter(Progetto.stato == "in_corso").count()
            
            return {
                "period_days": days,
                "users": {"total": total_users, "new": new_users},
                "events": {"total": total_events},
                "projects": {"active": active_projects}
            }
            
        except Exception as e:
            logger.error(f"Errore dashboard: {str(e)}")
            return {}
    
    def get_user_analytics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Analytics utenti"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Registrazioni giornaliere
            daily_registrations = db.query(
                func.date(User.created_at).label('date'),
                func.count(User.id).label('count')
            ).filter(User.created_at >= start_date).group_by(func.date(User.created_at)).all()
            
            return {
                "daily_registrations": [
                    {"date": reg.date.isoformat(), "count": reg.count}
                    for reg in daily_registrations
                ]
            }
            
        except Exception as e:
            logger.error(f"Errore user analytics: {str(e)}")
            return {}
    
    def get_event_analytics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Analytics eventi"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Eventi per categoria
            category_stats = db.query(
                Evento.categoria,
                func.count(Evento.id).label('count')
            ).filter(Evento.data_inizio >= start_date).group_by(Evento.categoria).all()
            
            return {
                "category_stats": [
                    {"category": stat.categoria.value if stat.categoria else "N/A", "count": stat.count}
                    for stat in category_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"Errore event analytics: {str(e)}")
            return {}
    
    def generate_report(self, db: Session, report_type: str, days: int = 30) -> Dict[str, Any]:
        """Genera report specifico"""
        try:
            if report_type == "overview":
                return self.get_dashboard_overview(db, days)
            elif report_type == "users":
                return self.get_user_analytics(db, days)
            elif report_type == "events":
                return self.get_event_analytics(db, days)
            else:
                return {"error": "Tipo report non supportato"}
                
        except Exception as e:
            logger.error(f"Errore generazione report {report_type}: {str(e)}")
            return {"error": str(e)}


# Istanza globale del servizio
analytics_service = AnalyticsService()
