"""
Support Domain Schemas
Pydantic schemas for API contracts
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

class TicketStatusEnum(str, Enum):
    """Ticket status enum"""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriorityEnum(str, Enum):
    """Ticket priority enum"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ChatRequest(BaseModel):
    """Chat request schema"""

    message: str = Field(..., min_length=1, max_length=2000)
    ticket_id: Optional[int] = None
    context: Optional[str] = None
    provider: Optional[str] = Field(default="gemini", pattern="^(gemini|openai|ollama)$")

class ChatResponse(BaseModel):
    """Chat response schema"""

    response: str
    confidence: int = Field(..., ge=0, le=100)
    provider: str
    ticket_id: int
    sentiment: Optional[str] = None
    processing_time: Optional[int] = None

class SupportMessageSchema(BaseModel):
    """Support message schema"""

    id: int
    ticket_id: int
    content: str
    is_ai: bool
    is_staff: bool
    ai_confidence: Optional[int] = None
    ai_provider: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SupportTicketSchema(BaseModel):
    """Support ticket schema"""

    id: int
    user_id: int
    title: str
    status: TicketStatusEnum
    priority: TicketPriorityEnum
    ai_handled: bool
    ai_confidence: Optional[int] = None
    ai_provider: Optional[str] = None
    sentiment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    messages: List[SupportMessageSchema] = []

    class Config:
        from_attributes = True

class TicketCreateRequest(BaseModel):
    """Ticket creation request"""

    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=2000)
    priority: Optional[TicketPriorityEnum] = TicketPriorityEnum.MEDIUM

class TicketListResponse(BaseModel):
    """Ticket list response"""

    tickets: List[SupportTicketSchema]
    total: int
    page: int
    page_size: int
