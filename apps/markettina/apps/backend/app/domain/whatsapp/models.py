"""
WhatsApp Message Models - SQLAlchemy models for message tracking.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class WhatsAppMessageStatus(str, Enum):
    """Status del messaggio WhatsApp."""
    PENDING = "pending"      # In coda per l'invio
    SENT = "sent"            # Inviato a WhatsApp API
    DELIVERED = "delivered"  # Consegnato al dispositivo
    READ = "read"            # Letto dal destinatario
    FAILED = "failed"        # Errore invio


class WhatsAppMessageType(str, Enum):
    """Tipo di messaggio WhatsApp."""
    TEMPLATE = "template"    # Messaggio template pre-approvato
    TEXT = "text"            # Messaggio testo (solo in 24h window)
    IMAGE = "image"          # Immagine
    DOCUMENT = "document"    # Documento


class WhatsAppMessage(Base):
    """
    Tracciamento messaggi WhatsApp inviati.

    Registra ogni messaggio inviato tramite Cloud API,
    con status aggiornato via webhook callbacks.
    """
    __tablename__ = "whatsapp_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # WhatsApp API identifiers
    waba_message_id: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        comment="Message ID returned by WhatsApp API"
    )

    # Recipient info
    phone_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Recipient phone in international format (+39...)"
    )
    lead_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True
    )

    # Message content
    message_type: Mapped[str] = mapped_column(
        String(20),
        default=WhatsAppMessageType.TEMPLATE.value
    )
    template_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Template name if using template message"
    )
    template_language: Mapped[str | None] = mapped_column(
        String(10),
        default="it",
        comment="Template language code"
    )
    message_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Message text content or template parameters JSON"
    )

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20),
        default=WhatsAppMessageStatus.PENDING.value,
        index=True
    )
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Campaign tracking (optional)
    campaign_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Internal campaign ID for tracking"
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_whatsapp_phone_status", "phone_number", "status"),
        Index("idx_whatsapp_campaign", "campaign_id"),
    )

    def __repr__(self) -> str:
        return f"<WhatsAppMessage(id={self.id}, phone={self.phone_number}, status={self.status})>"
