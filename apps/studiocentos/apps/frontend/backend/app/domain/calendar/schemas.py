"""Calendar API Schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CalendarConnectRequest(BaseModel):
    """Request per connessione calendario."""
    redirect_uri: str = Field(..., description="URL di redirect dopo auth")


class CalendarConnectResponse(BaseModel):
    """Response con URL autorizzazione."""
    authorization_url: str
    state: str


class CalendarCallbackRequest(BaseModel):
    """Request callback OAuth."""
    code: str
    state: str
    redirect_uri: str


class EventCreate(BaseModel):
    """Schema creazione evento."""
    summary: str = Field(..., min_length=1, max_length=200)
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None


class EventUpdate(BaseModel):
    """Schema aggiornamento evento."""
    summary: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    location: Optional[str] = None


class EventResponse(BaseModel):
    """Response evento."""
    id: str
    summary: str
    start: datetime
    end: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    html_link: str


class AvailabilityRequest(BaseModel):
    """Request slot disponibili."""
    start_date: datetime
    end_date: datetime
    slot_duration_minutes: int = Field(default=60, ge=15, le=480)


class AvailabilitySlot(BaseModel):
    """Slot disponibile."""
    start: datetime
    end: datetime
