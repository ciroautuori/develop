"""
LinkedIn Publishing Router - API endpoints per pubblicazione LinkedIn.

Endpoints:
- GET  /auth/url              - URL autorizzazione OAuth
- GET  /auth/callback         - Callback OAuth
- GET  /status                - Stato connessione
- GET  /profile               - Profilo utente
- GET  /organizations         - Company Pages gestite
- POST /publish/text          - Pubblica post testo
- POST /publish/image         - Pubblica post con immagine
- POST /publish/article       - Pubblica post con link
- POST /publish/company       - Pubblica su Company Page
- POST /publish               - Pubblicazione unificata
- GET  /analytics/{post_urn}  - Analytics post
"""

from datetime import datetime
from typing import Optional
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, HttpUrl

from app.core.api.dependencies.permissions import require_admin
from app.domain.auth.models import User
from app.integrations.linkedin_publishing import (
    get_linkedin_publishing_service,
    LinkedInPublishingService,
    LinkedInAPIError,
    Visibility,
    MediaCategory,
    PostContent,
    PostResult,
    LinkedInProfile,
    Organization,
    LinkedInStatus,
    PostAnalytics,
    TokenResponse
)

router = APIRouter(prefix="/social/linkedin", tags=["LinkedIn Publishing"])


# =============================================================================
# DEPENDENCIES
# =============================================================================


def get_service() -> LinkedInPublishingService:
    """Dependency per LinkedIn service."""
    return get_linkedin_publishing_service()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class AuthUrlResponse(BaseModel):
    """Response con URL autorizzazione."""
    authorization_url: str
    state: str
    expires_in: int = 600  # seconds


class AuthCallbackRequest(BaseModel):
    """Request callback OAuth."""
    code: str
    state: str


class TextPostRequest(BaseModel):
    """Request per post testo."""
    text: str = Field(..., min_length=1, max_length=3000, description="Testo del post")
    visibility: Visibility = Field(default=Visibility.PUBLIC, description="Visibilità")


class ImagePostRequest(BaseModel):
    """Request per post con immagine."""
    text: str = Field(..., min_length=1, max_length=3000, description="Testo del post")
    image_url: str = Field(..., description="URL immagine da caricare")
    title: Optional[str] = Field(None, max_length=200, description="Titolo immagine")
    description: Optional[str] = Field(None, max_length=300, description="Descrizione")
    visibility: Visibility = Field(default=Visibility.PUBLIC)


class ArticlePostRequest(BaseModel):
    """Request per post con link/articolo."""
    text: str = Field(..., min_length=1, max_length=3000, description="Testo del post")
    article_url: str = Field(..., description="URL articolo")
    title: Optional[str] = Field(None, max_length=200, description="Titolo")
    description: Optional[str] = Field(None, max_length=300, description="Descrizione")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail personalizzata")
    visibility: Visibility = Field(default=Visibility.PUBLIC)


class CompanyPostRequest(BaseModel):
    """Request per post su Company Page."""
    organization_id: str = Field(..., description="ID Company Page")
    text: str = Field(..., min_length=1, max_length=3000)
    visibility: Visibility = Field(default=Visibility.PUBLIC)
    media_category: MediaCategory = Field(default=MediaCategory.NONE)

    # Per IMAGE
    media_url: Optional[str] = None
    media_title: Optional[str] = None
    media_description: Optional[str] = None

    # Per ARTICLE
    article_url: Optional[str] = None
    article_title: Optional[str] = None
    article_description: Optional[str] = None


class UnifiedPublishRequest(BaseModel):
    """Request pubblicazione unificata."""
    text: str = Field(..., min_length=1, max_length=3000)
    visibility: Visibility = Field(default=Visibility.PUBLIC)
    media_category: MediaCategory = Field(default=MediaCategory.NONE)

    # Per IMAGE/VIDEO
    media_url: Optional[str] = None
    media_title: Optional[str] = None
    media_description: Optional[str] = None

    # Per ARTICLE
    article_url: Optional[str] = None
    article_title: Optional[str] = None
    article_description: Optional[str] = None

    # Company page (opzionale)
    organization_id: Optional[str] = None


class StatusResponse(BaseModel):
    """Response stato connessione."""
    connected: bool
    configured: bool
    has_token: bool
    profile: Optional[LinkedInProfile] = None
    organizations_count: int = 0
    error: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# OAUTH ENDPOINTS
# =============================================================================


# In-memory state storage (in produzione usare Redis)
_oauth_states: dict = {}


@router.get("/auth/url", response_model=AuthUrlResponse)
async def get_authorization_url(
    current_user: User = Depends(require_admin),
    service: LinkedInPublishingService = Depends(get_service)
):
    """
    Genera URL per autorizzazione OAuth LinkedIn.

    Redirect l'utente a questo URL per avviare il flusso OAuth.
    Il state viene memorizzato per validazione al callback.
    """
    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LinkedIn OAuth non configurato. Configurare LINKEDIN_CLIENT_ID e LINKEDIN_CLIENT_SECRET."
        )

    state = secrets.token_urlsafe(32)

    # Store state with user info and expiration
    _oauth_states[state] = {
        "user_id": current_user.id,
        "created_at": datetime.utcnow().timestamp()
    }

    # Cleanup old states (older than 10 minutes)
    current_time = datetime.utcnow().timestamp()
    expired_states = [s for s, v in _oauth_states.items() if current_time - v["created_at"] > 600]
    for s in expired_states:
        del _oauth_states[s]

    auth_url = service.get_authorization_url(state)

    return AuthUrlResponse(
        authorization_url=auth_url,
        state=state,
        expires_in=600
    )


@router.get("/auth/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code"),
    state: str = Query(..., description="State parameter"),
    service: LinkedInPublishingService = Depends(get_service)
):
    """
    Callback OAuth LinkedIn.

    Riceve authorization code e lo scambia per access token.
    In produzione, salvare il token nel database.
    """
    # Validate state
    if state not in _oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter"
        )

    state_data = _oauth_states.pop(state)

    # Check expiration
    if datetime.utcnow().timestamp() - state_data["created_at"] > 600:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization request expired"
        )

    try:
        token = await service.exchange_code_for_token(code)

        # In produzione: salvare token nel database associato all'utente
        # await save_linkedin_token(state_data["user_id"], token)

        # Get profile for confirmation
        profile = await service.get_profile()

        return {
            "success": True,
            "message": f"LinkedIn connesso con successo come {profile.first_name} {profile.last_name}",
            "profile": profile.model_dump(),
            "expires_at": token.expires_at.isoformat(),
            "note": "Token deve essere salvato in LINKEDIN_ACCESS_TOKEN"
        }

    except LinkedInAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# STATUS ENDPOINTS
# =============================================================================


@router.get("/status", response_model=LinkedInStatus)
async def get_linkedin_status(
    current_user: User = Depends(require_admin),
    service: LinkedInPublishingService = Depends(get_service)
):
    """
    Stato connessione LinkedIn.

    Verifica se il token è valido e restituisce info profilo.
    """
    return await service.get_status()


@router.get("/profile", response_model=LinkedInProfile)
async def get_profile(
    current_user: User = Depends(require_admin),
    service: LinkedInPublishingService = Depends(get_service)
):
    """
    Ottiene profilo LinkedIn corrente.
    """
    if not service.has_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LinkedIn non connesso. Completare OAuth flow."
        )

    try:
        return await service.get_profile()
    except LinkedInAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/organizations", response_model=list[Organization])
async def get_organizations(
    current_user: User = Depends(require_admin),
    service: LinkedInPublishingService = Depends(get_service)
):
    """
    Lista Company Pages gestite dall'utente.
    """
    if not service.has_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LinkedIn non connesso"
        )

    try:
        return await service.get_organizations()
    except LinkedInAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# PUBLISHING ENDPOINTS
# =============================================================================


@router.post("/publish/text", response_model=PostResult)
async def publish_text_post(
    request: TextPostRequest,
    current_user: User = Depends(require_admin),
    service: LinkedInPublishingService = Depends(get_service)
):
    """
    Pubblica post di solo testo su LinkedIn.

    Limite: 3000 caratteri.
    """
    if not service.has_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LinkedIn non connesso"
        )

    result = await service.publish_text_post(
        text=request.text,
        visibility=request.visibility
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error
        )

    return result


@router.post("/publish/image", response_model=PostResult)
async def publish_image_post(
    request: ImagePostRequest,
    current_user: User = Depends(require_admin),
    service: LinkedInPublishingService = Depends(get_service)
):
    """
    Pubblica post con immagine su LinkedIn.

    L'immagine viene scaricata dall'URL e caricata su LinkedIn CDN.
    Limite immagine: 8MB.
    """
    if not service.has_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LinkedIn non connesso"
        )

    result = await service.publish_image_post(
        text=request.text,
        image_url=request.image_url,
        title=request.title,
        description=request.description,
        visibility=request.visibility
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error
        )

    return result


@router.post("/publish/article", response_model=PostResult)
async def publish_article_post(
    request: ArticlePostRequest,
    current_user: User = Depends(require_admin),
    service: LinkedInPublishingService = Depends(get_service)
):
    """
    Pubblica post con link/articolo su LinkedIn.

    LinkedIn genera automaticamente preview del link.
    """
    if not service.has_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LinkedIn non connesso"
        )

    result = await service.publish_article_post(
        text=request.text,
        article_url=request.article_url,
        title=request.title,
        description=request.description,
        thumbnail_url=request.thumbnail_url,
        visibility=request.visibility
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error
        )

    return result


@router.post("/publish/company", response_model=PostResult)
async def publish_to_company_page(
    request: CompanyPostRequest,
    current_user: User = Depends(require_admin),
    service: LinkedInPublishingService = Depends(get_service)
):
    """
    Pubblica su Company Page LinkedIn.

    L'utente deve essere amministratore della pagina.
    """
    if not service.has_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LinkedIn non connesso"
        )

    content = PostContent(
        text=request.text,
        visibility=request.visibility,
        media_category=request.media_category,
        media_url=request.media_url,
        media_title=request.media_title,
        media_description=request.media_description,
        article_url=request.article_url,
        article_title=request.article_title,
        article_description=request.article_description
    )

    result = await service.publish_to_company(
        organization_id=request.organization_id,
        content=content
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error
        )

    return result


@router.post("/publish", response_model=PostResult)
async def publish_unified(
    request: UnifiedPublishRequest,
    current_user: User = Depends(require_admin),
    service: LinkedInPublishingService = Depends(get_service)
):
    """
    Endpoint unificato per pubblicazione LinkedIn.

    Supporta tutti i tipi di contenuto:
    - NONE: solo testo
    - IMAGE: testo + immagine
    - ARTICLE: testo + link

    Se organization_id è specificato, pubblica su Company Page.
    """
    if not service.has_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LinkedIn non connesso"
        )

    content = PostContent(
        text=request.text,
        visibility=request.visibility,
        media_category=request.media_category,
        media_url=request.media_url,
        media_title=request.media_title,
        media_description=request.media_description,
        article_url=request.article_url,
        article_title=request.article_title,
        article_description=request.article_description
    )

    # Company page or personal profile
    if request.organization_id:
        result = await service.publish_to_company(
            organization_id=request.organization_id,
            content=content
        )
    else:
        result = await service.publish(content)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error
        )

    return result


# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================


@router.get("/analytics/{post_urn:path}", response_model=PostAnalytics)
async def get_post_analytics(
    post_urn: str,
    current_user: User = Depends(require_admin),
    service: LinkedInPublishingService = Depends(get_service)
):
    """
    Ottiene analytics per un post LinkedIn.

    NOTA: Richiede Marketing Developer Platform (prodotto aggiuntivo LinkedIn).
    """
    if not service.has_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LinkedIn non connesso"
        )

    return await service.get_post_analytics(post_urn)
