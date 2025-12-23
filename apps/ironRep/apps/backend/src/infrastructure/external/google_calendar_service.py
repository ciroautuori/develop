"""
Google Calendar Service - Workout scheduling.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class GoogleCalendarService:
    """Google Calendar API for workout events."""

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.service = build("calendar", "v3", credentials=credentials)

    def create_workout_event(self, title: str, description: str, start_time: datetime,
                            duration_minutes: int = 60, exercises: Optional[List[str]] = None) -> Dict[str, Any]:
        end_time = start_time + timedelta(minutes=duration_minutes)
        full_desc = f"🏋️ {description}\n\n"
        if exercises:
            full_desc += "📋 Esercizi:\n" + "\n".join(f"• {ex}" for ex in exercises) + "\n"
        full_desc += "\n🔗 IronRep"

        event = {
            "summary": f"💪 {title}",
            "description": full_desc,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "Europe/Rome"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "Europe/Rome"},
            "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 30}]},
            "colorId": "11",
        }

        try:
            created = self.service.events().insert(calendarId="primary", body=event).execute()
            logger.info(f"Created event: {created.get('id')}")
            return {"event_id": created.get("id"), "html_link": created.get("htmlLink"), "summary": created.get("summary")}
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise

    def list_upcoming_events(self, days: int = 7, max_results: int = 20) -> List[Dict[str, Any]]:
        now = datetime.utcnow().isoformat() + "Z"
        future = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"
        try:
            result = self.service.events().list(calendarId="primary", timeMin=now, timeMax=future,
                                                maxResults=max_results, singleEvents=True, orderBy="startTime").execute()
            return [{"event_id": e.get("id"), "summary": e.get("summary"),
                    "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date")),
                    "html_link": e.get("htmlLink")} for e in result.get("items", [])]
        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            return []

    def delete_event(self, event_id: str) -> bool:
        try:
            self.service.events().delete(calendarId="primary", eventId=event_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return False
