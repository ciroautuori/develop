"""
🔌 Instagram Insights API Router

Endpoints per accedere a Instagram Insights dal frontend.
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.integrations.instagram_insights import (
    instagram_insights,
    get_instagram_insights_summary,
    MetricPeriod,
    PostInsights,
    StoryInsights,
    AccountInsights,
    AudienceDemographics,
    ContentPerformanceReport,
)

router = APIRouter(prefix="/instagram", tags=["instagram-insights"])


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class InsightsConfigStatus(BaseModel):
    """Status configurazione Instagram Insights."""
    configured: bool
    has_token: bool
    has_account_id: bool
    account_id: Optional[str] = None


class InsightsSummaryResponse(BaseModel):
    """Summary rapida per dashboard."""
    configured: bool
    username: Optional[str] = None
    followers: Optional[int] = None
    follower_growth: Optional[int] = None
    reach_28d: Optional[int] = None
    impressions_28d: Optional[int] = None
    avg_engagement_rate: Optional[float] = None
    recent_posts_count: Optional[int] = None
    error: Optional[str] = None


class MediaInsightsResponse(BaseModel):
    """Response con lista media insights."""
    count: int
    media: list[PostInsights]


class PerformanceReportResponse(BaseModel):
    """Report performance completo."""
    success: bool
    report: Optional[ContentPerformanceReport] = None
    error: Optional[str] = None


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status", response_model=InsightsConfigStatus)
async def get_insights_status():
    """
    Verifica se Instagram Insights è configurato.

    Restituisce lo stato della configurazione senza esporre token.
    """
    import os

    has_token = bool(os.getenv("FACEBOOK_ACCESS_TOKEN") or os.getenv("META_ACCESS_TOKEN"))
    has_account_id = bool(os.getenv("INSTAGRAM_ACCOUNT_ID"))

    return InsightsConfigStatus(
        configured=instagram_insights.is_configured,
        has_token=has_token,
        has_account_id=has_account_id,
        account_id=os.getenv("INSTAGRAM_ACCOUNT_ID")[:8] + "..." if has_account_id else None
    )


@router.get("/summary", response_model=InsightsSummaryResponse)
async def get_summary():
    """
    Ottiene summary rapida per dashboard.

    Include:
    - Follower count e growth
    - Reach e impressions ultimi 28 giorni
    - Engagement rate medio
    """
    result = await get_instagram_insights_summary()
    return InsightsSummaryResponse(**result)


@router.get("/account", response_model=AccountInsights)
async def get_account_insights(
    period: MetricPeriod = Query(
        MetricPeriod.DAYS_28,
        description="Periodo per metriche aggregate"
    )
):
    """
    Ottiene insights dell'account Instagram.

    Metriche disponibili:
    - Followers, following, media count
    - Reach e impressions
    - Profile views, website clicks
    - Follower growth
    """
    if not instagram_insights.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Instagram Insights non configurato. Imposta FACEBOOK_ACCESS_TOKEN e INSTAGRAM_ACCOUNT_ID."
        )

    try:
        return await instagram_insights.get_account_insights(period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/media", response_model=MediaInsightsResponse)
async def get_media_insights(
    limit: int = Query(25, ge=1, le=100, description="Numero massimo di post")
):
    """
    Ottiene insights di tutti i media recenti.

    Per ogni post:
    - Impressions, reach
    - Likes, comments, saves, shares
    - Engagement rate
    - Video views (per video/reels)
    """
    if not instagram_insights.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Instagram Insights non configurato."
        )

    try:
        media = await instagram_insights.get_all_media_insights(limit)
        return MediaInsightsResponse(count=len(media), media=media)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/media/{media_id}", response_model=PostInsights)
async def get_single_media_insights(media_id: str):
    """
    Ottiene insights di un singolo media.
    """
    if not instagram_insights.is_configured:
        raise HTTPException(status_code=503, detail="Instagram Insights non configurato.")

    try:
        return await instagram_insights.get_media_insights(media_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stories", response_model=list[StoryInsights])
async def get_stories_insights():
    """
    Ottiene insights delle stories attive.

    Nota: Le stories sono disponibili solo per 24 ore.
    """
    if not instagram_insights.is_configured:
        raise HTTPException(status_code=503, detail="Instagram Insights non configurato.")

    try:
        stories = await instagram_insights.get_stories()
        insights = []
        for story in stories:
            try:
                story_insight = await instagram_insights.get_story_insights(story["id"])
                insights.append(story_insight)
            except Exception:
                pass
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demographics", response_model=AudienceDemographics)
async def get_audience_demographics():
    """
    Ottiene demographics del pubblico.

    Richiede account Business con 100+ followers.

    Include:
    - Age-gender breakdown
    - Top countries
    - Top cities
    - Gender distribution
    """
    if not instagram_insights.is_configured:
        raise HTTPException(status_code=503, detail="Instagram Insights non configurato.")

    try:
        return await instagram_insights.get_audience_demographics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report", response_model=PerformanceReportResponse)
async def generate_performance_report(
    days: int = Query(28, ge=1, le=90, description="Giorni da analizzare")
):
    """
    Genera report completo di performance.

    Analizza:
    - Metriche aggregate
    - Best performing content
    - Best times to post
    - Recommendations AI-powered
    """
    if not instagram_insights.is_configured:
        return PerformanceReportResponse(
            success=False,
            error="Instagram Insights non configurato."
        )

    try:
        report = await instagram_insights.generate_performance_report(days)
        return PerformanceReportResponse(success=True, report=report)
    except Exception as e:
        return PerformanceReportResponse(success=False, error=str(e))


# =============================================================================
# WEBHOOK ENDPOINT (per real-time updates)
# =============================================================================

class WebhookPayload(BaseModel):
    """Payload webhook Instagram."""
    object: str
    entry: list[dict] = Field(default_factory=list)


@router.post("/webhook")
async def instagram_webhook(payload: WebhookPayload):
    """
    Endpoint per Instagram Webhooks.

    Riceve notifiche real-time per:
    - Nuovi commenti
    - Nuove menzioni
    - Stories views
    - etc.
    """
    # TODO: Process webhook events
    # Store insights updates in database

    return {"status": "ok"}


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
):
    """
    Endpoint per verifica webhook Instagram.

    Facebook richiede questo per validare l'endpoint.
    """
    import os

    expected_token = os.getenv("INSTAGRAM_WEBHOOK_VERIFY_TOKEN", "markettina-webhook-token")

    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return int(hub_challenge)

    raise HTTPException(status_code=403, detail="Verification failed")
