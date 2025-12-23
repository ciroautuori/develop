"""
Instagram Insights Router - API endpoints per metriche Instagram.

Espone gli endpoint REST per:
- Stato connessione Instagram
- Metriche account (followers, reach, impressions)
- Performance post (engagement, saves, shares)
- Stories insights
- Demographics audience
- Report performance completi

AUTENTICAZIONE: Tutti gli endpoint richiedono autenticazione admin.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.api.dependencies.auth_deps import get_current_user
from app.domain.auth.models import User, UserRole
from app.integrations.instagram_insights import (
    AccountInsights,
    AudienceDemographics,
    InstagramAPIError,
    InstagramStatus,
    MediaInsights,
    PerformanceReport,
    StoryInsights,
    get_instagram_insights_service,
    InsightsPeriod,
    MediaType,
)

router = APIRouter(prefix="/instagram", tags=["instagram-insights"])


# =============================================================================
# DEPENDENCIES
# =============================================================================


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Richiede ruolo admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required for Instagram Insights"
        )
    return current_user


# =============================================================================
# RESPONSE MODELS
# =============================================================================


class StatusResponse(BaseModel):
    """Response per stato connessione."""
    success: bool
    status: InstagramStatus
    message: str


class AccountResponse(BaseModel):
    """Response per metriche account."""
    success: bool
    data: AccountInsights
    cached: bool = False


class MediaListResponse(BaseModel):
    """Response per lista media insights."""
    success: bool
    data: List[MediaInsights]
    total: int
    page: int = 1


class SingleMediaResponse(BaseModel):
    """Response per singolo media."""
    success: bool
    data: MediaInsights


class StoriesResponse(BaseModel):
    """Response per stories insights."""
    success: bool
    data: List[StoryInsights]
    total: int


class DemographicsResponse(BaseModel):
    """Response per demographics."""
    success: bool
    data: AudienceDemographics


class ReportResponse(BaseModel):
    """Response per report performance."""
    success: bool
    data: PerformanceReport
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Response per errori."""
    success: bool = False
    error: str
    code: Optional[int] = None


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Stato Connessione Instagram",
    description="Verifica lo stato della connessione API Instagram e validità token."
)
async def get_instagram_status(
    admin: User = Depends(require_admin)
) -> StatusResponse:
    """
    Verifica connessione Instagram API.

    Returns:
        - connected: Se l'API è connessa
        - username: Username account
        - token_valid: Se il token è valido
        - token_expires_at: Scadenza token
        - permissions: Permessi disponibili
    """
    service = get_instagram_insights_service()

    try:
        status = await service.verify_connection()

        if status.connected:
            message = f"Connesso come @{status.username}"
        else:
            message = status.error or "Connessione non disponibile"

        return StatusResponse(
            success=status.connected,
            status=status,
            message=message
        )

    except Exception as e:
        return StatusResponse(
            success=False,
            status=InstagramStatus(error=str(e)),
            message=f"Errore verifica connessione: {str(e)}"
        )


@router.get(
    "/summary",
    response_model=Dict[str, Any],
    summary="Summary Rapido",
    description="Ottiene summary rapido per dashboard con metriche base."
)
async def get_instagram_summary(
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Summary rapido per dashboard.

    Returns:
        Dict con connected, username, followers, following, posts
    """
    service = get_instagram_insights_service()

    try:
        return await service.get_status_summary()
    except InstagramAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/account",
    response_model=AccountResponse,
    summary="Metriche Account",
    description="Ottiene metriche complete dell'account Instagram (followers, reach, impressions, etc.)."
)
async def get_account_insights(
    period: InsightsPeriod = Query(
        InsightsPeriod.DAYS_28,
        description="Periodo per metriche: day, week, days_28"
    ),
    use_cache: bool = Query(True, description="Usa cache (5 minuti)"),
    admin: User = Depends(require_admin)
) -> AccountResponse:
    """
    Metriche account Instagram.

    Metrics incluse:
    - followers_count, follows_count, media_count
    - reach, impressions (28 days)
    - profile_views, website_clicks
    - email_contacts, phone_call_clicks
    """
    service = get_instagram_insights_service()

    try:
        data = await service.get_account_insights(
            period=period,
            use_cache=use_cache
        )

        return AccountResponse(
            success=True,
            data=data,
            cached=use_cache
        )

    except InstagramAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/media",
    response_model=MediaListResponse,
    summary="Performance Post",
    description="Ottiene insights per tutti i post recenti con metriche di engagement."
)
async def get_media_insights(
    limit: int = Query(50, ge=1, le=100, description="Numero massimo post"),
    media_type: Optional[MediaType] = Query(None, description="Filtra per tipo media"),
    admin: User = Depends(require_admin)
) -> MediaListResponse:
    """
    Insights per tutti i media recenti.

    Ordinati per engagement rate decrescente.

    Metrics per media:
    - likes, comments, saves, shares
    - reach, impressions
    - engagement_rate (calculated)
    - video_views, plays (per video/reels)
    """
    service = get_instagram_insights_service()

    try:
        data = await service.get_all_media_insights(limit=limit)

        # Filter by type if specified
        if media_type:
            data = [m for m in data if m.media_type == media_type.value]

        return MediaListResponse(
            success=True,
            data=data,
            total=len(data)
        )

    except InstagramAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/media/{media_id}",
    response_model=SingleMediaResponse,
    summary="Dettaglio Singolo Post",
    description="Ottiene insights dettagliati per un singolo post."
)
async def get_single_media_insights(
    media_id: str,
    admin: User = Depends(require_admin)
) -> SingleMediaResponse:
    """
    Insights per singolo media.

    Args:
        media_id: ID del media Instagram (es. "17895695668004550")
    """
    service = get_instagram_insights_service()

    try:
        data = await service.get_media_insights(media_id)

        return SingleMediaResponse(
            success=True,
            data=data
        )

    except InstagramAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/stories",
    response_model=StoriesResponse,
    summary="Performance Stories",
    description="Ottiene insights per le stories attive."
)
async def get_stories_insights(
    admin: User = Depends(require_admin)
) -> StoriesResponse:
    """
    Insights per stories attive (24h).

    Metrics per story:
    - reach, impressions
    - replies, exits
    - taps_forward, taps_back
    """
    service = get_instagram_insights_service()

    try:
        data = await service.get_stories_insights()

        return StoriesResponse(
            success=True,
            data=data,
            total=len(data)
        )

    except InstagramAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/demographics",
    response_model=DemographicsResponse,
    summary="Demographics Audience",
    description="Ottiene dati demografici dell'audience (richiede min 100 followers)."
)
async def get_demographics(
    admin: User = Depends(require_admin)
) -> DemographicsResponse:
    """
    Dati demografici audience.

    Include:
    - age_gender: Breakdown età/genere (es. {"M.18-24": 150})
    - top_cities: Top 10 città followers
    - top_countries: Top 10 paesi followers
    - online_followers: Quando i followers sono online
    """
    service = get_instagram_insights_service()

    try:
        data = await service.get_audience_demographics()

        return DemographicsResponse(
            success=True,
            data=data
        )

    except InstagramAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/report",
    response_model=ReportResponse,
    summary="Report Performance",
    description="Genera report performance completo per il periodo specificato."
)
async def get_performance_report(
    days: int = Query(30, ge=1, le=90, description="Giorni da analizzare"),
    admin: User = Depends(require_admin)
) -> ReportResponse:
    """
    Report performance completo.

    Include:
    - Account insights (followers, reach, etc.)
    - Totali: posts, reach, impressions, engagement
    - Average engagement rate
    - Top 5 performing posts
    - Content type breakdown (IMAGE, REELS, etc.)
    - Best posting hours and days
    """
    service = get_instagram_insights_service()

    try:
        data = await service.generate_performance_report(days=days)

        return ReportResponse(
            success=True,
            data=data
        )

    except InstagramAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/top-posts",
    response_model=MediaListResponse,
    summary="Top Performing Posts",
    description="Ottiene i post con maggior engagement rate."
)
async def get_top_posts(
    limit: int = Query(10, ge=1, le=50, description="Numero post"),
    days: int = Query(30, ge=1, le=90, description="Giorni da analizzare"),
    admin: User = Depends(require_admin)
) -> MediaListResponse:
    """
    Top performing posts per engagement rate.
    """
    service = get_instagram_insights_service()

    try:
        all_media = await service.get_all_media_insights(limit=100)

        # Filter by period
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        filtered = [
            m for m in all_media
            if m.timestamp and m.timestamp >= cutoff
        ]

        # Already sorted by engagement_rate
        top_posts = filtered[:limit]

        return MediaListResponse(
            success=True,
            data=top_posts,
            total=len(top_posts)
        )

    except InstagramAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/best-times",
    response_model=Dict[str, Any],
    summary="Migliori Orari Pubblicazione",
    description="Analizza i migliori orari e giorni per pubblicare."
)
async def get_best_posting_times(
    days: int = Query(30, ge=7, le=90, description="Giorni da analizzare"),
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Analisi migliori orari/giorni per pubblicare.

    Returns:
        - best_hours: Top 5 ore con maggior engagement
        - best_days: Top 3 giorni con maggior engagement
        - hourly_breakdown: Engagement medio per ora
        - daily_breakdown: Engagement medio per giorno
    """
    service = get_instagram_insights_service()

    try:
        report = await service.generate_performance_report(days=days)

        return {
            "success": True,
            "best_hours": report.best_posting_hours,
            "best_days": report.best_posting_days,
            "analyzed_posts": report.total_posts,
            "avg_engagement_rate": report.avg_engagement_rate,
            "recommendation": _generate_posting_recommendation(report)
        }

    except InstagramAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _generate_posting_recommendation(report: PerformanceReport) -> str:
    """Genera raccomandazione testuale per posting."""
    if not report.best_posting_hours or not report.best_posting_days:
        return "Non abbastanza dati per generare raccomandazioni. Pubblica più contenuti!"

    hours = report.best_posting_hours[:2]
    days = report.best_posting_days[:2]

    hours_str = " e ".join([f"{h}:00" for h in hours])
    days_str = " e ".join(days)

    return (
        f"📈 I tuoi migliori orari sono {hours_str}. "
        f"I giorni con più engagement sono {days_str}. "
        f"Il tuo engagement rate medio è {report.avg_engagement_rate}%."
    )
