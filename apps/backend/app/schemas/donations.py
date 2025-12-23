from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class DonationCreate(BaseModel):
    amount: int = Field(..., ge=200, description="Amount in cents (minimum €2.00)")
    donor_name: str = Field(..., min_length=2, max_length=100)
    donor_email: EmailStr
    message: Optional[str] = Field(None, max_length=500)


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    donation_id: int


class DonationResponse(BaseModel):
    id: int
    amount: int
    donor_name: str
    donor_email: str
    message: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
