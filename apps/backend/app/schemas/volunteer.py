from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class VolunteerApplicationBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=20)
    message: str = Field(..., min_length=1, max_length=1000)


class VolunteerApplicationCreate(VolunteerApplicationBase):
    pass


class VolunteerApplicationRead(VolunteerApplicationBase):
    id: int
    submitted_at: datetime

    class Config:
        from_attributes = True
