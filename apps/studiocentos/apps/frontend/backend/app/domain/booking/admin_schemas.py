"""
Booking Admin Schemas - Calendar CRUD operations
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date, time


# ============================================================================
# BOOKING SCHEMAS
# ============================================================================

class BookingCreateRequest(BaseModel):
    """Schema per creazione booking manuale."""
    client_name: str = Field(..., min_length=1, max_length=200)
    client_email: str = Field(..., min_length=1, max_length=200)
    client_phone: Optional[str] = Field(None, max_length=50)
    client_company: Optional[str] = Field(None, max_length=200)
    
    service_type: str = Field(default="consultation")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    
    scheduled_at: datetime = Field(...)
    duration_minutes: int = Field(default=30, ge=15, le=480)
    timezone: str = Field(default="Europe/Rome")
    
    status: str = Field(default="confirmed")
    meeting_provider: str = Field(default="google_meet")
    meeting_url: Optional[str] = Field(None, max_length=500)
    
    admin_notes: Optional[str] = None
    client_notes: Optional[str] = None


class BookingUpdateRequest(BaseModel):
    """Schema per aggiornamento booking."""
    client_name: Optional[str] = Field(None, min_length=1, max_length=200)
    client_email: Optional[str] = Field(None, min_length=1, max_length=200)
    client_phone: Optional[str] = Field(None, max_length=50)
    client_company: Optional[str] = Field(None, max_length=200)
    
    service_type: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    
    status: Optional[str] = None
    meeting_url: Optional[str] = Field(None, max_length=500)
    
    admin_notes: Optional[str] = None
    client_notes: Optional[str] = None


class BookingResponse(BaseModel):
    """Schema response booking."""
    id: int
    client_name: str
    client_email: str
    client_phone: Optional[str]
    client_company: Optional[str]
    
    service_type: str
    title: str
    description: Optional[str]
    
    scheduled_at: datetime
    duration_minutes: int
    timezone: str
    
    status: str
    meeting_provider: str
    meeting_url: Optional[str]
    meeting_id: Optional[str]
    
    reminder_sent: bool
    reminder_sent_at: Optional[datetime]
    
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    
    admin_notes: Optional[str]
    client_notes: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Schema lista bookings con paginazione."""
    items: List[BookingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BookingRescheduleRequest(BaseModel):
    """Schema per reschedule booking."""
    scheduled_at: datetime = Field(...)
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    reason: Optional[str] = None


class BookingCancelRequest(BaseModel):
    """Schema per cancellazione booking."""
    reason: str = Field(..., min_length=1)
    send_notification: bool = Field(default=True)


# ============================================================================
# AVAILABILITY SLOT SCHEMAS
# ============================================================================

class AvailabilitySlotCreateRequest(BaseModel):
    """Schema per creazione slot disponibilità."""
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time = Field(...)
    end_time: time = Field(...)
    slot_duration: int = Field(default=30, ge=15, le=480)
    service_type: str = Field(default="consultation")
    is_active: bool = Field(default=True)
    
    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v, info):
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time deve essere dopo start_time')
        return v


class AvailabilitySlotUpdateRequest(BaseModel):
    """Schema per aggiornamento slot."""
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_duration: Optional[int] = Field(None, ge=15, le=480)
    service_type: Optional[str] = None
    is_active: Optional[bool] = None


class AvailabilitySlotResponse(BaseModel):
    """Schema response slot."""
    id: int
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration: int
    service_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# BLOCKED DATE SCHEMAS
# ============================================================================

class BlockedDateCreateRequest(BaseModel):
    """Schema per creazione data bloccata."""
    blocked_date: date = Field(...)
    reason: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    all_day: bool = Field(default=True)
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class BlockedDateResponse(BaseModel):
    """Schema response data bloccata."""
    id: int
    blocked_date: date
    reason: str
    description: Optional[str]
    all_day: bool
    start_time: Optional[time]
    end_time: Optional[time]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# CALENDAR VIEW SCHEMAS
# ============================================================================

class CalendarDayView(BaseModel):
    """Vista calendario giornaliera."""
    date: date
    bookings: List[BookingResponse]
    available_slots: List[dict]
    is_blocked: bool


class CalendarWeekView(BaseModel):
    """Vista calendario settimanale."""
    week_start: date
    week_end: date
    days: List[CalendarDayView]


class CalendarMonthView(BaseModel):
    """Vista calendario mensile."""
    year: int
    month: int
    days: List[CalendarDayView]
    total_bookings: int
    confirmed_bookings: int
    pending_bookings: int
    cancelled_bookings: int


class BookingStatsResponse(BaseModel):
    """Statistiche bookings."""
    total: int
    confirmed: int
    pending: int
    cancelled: int
    completed: int
    no_show: int
    conversion_rate: float
    avg_duration: float
    most_popular_service: Optional[str]
