"""
Customers Domain Models - Anagrafica clienti con CRM.

Questo modulo implementa un sistema CRM completo per gestire
i clienti in modo centralizzato, eliminando la duplicazione dati
presente nel dominio booking.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import decrypt_pii, encrypt_pii
from app.infrastructure.database.session import Base

if TYPE_CHECKING:
    from app.domain.auth.admin_models import AdminUser


class CustomerStatus(str, Enum):
    """Status del cliente nel funnel di vendita."""
    LEAD = "lead"              # Primo contatto, non qualificato
    PROSPECT = "prospect"      # Qualificato, in negoziazione
    ACTIVE = "active"          # Cliente attivo con contratto
    INACTIVE = "inactive"      # Ex-cliente senza contratti attivi
    CHURNED = "churned"        # Cliente perso definitivamente


class CustomerType(str, Enum):
    """Tipologia di cliente."""
    INDIVIDUAL = "individual"  # Persona fisica
    BUSINESS = "business"      # Azienda
    AGENCY = "agency"          # Agenzia/Partner
    NON_PROFIT = "non_profit"  # No-profit


class CustomerSource(str, Enum):
    """Canale di acquisizione cliente."""
    WEBSITE = "website"        # Form sito web
    REFERRAL = "referral"      # Referral da altro cliente
    ADVERTISING = "advertising"  # Campagne advertising
    EVENT = "event"            # Eventi/Conferenze
    DIRECT = "direct"          # Contatto diretto
    ORGANIC = "organic"        # SEO/Social organico
    OTHER = "other"            # Altro


class Customer(Base):
    """
    Anagrafica cliente centralizzata con funzionalità CRM.

    Questo modello sostituisce i dati cliente duplicati nel dominio booking
    e fornisce un'unica fonte di verità per tutti i dati cliente.

    Features:
    - PII encryption (email, phone)
    - Customer Lifetime Value tracking
    - Engagement tracking (ultimo contatto, follow-up)
    - Soft delete per GDPR compliance
    """
    __tablename__ = "customers"

    # ========================================================================
    # PRIMARY KEY
    # ========================================================================

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # ========================================================================
    # BASIC INFO
    # ========================================================================

    # Nome completo o ragione sociale
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Email CRITTOGRAFATA (PII) - stored in _email column
    _email = Column("email", String(500), nullable=False, unique=True, index=True)

    # Telefono CRITTOGRAFATO (PII) - stored in _phone column
    _phone = Column("phone", String(500), nullable=True)

    # Company info (se business)
    company_name: Mapped[str | None] = mapped_column(String(255), index=True)
    company_vat_id: Mapped[str | None] = mapped_column(String(50))  # P.IVA / VAT
    company_website: Mapped[str | None] = mapped_column(String(255))

    # Address
    address_line1: Mapped[str | None] = mapped_column(String(255))
    address_line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    state_province: Mapped[str | None] = mapped_column(String(100))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(2), default="IT")  # ISO 3166-1 alpha-2

    # ========================================================================
    # CRM FIELDS
    # ========================================================================

    status: Mapped[str] = mapped_column(
        String(50),
        default=CustomerStatus.LEAD.value,
        nullable=False,
        index=True
    )

    customer_type: Mapped[str] = mapped_column(
        String(50),
        default=CustomerType.INDIVIDUAL.value,
        nullable=False
    )

    source: Mapped[str] = mapped_column(
        String(50),
        default=CustomerSource.WEBSITE.value,
        nullable=False,
        index=True
    )

    # Assigned to (admin user responsible)
    assigned_to: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id"),
        nullable=True
    )

    # Tags (comma-separated for simplicity)
    tags: Mapped[str | None] = mapped_column(Text)  # "vip,recurring,enterprise"

    # Notes generali
    notes: Mapped[str | None] = mapped_column(Text)

    # ========================================================================
    # FINANCIAL TRACKING
    # ========================================================================

    # Customer Lifetime Value (calcolato da Finance domain)
    lifetime_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00")
    )

    # Totale speso dal cliente (da fatture)
    total_spent: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00")
    )

    # Average deal size
    avg_deal_size: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00")
    )

    # Numero progetti completati
    completed_projects: Mapped[int] = mapped_column(Integer, default=0)

    # Ultima transazione
    last_purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ========================================================================
    # ENGAGEMENT TRACKING
    # ========================================================================

    # Ultimo contatto
    last_contact_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_contact_type: Mapped[str | None] = mapped_column(String(50))

    # Prossimo follow-up
    next_followup_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_followup_notes: Mapped[str | None] = mapped_column(Text)

    # ========================================================================
    # PRIVACY & MARKETING
    # ========================================================================

    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    marketing_consent_date: Mapped[datetime | None] = mapped_column(DateTime)

    # ========================================================================
    # AUDIT FIELDS
    # ========================================================================

    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id"),
        nullable=True
    )

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    # Admin users
    admin: Mapped[Optional["AdminUser"]] = relationship(
        "AdminUser",
        foreign_keys=[assigned_to],
        lazy="select"
    )
    creator: Mapped["AdminUser"] = relationship(
        "AdminUser",
        foreign_keys=[created_by],
        lazy="select"
    )
    deleter: Mapped[Optional["AdminUser"]] = relationship(
        "AdminUser",
        foreign_keys=[deleted_by],
        lazy="select"
    )

    # Customer notes (1-to-many)
    customer_notes: Mapped[list["CustomerNote"]] = relationship(
        "CustomerNote",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Customer interactions log (1-to-many)
    interactions: Mapped[list["CustomerInteraction"]] = relationship(
        "CustomerInteraction",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Bookings (backref from Booking when we add customer_id FK)
    # bookings: Mapped[list["Booking"]] = relationship(
    #     "Booking",
    #     back_populates="customer",
    #     lazy="dynamic"
    # )

    # Quotes (will be added when quotes domain is created)
    # quotes: Mapped[list["Quote"]] = relationship(
    #     "Quote",
    #     back_populates="customer",
    #     lazy="dynamic"
    # )

    # ========================================================================
    # HYBRID PROPERTIES - PII ENCRYPTION/DECRYPTION
    # ========================================================================

    @hybrid_property
    def email(self) -> str:
        """Decrypt email on read."""
        if not self._email:
            return None
        try:
            return decrypt_pii(self._email)
        except Exception:
            # If decryption fails, return None and log error
            return None

    @email.setter
    def email(self, value: str):
        """Encrypt email on write."""
        if value:
            self._email = encrypt_pii(value)
        else:
            self._email = None

    @hybrid_property
    def phone(self) -> str | None:
        """Decrypt phone on read."""
        if not self._phone:
            return None
        try:
            return decrypt_pii(self._phone)
        except Exception:
            return None

    @phone.setter
    def phone(self, value: str | None):
        """Encrypt phone on write."""
        if value:
            self._phone = encrypt_pii(value)
        else:
            self._phone = None

    # ========================================================================
    # BUSINESS LOGIC PROPERTIES
    # ========================================================================

    @hybrid_property
    def is_active_customer(self) -> bool:
        """Verifica se è un cliente attivo."""
        return self.status == CustomerStatus.ACTIVE.value

    @hybrid_property
    def days_since_last_contact(self) -> int | None:
        """Giorni dall'ultimo contatto."""
        if not self.last_contact_date:
            return None
        delta = datetime.utcnow() - self.last_contact_date
        return delta.days

    @hybrid_property
    def needs_followup(self) -> bool:
        """Verifica se serve un follow-up."""
        if not self.next_followup_date:
            return False
        return self.next_followup_date <= date.today()

    # ========================================================================
    # CONSTRAINTS
    # ========================================================================

    __table_args__ = (
        CheckConstraint(
            "lifetime_value >= 0",
            name="positive_lifetime_value"
        ),
        CheckConstraint(
            "total_spent >= 0",
            name="positive_total_spent"
        ),
        CheckConstraint(
            "completed_projects >= 0",
            name="positive_completed_projects"
        ),
    )

    def __repr__(self):
        return f"<Customer {self.id}: {self.name} ({self.status})>"


class CustomerNote(Base):
    """
    Note libere su un cliente.

    Utilizzato dal team per annotazioni interne, follow-up notes, etc.
    """
    __tablename__ = "customer_notes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Note content
    note: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="customer_notes"
    )
    admin: Mapped["AdminUser"] = relationship("AdminUser")

    def __repr__(self):
        return f"<CustomerNote {self.id} for Customer {self.customer_id}>"


class CustomerInteraction(Base):
    """
    Log delle interazioni con un cliente.

    Traccia: email inviate, chiamate, meeting, demo, follow-up, etc.
    Fornisce una timeline completa delle relazioni con il cliente.
    """
    __tablename__ = "customer_interactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Interaction type
    interaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # email, call, meeting, demo, support, etc.

    # Details
    subject: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    # Outcome
    outcome: Mapped[str | None] = mapped_column(String(50))
    # positive, neutral, negative, no_answer, etc.

    next_action: Mapped[str | None] = mapped_column(Text)  # Cosa fare dopo

    # Scheduled vs Completed
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Metadata
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="interactions"
    )
    admin: Mapped["AdminUser"] = relationship("AdminUser")

    def __repr__(self):
        return f"<CustomerInteraction {self.id}: {self.interaction_type} for Customer {self.customer_id}>"
