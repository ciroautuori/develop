"""
Quotes Domain Models - Preventivi e Proposte Commerciali.

Questo modulo implementa un sistema completo di preventivazione con:
- Quote versioning (v1, v2, v3 dopo negoziazioni)
- Line items dettagliati con pricing
- Status tracking del funnel
- Integration con Customers domain
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, TYPE_CHECKING, List
from enum import Enum

from sqlalchemy import (
    Column, BigInteger, String, Text, Numeric, Date, DateTime,
    Boolean, Integer, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

from app.infrastructure.database.session import Base

if TYPE_CHECKING:
    from app.domain.auth.admin_models import AdminUser
    from app.domain.customers.models import Customer


class QuoteStatus(str, Enum):
    """Status del preventivo nel funnel di vendita."""
    DRAFT = "draft"              # Bozza, non ancora inviata
    SENT = "sent"                # Inviata al cliente
    VIEWED = "viewed"            # Cliente ha visualizzato
    ACCEPTED = "accepted"        # Cliente ha accettato
    REJECTED = "rejected"        # Cliente ha rifiutato
    EXPIRED = "expired"          # Scaduta (oltre valid_until)
    CANCELLED = "cancelled"      # Annullata internamente


class Quote(Base):
    """
    Preventivo/Proposta commerciale.

    Rappresenta un preventivo inviato a un cliente con line items dettagliati,
    pricing, validità e tracking del funnel.

    Features:
    - Versioning (v1, v2, v3)
    - Automatic quote number generation
    - Financial calculations (subtotal, tax, total)
    - Status tracking con timestamps
    - Integration con Customers
    """
    __tablename__ = "quotes"

    # ========================================================================
    # PRIMARY KEY
    # ========================================================================

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # ========================================================================
    # QUOTE IDENTIFICATION
    # ========================================================================

    # Quote number (auto-generated: QUOTE-2025-0001)
    quote_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    # Title/Subject
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Description/Notes
    description: Mapped[Optional[str]] = mapped_column(Text)

    # ========================================================================
    # CUSTOMER RELATIONSHIP
    # ========================================================================

    customer_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    # ========================================================================
    # VERSIONING
    # ========================================================================

    # Version number (1, 2, 3, ...)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Is this the latest version?
    is_latest: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Parent quote ID (if this is a new version of existing quote)
    parent_quote_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("quotes.id"),
        nullable=True
    )

    # ========================================================================
    # FINANCIAL FIELDS
    # ========================================================================

    # Currency
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)

    # Subtotal (sum of line items, calculated)
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal('0.00'),
        nullable=False
    )

    # Tax rate (%)
    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal('22.00'),  # IVA italiana 22%
        nullable=False
    )

    # Tax amount (calculated: subtotal * tax_rate / 100)
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal('0.00'),
        nullable=False
    )

    # Discount (%)
    discount_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal('0.00'),
        nullable=False
    )

    # Discount amount (calculated)
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal('0.00'),
        nullable=False
    )

    # Total (subtotal - discount + tax)
    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal('0.00'),
        nullable=False
    )

    # ========================================================================
    # VALIDITY & DATES
    # ========================================================================

    # Quote issue date
    issue_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    # Valid until date
    valid_until: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Payment terms (days)
    payment_terms_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    # Expected delivery/completion date
    delivery_date: Mapped[Optional[date]] = mapped_column(Date)

    # ========================================================================
    # STATUS TRACKING
    # ========================================================================

    status: Mapped[str] = mapped_column(
        String(50),
        default=QuoteStatus.DRAFT.value,
        nullable=False,
        index=True
    )

    # Sent timestamp
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Viewed timestamp (first time)
    viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Accepted timestamp
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    accepted_by_name: Mapped[Optional[str]] = mapped_column(String(255))
    accepted_by_email: Mapped[Optional[str]] = mapped_column(String(255))

    # Rejected timestamp
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # ========================================================================
    # TERMS & CONDITIONS
    # ========================================================================

    # Payment terms text
    payment_terms: Mapped[Optional[str]] = mapped_column(Text)

    # Terms and conditions
    terms_and_conditions: Mapped[Optional[str]] = mapped_column(Text)

    # Notes to customer (visible on PDF)
    notes_to_customer: Mapped[Optional[str]] = mapped_column(Text)

    # Internal notes (not visible to customer)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text)

    # ========================================================================
    # PDF & FILES
    # ========================================================================

    # Generated PDF file path
    pdf_file_path: Mapped[Optional[str]] = mapped_column(String(500))

    # PDF generated at
    pdf_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

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
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    deleted_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id")
    )

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    # Customer relationship
    customer: Mapped["Customer"] = relationship(
        "Customer",
        foreign_keys=[customer_id],
        lazy="select"
    )

    # Line items (1-to-many)
    line_items: Mapped[List["QuoteLineItem"]] = relationship(
        "QuoteLineItem",
        back_populates="quote",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="QuoteLineItem.position"
    )

    # Parent quote (for versioning)
    parent_quote: Mapped[Optional["Quote"]] = relationship(
        "Quote",
        remote_side=[id],
        foreign_keys=[parent_quote_id],
        lazy="select"
    )

    # Child versions
    versions: Mapped[List["Quote"]] = relationship(
        "Quote",
        remote_side=[parent_quote_id],
        foreign_keys=[parent_quote_id],
        lazy="select"
    )

    # Admin users
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

    # ========================================================================
    # HYBRID PROPERTIES
    # ========================================================================

    @hybrid_property
    def is_expired(self) -> bool:
        """Verifica se il preventivo è scaduto."""
        if self.status == QuoteStatus.ACCEPTED.value:
            return False  # Accepted quotes don't expire
        return self.valid_until < date.today()

    @hybrid_property
    def days_until_expiry(self) -> int:
        """Giorni rimanenti prima della scadenza."""
        if self.status == QuoteStatus.ACCEPTED.value:
            return 0
        delta = self.valid_until - date.today()
        return delta.days

    @hybrid_property
    def days_since_sent(self) -> Optional[int]:
        """Giorni da quando è stato inviato."""
        if not self.sent_at:
            return None
        delta = datetime.utcnow() - self.sent_at
        return delta.days

    @hybrid_property
    def conversion_time_days(self) -> Optional[int]:
        """Giorni tra invio e accettazione."""
        if not self.sent_at or not self.accepted_at:
            return None
        delta = self.accepted_at - self.sent_at
        return delta.days

    # ========================================================================
    # CONSTRAINTS
    # ========================================================================

    __table_args__ = (
        CheckConstraint('subtotal >= 0', name='ck_quotes_positive_subtotal'),
        CheckConstraint('tax_rate >= 0 AND tax_rate <= 100', name='ck_quotes_valid_tax_rate'),
        CheckConstraint('discount_percentage >= 0 AND discount_percentage <= 100', name='ck_quotes_valid_discount'),
        CheckConstraint('total >= 0', name='ck_quotes_positive_total'),
        CheckConstraint('version >= 1', name='ck_quotes_positive_version'),
        CheckConstraint('payment_terms_days >= 0', name='ck_quotes_positive_payment_terms'),
    )

    def __repr__(self):
        return f"<Quote {self.quote_number} ({self.status}) - {self.total} {self.currency}>"


class QuoteLineItem(Base):
    """
    Line item di un preventivo.

    Rappresenta una singola riga di prodotto/servizio nel preventivo
    con descrizione, quantità, prezzo unitario e calcoli.
    """
    __tablename__ = "quote_line_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    quote_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("quotes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Position/Order in quote (for sorting)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Item details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # SKU/Product code (optional)
    sku: Mapped[Optional[str]] = mapped_column(String(100))

    # Pricing
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal('1.00'),
        nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    # Discount on this item (%)
    discount_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal('0.00'),
        nullable=False
    )

    # Calculated fields
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal('0.00'),
        nullable=False
    )

    # Subtotal (quantity * unit_price - discount)
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal('0.00'),
        nullable=False
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    quote: Mapped["Quote"] = relationship(
        "Quote",
        back_populates="line_items"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='ck_line_items_positive_quantity'),
        CheckConstraint('unit_price >= 0', name='ck_line_items_non_negative_price'),
        CheckConstraint('discount_percentage >= 0 AND discount_percentage <= 100', name='ck_line_items_valid_discount'),
        CheckConstraint('subtotal >= 0', name='ck_line_items_positive_subtotal'),
    )

    def __repr__(self):
        return f"<QuoteLineItem {self.name} - {self.quantity} x {self.unit_price}>"


class QuoteVersion(Base):
    """
    Tracking delle versioni di un preventivo.

    Mantiene uno storico delle modifiche tra versioni.
    Utile per audit e confronto versioni.
    """
    __tablename__ = "quote_versions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # Quote originale e nuova versione
    original_quote_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("quotes.id"),
        nullable=False,
        index=True
    )
    new_quote_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("quotes.id"),
        nullable=False,
        index=True
    )

    # Version info
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Change summary
    changes_summary: Mapped[Optional[str]] = mapped_column(Text)

    # Reason for new version
    reason: Mapped[Optional[str]] = mapped_column(Text)

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
    original_quote: Mapped["Quote"] = relationship(
        "Quote",
        foreign_keys=[original_quote_id],
        lazy="select"
    )
    new_quote: Mapped["Quote"] = relationship(
        "Quote",
        foreign_keys=[new_quote_id],
        lazy="select"
    )
    creator: Mapped["AdminUser"] = relationship("AdminUser")

    def __repr__(self):
        return f"<QuoteVersion v{self.version_number}: {self.original_quote_id} → {self.new_quote_id}>"
