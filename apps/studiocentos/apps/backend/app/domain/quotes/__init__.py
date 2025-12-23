"""
Quotes Domain - Sistema di preventivazione StudioCentOS.

Questo dominio gestisce la creazione, invio e tracking dei preventivi commerciali,
con supporto per versionamento, line items dettagliati e generazione PDF.
"""

from .models import (
    Quote,
    QuoteLineItem,
    QuoteStatus,
    QuoteVersion,
)
from .schemas import (
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteListItem,
    QuoteLineItemCreate,
    QuoteLineItemUpdate,
    QuoteLineItemResponse,
    QuoteStats,
)
from .services import QuoteService

__all__ = [
    # Models
    "Quote",
    "QuoteLineItem",
    "QuoteStatus",
    "QuoteVersion",
    # Schemas
    "QuoteCreate",
    "QuoteUpdate",
    "QuoteResponse",
    "QuoteListItem",
    "QuoteLineItemCreate",
    "QuoteLineItemUpdate",
    "QuoteLineItemResponse",
    "QuoteStats",
    # Services
    "QuoteService",
]
