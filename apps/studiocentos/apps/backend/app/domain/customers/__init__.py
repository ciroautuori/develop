"""
Customers Domain - CRM centralizzato StudioCentOS.

Questo dominio gestisce l'anagrafica clienti completa con funzionalità CRM.
"""

from .models import (
    Customer,
    CustomerNote,
    CustomerInteraction,
    CustomerStatus,
    CustomerType,
    CustomerSource,
)
from .schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListItem,
    CustomerNoteCreate,
    CustomerNoteResponse,
    CustomerInteractionCreate,
    CustomerInteractionResponse,
    CustomerStats,
)
from .services import CustomerService

__all__ = [
    # Models
    "Customer",
    "CustomerNote",
    "CustomerInteraction",
    "CustomerStatus",
    "CustomerType",
    "CustomerSource",
    # Schemas
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerListItem",
    "CustomerNoteCreate",
    "CustomerNoteResponse",
    "CustomerInteractionCreate",
    "CustomerInteractionResponse",
    "CustomerStats",
    # Services
    "CustomerService",
]
