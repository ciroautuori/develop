"""
Booking Services - Integrazione videocall e notifiche.
Now with REAL Google Calendar + Meet + Gmail integration!
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

# Import real Google services
from app.domain.google.calendar_service import (
    create_booking_with_meet,
    update_booking_event,
    cancel_booking_event,
    get_available_slots,
    GoogleCalendarService
)
from app.domain.google.gmail_service import (
    send_booking_confirmation,
    send_booking_reminder
)


async def create_google_meet_link(
    db: Session,
    admin_id: int,
    title: str,
    start_time: datetime,
    duration_minutes: int,
    attendee_email: str,
    attendee_name: str = ""
) -> Optional[Dict[str, Any]]:
    """
    Create Google Meet link using Google Calendar API.

    This creates a real calendar event with Google Meet conference.

    Args:
        db: Database session
        admin_id: Admin user ID (for OAuth token)
        title: Meeting title
        start_time: Meeting start time
        duration_minutes: Meeting duration
        attendee_email: Client email
        attendee_name: Client name

    Returns:
        Dict with event_id, meet_link, html_link, etc.
    """
    result = await create_booking_with_meet(
        db=db,
        admin_id=admin_id,
        booking_title=title,
        booking_description=f"Prenotazione con {attendee_name}",
        start_time=start_time,
        duration_minutes=duration_minutes,
        client_email=attendee_email,
        client_name=attendee_name
    )

    return result


async def create_zoom_meeting(
    title: str,
    start_time: datetime,
    duration_minutes: int
) -> Dict[str, Any]:
    """
    Create Zoom meeting using Zoom API.

    Zoom API integration requires:
    - Zoom App credentials (JWT or OAuth)
    - API endpoint: https://api.zoom.us/v2/users/{userId}/meetings

    See: https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/meetingCreate
    """
    # Placeholder - returns mock meeting URL
    # Configure ZOOM_API_KEY and ZOOM_API_SECRET in environment for production

    return {
        "join_url": f"https://zoom.us/j/placeholder-{start_time.timestamp()}",
        "meeting_id": f"{int(start_time.timestamp())}",
        "password": "123456"
    }


async def send_booking_confirmation_email(
    db: Session,
    admin_id: int,
    booking: Any
) -> bool:
    """
    Send booking confirmation email to client via Gmail API.

    Args:
        db: Database session
        admin_id: Admin user ID
        booking: Booking object with client_email, title, scheduled_at, etc.

    Returns:
        True if email sent successfully
    """
    return await send_booking_confirmation(
        db=db,
        admin_id=admin_id,
        client_email=booking.client_email,
        client_name=booking.client_name,
        booking_title=booking.title,
        booking_date=booking.scheduled_at,
        duration_minutes=booking.duration_minutes,
        meet_link=getattr(booking, 'meeting_url', None),
        calendar_link=getattr(booking, 'calendar_link', None)
    )


async def send_booking_reminder_email(
    db: Session,
    admin_id: int,
    booking: Any,
    hours_before: int = 24
) -> bool:
    """
    Send booking reminder email (24h before) via Gmail API.

    Args:
        db: Database session
        admin_id: Admin user ID
        booking: Booking object
        hours_before: Hours before the meeting

    Returns:
        True if email sent successfully
    """
    return await send_booking_reminder(
        db=db,
        admin_id=admin_id,
        client_email=booking.client_email,
        client_name=booking.client_name,
        booking_title=booking.title,
        booking_date=booking.scheduled_at,
        meet_link=getattr(booking, 'meeting_url', None),
        hours_before=hours_before
    )


async def create_calendar_invite(booking: Any) -> str:
    """
    Create .ics calendar invite file.

    iCalendar format (.ics) generation requires:
    - `icalendar` library (pip install icalendar)
    - Meeting details: title, start, end, location
    - Videocall link as URL or description

    See: RFC 5545 - Internet Calendaring (iCalendar)
    """
    # Placeholder - requires icalendar library
    return "calendar_invite.ics"


async def get_booking_available_slots(
    db: Session,
    admin_id: int,
    date: datetime,
    duration_minutes: int = 60
) -> list:
    """
    Get available booking slots for a date using Google Calendar.

    Args:
        db: Database session
        admin_id: Admin user ID
        date: Date to check
        duration_minutes: Meeting duration

    Returns:
        List of available time slots
    """
    return await get_available_slots(
        db=db,
        admin_id=admin_id,
        date=date,
        duration_minutes=duration_minutes
    )


async def update_booking_calendar_event(
    db: Session,
    admin_id: int,
    event_id: str,
    new_start_time: Optional[datetime] = None,
    new_duration_minutes: Optional[int] = None,
    new_title: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Update an existing booking in Google Calendar.
    """
    return await update_booking_event(
        db=db,
        admin_id=admin_id,
        event_id=event_id,
        new_start_time=new_start_time,
        new_duration_minutes=new_duration_minutes,
        new_title=new_title
    )


async def cancel_booking_calendar_event(
    db: Session,
    admin_id: int,
    event_id: str
) -> bool:
    """
    Cancel/delete a booking from Google Calendar.
    """
    return await cancel_booking_event(
        db=db,
        admin_id=admin_id,
        event_id=event_id
    )
