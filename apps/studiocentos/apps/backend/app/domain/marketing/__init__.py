"""
Marketing Domain - Email Automation + Lead Generation
Sistema automatico per campagne email e ricerca clienti Salerno/Campania
"""

from .models import EmailCampaign, Lead, LeadSource, LeadStatus
from .schemas import (
    EmailCampaignCreate,
    EmailCampaignResponse,
    LeadCreate,
    LeadResponse,
    LeadListResponse
)
from .service import MarketingService
from .leads_router import router

__all__ = [
    # Models
    'EmailCampaign',
    'Lead',
    'LeadSource',
    'LeadStatus',
    # Schemas
    'EmailCampaignCreate',
    'EmailCampaignResponse',
    'LeadCreate',
    'LeadResponse',
    'LeadListResponse',
    # Service
    'MarketingService',
    # Router
    'router',
]
