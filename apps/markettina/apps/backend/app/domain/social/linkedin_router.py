"""
🔌 LinkedIn Publishing Router

Endpoints per pubblicazione su LinkedIn.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.integrations.linkedin_publishing import (
    linkedin_service,
    LinkedInPostRequest,
    LinkedInPostResponse,
    LinkedInProfile,
    LinkedInVisibility,
    LinkedInMediaType,
)

router = APIRouter(prefix="/linkedin", tags=["linkedin"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class LinkedInStatusResponse(BaseModel):
    """Status configurazione LinkedIn."""
    configured: bool
    has_token: bool
    client_id_set: bool
    profile: Optional[LinkedInProfile] = None


class PublishTextRequest(BaseModel):
    """Request per post testuale."""
    text: str
    visibility: LinkedInVisibility = LinkedInVisibility.ANYONE


class PublishImageRequest(BaseModel):
    """Request per post con immagine."""
    text: str
    image_url: str
    visibility: LinkedInVisibility = LinkedInVisibility.ANYONE


class PublishArticleRequest(BaseModel):
    """Request per post con articolo."""
    text: str
    article_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    visibility: LinkedInVisibility = LinkedInVisibility.ANYONE


# =============================================================================
# OAUTH ENDPOINTS
# =============================================================================

@router.get("/auth/url")
async def get_auth_url(state: str = Query("markettina_linkedin_auth")):
    """
    Ottiene l'URL per autorizzazione LinkedIn OAuth.

    L'utente deve visitare questo URL per autorizzare MARKETTINA.
    """
    if not linkedin_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="LinkedIn non configurato. Imposta LINKEDIN_CLIENT_ID e LINKEDIN_CLIENT_SECRET."
        )

    url = linkedin_service.get_authorization_url(state)
    return {"authorization_url": url}


@router.get("/auth/callback")
async def oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None
):
    """
    Callback OAuth da LinkedIn.

    LinkedIn redirige qui dopo l'autorizzazione.
    """
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"LinkedIn OAuth error: {error_description or error}"
        )

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Missing authorization code"
        )

    try:
        token_data = await linkedin_service.exchange_code_for_token(code)

        return {
            "success": True,
            "message": "LinkedIn collegato con successo!",
            "access_token": token_data.get("access_token"),
            "expires_in": token_data.get("expires_in"),
            "note": "Salva l'access_token come LINKEDIN_ACCESS_TOKEN nelle variabili d'ambiente."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# STATUS
# =============================================================================

@router.get("/status", response_model=LinkedInStatusResponse)
async def get_status():
    """
    Verifica lo status della connessione LinkedIn.
    """
    profile = None

    if linkedin_service.has_token:
        try:
            profile = await linkedin_service.get_profile()
        except Exception:
            pass

    return LinkedInStatusResponse(
        configured=linkedin_service.is_configured,
        has_token=linkedin_service.has_token,
        client_id_set=bool(linkedin_service.client_id),
        profile=profile
    )


@router.get("/profile", response_model=LinkedInProfile)
async def get_profile():
    """
    Ottiene il profilo LinkedIn autenticato.
    """
    if not linkedin_service.has_token:
        raise HTTPException(
            status_code=401,
            detail="Non autenticato su LinkedIn. Usa /auth/url per iniziare."
        )

    try:
        return await linkedin_service.get_profile()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# PUBLISHING
# =============================================================================

@router.post("/publish/text", response_model=LinkedInPostResponse)
async def publish_text_post(request: PublishTextRequest):
    """
    Pubblica un post di solo testo su LinkedIn.
    """
    if not linkedin_service.has_token:
        return LinkedInPostResponse(
            success=False,
            error="Non autenticato su LinkedIn"
        )

    return await linkedin_service.create_text_post(
        text=request.text,
        visibility=request.visibility
    )


@router.post("/publish/image", response_model=LinkedInPostResponse)
async def publish_image_post(request: PublishImageRequest):
    """
    Pubblica un post con immagine su LinkedIn.

    L'immagine viene scaricata dall'URL e caricata su LinkedIn.
    """
    if not linkedin_service.has_token:
        return LinkedInPostResponse(
            success=False,
            error="Non autenticato su LinkedIn"
        )

    return await linkedin_service.create_image_post(
        text=request.text,
        image_url=request.image_url,
        visibility=request.visibility
    )


@router.post("/publish/article", response_model=LinkedInPostResponse)
async def publish_article_post(request: PublishArticleRequest):
    """
    Pubblica un post con link a un articolo su LinkedIn.

    LinkedIn genererà automaticamente l'anteprima del link.
    """
    if not linkedin_service.has_token:
        return LinkedInPostResponse(
            success=False,
            error="Non autenticato su LinkedIn"
        )

    return await linkedin_service.create_article_post(
        text=request.text,
        article_url=request.article_url,
        title=request.title,
        description=request.description,
        visibility=request.visibility
    )


@router.post("/publish", response_model=LinkedInPostResponse)
async def publish_unified(request: LinkedInPostRequest):
    """
    Endpoint unificato per pubblicazione.

    Sceglie automaticamente il tipo di post basandosi sulla request.
    """
    if not linkedin_service.has_token:
        return LinkedInPostResponse(
            success=False,
            error="Non autenticato su LinkedIn"
        )

    return await linkedin_service.publish(request)


# =============================================================================
# ANALYTICS
# =============================================================================

@router.get("/posts/{post_id}/stats")
async def get_post_stats(post_id: str):
    """
    Ottiene statistiche base di un post.
    """
    if not linkedin_service.has_token:
        raise HTTPException(status_code=401, detail="Non autenticato")

    stats = await linkedin_service.get_post_stats(post_id)
    return stats
