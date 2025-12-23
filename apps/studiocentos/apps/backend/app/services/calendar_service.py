"""
Google Calendar Service - Integrazione completa
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Servizio per gestione Google Calendar."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self):
        self.credentials = None
        self.service = None
    
    def get_oauth_flow(self, redirect_uri: str) -> Flow:
        """
        Crea OAuth2 flow per autenticazione Google.
        
        Args:
            redirect_uri: URL di redirect dopo auth
            
        Returns:
            Flow: OAuth2 flow configurato
        """
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        return flow
    
    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """
        Genera URL per autorizzazione Google.
        
        Args:
            redirect_uri: URL di redirect
            state: State token per sicurezza
            
        Returns:
            str: URL di autorizzazione
        """
        flow = self.get_oauth_flow(redirect_uri)
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'
        )
        return auth_url
    
    def exchange_code_for_tokens(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Scambia authorization code per access/refresh tokens.
        
        Args:
            code: Authorization code da Google
            redirect_uri: URL di redirect usato
            
        Returns:
            Dict con tokens (access_token, refresh_token, etc.)
        """
        flow = self.get_oauth_flow(redirect_uri)
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
    
    def load_credentials(self, token_data: Dict[str, Any]) -> Credentials:
        """
        Carica credentials da token data.
        
        Args:
            token_data: Dict con token info
            
        Returns:
            Credentials: Google credentials
        """
        credentials = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )
        
        # Refresh se scaduto
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        
        return credentials
    
    def initialize_service(self, credentials: Credentials):
        """
        Inizializza servizio Google Calendar.
        
        Args:
            credentials: Google credentials
        """
        self.credentials = credentials
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        Lista tutti i calendari dell'utente.
        
        Returns:
            List di calendari
        """
        if not self.service:
            raise ValueError("Service not initialized")
        
        try:
            calendar_list = self.service.calendarList().list().execute()
            return calendar_list.get('items', [])
        except HttpError as e:
            logger.error(f"Error listing calendars: {e}")
            raise
    
    def get_events(
        self,
        calendar_id: str = 'primary',
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Ottieni eventi da calendario.
        
        Args:
            calendar_id: ID calendario (default: primary)
            time_min: Data inizio range
            time_max: Data fine range
            max_results: Numero massimo risultati
            
        Returns:
            List di eventi
        """
        if not self.service:
            raise ValueError("Service not initialized")
        
        # Default: prossimi 30 giorni
        if not time_min:
            time_min = datetime.utcnow()
        if not time_max:
            time_max = time_min + timedelta(days=30)
        
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except HttpError as e:
            logger.error(f"Error getting events: {e}")
            raise
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Crea nuovo evento.
        
        Args:
            summary: Titolo evento
            start_time: Data/ora inizio
            end_time: Data/ora fine
            description: Descrizione
            location: Luogo
            attendees: Lista email partecipanti
            calendar_id: ID calendario
            
        Returns:
            Dict con evento creato
        """
        if not self.service:
            raise ValueError("Service not initialized")
        
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Europe/Rome',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Europe/Rome',
            },
        }
        
        if description:
            event['description'] = description
        
        if location:
            event['location'] = location
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
            event['conferenceData'] = {
                'createRequest': {
                    'requestId': f"meet-{datetime.utcnow().timestamp()}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        
        try:
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                conferenceDataVersion=1 if attendees else 0,
                sendUpdates='all' if attendees else 'none'
            ).execute()
            
            return created_event
        except HttpError as e:
            logger.error(f"Error creating event: {e}")
            raise
    
    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Aggiorna evento esistente.
        
        Args:
            event_id: ID evento da aggiornare
            summary: Nuovo titolo
            start_time: Nuova data/ora inizio
            end_time: Nuova data/ora fine
            description: Nuova descrizione
            location: Nuovo luogo
            calendar_id: ID calendario
            
        Returns:
            Dict con evento aggiornato
        """
        if not self.service:
            raise ValueError("Service not initialized")
        
        try:
            # Get evento esistente
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Aggiorna campi
            if summary:
                event['summary'] = summary
            if start_time:
                event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Europe/Rome',
                }
            if end_time:
                event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Europe/Rome',
                }
            if description:
                event['description'] = description
            if location:
                event['location'] = location
            
            # Update
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            return updated_event
        except HttpError as e:
            logger.error(f"Error updating event: {e}")
            raise
    
    def delete_event(
        self,
        event_id: str,
        calendar_id: str = 'primary',
        send_updates: bool = True
    ):
        """
        Elimina evento.
        
        Args:
            event_id: ID evento da eliminare
            calendar_id: ID calendario
            send_updates: Invia notifiche ai partecipanti
        """
        if not self.service:
            raise ValueError("Service not initialized")
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all' if send_updates else 'none'
            ).execute()
        except HttpError as e:
            logger.error(f"Error deleting event: {e}")
            raise
    
    def get_availability_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        slot_duration_minutes: int = 60,
        calendar_id: str = 'primary'
    ) -> List[Dict[str, datetime]]:
        """
        Calcola slot disponibili in un range di date.
        
        Args:
            start_date: Data inizio
            end_date: Data fine
            slot_duration_minutes: Durata slot in minuti
            calendar_id: ID calendario
            
        Returns:
            List di slot disponibili {start, end}
        """
        # Get eventi esistenti
        events = self.get_events(calendar_id, start_date, end_date)
        
        # Orario lavorativo: 9:00 - 18:00
        working_hours_start = 9
        working_hours_end = 18
        
        available_slots = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            # Skip weekend
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_date += timedelta(days=1)
                continue
            
            # Genera slot per la giornata
            slot_start = datetime.combine(
                current_date,
                datetime.min.time().replace(hour=working_hours_start)
            )
            day_end = datetime.combine(
                current_date,
                datetime.min.time().replace(hour=working_hours_end)
            )
            
            while slot_start + timedelta(minutes=slot_duration_minutes) <= day_end:
                slot_end = slot_start + timedelta(minutes=slot_duration_minutes)
                
                # Check se slot è libero
                is_free = True
                for event in events:
                    event_start = datetime.fromisoformat(
                        event['start'].get('dateTime', event['start'].get('date'))
                    )
                    event_end = datetime.fromisoformat(
                        event['end'].get('dateTime', event['end'].get('date'))
                    )
                    
                    # Check overlap
                    if not (slot_end <= event_start or slot_start >= event_end):
                        is_free = False
                        break
                
                if is_free:
                    available_slots.append({
                        'start': slot_start,
                        'end': slot_end
                    })
                
                slot_start = slot_end
            
            current_date += timedelta(days=1)
        
        return available_slots


# Singleton instance
calendar_service = GoogleCalendarService()
