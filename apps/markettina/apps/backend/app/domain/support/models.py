"""
Support Domain Models
SQLAlchemy models for AI Customer Support
"""

import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.database.session import Base


class TicketStatus(str, enum.Enum):
    """Support ticket status enum"""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, enum.Enum):
    """Support ticket priority enum"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class SupportTicket(Base):
    """Support Ticket Model"""

    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)  # Multi-tenant support
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    priority = Column(Enum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)

    # AI Metadata
    ai_handled = Column(Boolean, default=True)
    ai_confidence = Column(Integer)  # 0-100
    ai_provider = Column(String(50))  # gemini, openai, ollama
    sentiment = Column(String(20))  # positive, neutral, negative

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships

    # user = relationship("User", back_populates="support_tickets")
    messages = relationship(
        "SupportMessage",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="SupportMessage.created_at",
    )

class SupportMessage(Base):
    """Support Message Model"""

    __tablename__ = "support_messages"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)  # Multi-tenant support
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_ai = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)

    # AI Metadata
    ai_confidence = Column(Integer, nullable=True)
    ai_provider = Column(String(50), nullable=True)
    processing_time = Column(Integer, nullable=True)  # milliseconds

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket = relationship("SupportTicket", back_populates="messages")
