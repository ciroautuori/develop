"""
Booking API Router - Sistema prenotazione appuntamenti con videocall.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from typing import List
from datetime import datetime, timedelta, date, time as dt_time
import pytz

from app.infrastructure.database.session import get_db
from .models import Booking, AvailabilitySlot, BlockedDate, BookingStatus
from .schemas import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    AvailabilityResponse,
    AvailableSlot,
    CalendarRequest,
    CalendarResponse,
    BlockedDateResponse
)
from .services import (
    create_google_meet_link,
    create_zoom_meeting,
    send_booking_confirmation_email,
    send_booking_reminder_email
)

router = APIRouter(prefix="/api/v1/booking", tags=["booking"])


# ============================================================================
# PUBLIC ENDPOINTS - Calendario e prenotazioni
# ============================================================================

@router.get("/availability")
async def get_availability(
    date: str,
    db: Session = Depends(get_db)
):
    """
    Get availability for a specific date.
    Frontend-compatible endpoint for /api/v1/booking/availability?date=YYYY-MM-DD
    """
    from datetime import datetime, timedelta, time as dt_time

    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Get availability slots for this day of week
    day_of_week = target_date.weekday()
    slots_query = select(AvailabilitySlot).where(
        and_(
            AvailabilitySlot.is_active == True,
            AvailabilitySlot.day_of_week == day_of_week
        )
    )
    slots_result = db.execute(slots_query)
    availability_slots = slots_result.scalars().all()

    # Get existing bookings for this date
    start_datetime = datetime.combine(target_date, dt_time.min)
    end_datetime = datetime.combine(target_date, dt_time.max)

    bookings_query = select(Booking).where(
        and_(
            Booking.scheduled_at >= start_datetime,
            Booking.scheduled_at <= end_datetime,
            Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value])
        )
    )
    bookings_result = db.execute(bookings_query)
    existing_bookings = bookings_result.scalars().all()

    # Generate available time slots
    slots = []
    for slot in availability_slots:
        current_time = datetime.combine(target_date, slot.start_time)
        end_time = datetime.combine(target_date, slot.end_time)

        while current_time < end_time:
            # Check if slot is already booked
            is_available = not any(
                b.scheduled_at <= current_time < b.scheduled_at + timedelta(minutes=b.duration_minutes)
                for b in existing_bookings
            )

            # Only show future slots
            if current_time > datetime.now() and is_available:
                slots.append({
                    "time": current_time.strftime("%H:%M"),
                    "available": True
                })

            current_time += timedelta(minutes=slot.slot_duration)

    return {"slots": slots}

@router.post("/calendar/availability", response_model=CalendarResponse)
async def get_calendar_availability(
    request: CalendarRequest,
    db: Session = Depends(get_db)
):
    """
    Get calendar availability for date range.

    Mostra slot disponibili per prenotare appuntamenti.
    """
    # Get availability slots
    slots_query = select(AvailabilitySlot).where(
        AvailabilitySlot.is_active == True
    )
    if request.service_type:
        slots_query = slots_query.where(
            AvailabilitySlot.service_type == request.service_type
        )

    slots_result = db.execute(slots_query)
    availability_slots = slots_result.scalars().all()

    # Get blocked dates
    blocked_query = select(BlockedDate).where(
        and_(
            BlockedDate.blocked_date >= request.start_date,
            BlockedDate.blocked_date <= request.end_date
        )
    )
    blocked_result = db.execute(blocked_query)
    blocked_dates = [b.blocked_date for b in blocked_result.scalars().all()]

    # Get existing bookings
    bookings_query = select(Booking).where(
        and_(
            Booking.scheduled_at >= datetime.combine(request.start_date, dt_time.min),
            Booking.scheduled_at <= datetime.combine(request.end_date, dt_time.max),
            Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value])
        )
    )
    bookings_result = db.execute(bookings_query)
    existing_bookings = bookings_result.scalars().all()

    # Build availability response
    availability = []
    current_date = request.start_date

    while current_date <= request.end_date:
        if current_date not in blocked_dates:
            day_of_week = current_date.weekday()
            day_slots = [s for s in availability_slots if s.day_of_week == day_of_week]

            available_slots = []
            for slot in day_slots:
                # Generate time slots
                current_time = datetime.combine(current_date, slot.start_time)
                end_time = datetime.combine(current_date, slot.end_time)

                while current_time < end_time:
                    # Check if slot is already booked
                    is_available = not any(
                        b.scheduled_at <= current_time < b.scheduled_at + timedelta(minutes=b.duration_minutes)
                        for b in existing_bookings
                    )

                    # Only show future slots
                    if current_time > datetime.now() and is_available:
                        available_slots.append(AvailableSlot(
                            datetime=current_time,
                            duration_minutes=slot.slot_duration,
                            service_type=slot.service_type,
                            available=True
                        ))

                    current_time += timedelta(minutes=slot.slot_duration)

            if available_slots:
                availability.append(AvailabilityResponse(
                    date=current_date,
                    slots=available_slots,
                    total_available=len(available_slots)
                ))

        current_date += timedelta(days=1)

    return CalendarResponse(
        availability=availability,
        blocked_dates=blocked_dates,
        bookings_count=len(existing_bookings)
    )


@router.post("/bookings", response_model=BookingResponse, status_code=201)
async def create_booking(
    booking: BookingCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Create new booking.

    Prenota un appuntamento con videocall automatica.
    """
    # Validate slot is available
    scheduled_at = booking.scheduled_at

    # Check if slot is in the future
    if scheduled_at <= datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Cannot book appointments in the past"
        )

    # Check for conflicts - get all bookings for that day and check in Python
    start_of_day = datetime.combine(scheduled_at.date(), dt_time.min)
    end_of_day = datetime.combine(scheduled_at.date(), dt_time.max)

    conflict_query = select(Booking).where(
        and_(
            Booking.scheduled_at >= start_of_day,
            Booking.scheduled_at <= end_of_day,
            Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value])
        )
    )
    conflict_result = db.execute(conflict_query)
    existing_bookings = conflict_result.scalars().all()

    # Check if new booking overlaps with any existing booking
    for existing in existing_bookings:
        existing_end = existing.scheduled_at + timedelta(minutes=existing.duration_minutes)
        new_end = scheduled_at + timedelta(minutes=booking.duration_minutes)

        # Check overlap: new starts before existing ends AND new ends after existing starts
        if scheduled_at < existing_end and new_end > existing.scheduled_at:
            raise HTTPException(
                status_code=409,
                detail="This time slot is already booked"
            )

    # Create booking
    # Generate title if not provided
    title = booking.title or f"Consultation with {booking.client_name}"

    new_booking = Booking(
        client_name=booking.client_name,
        client_email=booking.client_email,
        client_phone=booking.client_phone,
        client_company=booking.client_company,
        service_type=booking.service_type,
        title=title,
        description=booking.description or f"Meeting scheduled for {scheduled_at.strftime('%d/%m/%Y at %H:%M')}",
        scheduled_at=scheduled_at,
        duration_minutes=booking.duration_minutes,
        timezone=booking.timezone,
        status=BookingStatus.PENDING.value,
        meeting_provider=booking.meeting_provider,
        client_notes=booking.client_notes,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer")
    )

    # Save booking first to get ID
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    # Generate meeting link based on provider
    # Use admin_id=1 (default admin) for public bookings
    admin_id = 1

    try:
        if booking.meeting_provider == "google_meet":
            meeting_result = await create_google_meet_link(
                db=db,
                admin_id=admin_id,
                title=title,
                start_time=scheduled_at,
                duration_minutes=booking.duration_minutes,
                attendee_email=booking.client_email,
                attendee_name=booking.client_name
            )
            if meeting_result:
                new_booking.meeting_url = meeting_result.get("meet_link")
                new_booking.meeting_id = meeting_result.get("event_id")
                db.commit()
                db.refresh(new_booking)

        elif booking.meeting_provider == "zoom":
            meeting_data = await create_zoom_meeting(
                title=title,
                start_time=scheduled_at,
                duration_minutes=booking.duration_minutes
            )
            new_booking.meeting_url = meeting_data["join_url"]
            new_booking.meeting_id = meeting_data["meeting_id"]
            new_booking.meeting_password = meeting_data.get("password")
            db.commit()
            db.refresh(new_booking)

    except Exception as e:
        # If meeting creation fails, still create booking but log error
        print(f"Failed to create meeting link: {e}")

    # Send confirmation email
    try:
        await send_booking_confirmation_email(
            db=db,
            admin_id=admin_id,
            booking=new_booking
        )
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")

    return BookingResponse.from_orm(new_booking)


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """Get booking by ID."""
    query = select(Booking).where(Booking.id == booking_id)
    result = db.execute(query)
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return BookingResponse.from_orm(booking)


@router.post("/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: int,
    reason: str,
    db: Session = Depends(get_db)
):
    """Cancel booking."""
    query = select(Booking).where(Booking.id == booking_id)
    result = db.execute(query)
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status == BookingStatus.CANCELLED.value:
        raise HTTPException(status_code=400, detail="Booking already cancelled")

    booking.status = BookingStatus.CANCELLED.value
    booking.cancelled_at = datetime.utcnow()
    booking.cancellation_reason = reason

    db.commit()

    return {"message": "Booking cancelled successfully"}


@router.get("/health")
async def booking_health():
    """Health check for booking service."""
    return {
        "status": "healthy",
        "service": "booking",
        "features": [
            "calendar_availability",
            "booking_creation",
            "google_meet_integration",
            "zoom_integration",
            "email_notifications"
        ]
    }
