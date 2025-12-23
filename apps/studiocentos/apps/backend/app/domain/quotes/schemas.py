"""
Quotes Domain Schemas - Pydantic validation models.

Gestisce la validazione degli input e la serializzazione delle risposte API
per il dominio quotes.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator

from .models import QuoteStatus


# ============================================================================
# QUOTE LINE ITEM SCHEMAS
# ============================================================================

class QuoteLineItemBase(BaseModel):
    """Base schema for quote line item."""
    name: str = Field(..., min_length=1, max_length=255, description="Nome prodotto/servizio")
    description: Optional[str] = Field(None, description="Descrizione dettagliata")
    sku: Optional[str] = Field(None, max_length=100, description="Codice prodotto")
    quantity: Decimal = Field(..., gt=0, description="Quantità")
    unit_price: Decimal = Field(..., ge=0, description="Prezzo unitario")
    discount_percentage: Decimal = Field(default=Decimal('0.00'), ge=0, le=100, description="Sconto %")
    position: int = Field(default=0, ge=0, description="Posizione nella lista")


class QuoteLineItemCreate(QuoteLineItemBase):
    """Schema for creating a quote line item."""
    pass


class QuoteLineItemUpdate(BaseModel):
    """Schema for updating a quote line item (partial)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, max_length=100)
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    position: Optional[int] = Field(None, ge=0)


class QuoteLineItemResponse(QuoteLineItemBase):
    """Schema for quote line item response."""
    id: int
    quote_id: int
    discount_amount: Decimal
    subtotal: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# QUOTE SCHEMAS
# ============================================================================

class QuoteBase(BaseModel):
    """Base schema for quote."""
    title: str = Field(..., min_length=1, max_length=255, description="Titolo preventivo")
    description: Optional[str] = Field(None, description="Descrizione/Note")
    customer_id: int = Field(..., description="ID cliente")

    # Financial
    currency: str = Field(default="EUR", max_length=3, description="Valuta (ISO 4217)")
    tax_rate: Decimal = Field(default=Decimal('22.00'), ge=0, le=100, description="Aliquota IVA %")
    discount_percentage: Decimal = Field(default=Decimal('0.00'), ge=0, le=100, description="Sconto globale %")

    # Dates
    issue_date: date = Field(default_factory=date.today, description="Data emissione")
    valid_until: date = Field(..., description="Valido fino al")
    payment_terms_days: int = Field(default=30, ge=0, description="Giorni pagamento")
    delivery_date: Optional[date] = Field(None, description="Data consegna prevista")

    # Terms
    payment_terms: Optional[str] = Field(None, description="Condizioni di pagamento")
    terms_and_conditions: Optional[str] = Field(None, description="Termini e condizioni")
    notes_to_customer: Optional[str] = Field(None, description="Note per il cliente")
    internal_notes: Optional[str] = Field(None, description="Note interne")

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        """Valida che currency sia un codice ISO valido."""
        valid_currencies = ['EUR', 'USD', 'GBP', 'CHF']
        if v.upper() not in valid_currencies:
            raise ValueError(f"Currency deve essere uno di: {', '.join(valid_currencies)}")
        return v.upper()

    @field_validator('valid_until')
    @classmethod
    def validate_valid_until(cls, v, info):
        """Valida che valid_until sia nel futuro."""
        values = info.data
        issue_date = values.get('issue_date', date.today())
        if v < issue_date:
            raise ValueError("valid_until deve essere >= issue_date")
        return v


class QuoteCreate(QuoteBase):
    """Schema for creating a new quote."""
    line_items: List[QuoteLineItemCreate] = Field(
        ...,
        min_length=1,
        description="Line items del preventivo (almeno 1 richiesto)"
    )


class QuoteUpdate(BaseModel):
    """Schema for updating a quote (partial)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

    # Financial
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)

    # Dates
    valid_until: Optional[date] = None
    payment_terms_days: Optional[int] = Field(None, ge=0)
    delivery_date: Optional[date] = None

    # Terms
    payment_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    notes_to_customer: Optional[str] = None
    internal_notes: Optional[str] = None


class QuoteResponse(QuoteBase):
    """Schema for quote response (full details)."""
    id: int
    quote_number: str

    # Versioning
    version: int
    is_latest: bool
    parent_quote_id: Optional[int]

    # Calculated financials
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total: Decimal

    # Status
    status: str
    sent_at: Optional[datetime]
    viewed_at: Optional[datetime]
    accepted_at: Optional[datetime]
    accepted_by_name: Optional[str]
    accepted_by_email: Optional[str]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]

    # PDF
    pdf_file_path: Optional[str]
    pdf_generated_at: Optional[datetime]

    # Line items
    line_items: List[QuoteLineItemResponse]

    # Metadata
    created_by: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True


class QuoteListItem(BaseModel):
    """Lightweight schema for quote list."""
    id: int
    quote_number: str
    title: str
    customer_id: int
    status: str
    version: int
    is_latest: bool
    total: Decimal
    currency: str
    valid_until: date
    created_at: datetime
    sent_at: Optional[datetime]
    accepted_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# QUOTE ACTIONS SCHEMAS
# ============================================================================

class QuoteSendRequest(BaseModel):
    """Schema for sending a quote to customer."""
    customer_email: Optional[str] = Field(None, description="Override customer email")
    cc_emails: Optional[List[str]] = Field(None, description="CC these emails")
    custom_message: Optional[str] = Field(None, description="Custom message to include")


class QuoteAcceptRequest(BaseModel):
    """Schema for accepting a quote."""
    accepted_by_name: str = Field(..., min_length=1, max_length=255)
    accepted_by_email: str = Field(..., description="Email del firmatario")
    signature: Optional[str] = Field(None, description="Firma digitale")
    notes: Optional[str] = Field(None, description="Note cliente")


class QuoteRejectRequest(BaseModel):
    """Schema for rejecting a quote."""
    rejection_reason: str = Field(..., min_length=1, description="Motivo del rifiuto")


class QuoteDuplicateRequest(BaseModel):
    """Schema for creating a new version of a quote."""
    reason: Optional[str] = Field(None, description="Motivo della nuova versione")
    changes_summary: Optional[str] = Field(None, description="Sommario modifiche")


# ============================================================================
# ANALYTICS & STATS SCHEMAS
# ============================================================================

class QuoteStats(BaseModel):
    """Quote analytics and statistics."""
    total_quotes: int = Field(description="Totale preventivi")
    by_status: dict[str, int] = Field(description="Preventivi per status")
    total_value: Decimal = Field(description="Valore totale preventivi")
    accepted_value: Decimal = Field(description="Valore preventivi accettati")
    conversion_rate: Decimal = Field(description="Tasso di conversione %")
    avg_quote_value: Decimal = Field(description="Valore medio preventivo")
    avg_conversion_time_days: Optional[Decimal] = Field(
        None,
        description="Tempo medio conversione (giorni)"
    )


class QuoteFilters(BaseModel):
    """Schema for quote listing filters."""
    customer_id: Optional[int] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    is_latest: Optional[bool] = Field(None, description="Solo ultime versioni")
    from_date: Optional[date] = Field(None, description="Da data emissione")
    to_date: Optional[date] = Field(None, description="A data emissione")
    min_value: Optional[Decimal] = Field(None, ge=0, description="Valore minimo")
    max_value: Optional[Decimal] = Field(None, ge=0, description="Valore massimo")
    search: Optional[str] = Field(None, description="Cerca in title, quote_number")
    skip: int = Field(default=0, ge=0, description="Pagination offset")
    limit: int = Field(default=50, ge=1, le=100, description="Pagination limit")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Valida che status sia uno dei valori enum."""
        if v is None:
            return v
        valid_statuses = [s.value for s in QuoteStatus]
        if v not in valid_statuses:
            raise ValueError(f"Status deve essere uno di: {', '.join(valid_statuses)}")
        return v


class QuoteConversionReport(BaseModel):
    """Report di conversione preventivi."""
    period_start: date
    period_end: date
    total_sent: int
    total_accepted: int
    total_rejected: int
    total_expired: int
    conversion_rate: Decimal
    total_value_sent: Decimal
    total_value_accepted: Decimal
    avg_time_to_accept_days: Optional[Decimal]
    top_converting_customers: List[dict]


# ============================================================================
# QUOTE VERSION SCHEMAS
# ============================================================================

class QuoteVersionResponse(BaseModel):
    """Schema for quote version history."""
    id: int
    original_quote_id: int
    new_quote_id: int
    version_number: int
    changes_summary: Optional[str]
    reason: Optional[str]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True
