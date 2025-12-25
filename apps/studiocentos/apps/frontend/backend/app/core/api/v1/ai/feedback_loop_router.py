"""
AI Feedback Loop Router - API endpoints per il sistema di apprendimento.

Espone gli endpoint REST per:
- Stato del sistema Feedback Loop
- Ingestione dati performance
- Analisi pattern
- Generazione learning signals
- Ottimizzazione prompt
- Sync da Instagram
- Suggerimenti contenuti

AUTENTICAZIONE: Tutti gli endpoint richiedono autenticazione admin.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field

from app.core.api.dependencies.auth_deps import get_current_user
from app.domain.auth.models import User, UserRole
from app.services.ai_feedback_loop import (
    get_feedback_loop_service,
    ContentPatterns,
    LearningSignals,
    OptimizedPrompt,
    PostPerformance,
    SyncResult,
    FeedbackLoopStatus,
)

router = APIRouter(prefix="/feedback-loop", tags=["ai-feedback-loop"])


# =============================================================================
# DEPENDENCIES
# =============================================================================


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Richiede ruolo admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required for AI Feedback Loop"
        )
    return current_user


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class StatusResponse(BaseModel):
    """Response per stato sistema."""
    success: bool
    data: FeedbackLoopStatus


class IngestRequest(BaseModel):
    """Request per ingestione dati."""
    posts: List[PostPerformance]
    followers_count: int = Field(ge=0, description="Numero followers account")


class IngestResponse(BaseModel):
    """Response per ingestione."""
    success: bool
    ingested: int
    message: str


class PatternsResponse(BaseModel):
    """Response per patterns."""
    success: bool
    data: ContentPatterns


class SignalsResponse(BaseModel):
    """Response per learning signals."""
    success: bool
    data: LearningSignals


class OptimizePromptRequest(BaseModel):
    """Request per ottimizzazione prompt."""
    prompt: str = Field(..., min_length=10, description="Prompt da ottimizzare")
    platform: str = Field(default="instagram", description="Piattaforma target")


class OptimizePromptResponse(BaseModel):
    """Response per prompt ottimizzato."""
    success: bool
    data: OptimizedPrompt


class SyncResponse(BaseModel):
    """Response per sync."""
    success: bool
    data: SyncResult


class SuggestionsResponse(BaseModel):
    """Response per suggerimenti."""
    success: bool
    suggestions: List[Dict[str, Any]]


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Stato Sistema Feedback Loop",
    description="Verifica lo stato del sistema di feedback loop AI."
)
async def get_status(
    admin: User = Depends(require_admin)
) -> StatusResponse:
    """
    Stato del sistema Feedback Loop.

    Returns:
        - enabled: Se il sistema è abilitato
        - platforms_configured: Piattaforme configurate
        - total_posts_analyzed: Post totali analizzati
        - last_sync: Ultimo sync
        - patterns_available: Pattern disponibili per piattaforma
    """
    service = get_feedback_loop_service()
    status = await service.get_status()

    return StatusResponse(
        success=True,
        data=status
    )


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Ingestione Dati Performance",
    description="Ingestisce manualmente dati performance per analisi."
)
async def ingest_performance_data(
    request: IngestRequest,
    admin: User = Depends(require_admin)
) -> IngestResponse:
    """
    Ingestisce dati performance.

    Utile per:
    - Import dati da altre fonti
    - Test del sistema
    - Dati storici

    Body:
        - posts: Lista di PostPerformance
        - followers_count: Numero followers per calcolo score
    """
    service = get_feedback_loop_service()

    try:
        ingested = await service.ingest_performance_data(
            posts=request.posts,
            followers_count=request.followers_count
        )

        return IngestResponse(
            success=True,
            ingested=ingested,
            message=f"Ingestiti {ingested}/{len(request.posts)} post con successo"
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/patterns/{platform}",
    response_model=PatternsResponse,
    summary="Pattern Identificati",
    description="Ottiene i pattern identificati dai contenuti performanti."
)
async def get_patterns(
    platform: str,
    days: int = Query(30, ge=7, le=90, description="Giorni da analizzare"),
    use_cache: bool = Query(True, description="Usa cache (1 ora)"),
    admin: User = Depends(require_admin)
) -> PatternsResponse:
    """
    Pattern identificati per piattaforma.

    Returns:
        - best_posting_hours: Ore migliori per pubblicare
        - best_posting_days: Giorni migliori
        - top_content_types: Tipi contenuto performanti
        - top_hashtags: Hashtag più efficaci
        - avg_engagement_rate: Engagement rate medio
        - high_performance_threshold: Soglia high performer
    """
    service = get_feedback_loop_service()

    try:
        patterns = await service.analyze_patterns(
            platform=platform,
            days=days,
            use_cache=use_cache
        )

        return PatternsResponse(
            success=True,
            data=patterns
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/signals/{platform}",
    response_model=SignalsResponse,
    summary="Learning Signals",
    description="Ottiene i segnali di apprendimento per la generazione contenuti."
)
async def get_learning_signals(
    platform: str,
    use_cache: bool = Query(True, description="Usa cache"),
    admin: User = Depends(require_admin)
) -> SignalsResponse:
    """
    Learning signals per Content Creator Agent.

    Returns:
        - do_more: Azioni da fare di più
        - do_less: Azioni da evitare
        - experiment_with: Esperimenti suggeriti
        - content_mix: Mix contenuti consigliato
        - optimal_frequency: Frequenza pubblicazione
        - post_at_hours: Ore consigliate
        - post_on_days: Giorni consigliati
    """
    service = get_feedback_loop_service()

    try:
        signals = await service.generate_learning_signals(
            platform=platform,
            use_cache=use_cache
        )

        return SignalsResponse(
            success=True,
            data=signals
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/optimize-prompt",
    response_model=OptimizePromptResponse,
    summary="Ottimizza Prompt",
    description="Ottimizza un prompt basandosi sui learning signals."
)
async def optimize_prompt(
    request: OptimizePromptRequest,
    admin: User = Depends(require_admin)
) -> OptimizePromptResponse:
    """
    Ottimizza prompt per generazione contenuti.

    Il prompt viene arricchito con:
    - Suggerimenti formato
    - Lunghezza caption ottimale
    - Hashtag suggeriti
    - CTA consigliati
    - Timing pubblicazione

    Body:
        - prompt: Prompt originale
        - platform: Piattaforma target
    """
    service = get_feedback_loop_service()

    try:
        optimized = await service.optimize_prompt(
            base_prompt=request.prompt,
            platform=request.platform
        )

        return OptimizePromptResponse(
            success=True,
            data=optimized
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/sync-from-instagram",
    response_model=SyncResponse,
    summary="Sync da Instagram",
    description="Sincronizza automaticamente dati performance da Instagram."
)
async def sync_from_instagram(
    limit: int = Query(50, ge=10, le=100, description="Max post da sincronizzare"),
    admin: User = Depends(require_admin)
) -> SyncResponse:
    """
    Sync automatico da Instagram.

    Recupera insights da Instagram Graph API e li ingestisce
    nel sistema di feedback loop.

    Prerequisiti:
    - INSTAGRAM_ACCOUNT_ID configurato
    - INSTAGRAM_ACCESS_TOKEN valido
    """
    service = get_feedback_loop_service()

    try:
        result = await service.sync_from_instagram(limit=limit)

        success = len(result.errors) == 0

        return SyncResponse(
            success=success,
            data=result
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/suggestions/{platform}",
    response_model=SuggestionsResponse,
    summary="Suggerimenti Contenuti",
    description="Genera suggerimenti contenuti basati sui pattern."
)
async def get_content_suggestions(
    platform: str,
    count: int = Query(5, ge=1, le=10, description="Numero suggerimenti"),
    admin: User = Depends(require_admin)
) -> SuggestionsResponse:
    """
    Suggerimenti contenuti.

    Ogni suggerimento include:
    - type: Tipo contenuto (carousel, reel, etc.)
    - topic_template: Template topic
    - best_time: Orario migliore
    - best_day: Giorno migliore
    - hashtag_count: Numero hashtag suggerito
    - suggested_hashtags: Hashtag suggeriti
    - cta: CTA consigliato
    """
    service = get_feedback_loop_service()

    try:
        suggestions = await service.get_content_suggestions(
            platform=platform,
            count=count
        )

        return SuggestionsResponse(
            success=True,
            suggestions=suggestions
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/history",
    response_model=Dict[str, Any],
    summary="Storico Analisi",
    description="Ottiene storico delle analisi effettuate."
)
async def get_analysis_history(
    platform: Optional[str] = Query(None, description="Filtra per piattaforma"),
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Storico analisi feedback loop.

    Returns:
        - total_posts: Post totali analizzati
        - platforms: Dati per piattaforma
        - last_analysis: Ultima analisi
    """
    service = get_feedback_loop_service()
    status = await service.get_status()

    history = {
        "total_posts": status.total_posts_analyzed,
        "platforms": {},
        "last_sync": status.last_sync.isoformat() if status.last_sync else None,
        "patterns_available": status.patterns_available
    }

    for p in status.platforms_configured:
        if platform and p != platform:
            continue

        try:
            patterns = await service.analyze_patterns(p, use_cache=True)
            history["platforms"][p] = {
                "posts_analyzed": patterns.analyzed_posts,
                "avg_engagement": patterns.avg_engagement_rate,
                "best_hours": patterns.best_posting_hours[:3],
                "best_days": patterns.best_posting_days[:2],
                "top_content_types": patterns.top_content_types[:2]
            }
        except Exception:
            history["platforms"][p] = {"error": "No data available"}

    return {"success": True, "data": history}


@router.delete(
    "/cache",
    summary="Pulisci Cache",
    description="Pulisce la cache di patterns e signals."
)
async def clear_cache(
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Pulisce cache per forzare ricalcolo.
    """
    service = get_feedback_loop_service()

    service._patterns_cache.clear()
    service._signals_cache.clear()
    service._cache_expiry.clear()

    return {
        "success": True,
        "message": "Cache pulita con successo"
    }
