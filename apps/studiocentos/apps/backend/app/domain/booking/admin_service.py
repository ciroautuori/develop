"""
Booking Admin Service - Calendar management business logic
"""
from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_
from fastapi import HTTPException, status
import logging

from .models import Booking, AvailabilitySlot, BlockedDate, BookingStatus
from .admin_schemas import (
    BookingCreateRequest, BookingUpdateRequest, BookingResponse, BookingListResponse,
    BookingRescheduleRequest, BookingCancelRequest,
    AvailabilitySlotCreateRequest, AvailabilitySlotUpdateRequest, AvailabilitySlotResponse,
    BlockedDateCreateRequest, BlockedDateResponse,
    CalendarDayView, CalendarWeekView, CalendarMonthView, BookingStatsResponse
)

# Google Calendar integration
from .services import (
    create_google_meet_link,
    update_booking_event,
    cancel_booking_event
)

logger = logging.getLogger(__name__)


class BookingAdminService:
    """Servizio per gestione admin bookings."""

    # ========================================================================
    # BOOKINGS CRUD
    # ========================================================================

    @staticmethod
    async def create_booking(db: Session, data: BookingCreateRequest, admin_id: int = None) -> Booking:
        """
        Crea nuovo booking manualmente con integrazione Google Calendar.

        Se admin_id è fornito e meeting_provider='google_meet', crea evento Google Calendar.
        """
        booking = Booking(**data.model_dump())
        db.add(booking)
        db.commit()
        db.refresh(booking)

        # Google Calendar integration: crea evento se meeting_provider è google_meet
        if admin_id and booking.meeting_provider == "google_meet" and booking.client_email:
            try:
                logger.info(f"Creating Google Calendar event for booking {booking.id}")

                result = await create_google_meet_link(
                    db=db,
                    admin_id=admin_id,
                    title=booking.title or f"Appuntamento con {booking.client_name}",
                    start_time=booking.scheduled_at,
                    duration_minutes=booking.duration_minutes or 60,
                    attendee_email=booking.client_email,
                    attendee_name=booking.client_name or ""
                )

                if result:
                    # Salva event_id e meet_link nel booking
                    booking.meeting_url = result.get("meet_link")
                    booking.meeting_id = result.get("event_id")
                    db.commit()
                    db.refresh(booking)
                    logger.info(f"Google Meet link created: {booking.meeting_url}")
                else:
                    logger.warning(f"Failed to create Google Calendar event for booking {booking.id}")

            except Exception as e:
                # Non bloccare la creazione del booking se Google Calendar fallisce
                logger.error(f"Google Calendar error for booking {booking.id}: {e}", exc_info=True)

        return booking

    @staticmethod
    def get_bookings(
        db: Session,
        page: int = 1,
        page_size: int = 50,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        status: Optional[str] = None,
        service_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> BookingListResponse:
        """Ottieni lista bookings con filtri."""
        query = select(Booking)

        # Filtri data
        if date_from:
            query = query.where(Booking.scheduled_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            query = query.where(Booking.scheduled_at <= datetime.combine(date_to, datetime.max.time()))

        # Filtri
        if status:
            query = query.where(Booking.status == status)
        if service_type:
            query = query.where(Booking.service_type == service_type)
        if search:
            query = query.where(
                or_(
                    Booking.client_name.ilike(f"%{search}%"),
                    Booking.client_email.ilike(f"%{search}%"),
                    Booking.title.ilike(f"%{search}%")
                )
            )

        # Count
        total = db.execute(select(func.count()).select_from(query.subquery())).scalar()

        # Ordinamento e paginazione
        query = query.order_by(Booking.scheduled_at.desc())
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        bookings = db.execute(query).scalars().all()

        return BookingListResponse(
            items=[BookingResponse.model_validate(b) for b in bookings],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )

    @staticmethod
    def get_booking(db: Session, booking_id: int) -> Booking:
        """Ottieni singolo booking."""
        booking = db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking {booking_id} non trovato"
            )
        return booking

    @staticmethod
    async def update_booking(db: Session, booking_id: int, data: BookingUpdateRequest, admin_id: int = None) -> Booking:
        """
        Aggiorna booking con sincronizzazione Google Calendar.

        Se il booking ha meeting_id (evento Google), aggiorna anche l'evento.
        """
        booking = BookingAdminService.get_booking(db, booking_id)

        update_data = data.model_dump(exclude_unset=True)

        # Traccia se scheduled_at è cambiato per aggiornare Google Calendar
        scheduled_at_changed = 'scheduled_at' in update_data and update_data['scheduled_at'] != booking.scheduled_at
        duration_changed = 'duration_minutes' in update_data and update_data['duration_minutes'] != booking.duration_minutes
        title_changed = 'title' in update_data and update_data['title'] != booking.title

        for field, value in update_data.items():
            setattr(booking, field, value)

        db.commit()
        db.refresh(booking)

        # Google Calendar sync: aggiorna evento se esiste
        if admin_id and booking.meeting_id and (scheduled_at_changed or duration_changed or title_changed):
            try:
                logger.info(f"Updating Google Calendar event {booking.meeting_id} for booking {booking.id}")

                # Se cambia scheduled_at o duration, passa sempre entrambi per calcolare end_time
                start_time = booking.scheduled_at if scheduled_at_changed else None
                duration = booking.duration_minutes if (scheduled_at_changed or duration_changed) else None

                result = await update_booking_event(
                    db=db,
                    admin_id=admin_id,
                    event_id=booking.meeting_id,
                    new_start_time=start_time,
                    new_duration_minutes=duration,
                    new_title=booking.title if title_changed else None
                )

                if result:
                    logger.info(f"Google Calendar event updated for booking {booking.id}")
                else:
                    logger.warning(f"Failed to update Google Calendar event for booking {booking.id}")

            except Exception as e:
                logger.error(f"Google Calendar update error for booking {booking.id}: {e}", exc_info=True)

        return booking

    @staticmethod
    async def delete_booking(db: Session, booking_id: int, admin_id: int = None):
        """
        Elimina booking con sincronizzazione Google Calendar.

        Se il booking ha meeting_id (evento Google), elimina anche l'evento.
        """
        booking = BookingAdminService.get_booking(db, booking_id)

        # Google Calendar sync: elimina evento se esiste
        if admin_id and booking.meeting_id:
            try:
                logger.info(f"Deleting Google Calendar event {booking.meeting_id} for booking {booking.id}")

                success = await cancel_booking_event(
                    db=db,
                    admin_id=admin_id,
                    event_id=booking.meeting_id
                )

                if success:
                    logger.info(f"Google Calendar event deleted for booking {booking.id}")
                else:
                    logger.warning(f"Failed to delete Google Calendar event for booking {booking.id}")

            except Exception as e:
                logger.error(f"Google Calendar delete error for booking {booking.id}: {e}", exc_info=True)

        db.delete(booking)
        db.commit()

    @staticmethod
    def confirm_booking(db: Session, booking_id: int) -> Booking:
        """Conferma booking."""
        booking = BookingAdminService.get_booking(db, booking_id)
        booking.status = BookingStatus.CONFIRMED.value
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    async def cancel_booking(db: Session, booking_id: int, data: BookingCancelRequest, admin_id: int = None) -> Booking:
        """
        Cancella booking con sincronizzazione Google Calendar.

        Se il booking ha meeting_id (evento Google), elimina anche l'evento.
        """
        booking = BookingAdminService.get_booking(db, booking_id)
        booking.status = BookingStatus.CANCELLED.value
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = data.reason

        # Google Calendar sync: elimina evento se esiste
        if admin_id and booking.meeting_id:
            try:
                logger.info(f"Cancelling Google Calendar event {booking.meeting_id} for booking {booking.id}")

                success = await cancel_booking_event(
                    db=db,
                    admin_id=admin_id,
                    event_id=booking.meeting_id
                )

                if success:
                    logger.info(f"Google Calendar event cancelled for booking {booking.id}")
                else:
                    logger.warning(f"Failed to cancel Google Calendar event for booking {booking.id}")

            except Exception as e:
                logger.error(f"Google Calendar cancel error for booking {booking.id}: {e}", exc_info=True)

        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    async def reschedule_booking(db: Session, booking_id: int, data: BookingRescheduleRequest, admin_id: int = None) -> Booking:
        """
        Reschedule booking con sincronizzazione Google Calendar.

        Se il booking ha meeting_id (evento Google), aggiorna anche l'evento.
        """
        booking = BookingAdminService.get_booking(db, booking_id)
        booking.scheduled_at = data.scheduled_at
        if data.duration_minutes:
            booking.duration_minutes = data.duration_minutes
        if data.reason:
            booking.admin_notes = f"{booking.admin_notes or ''}\nRescheduled: {data.reason}"

        # Google Calendar sync: aggiorna evento se esiste
        if admin_id and booking.meeting_id:
            try:
                logger.info(f"Rescheduling Google Calendar event {booking.meeting_id} for booking {booking.id}")

                # Passa sempre start_time E duration per calcolare end_time
                result = await update_booking_event(
                    db=db,
                    admin_id=admin_id,
                    event_id=booking.meeting_id,
                    new_start_time=data.scheduled_at,
                    new_duration_minutes=data.duration_minutes or booking.duration_minutes,
                    new_title=None
                )

                if result:
                    logger.info(f"Google Calendar event rescheduled for booking {booking.id}")
                else:
                    logger.warning(f"Failed to reschedule Google Calendar event for booking {booking.id}")

            except Exception as e:
                logger.error(f"Google Calendar reschedule error for booking {booking.id}: {e}", exc_info=True)

        db.commit()
        db.refresh(booking)
        return booking

    # ========================================================================
    # AVAILABILITY SLOTS
    # ========================================================================

    @staticmethod
    def create_availability_slot(db: Session, data: AvailabilitySlotCreateRequest) -> AvailabilitySlot:
        """Crea slot disponibilità."""
        slot = AvailabilitySlot(**data.model_dump())
        db.add(slot)
        db.commit()
        db.refresh(slot)
        return slot

    @staticmethod
    def get_availability_slots(db: Session, is_active: Optional[bool] = None) -> List[AvailabilitySlot]:
        """Ottieni tutti gli slot disponibilità."""
        query = select(AvailabilitySlot)
        if is_active is not None:
            query = query.where(AvailabilitySlot.is_active == is_active)
        query = query.order_by(AvailabilitySlot.day_of_week, AvailabilitySlot.start_time)
        return db.execute(query).scalars().all()

    @staticmethod
    def update_availability_slot(db: Session, slot_id: int, data: AvailabilitySlotUpdateRequest) -> AvailabilitySlot:
        """Aggiorna slot disponibilità."""
        slot = db.get(AvailabilitySlot, slot_id)
        if not slot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot non trovato")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(slot, field, value)

        db.commit()
        db.refresh(slot)
        return slot

    @staticmethod
    def delete_availability_slot(db: Session, slot_id: int):
        """Elimina slot disponibilità."""
        slot = db.get(AvailabilitySlot, slot_id)
        if not slot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot non trovato")
        db.delete(slot)
        db.commit()

    # ========================================================================
    # BLOCKED DATES
    # ========================================================================

    @staticmethod
    def create_blocked_date(db: Session, data: BlockedDateCreateRequest) -> BlockedDate:
        """Crea data bloccata."""
        blocked = BlockedDate(**data.model_dump())
        db.add(blocked)
        db.commit()
        db.refresh(blocked)
        return blocked

    @staticmethod
    def get_blocked_dates(db: Session, from_date: Optional[date] = None, to_date: Optional[date] = None) -> List[BlockedDate]:
        """Ottieni date bloccate."""
        query = select(BlockedDate)
        if from_date:
            query = query.where(BlockedDate.blocked_date >= from_date)
        if to_date:
            query = query.where(BlockedDate.blocked_date <= to_date)
        query = query.order_by(BlockedDate.blocked_date)
        return db.execute(query).scalars().all()

    @staticmethod
    def delete_blocked_date(db: Session, blocked_id: int):
        """Elimina data bloccata."""
        blocked = db.get(BlockedDate, blocked_id)
        if not blocked:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data bloccata non trovata")
        db.delete(blocked)
        db.commit()

    # ========================================================================
    # CALENDAR VIEWS
    # ========================================================================

    @staticmethod
    def get_calendar_day(db: Session, target_date: date) -> CalendarDayView:
        """Vista calendario giornaliera."""
        # Get bookings
        bookings = db.execute(
            select(Booking).where(
                and_(
                    Booking.scheduled_at >= datetime.combine(target_date, datetime.min.time()),
                    Booking.scheduled_at < datetime.combine(target_date + timedelta(days=1), datetime.min.time())
                )
            ).order_by(Booking.scheduled_at)
        ).scalars().all()

        # Check if blocked
        blocked = db.execute(
            select(BlockedDate).where(BlockedDate.blocked_date == target_date)
        ).scalar_one_or_none()

        return CalendarDayView(
            date=target_date,
            bookings=[BookingResponse.model_validate(b) for b in bookings],
            available_slots=[],
            is_blocked=blocked is not None
        )

    @staticmethod
    def get_calendar_week(db: Session, target_date: date) -> CalendarWeekView:
        """Vista calendario settimanale."""
        week_start = target_date - timedelta(days=target_date.weekday())
        week_end = week_start + timedelta(days=6)

        days = []
        current = week_start
        while current <= week_end:
            days.append(BookingAdminService.get_calendar_day(db, current))
            current += timedelta(days=1)

        return CalendarWeekView(
            week_start=week_start,
            week_end=week_end,
            days=days
        )

    @staticmethod
    def get_calendar_month(db: Session, year: int, month: int) -> CalendarMonthView:
        """Vista calendario mensile."""
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        # Get all bookings del mese
        bookings = db.execute(
            select(Booking).where(
                and_(
                    Booking.scheduled_at >= datetime.combine(first_day, datetime.min.time()),
                    Booking.scheduled_at <= datetime.combine(last_day, datetime.max.time())
                )
            )
        ).scalars().all()

        # Stats
        total = len(bookings)
        confirmed = sum(1 for b in bookings if b.status == BookingStatus.CONFIRMED.value)
        pending = sum(1 for b in bookings if b.status == BookingStatus.PENDING.value)
        cancelled = sum(1 for b in bookings if b.status == BookingStatus.CANCELLED.value)

        # Days
        days = []
        current = first_day
        while current <= last_day:
            days.append(BookingAdminService.get_calendar_day(db, current))
            current += timedelta(days=1)

        return CalendarMonthView(
            year=year,
            month=month,
            days=days,
            total_bookings=total,
            confirmed_bookings=confirmed,
            pending_bookings=pending,
            cancelled_bookings=cancelled
        )

    # ========================================================================
    # STATISTICS
    # ========================================================================

    @staticmethod
    def get_booking_stats(db: Session, from_date: Optional[date] = None, to_date: Optional[date] = None) -> BookingStatsResponse:
        """Ottieni statistiche bookings."""
        query = select(Booking)

        if from_date:
            query = query.where(Booking.scheduled_at >= datetime.combine(from_date, datetime.min.time()))
        if to_date:
            query = query.where(Booking.scheduled_at <= datetime.combine(to_date, datetime.max.time()))

        bookings = db.execute(query).scalars().all()

        total = len(bookings)
        confirmed = sum(1 for b in bookings if b.status == BookingStatus.CONFIRMED.value)
        pending = sum(1 for b in bookings if b.status == BookingStatus.PENDING.value)
        cancelled = sum(1 for b in bookings if b.status == BookingStatus.CANCELLED.value)
        completed = sum(1 for b in bookings if b.status == BookingStatus.COMPLETED.value)
        no_show = sum(1 for b in bookings if b.status == BookingStatus.NO_SHOW.value)

        conversion_rate = (confirmed / total * 100) if total > 0 else 0
        avg_duration = sum(b.duration_minutes for b in bookings) / total if total > 0 else 0

        # Most popular service
        service_counts = {}
        for b in bookings:
            service_counts[b.service_type] = service_counts.get(b.service_type, 0) + 1
        most_popular = max(service_counts.items(), key=lambda x: x[1])[0] if service_counts else None

        return BookingStatsResponse(
            total=total,
            confirmed=confirmed,
            pending=pending,
            cancelled=cancelled,
            completed=completed,
            no_show=no_show,
            conversion_rate=round(conversion_rate, 2),
            avg_duration=round(avg_duration, 2),
            most_popular_service=most_popular
        )
