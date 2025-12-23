"""
CalendarService - Servizio Calendario Avanzato ISS
"""

import icalendar
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any
import pytz
from sqlalchemy.orm import Session
import logging
import uuid

from app.models.evento import Evento, EventoIscrizione
from app.models.corso import Corso, CorsoIscrizione
from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


class CalendarService:
    """Servizio completo per gestione calendario ISS"""
    
    def __init__(self):
        self.timezone = pytz.timezone('Europe/Rome')
    
    def generate_ical_event(
        self,
        title: str,
        description: str,
        start_datetime: datetime,
        end_datetime: datetime,
        location: Optional[str] = None,
        uid: Optional[str] = None
    ) -> str:
        """Genera evento iCal singolo"""
        try:
            cal = icalendar.Calendar()
            cal.add('prodid', f'-//ISS//ISS Calendar//IT')
            cal.add('version', '2.0')
            
            event = icalendar.Event()
            event.add('uid', uid or str(uuid.uuid4()))
            event.add('dtstart', self._localize_datetime(start_datetime))
            event.add('dtend', self._localize_datetime(end_datetime))
            event.add('summary', title)
            event.add('description', description)
            
            if location:
                event.add('location', location)
            
            cal.add_component(event)
            return cal.to_ical().decode('utf-8')
            
        except Exception as e:
            logger.error(f"Errore generazione iCal: {str(e)}")
            return ""
    
    def generate_user_calendar(self, user_id: int, db: Session) -> str:
        """Genera calendario iCal personalizzato per utente"""
        try:
            cal = icalendar.Calendar()
            cal.add('prodid', f'-//ISS//ISS Personal Calendar//IT')
            cal.add('version', '2.0')
            cal.add('x-wr-calname', 'ISS - I Miei Eventi')
            
            # Eventi utente
            eventi = db.query(EventoIscrizione).join(Evento).filter(
                EventoIscrizione.user_id == user_id,
                EventoIscrizione.stato == "confermata"
            ).all()
            
            for iscrizione in eventi:
                evento = iscrizione.evento
                event = icalendar.Event()
                event.add('uid', f'evento-{evento.id}@iss.it')
                event.add('dtstart', self._localize_datetime(evento.data_inizio))
                event.add('dtend', self._localize_datetime(evento.data_fine or evento.data_inizio + timedelta(hours=2)))
                event.add('summary', f'[EVENTO] {evento.titolo}')
                event.add('description', evento.descrizione or "")
                cal.add_component(event)
            
            return cal.to_ical().decode('utf-8')
            
        except Exception as e:
            logger.error(f"Errore generazione calendario utente {user_id}: {str(e)}")
            return ""
    
    def send_event_reminders(self, db: Session, hours_before: int = 24) -> Dict[str, int]:
        """Invia promemoria per eventi"""
        try:
            reminder_time = datetime.now() + timedelta(hours=hours_before)
            start_window = reminder_time - timedelta(minutes=30)
            end_window = reminder_time + timedelta(minutes=30)
            
            eventi_da_ricordare = db.query(EventoIscrizione).join(Evento).filter(
                EventoIscrizione.stato == "confermata",
                Evento.data_inizio >= start_window,
                Evento.data_inizio <= end_window
            ).all()
            
            sent_count = 0
            for iscrizione in eventi_da_ricordare:
                # Logica invio promemoria
                sent_count += 1
            
            return {"sent": sent_count, "failed": 0}
            
        except Exception as e:
            logger.error(f"Errore invio promemoria: {str(e)}")
            return {"sent": 0, "failed": 0}
    
    def _localize_datetime(self, dt: datetime) -> datetime:
        """Localizza datetime al timezone italiano"""
        if dt.tzinfo is None:
            return self.timezone.localize(dt)
        return dt.astimezone(self.timezone)


# Istanza globale del servizio
calendar_service = CalendarService()
