"""
🔌 AI Feedback Loop Router

Endpoints per gestire il sistema di feedback loop AI:
- Ingestione dati performance
- Visualizzazione pattern
- Learning signals
- Ottimizzazione contenuti
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.ai_feedback_loop import (
    feedback_loop,
    Platform,
    ContentType,
    PerformanceMetrics,
    SuccessPattern,
    LearningSignals,
    ContentOptimizationSuggestion,
    OptimizedPrompt,
)

router = APIRouter(prefix="/feedback-loop", tags=["ai-feedback-loop"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class IngestPerformanceRequest(BaseModel):
    """Request per ingestione dati performance."""
    post_id: str
    platform: Platform
    metrics: dict[str, Any]
    content_features: dict[str, Any]


class OptimizePromptRequest(BaseModel):
    """Request per ottimizzazione prompt."""
    prompt: str
    platform: Platform
    content_type: ContentType = ContentType.POST_IMAGE


class OptimizeContentRequest(BaseModel):
    """Request per suggerimenti ottimizzazione contenuto."""
    caption: str
    platform: Platform
    hashtags: list[str] = Field(default_factory=list)


class FeedbackLoopStatusResponse(BaseModel):
    """Status del feedback loop."""
    platforms: dict[str, dict[str, Any]]
    total_data_points: int
    is_learning: bool


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status", response_model=FeedbackLoopStatusResponse)
async def get_feedback_loop_status():
    """
    Ottiene lo status del feedback loop.

    Mostra:
    - Dati per piattaforma
    - Totale data points
    - Se il sistema sta apprendendo
    """
    platforms_status = {}
    total_points = 0

    for platform in Platform:
        cache_key = platform.value
        data = feedback_loop._performance_cache.get(cache_key, [])
        signals = feedback_loop._learning_signals.get(platform.value)

        platforms_status[platform.value] = {
            "data_points": len(data),
            "has_signals": signals is not None,
            "confidence": signals.confidence_score if signals else 0.0,
            "last_updated": signals.last_updated.isoformat() if signals else None
        }
        total_points += len(data)

    return FeedbackLoopStatusResponse(
        platforms=platforms_status,
        total_data_points=total_points,
        is_learning=total_points >= 20
    )


@router.post("/ingest", response_model=PerformanceMetrics)
async def ingest_performance_data(request: IngestPerformanceRequest):
    """
    Ingerisce dati di performance da un post.

    Chiamato automaticamente quando si recuperano insights da Instagram/Facebook.
    """
    try:
        result = await feedback_loop.ingest_performance_data(
            post_id=request.post_id,
            platform=request.platform,
            metrics=request.metrics,
            content_features=request.content_features
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns/{platform}", response_model=list[SuccessPattern])
async def get_patterns(
    platform: Platform,
    min_data_points: int = Query(20, ge=5, le=100)
):
    """
    Ottiene i pattern di successo identificati per una piattaforma.
    """
    try:
        patterns = await feedback_loop.analyze_patterns(platform, min_data_points)
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/{platform}", response_model=LearningSignals)
async def get_learning_signals(platform: Platform):
    """
    Ottiene i learning signals per una piattaforma.

    Questi segnali rappresentano ciò che l'AI ha "imparato"
    dalla performance passata.
    """
    try:
        signals = await feedback_loop.generate_learning_signals(platform)
        return signals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-prompt", response_model=OptimizedPrompt)
async def optimize_prompt(request: OptimizePromptRequest):
    """
    Ottimizza un prompt basandosi sui learning signals.

    Aggiunge context e constraints basati su performance passate.
    """
    try:
        result = await feedback_loop.optimize_prompt(
            original_prompt=request.prompt,
            platform=request.platform,
            content_type=request.content_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-content", response_model=list[ContentOptimizationSuggestion])
async def optimize_content(request: OptimizeContentRequest):
    """
    Suggerisce ottimizzazioni per contenuto specifico.
    """
    try:
        content = {
            "caption": request.caption,
            "hashtags": request.hashtags
        }
        suggestions = await feedback_loop.suggest_optimizations(content, request.platform)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-from-instagram")
async def sync_from_instagram():
    """
    Sincronizza dati performance da Instagram Insights.

    Recupera ultimi N post e ingerisce metriche nel feedback loop.
    """
    try:
        from app.integrations.instagram_insights import instagram_insights

        if not instagram_insights.is_configured:
            return {
                "success": False,
                "error": "Instagram Insights non configurato"
            }

        # Get recent media with insights
        media_insights = await instagram_insights.get_all_media_insights(limit=50)

        ingested = 0
        for media in media_insights:
            await feedback_loop.ingest_performance_data(
                post_id=media.media_id,
                platform=Platform.INSTAGRAM,
                metrics={
                    "impressions": media.impressions,
                    "reach": media.reach,
                    "likes": media.likes,
                    "comments": media.comments,
                    "shares": media.shares,
                    "saves": media.saves,
                    "video_views": media.video_views
                },
                content_features={
                    "published_at": media.timestamp.isoformat(),
                    "content_type": media.media_type.value.lower(),
                    "caption": media.caption or ""
                }
            )
            ingested += 1

        # Generate learning signals
        signals = await feedback_loop.generate_learning_signals(Platform.INSTAGRAM)

        return {
            "success": True,
            "posts_ingested": ingested,
            "learning_confidence": signals.confidence_score,
            "patterns_found": len(await feedback_loop.analyze_patterns(Platform.INSTAGRAM))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/recommendations/{platform}")
async def get_recommendations(platform: Platform):
    """
    Ottiene raccomandazioni pratiche basate sui learning.
    """
    patterns = await feedback_loop.analyze_patterns(platform, min_data_points=10)

    recommendations = [p.recommendation for p in patterns if p.confidence >= 0.5]

    if not recommendations:
        recommendations = [
            "📊 Non ci sono ancora abbastanza dati per generare raccomandazioni.",
            "📱 Continua a pubblicare e raccogliere insights!",
            "💡 Suggerimento: Sincronizza i dati da Instagram con /sync-from-instagram"
        ]

    return {
        "platform": platform.value,
        "recommendations": recommendations,
        "data_points": len(feedback_loop._performance_cache.get(platform.value, []))
    }
