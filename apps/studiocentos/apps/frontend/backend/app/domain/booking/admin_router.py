"""
Booking Admin Router - Calendar CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.infrastructure.database.session import get_db
from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser

from .admin_service import BookingAdminService
from .admin_schemas import *

router = APIRouter(prefix="/api/v1/admin/bookings", tags=["admin-bookings"])


# ============================================================================
# STATISTICS (MUST BE BEFORE /{booking_id} routes!)
# ============================================================================

@router.get("/stats", response_model=BookingStatsResponse)
def get_booking_stats(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Statistiche bookings."""
    return BookingAdminService.get_booking_stats(db, from_date, to_date)


# ============================================================================
# BOOKINGS ENDPOINTS
# ============================================================================

@router.post("", response_model=BookingResponse)
async def create_booking(
    data: BookingCreateRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Crea nuovo booking manualmente con Google Calendar sync."""
    booking = await BookingAdminService.create_booking(db, data, admin_id=admin.id)
    return BookingResponse.model_validate(booking)


@router.get("", response_model=BookingListResponse)
def list_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    service_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Lista bookings con filtri."""
    return BookingAdminService.get_bookings(
        db=db,
        page=page,
        page_size=page_size,
        date_from=date_from,
        date_to=date_to,
        status=status,
        service_type=service_type,
        search=search
    )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Ottieni singolo booking."""
    booking = BookingAdminService.get_booking(db, booking_id)
    return BookingResponse.model_validate(booking)


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    data: BookingUpdateRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Aggiorna booking con Google Calendar sync."""
    booking = await BookingAdminService.update_booking(db, booking_id, data, admin_id=admin.id)
    return BookingResponse.model_validate(booking)


@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Elimina booking con Google Calendar sync."""
    await BookingAdminService.delete_booking(db, booking_id, admin_id=admin.id)
    return {"message": "Booking eliminato"}


@router.post("/{booking_id}/confirm", response_model=BookingResponse)
def confirm_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Conferma booking."""
    booking = BookingAdminService.confirm_booking(db, booking_id)
    return BookingResponse.model_validate(booking)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    data: BookingCancelRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Cancella booking con Google Calendar sync."""
    booking = await BookingAdminService.cancel_booking(db, booking_id, data, admin_id=admin.id)
    return BookingResponse.model_validate(booking)


@router.post("/{booking_id}/reschedule", response_model=BookingResponse)
async def reschedule_booking(
    booking_id: int,
    data: BookingRescheduleRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Reschedule booking con Google Calendar sync."""
    booking = await BookingAdminService.reschedule_booking(db, booking_id, data, admin_id=admin.id)
    return BookingResponse.model_validate(booking)


# ============================================================================
# AVAILABILITY SLOTS
# ============================================================================

@router.post("/availability/slots", response_model=AvailabilitySlotResponse)
def create_availability_slot(
    data: AvailabilitySlotCreateRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Crea slot disponibilità."""
    slot = BookingAdminService.create_availability_slot(db, data)
    return AvailabilitySlotResponse.model_validate(slot)


@router.get("/availability/slots", response_model=List[AvailabilitySlotResponse])
def list_availability_slots(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Lista slot disponibilità."""
    slots = BookingAdminService.get_availability_slots(db, is_active)
    return [AvailabilitySlotResponse.model_validate(s) for s in slots]


@router.put("/availability/slots/{slot_id}", response_model=AvailabilitySlotResponse)
def update_availability_slot(
    slot_id: int,
    data: AvailabilitySlotUpdateRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Aggiorna slot disponibilità."""
    slot = BookingAdminService.update_availability_slot(db, slot_id, data)
    return AvailabilitySlotResponse.model_validate(slot)


@router.delete("/availability/slots/{slot_id}")
def delete_availability_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Elimina slot disponibilità."""
    BookingAdminService.delete_availability_slot(db, slot_id)
    return {"message": "Slot eliminato"}


# ============================================================================
# BLOCKED DATES
# ============================================================================

@router.post("/blocked-dates", response_model=BlockedDateResponse)
def create_blocked_date(
    data: BlockedDateCreateRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Crea data bloccata."""
    blocked = BookingAdminService.create_blocked_date(db, data)
    return BlockedDateResponse.model_validate(blocked)


@router.get("/blocked-dates", response_model=List[BlockedDateResponse])
def list_blocked_dates(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Lista date bloccate."""
    blocked = BookingAdminService.get_blocked_dates(db, from_date, to_date)
    return [BlockedDateResponse.model_validate(b) for b in blocked]


@router.delete("/blocked-dates/{blocked_id}")
def delete_blocked_date(
    blocked_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Elimina data bloccata."""
    BookingAdminService.delete_blocked_date(db, blocked_id)
    return {"message": "Data bloccata eliminata"}


# ============================================================================
# CALENDAR VIEWS
# ============================================================================

@router.get("/calendar/day", response_model=CalendarDayView)
def get_calendar_day(
    target_date: date = Query(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Vista calendario giornaliera."""
    return BookingAdminService.get_calendar_day(db, target_date)


@router.get("/calendar/week", response_model=CalendarWeekView)
def get_calendar_week(
    target_date: date = Query(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Vista calendario settimanale."""
    return BookingAdminService.get_calendar_week(db, target_date)


@router.get("/calendar/month", response_model=CalendarMonthView)
def get_calendar_month(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Vista calendario mensile."""
    return BookingAdminService.get_calendar_month(db, year, month)


# (Statistics moved to top of file to avoid route conflict with /{booking_id})
