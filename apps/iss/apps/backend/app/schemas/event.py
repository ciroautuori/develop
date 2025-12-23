from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100)
    excerpt: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1)
    image_url: str = Field(..., min_length=1)
    event_date: datetime
    location: str = Field(..., min_length=1, max_length=200)
    is_active: bool = True


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    excerpt: Optional[str] = Field(None, min_length=1, max_length=300)
    content: Optional[str] = Field(None, min_length=1)
    image_url: Optional[str] = Field(None, min_length=1)
    event_date: Optional[datetime] = None
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    is_active: Optional[bool] = None


class EventRead(EventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
