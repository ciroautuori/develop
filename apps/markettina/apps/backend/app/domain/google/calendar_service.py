"""
Google Calendar + Meet Service
Real implementation using Google Calendar API v3
"""
import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger(__name__)

# Google Calendar API Base URL
CALENDAR_API_BASE = "https://www.googleapis.com/calendar/v3"


def get_admin_google_token(db: Session, admin_id: int) -> str | None:
    """
    Get valid Google OAuth token for admin from admin_google_settings.

    Returns None if no token found or token expired and refresh failed.
    """
    from datetime import datetime

    import httpx

    from app.domain.google.models import AdminGoogleSettings

    settings_obj = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin_id
    ).first()

    if not settings_obj or not settings_obj.access_token:
        logger.warning(f"No Google settings found for admin {admin_id}")
        return None

    # Check if token is expired
    if settings_obj.token_expires_at:
        now = datetime.now(UTC)
        if settings_obj.token_expires_at.replace(tzinfo=UTC) > now:
            # Token still valid
            return settings_obj.access_token

    # Token expired, try to refresh
    if not settings_obj.refresh_token:
        logger.warning(f"No refresh token for admin {admin_id}")
        return None

    try:
        logger.info(f"Refreshing Google token for admin {admin_id}")

        response = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": settings_obj.refresh_token,
                "grant_type": "refresh_token"
            },
            timeout=10.0
        )

        if response.status_code == 200:
            data = response.json()

            # Update tokens
            settings_obj.access_token = data["access_token"]
            settings_obj.token_expires_at = datetime.now(UTC).replace(
                microsecond=0
            ) + timedelta(seconds=data.get("expires_in", 3600))

            db.commit()
            logger.info(f"Google token refreshed for admin {admin_id}")
            return settings_obj.access_token
        logger.error(f"Token refresh failed for admin {admin_id}: {response.status_code}")
        return None

    except Exception as e:
        logger.error(f"Error refreshing token for admin {admin_id}: {e}", exc_info=True)
        return None


class GoogleCalendarService:
    """Service for Google Calendar API with Meet integration."""

    def __init__(self, access_token: str, calendar_id: str = "primary"):
        """
        Initialize Calendar service.

        Args:
            access_token: Valid Google OAuth access token with calendar scope
            calendar_id: Calendar ID (default: primary)
        """
        self.access_token = access_token
        self.calendar_id = calendar_id
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @classmethod
    def from_admin_token(
        cls,
        db: Session,
        admin_id: int,
        calendar_id: str = "primary"
    ) -> Optional["GoogleCalendarService"]:
        """Create service instance from admin's stored OAuth token in admin_google_settings."""
        token = get_admin_google_token(db, admin_id)
        if not token:
            logger.warning(f"No valid Google OAuth token for admin {admin_id}")
            return None
        return cls(access_token=token, calendar_id=calendar_id)

    async def create_event_with_meet(
        self,
        title: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        attendees: list[str],
        send_notifications: bool = True,
        timezone_str: str = "Europe/Rome"
    ) -> dict[str, Any] | None:
        """
        Create a calendar event with Google Meet video conferencing.

        Args:
            title: Event title
            description: Event description
            start_time: Event start time (datetime with timezone)
            end_time: Event end time
            attendees: List of attendee email addresses
            send_notifications: Whether to send email notifications
            timezone_str: Timezone for the event

        Returns:
            Event data including Meet link, or None if failed
        """
        # Generate unique conference request ID
        conference_request_id = str(uuid.uuid4())

        event_body = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": timezone_str,
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": timezone_str,
            },
            "attendees": [{"email": email} for email in attendees],
            "conferenceData": {
                "createRequest": {
                    "requestId": conference_request_id,
                    "conferenceSolutionKey": {
                        "type": "hangoutsMeet"
                    }
                }
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 1440},  # 24h before
                    {"method": "popup", "minutes": 30},    # 30min before
                ]
            }
        }

        url = f"{CALENDAR_API_BASE}/calendars/{self.calendar_id}/events"
        params = {
            "conferenceDataVersion": 1,  # Required for Meet
            "sendUpdates": "all" if send_notifications else "none"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=event_body,
                    params=params,
                    timeout=30.0
                )

                if response.status_code not in [200, 201]:
                    logger.error(f"Calendar API error: {response.status_code} - {response.text}")
                    return None

                data = response.json()

                # Extract Meet link
                meet_link = None
                conference_data = data.get("conferenceData", {})
                entry_points = conference_data.get("entryPoints", [])
                for ep in entry_points:
                    if ep.get("entryPointType") == "video":
                        meet_link = ep.get("uri")
                        break

                return {
                    "event_id": data.get("id"),
                    "html_link": data.get("htmlLink"),
                    "meet_link": meet_link,
                    "meet_id": conference_data.get("conferenceId"),
                    "status": data.get("status"),
                    "created": data.get("created"),
                    "summary": data.get("summary"),
                    "start": data.get("start"),
                    "end": data.get("end"),
                }

        except Exception as e:
            logger.error(f"Error creating calendar event: {e}", exc_info=True)
            return None

    async def update_event(
        self,
        event_id: str,
        title: str | None = None,
        description: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        attendees: list[str] | None = None,
        send_notifications: bool = True,
        timezone_str: str = "Europe/Rome"
    ) -> dict[str, Any] | None:
        """Update an existing calendar event."""

        # First get the existing event
        existing = await self.get_event(event_id)
        if not existing:
            return None

        # Build update body
        event_body = {}

        if title:
            event_body["summary"] = title
        if description:
            event_body["description"] = description
        if start_time:
            event_body["start"] = {
                "dateTime": start_time.isoformat(),
                "timeZone": timezone_str,
            }
        if end_time:
            event_body["end"] = {
                "dateTime": end_time.isoformat(),
                "timeZone": timezone_str,
            }
        if attendees is not None:
            event_body["attendees"] = [{"email": email} for email in attendees]

        url = f"{CALENDAR_API_BASE}/calendars/{self.calendar_id}/events/{event_id}"
        params = {
            "sendUpdates": "all" if send_notifications else "none"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    url,
                    headers=self.headers,
                    json=event_body,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Calendar update error: {response.status_code} - {response.text}")
                    return None

                return response.json()

        except Exception as e:
            logger.error(f"Error updating calendar event: {e}", exc_info=True)
            return None

    async def delete_event(
        self,
        event_id: str,
        send_notifications: bool = True
    ) -> bool:
        """Delete a calendar event."""
        url = f"{CALENDAR_API_BASE}/calendars/{self.calendar_id}/events/{event_id}"
        params = {
            "sendUpdates": "all" if send_notifications else "none"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code not in [200, 204]:
                    logger.error(f"Calendar delete error: {response.status_code} - {response.text}")
                    return False

                return True

        except Exception as e:
            logger.error(f"Error deleting calendar event: {e}", exc_info=True)
            return False

    async def get_event(self, event_id: str) -> dict[str, Any] | None:
        """Get a single calendar event."""
        url = f"{CALENDAR_API_BASE}/calendars/{self.calendar_id}/events/{event_id}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Calendar get error: {response.status_code} - {response.text}")
                    return None

                return response.json()

        except Exception as e:
            logger.error(f"Error getting calendar event: {e}", exc_info=True)
            return None

    async def list_events(
        self,
        time_min: datetime | None = None,
        time_max: datetime | None = None,
        max_results: int = 50,
        single_events: bool = True
    ) -> list[dict[str, Any]]:
        """List calendar events in a time range."""
        if not time_min:
            time_min = datetime.now(UTC)
        if not time_max:
            time_max = time_min + timedelta(days=30)

        url = f"{CALENDAR_API_BASE}/calendars/{self.calendar_id}/events"
        params = {
            "timeMin": time_min.isoformat(),
            "timeMax": time_max.isoformat(),
            "maxResults": max_results,
            "singleEvents": str(single_events).lower(),
            "orderBy": "startTime"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Calendar list error: {response.status_code} - {response.text}")
                    return []

                data = response.json()
                return data.get("items", [])

        except Exception as e:
            logger.error(f"Error listing calendar events: {e}", exc_info=True)
            return []

    async def get_free_busy(
        self,
        time_min: datetime,
        time_max: datetime,
        calendars: list[str] | None = None
    ) -> dict[str, list[dict[str, str]]]:
        """
        Get free/busy information for calendars.

        Returns:
            Dict mapping calendar IDs to list of busy time ranges
        """
        if not calendars:
            calendars = [self.calendar_id]

        url = f"{CALENDAR_API_BASE}/freeBusy"
        body = {
            "timeMin": time_min.isoformat(),
            "timeMax": time_max.isoformat(),
            "items": [{"id": cal} for cal in calendars]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=body,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"FreeBusy error: {response.status_code} - {response.text}")
                    return {}

                data = response.json()
                result = {}

                for cal_id, cal_data in data.get("calendars", {}).items():
                    result[cal_id] = cal_data.get("busy", [])

                return result

        except Exception as e:
            logger.error(f"Error getting free/busy: {e}", exc_info=True)
            return {}

    async def list_calendars(self) -> list[dict[str, Any]]:
        """List all calendars accessible to the user."""
        url = f"{CALENDAR_API_BASE}/users/me/calendarList"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Calendar list error: {response.status_code} - {response.text}")
                    return []

                data = response.json()
                return data.get("items", [])

        except Exception as e:
            logger.error(f"Error listing calendars: {e}", exc_info=True)
            return []


# =============================================================================
# Booking Integration Functions
# =============================================================================

async def create_booking_with_meet(
    db: Session,
    admin_id: int,
    booking_title: str,
    booking_description: str,
    start_time: datetime,
    duration_minutes: int,
    client_email: str,
    client_name: str
) -> dict[str, Any] | None:
    """
    Create a complete booking with Google Calendar event and Meet link.

    This is the main function to call from the booking service.

    Returns:
        Dict with event_id, meet_link, html_link, etc.
    """
    service = GoogleCalendarService.from_admin_token(db, admin_id)
    if not service:
        logger.error(f"Could not create calendar service for admin {admin_id}")
        return None

    end_time = start_time + timedelta(minutes=duration_minutes)

    # Build description with client info
    full_description = f"""
Prenotazione MARKETTINA

👤 Cliente: {client_name}
📧 Email: {client_email}

{booking_description}

---
Gestito da MARKETTINA Backoffice
    """.strip()

    result = await service.create_event_with_meet(
        title=booking_title,
        description=full_description,
        start_time=start_time,
        end_time=end_time,
        attendees=[client_email],
        send_notifications=True
    )

    if result:
        logger.info(f"Created booking event: {result.get('event_id')} with Meet: {result.get('meet_link')}")

    return result


async def update_booking_event(
    db: Session,
    admin_id: int,
    event_id: str,
    new_start_time: datetime | None = None,
    new_duration_minutes: int | None = None,
    new_title: str | None = None
) -> dict[str, Any] | None:
    """Update an existing booking calendar event."""
    service = GoogleCalendarService.from_admin_token(db, admin_id)
    if not service:
        return None

    end_time = None
    if new_start_time and new_duration_minutes:
        end_time = new_start_time + timedelta(minutes=new_duration_minutes)

    return await service.update_event(
        event_id=event_id,
        title=new_title,
        start_time=new_start_time,
        end_time=end_time,
        send_notifications=True
    )


async def cancel_booking_event(
    db: Session,
    admin_id: int,
    event_id: str
) -> bool:
    """Cancel/delete a booking calendar event."""
    service = GoogleCalendarService.from_admin_token(db, admin_id)
    if not service:
        return False

    return await service.delete_event(event_id, send_notifications=True)


async def get_available_slots(
    db: Session,
    admin_id: int,
    date: datetime,
    duration_minutes: int = 60,
    work_start_hour: int = 9,
    work_end_hour: int = 18
) -> list[dict[str, datetime]]:
    """
    Get available time slots for a specific date.

    Returns:
        List of available slots with start and end times
    """
    service = GoogleCalendarService.from_admin_token(db, admin_id)
    if not service:
        return []

    # Set time range for the day
    day_start = date.replace(hour=work_start_hour, minute=0, second=0, microsecond=0)
    day_end = date.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)

    # Get busy times
    busy = await service.get_free_busy(day_start, day_end)
    busy_periods = busy.get("primary", [])

    # Calculate available slots
    available = []
    current = day_start

    for busy_period in busy_periods:
        busy_start = datetime.fromisoformat(busy_period["start"].replace("Z", "+00:00"))
        busy_end = datetime.fromisoformat(busy_period["end"].replace("Z", "+00:00"))

        # If there's time before this busy period
        while current + timedelta(minutes=duration_minutes) <= busy_start:
            available.append({
                "start": current,
                "end": current + timedelta(minutes=duration_minutes)
            })
            current = current + timedelta(minutes=30)  # 30min increments

        # Move past busy period
        current = max(current, busy_end)

    # Add remaining slots after last busy period
    while current + timedelta(minutes=duration_minutes) <= day_end:
        available.append({
            "start": current,
            "end": current + timedelta(minutes=duration_minutes)
        })
        current = current + timedelta(minutes=30)

    return available
