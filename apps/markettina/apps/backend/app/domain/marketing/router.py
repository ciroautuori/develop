"""
Marketing Router - API Endpoints
Lead generation + Email automation
"""


from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.core.api.dependencies.database import get_db
from app.domain.auth.admin_models import AdminUser

from .ab_testing_router import router as ab_testing_router
from .acquisition_router import router as acquisition_router
from .analytics_router import router as analytics_router
from .competitor_router import router as competitor_router
from .schemas import (
    EmailCampaignCreate,
    EmailCampaignResponse,
    GenerateEmailRequest,
    GenerateEmailResponse,
    LeadCreate,
    LeadListResponse,
    LeadResponse,
)
from .service import MarketingService
from .webhook_router import router as webhook_router
from .workflow_router import router as workflow_router

router = APIRouter(tags=["marketing"])

# Include acquisition router for unified client acquisition pipeline
router.include_router(acquisition_router)

# Include workflow automation router
router.include_router(workflow_router)

# Include analytics & reporting router
router.include_router(analytics_router)

# Include A/B testing router
router.include_router(ab_testing_router)

# Include webhook router
router.include_router(webhook_router)

# Include competitor monitoring router
router.include_router(competitor_router)


# ============================================================================
# LEADS ENDPOINTS
# ============================================================================

@router.post("/leads", response_model=LeadResponse)
def create_lead(
    data: LeadCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Crea nuovo lead."""
    return MarketingService.create_lead(db=db, data=data)


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Ottieni lead per ID."""
    return MarketingService.get_lead(db=db, lead_id=lead_id)


@router.get("/leads/search/salerno-campania", response_model=LeadListResponse)
def search_salerno_campania(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Ricerca automatica lead Salerno/Campania.
    Integrare Google Maps, LinkedIn, CCIAA.
    """
    return MarketingService.search_leads_salerno_campania(
        db=db,
        page=page,
        page_size=page_size
    )


# ============================================================================
# EMAIL GENERATION with AI
# ============================================================================

@router.post("/emails/generate", response_model=GenerateEmailResponse)
async def generate_email_ai(
    request: GenerateEmailRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Genera email personalizzata con AI.

    Usa iModels (GROQ/OpenRouter/Gemini) per generare:
    - Subject accattivante
    - HTML content professionale
    - Plain text version

    Personalizzato per regione e settore target.
    """
    return await MarketingService.generate_email_with_ai(db=db, request=request, admin=admin)


# ============================================================================
# EMAIL CAMPAIGNS
# ============================================================================

@router.post("/campaigns", response_model=EmailCampaignResponse)
def create_campaign(
    data: EmailCampaignCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Crea nuova campagna email.

    Può essere generata con AI o manuale.
    """
    return MarketingService.create_campaign(db=db, data=data)


@router.post("/campaigns/{campaign_id}/send")
async def send_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Invia campagna email a tutti i lead target.
    Implementare con SMTP/SendGrid.
    """
    return {"message": "Implement email sending with SMTP"}
