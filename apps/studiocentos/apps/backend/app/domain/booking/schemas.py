"""
Booking Domain Schemas - Pydantic models.
"""

from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, HttpUrl

from .models import BookingStatus, MeetingProvider, ServiceType


# ============================================================================
# BOOKING SCHEMAS
# ============================================================================

class BookingCreate(BaseModel):
    """Schema for creating booking."""
    client_name: str = Field(..., max_length=200)
    client_email: EmailStr
    client_phone: Optional[str] = Field(None, max_length=50)
    client_company: Optional[str] = Field(None, max_length=200)
    service_type: str = Field(default=ServiceType.CONSULTATION.value)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=15, le=180)
    timezone: str = Field(default="Europe/Rome")
    meeting_provider: str = Field(default=MeetingProvider.GOOGLE_MEET.value)
    client_notes: Optional[str] = None


class BookingUpdate(BaseModel):
    """Schema for updating booking."""
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    meeting_url: Optional[HttpUrl] = None
    meeting_id: Optional[str] = None
    meeting_password: Optional[str] = None
    admin_notes: Optional[str] = None
    cancellation_reason: Optional[str] = None


class BookingResponse(BaseModel):
    """Schema for booking response."""
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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AVAILABILITY SCHEMAS
# ============================================================================

class AvailabilitySlotCreate(BaseModel):
    """Schema for creating availability slot."""
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time
    slot_duration: int = Field(default=30, ge=15, le=180)
    service_type: str = Field(default=ServiceType.CONSULTATION.value)
    is_active: bool = True


class AvailabilitySlotResponse(BaseModel):
    """Schema for availability slot response."""
    id: int
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration: int
    service_type: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AvailableSlot(BaseModel):
    """Schema for available time slot."""
    datetime: datetime
    duration_minutes: int
    service_type: str
    available: bool = True


class AvailabilityResponse(BaseModel):
    """Schema for availability response."""
    date: date
    slots: List[AvailableSlot]
    total_available: int


# ============================================================================
# BLOCKED DATE SCHEMAS
# ============================================================================

class BlockedDateCreate(BaseModel):
    """Schema for creating blocked date."""
    blocked_date: date
    reason: str = Field(..., max_length=200)
    description: Optional[str] = None
    all_day: bool = True
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class BlockedDateResponse(BaseModel):
    """Schema for blocked date response."""
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
# CALENDAR SCHEMAS
# ============================================================================

class CalendarRequest(BaseModel):
    """Schema for calendar availability request."""
    start_date: date
    end_date: date
    service_type: Optional[str] = None
    timezone: str = Field(default="Europe/Rome")


class CalendarResponse(BaseModel):
    """Schema for calendar response."""
    availability: List[AvailabilityResponse]
    blocked_dates: List[date]
    bookings_count: int
