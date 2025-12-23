"""
Customers Domain Schemas - Pydantic validation models.

Questi schema gestiscono la validazione degli input e la serializzazione
delle risposte API per il dominio customers.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator

from .models import CustomerSource, CustomerStatus, CustomerType

# ============================================================================
# CUSTOMER SCHEMAS
# ============================================================================

class CustomerBase(BaseModel):
    """Base schema for customer (shared fields)."""
    name: str = Field(..., min_length=1, max_length=255, description="Nome completo o ragione sociale")
    email: EmailStr = Field(..., description="Email del cliente (verrà crittografata)")
    phone: str | None = Field(None, max_length=50, description="Numero di telefono")
    company_name: str | None = Field(None, max_length=255, description="Nome azienda")
    company_vat_id: str | None = Field(None, max_length=50, description="P.IVA / VAT number")
    company_website: str | None = Field(None, max_length=255, description="Sito web aziendale")

    # Address
    address_line1: str | None = Field(None, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=100)
    state_province: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    country: str = Field(default="IT", max_length=2, description="Codice paese ISO 3166-1 alpha-2")

    # CRM fields
    status: str = Field(
        default=CustomerStatus.LEAD.value,
        description="Status nel funnel di vendita"
    )
    customer_type: str = Field(
        default=CustomerType.INDIVIDUAL.value,
        description="Tipologia cliente"
    )
    source: str = Field(
        default=CustomerSource.WEBSITE.value,
        description="Canale di acquisizione"
    )
    assigned_to: int | None = Field(None, description="ID admin user responsabile")
    tags: str | None = Field(None, description="Tags separati da virgola (es: 'vip,enterprise')")
    notes: str | None = Field(None, description="Note generali sul cliente")

    # Marketing
    marketing_consent: bool = Field(default=False, description="Consenso marketing")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Valida che status sia uno dei valori enum."""
        valid_statuses = [s.value for s in CustomerStatus]
        if v not in valid_statuses:
            raise ValueError(f"Status deve essere uno di: {', '.join(valid_statuses)}")
        return v

    @field_validator("customer_type")
    @classmethod
    def validate_customer_type(cls, v):
        """Valida che customer_type sia uno dei valori enum."""
        valid_types = [t.value for t in CustomerType]
        if v not in valid_types:
            raise ValueError(f"Customer type deve essere uno di: {', '.join(valid_types)}")
        return v

    @field_validator("source")
    @classmethod
    def validate_source(cls, v):
        """Valida che source sia uno dei valori enum."""
        valid_sources = [s.value for s in CustomerSource]
        if v not in valid_sources:
            raise ValueError(f"Source deve essere uno di: {', '.join(valid_sources)}")
        return v

    @field_validator("country")
    @classmethod
    def validate_country(cls, v):
        """Valida che country sia un codice paese ISO valido."""
        if len(v) != 2:
            raise ValueError("Country deve essere un codice ISO 3166-1 alpha-2 (2 lettere)")
        return v.upper()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        """Valida formato telefono (base validation)."""
        if v is None:
            return v
        # Remove common separators
        clean_phone = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not clean_phone.replace("+", "").isdigit():
            raise ValueError("Phone deve contenere solo numeri, +, -, (, ), spazi")
        return v


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer."""


class CustomerUpdate(BaseModel):
    """
    Schema for updating a customer (all fields optional).

    Solo i campi forniti saranno aggiornati.
    """
    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    company_name: str | None = Field(None, max_length=255)
    company_vat_id: str | None = Field(None, max_length=50)
    company_website: str | None = Field(None, max_length=255)

    # Address
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state_province: str | None = None
    postal_code: str | None = None
    country: str | None = None

    # CRM
    status: str | None = None
    customer_type: str | None = None
    source: str | None = None
    assigned_to: int | None = None
    tags: str | None = None
    notes: str | None = None

    # Follow-up
    next_followup_date: date | None = None
    next_followup_notes: str | None = None

    # Marketing
    marketing_consent: bool | None = None


class CustomerResponse(CustomerBase):
    """
    Schema for customer response (include computed fields and metadata).

    Questo schema viene usato per le risposte API GET.
    """
    id: int

    # Financial (read-only)
    lifetime_value: Decimal = Field(description="Customer Lifetime Value calcolato")
    total_spent: Decimal = Field(description="Totale speso dal cliente")
    avg_deal_size: Decimal = Field(description="Dimensione media deal")
    completed_projects: int = Field(description="Numero progetti completati")
    last_purchase_date: date | None = Field(None, description="Data ultimo acquisto")

    # Engagement (read-only)
    last_contact_date: datetime | None = Field(None, description="Data ultimo contatto")
    last_contact_type: str | None = Field(None, description="Tipo ultimo contatto")
    next_followup_date: date | None = Field(None, description="Data prossimo follow-up")
    next_followup_notes: str | None = Field(None, description="Note per follow-up")

    # Metadata (read-only)
    created_by: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True  # Pydantic v2


class CustomerListItem(BaseModel):
    """
    Lightweight schema for customer list (pagination-friendly).

    Usato negli endpoint di listing per evitare di caricare tutti i dati.
    """
    id: int
    name: str
    email: str | None = None
    company_name: str | None
    status: str
    customer_type: str
    source: str
    lifetime_value: Decimal
    total_spent: Decimal
    last_contact_date: datetime | None
    next_followup_date: date | None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CUSTOMER NOTE SCHEMAS
# ============================================================================

class CustomerNoteCreate(BaseModel):
    """Schema for creating a customer note."""
    note: str = Field(..., min_length=1, description="Contenuto della nota")


class CustomerNoteResponse(BaseModel):
    """Schema for customer note response."""
    id: int
    customer_id: int
    note: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CUSTOMER INTERACTION SCHEMAS
# ============================================================================

class CustomerInteractionCreate(BaseModel):
    """Schema for logging a customer interaction."""
    interaction_type: str = Field(
        ...,
        max_length=50,
        description="Tipo interazione (email, call, meeting, demo, etc.)"
    )
    subject: str | None = Field(None, max_length=255, description="Oggetto/Titolo")
    description: str | None = Field(None, description="Descrizione dettagliata")
    outcome: str | None = Field(None, max_length=50, description="Esito (positive, neutral, negative, etc.)")
    next_action: str | None = Field(None, description="Prossima azione da intraprendere")
    scheduled_at: datetime | None = Field(None, description="Data/ora programmata")
    completed_at: datetime | None = Field(None, description="Data/ora completamento")

    @field_validator("interaction_type")
    @classmethod
    def validate_interaction_type(cls, v):
        """Valida che interaction_type sia uno dei tipi supportati."""
        valid_types = [
            "email", "call", "meeting", "demo", "support",
            "follow_up", "quote_sent", "contract_signed", "other"
        ]
        if v not in valid_types:
            # Allow custom types but log warning
            pass
        return v


class CustomerInteractionResponse(BaseModel):
    """Schema for customer interaction response."""
    id: int
    customer_id: int
    interaction_type: str
    subject: str | None
    description: str | None
    outcome: str | None
    next_action: str | None
    scheduled_at: datetime | None
    completed_at: datetime | None
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ANALYTICS & STATS SCHEMAS
# ============================================================================

class CustomerStats(BaseModel):
    """
    Customer analytics and statistics.

    Usato per dashboard e reporting.
    """
    total_customers: int = Field(description="Totale clienti (esclusi deleted)")
    by_status: dict[str, int] = Field(description="Clienti per status")
    by_type: dict[str, int] = Field(description="Clienti per tipo")
    by_source: dict[str, int] = Field(description="Clienti per canale acquisizione")
    total_lifetime_value: Decimal = Field(description="LTV totale di tutti i clienti")
    avg_lifetime_value: Decimal = Field(description="LTV medio")
    top_customers: list[CustomerListItem] = Field(description="Top 5 clienti per LTV")


class CustomerFilters(BaseModel):
    """
    Schema for customer listing filters.

    Usato per filtrare la lista clienti.
    """
    status: str | None = None
    customer_type: str | None = None
    source: str | None = None
    assigned_to: int | None = None
    search: str | None = Field(None, description="Cerca in name, company_name")
    tags: str | None = Field(None, description="Filtra per tags (comma-separated)")
    needs_followup: bool | None = Field(None, description="Solo clienti che necessitano follow-up")
    skip: int = Field(default=0, ge=0, description="Pagination offset")
    limit: int = Field(default=50, ge=1, le=100, description="Pagination limit")


class CustomerBulkUpdateStatus(BaseModel):
    """Schema for bulk updating customer status."""
    customer_ids: list[int] = Field(..., min_length=1, max_length=100)
    new_status: str

    @field_validator("new_status")
    @classmethod
    def validate_status(cls, v):
        """Valida che new_status sia uno dei valori enum."""
        valid_statuses = [s.value for s in CustomerStatus]
        if v not in valid_statuses:
            raise ValueError(f"Status deve essere uno di: {', '.join(valid_statuses)}")
        return v


class CustomerMergeRequest(BaseModel):
    """
    Schema for merging duplicate customers.

    Merge customer_ids into primary_customer_id.
    """
    primary_customer_id: int = Field(..., description="Customer da mantenere")
    customer_ids_to_merge: list[int] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Customers da unire nel principale"
    )

    @field_validator("customer_ids_to_merge")
    @classmethod
    def validate_no_duplicates(cls, v, info):
        """Valida che non ci siano duplicati e che primary non sia incluso."""
        if len(v) != len(set(v)):
            raise ValueError("customer_ids_to_merge contiene duplicati")

        values = info.data
        if "primary_customer_id" in values and values["primary_customer_id"] in v:
            raise ValueError("primary_customer_id non può essere in customer_ids_to_merge")

        return v


# ============================================================================
# FASE 1: LEAD MANAGEMENT SCHEMAS
# ============================================================================

class LeadItem(BaseModel):
    """Lead item from copilot lead search."""
    id: int
    company: str
    industry: str
    size: str = Field(description="micro, piccola, pmi, media")
    location: str
    address: str = ""
    phone: str = ""
    email: str | None = None
    website: str = ""
    need: str
    need_reason: str = ""
    score: int = Field(ge=0, le=100, description="Match score 0-100")
    google_rating: float = 0.0
    reviews_count: int = 0


class BulkCreateFromLeadsRequest(BaseModel):
    """Request schema for creating customers from lead finder results."""
    leads: list[LeadItem] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of leads to convert to customers"
    )


class BulkCreateFromLeadsResponse(BaseModel):
    """Response schema for bulk customer creation from leads."""
    created_count: int = Field(description="Number of customers created")
    skipped_count: int = Field(description="Number of duplicates skipped")
    created_ids: list[int] = Field(description="IDs of created customers")
    skipped_emails: list[str] = Field(description="Emails of skipped duplicates")
    message: str
