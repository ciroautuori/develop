"""
WhatsApp API Schemas - Pydantic models for request/response validation.
"""

import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class TemplateParameter(BaseModel):
    """Parametro per template message."""
    type: str = "text"
    text: str


class TemplateComponent(BaseModel):
    """Componente template (header, body, buttons)."""
    type: str = "body"
    parameters: list[TemplateParameter] = []


class SendTemplateRequest(BaseModel):
    """Request per invio messaggio template."""
    phone: str = Field(..., description="Phone number in international format (+39...)")
    template_name: str = Field(..., description="Approved template name")
    language: str = Field(default="it", description="Template language code")
    components: list[TemplateComponent] = Field(default=[], description="Template parameters")
    lead_id: int | None = Field(default=None, description="Lead ID for tracking")
    campaign_id: str | None = Field(default=None, description="Campaign ID for tracking")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate and normalize phone number."""
        # Remove spaces and dashes
        cleaned = re.sub(r"[\s\-\(\)]", "", v)

        # Ensure starts with +
        if not cleaned.startswith("+"):
            # Assume Italian if no prefix
            if cleaned.startswith("39"):
                cleaned = "+" + cleaned
            else:
                cleaned = "+39" + cleaned

        # Basic validation: should be 10-15 digits after +
        digits = cleaned[1:]
        if not digits.isdigit() or not (10 <= len(digits) <= 15):
            raise ValueError("Invalid phone number format. Use international format: +39XXXXXXXXXX")

        return cleaned


class SendTextRequest(BaseModel):
    """Request per invio messaggio testo (solo in 24h window)."""
    phone: str = Field(..., description="Phone number in international format")
    message: str = Field(..., max_length=4096, description="Message text")
    lead_id: int | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Reuse phone validation logic."""
        return SendTemplateRequest.validate_phone(v)


class SendBulkRequest(BaseModel):
    """Request per invio massivo."""
    phones: list[str] = Field(..., min_length=1, max_length=100)
    template_name: str
    language: str = "it"
    components: list[TemplateComponent] = []
    campaign_id: str | None = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class MessageResponse(BaseModel):
    """Response per singolo messaggio inviato."""
    success: bool
    message_id: str | None = None
    phone: str
    status: str
    error: str | None = None


class SendTemplateResponse(BaseModel):
    """Response per invio template."""
    success: bool
    data: MessageResponse


class BulkSendResponse(BaseModel):
    """Response per invio massivo."""
    success: bool
    total: int
    sent: int
    failed: int
    results: list[MessageResponse]


class MessageStatusResponse(BaseModel):
    """Status di un messaggio."""
    id: int
    waba_message_id: str | None
    phone: str
    template_name: str | None
    status: str
    sent_at: datetime | None
    delivered_at: datetime | None
    read_at: datetime | None
    error: str | None


class MessagesListResponse(BaseModel):
    """Lista messaggi con paginazione."""
    success: bool
    data: list[MessageStatusResponse]
    total: int
    page: int
    page_size: int


class TemplateInfo(BaseModel):
    """Info template WhatsApp."""
    name: str
    language: str
    status: str
    category: str
    components: list[dict[str, Any]] = []


class TemplatesListResponse(BaseModel):
    """Lista template disponibili."""
    success: bool
    data: list[TemplateInfo]


# ============================================================================
# WEBHOOK SCHEMAS
# ============================================================================

class WebhookMessageStatus(BaseModel):
    """Status update da webhook."""
    id: str
    status: str
    timestamp: str
    recipient_id: str | None = None
    errors: list[dict[str, Any]] | None = None


class WebhookEntry(BaseModel):
    """Entry webhook payload."""
    id: str
    changes: list[dict[str, Any]]


class WebhookPayload(BaseModel):
    """Payload completo webhook Meta."""
    object: str
    entry: list[WebhookEntry]
