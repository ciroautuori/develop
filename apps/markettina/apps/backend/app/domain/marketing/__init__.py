"""
Marketing Domain - Email Automation + Lead Generation
Sistema automatico per campagne email e ricerca clienti Salerno/Campania
"""

from .models import EmailCampaign, Lead, LeadSource, LeadStatus
from .router import router
from .schemas import (
    EmailCampaignCreate,
    EmailCampaignResponse,
    LeadCreate,
    LeadListResponse,
    LeadResponse,
)
from .service import MarketingService

__all__ = [
    # Models
    "EmailCampaign",
    "Lead",
    "LeadSource",
    "LeadStatus",
    # Schemas
    "EmailCampaignCreate",
    "EmailCampaignResponse",
    "LeadCreate",
    "LeadResponse",
    "LeadListResponse",
    # Service
    "MarketingService",
    # Router
    "router",
]
