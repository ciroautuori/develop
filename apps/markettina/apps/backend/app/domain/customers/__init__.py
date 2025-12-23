"""
Customers Domain - CRM centralizzato MARKETTINA.

Questo dominio gestisce l'anagrafica clienti completa con funzionalità CRM.
"""

from .models import (
    Customer,
    CustomerInteraction,
    CustomerNote,
    CustomerSource,
    CustomerStatus,
    CustomerType,
)
from .schemas import (
    CustomerCreate,
    CustomerInteractionCreate,
    CustomerInteractionResponse,
    CustomerListItem,
    CustomerNoteCreate,
    CustomerNoteResponse,
    CustomerResponse,
    CustomerStats,
    CustomerUpdate,
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
