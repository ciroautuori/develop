"""
Booking Domain Models - Appuntamenti e Videocall.
"""

from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base

if TYPE_CHECKING:
    from app.domain.customers.models import Customer


class BookingStatus(str, Enum):
    """Status della prenotazione."""
    PENDING = "pending"  # In attesa di conferma
    CONFIRMED = "confirmed"  # Confermata
    CANCELLED = "cancelled"  # Cancellata
    COMPLETED = "completed"  # Completata
    NO_SHOW = "no_show"  # Cliente non si è presentato


class MeetingProvider(str, Enum):
    """Provider per videocall."""
    GOOGLE_MEET = "google_meet"
    ZOOM = "zoom"
    MICROSOFT_TEAMS = "teams"
    WHEREBY = "whereby"
    JITSI = "jitsi"


class ServiceType(str, Enum):
    """Tipi di servizio prenotabili."""
    CONSULTATION = "consultation"  # Consulenza
    DEMO = "demo"  # Demo prodotto
    TECHNICAL_SUPPORT = "technical_support"  # Supporto tecnico
    TRAINING = "training"  # Formazione
    DISCOVERY_CALL = "discovery_call"  # Discovery call


class AvailabilitySlot(Base):
    """
    Slot di disponibilità per appuntamenti.

    Definisce quando siamo disponibili per appuntamenti.
    """
    __tablename__ = "availability_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Giorno della settimana (0=Lunedì, 6=Domenica)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)

    # Orari
    start_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)

    # Durata slot in minuti
    slot_duration: Mapped[int] = mapped_column(Integer, default=30)

    # Tipo di servizio
    service_type: Mapped[str] = mapped_column(
        String(50),
        default=ServiceType.CONSULTATION.value
    )

    # Attivo/Disattivo
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class Booking(Base):
    """
    Prenotazione appuntamento.

    Rappresenta un appuntamento prenotato con videocall.
    """
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # ========================================================================
    # CUSTOMER RELATIONSHIP (NEW - Phase 3)
    # ========================================================================

    # Link to centralized Customer entity
    customer_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True,  # Nullable for backward compatibility with existing bookings
        index=True
    )

    # ========================================================================
    # DEPRECATED CLIENT INFO FIELDS
    # Questi campi sono deprecated e saranno rimossi in futuro.
    # Usare customer_id per linkare a Customer centralizzato.
    # Mantenuti temporaneamente per backward compatibility.
    # ========================================================================

    # DEPRECATED: Use customer.name instead
    client_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # DEPRECATED: Use customer.email instead
    client_email: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # DEPRECATED: Use customer.phone instead
    client_phone: Mapped[Optional[str]] = mapped_column(String(50))

    # DEPRECATED: Use customer.company_name instead
    client_company: Mapped[Optional[str]] = mapped_column(String(200))

    # ========================================================================
    # BOOKING DETAILS
    # ========================================================================
    service_type: Mapped[str] = mapped_column(
        String(50),
        default=ServiceType.CONSULTATION.value
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Data e ora
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Rome")

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default=BookingStatus.PENDING.value,
        index=True
    )

    # Videocall info
    meeting_provider: Mapped[str] = mapped_column(
        String(50),
        default=MeetingProvider.GOOGLE_MEET.value
    )
    meeting_url: Mapped[Optional[str]] = mapped_column(String(500))
    meeting_id: Mapped[Optional[str]] = mapped_column(String(200))
    meeting_password: Mapped[Optional[str]] = mapped_column(String(100))

    # Reminders
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Cancellation
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Notes
    admin_notes: Mapped[Optional[str]] = mapped_column(Text)
    client_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    referrer: Mapped[Optional[str]] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    # Customer relationship (NEW - Phase 3)
    customer: Mapped[Optional["Customer"]] = relationship(
        "Customer",
        foreign_keys=[customer_id],
        lazy="select"
    )

    follow_ups: Mapped[list["BookingFollowUp"]] = relationship(
        "BookingFollowUp",
        back_populates="booking",
        cascade="all, delete-orphan"
    )


class BookingFollowUp(Base):
    """
    Follow-up dopo appuntamento.
    """
    __tablename__ = "booking_follow_ups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bookings.id", ondelete="CASCADE")
    )

    # Contenuto follow-up
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Status
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    booking: Mapped["Booking"] = relationship(
        "Booking",
        back_populates="follow_ups"
    )


class BlockedDate(Base):
    """
    Date bloccate (ferie, festività, etc).
    """
    __tablename__ = "blocked_dates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Data bloccata
    blocked_date: Mapped[datetime.date] = mapped_column(DateTime, nullable=False, index=True)

    # Motivo
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Tutto il giorno o orario specifico
    all_day: Mapped[bool] = mapped_column(Boolean, default=True)
    start_time: Mapped[Optional[datetime.time]] = mapped_column(Time)
    end_time: Mapped[Optional[datetime.time]] = mapped_column(Time)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
