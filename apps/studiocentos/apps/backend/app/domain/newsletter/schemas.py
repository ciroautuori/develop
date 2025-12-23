from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class SubscriberBase(BaseModel):
    email: EmailStr
    source: Optional[str] = "website"

class SubscriberCreate(SubscriberBase):
    pass

class SubscriberResponse(SubscriberBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
