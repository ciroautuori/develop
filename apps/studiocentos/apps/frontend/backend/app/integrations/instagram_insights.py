"""
Instagram Insights Service - Graph API Integration.

Servizio completo per recupero metriche Instagram Business Account.
Utilizza Meta Graph API v18.0 per insights, demographics e performance.

PREREQUISITI:
- Instagram Business Account collegato a Facebook Page
- Meta App con permessi: instagram_basic, instagram_manage_insights, pages_show_list
- Long-lived access token (60 days) - refresh via /oauth/access_token

REFERENCE:
- https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights
- https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
import structlog
from pydantic import BaseModel, Field

from app.core.config import settings

logger = structlog.get_logger(__name__)


# =============================================================================
# ENUMS
# =============================================================================


class InsightsPeriod(str, Enum):
    """Periodi validi per Instagram Insights API."""
    DAY = "day"
    WEEK = "week"
    DAYS_28 = "days_28"
    LIFETIME = "lifetime"


class MediaType(str, Enum):
    """Tipi di media Instagram."""
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    CAROUSEL_ALBUM = "CAROUSEL_ALBUM"
    REELS = "REELS"
    STORY = "STORY"


# =============================================================================
# PYDANTIC MODELS - Response Schemas
# =============================================================================


class AccountInsights(BaseModel):
    """Metriche account Instagram."""
    account_id: str
    username: str
    followers_count: int = 0
    follows_count: int = 0
    media_count: int = 0
    reach: int = 0  # 28 days
    impressions: int = 0  # 28 days
    profile_views: int = 0  # 28 days
    website_clicks: int = 0  # 28 days
    email_contacts: int = 0  # 28 days
    phone_call_clicks: int = 0  # 28 days
    text_message_clicks: int = 0  # 28 days
    get_directions_clicks: int = 0  # 28 days
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class MediaInsights(BaseModel):
    """Metriche singolo post/media."""
    media_id: str
    media_type: str
    permalink: Optional[str] = None
    caption: Optional[str] = None
    timestamp: Optional[datetime] = None
    thumbnail_url: Optional[str] = None
    media_url: Optional[str] = None

    # Engagement metrics
    likes: int = 0
    comments: int = 0
    saves: int = 0
    shares: int = 0

    # Reach metrics
    reach: int = 0
    impressions: int = 0

    # Video-specific
    video_views: int = 0
    plays: int = 0

    # Calculated
    engagement_rate: float = 0.0

    def calculate_engagement_rate(self, followers: int) -> None:
        """Calcola engagement rate."""
        if followers > 0:
            total_engagement = self.likes + self.comments + self.saves + self.shares
            self.engagement_rate = round((total_engagement / followers) * 100, 2)


class StoryInsights(BaseModel):
    """Metriche story Instagram."""
    story_id: str
    media_type: str = "STORY"
    timestamp: Optional[datetime] = None

    # Story metrics
    reach: int = 0
    impressions: int = 0
    replies: int = 0
    exits: int = 0
    taps_forward: int = 0
    taps_back: int = 0


class AudienceDemographics(BaseModel):
    """Dati demografici audience."""
    account_id: str

    # Age/Gender breakdown
    age_gender: Dict[str, int] = Field(default_factory=dict)
    # e.g. {"M.18-24": 150, "F.25-34": 200, ...}

    # Top cities
    top_cities: Dict[str, int] = Field(default_factory=dict)
    # e.g. {"Rome, Lazio": 500, "Milan, Lombardia": 300}

    # Top countries
    top_countries: Dict[str, int] = Field(default_factory=dict)
    # e.g. {"IT": 800, "US": 100}

    # Follower online times
    online_followers: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    # e.g. {"0": {"0": 100, "1": 50, ...}, "1": {...}}  # day -> hour -> count

    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class PerformanceReport(BaseModel):
    """Report performance completo."""
    account_id: str
    period_start: datetime
    period_end: datetime

    # Account metrics
    account_insights: AccountInsights

    # Content performance
    total_posts: int = 0
    total_reach: int = 0
    total_impressions: int = 0
    total_engagement: int = 0
    avg_engagement_rate: float = 0.0

    # Top performing posts
    top_posts: List[MediaInsights] = Field(default_factory=list)

    # Content type breakdown
    content_type_performance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    # e.g. {"IMAGE": {"count": 10, "avg_reach": 500}, "REELS": {...}}

    # Best times to post
    best_posting_hours: List[int] = Field(default_factory=list)
    best_posting_days: List[str] = Field(default_factory=list)

    generated_at: datetime = Field(default_factory=datetime.utcnow)


class InstagramStatus(BaseModel):
    """Stato connessione Instagram API."""
    connected: bool = False
    account_id: Optional[str] = None
    username: Optional[str] = None
    account_type: Optional[str] = None
    token_valid: bool = False
    token_expires_at: Optional[datetime] = None
    permissions: List[str] = Field(default_factory=list)
    error: Optional[str] = None


# =============================================================================
# INSTAGRAM INSIGHTS SERVICE
# =============================================================================


class InstagramInsightsService:
    """
    Servizio per recupero metriche Instagram via Graph API.

    Gestisce:
    - Account insights (followers, reach, impressions)
    - Media insights (engagement, saves, shares)
    - Story insights
    - Audience demographics
    - Performance reports

    RATE LIMITS:
    - 200 calls/hour per user token
    - 4800 calls/day per app

    Usage:
        service = InstagramInsightsService()
        if await service.verify_connection():
            insights = await service.get_account_insights()
    """

    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(self):
        self.account_id = settings.INSTAGRAM_ACCOUNT_ID
        self.access_token = settings.INSTAGRAM_ACCESS_TOKEN
        self._client: Optional[httpx.AsyncClient] = None
        self._account_cache: Optional[AccountInsights] = None
        self._cache_expiry: Optional[datetime] = None

    @property
    def is_configured(self) -> bool:
        """Verifica se le credenziali sono configurate."""
        return bool(self.account_id and self.access_token)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                follow_redirects=True
            )
        return self._client

    async def close(self) -> None:
        """Chiudi HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """
        Esegue richiesta a Graph API con error handling.

        Args:
            endpoint: Endpoint relativo (es. "/{account_id}/insights")
            params: Query parameters
            method: HTTP method

        Returns:
            Response JSON data

        Raises:
            InstagramAPIError: Se la richiesta fallisce
        """
        if not self.is_configured:
            raise InstagramAPIError("Instagram API non configurata. Imposta INSTAGRAM_ACCOUNT_ID e INSTAGRAM_ACCESS_TOKEN.")

        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        params["access_token"] = self.access_token

        client = await self._get_client()

        try:
            if method == "GET":
                response = await client.get(url, params=params)
            else:
                response = await client.post(url, data=params)

            data = response.json()

            if response.status_code != 200:
                error = data.get("error", {})
                error_msg = error.get("message", "Unknown error")
                error_code = error.get("code", 0)

                logger.error(
                    "instagram_api_error",
                    endpoint=endpoint,
                    status=response.status_code,
                    error_code=error_code,
                    error_msg=error_msg
                )

                raise InstagramAPIError(
                    f"Instagram API Error [{error_code}]: {error_msg}",
                    code=error_code
                )

            return data

        except httpx.TimeoutException:
            logger.error("instagram_api_timeout", endpoint=endpoint)
            raise InstagramAPIError("Instagram API timeout")
        except httpx.RequestError as e:
            logger.error("instagram_api_request_error", endpoint=endpoint, error=str(e))
            raise InstagramAPIError(f"Request error: {str(e)}")

    # =========================================================================
    # CONNECTION & STATUS
    # =========================================================================

    async def verify_connection(self) -> InstagramStatus:
        """
        Verifica connessione e validità token.

        Returns:
            InstagramStatus con dettagli connessione
        """
        status = InstagramStatus()

        if not self.is_configured:
            status.error = "Credenziali non configurate"
            return status

        try:
            # Get account info
            data = await self._make_request(
                f"/{self.account_id}",
                params={
                    "fields": "id,username,account_type,followers_count,follows_count,media_count"
                }
            )

            status.connected = True
            status.account_id = data.get("id")
            status.username = data.get("username")
            status.account_type = data.get("account_type")
            status.token_valid = True

            # Get token debug info
            try:
                debug_data = await self._make_request(
                    "/debug_token",
                    params={"input_token": self.access_token}
                )
                token_info = debug_data.get("data", {})
                expires_at = token_info.get("data_access_expires_at")
                if expires_at:
                    status.token_expires_at = datetime.fromtimestamp(expires_at)
                status.permissions = token_info.get("scopes", [])
            except Exception:
                pass  # Token debug is optional

            logger.info(
                "instagram_connection_verified",
                username=status.username,
                account_type=status.account_type
            )

        except InstagramAPIError as e:
            status.error = str(e)
            logger.warning("instagram_connection_failed", error=str(e))

        return status

    async def get_status_summary(self) -> Dict[str, Any]:
        """
        Ottiene summary rapido per dashboard.

        Returns:
            Dict con stato e metriche base
        """
        status = await self.verify_connection()

        summary = {
            "connected": status.connected,
            "username": status.username,
            "account_type": status.account_type,
            "token_valid": status.token_valid,
            "error": status.error
        }

        if status.connected:
            try:
                # Get basic metrics
                data = await self._make_request(
                    f"/{self.account_id}",
                    params={
                        "fields": "followers_count,follows_count,media_count"
                    }
                )
                summary.update({
                    "followers": data.get("followers_count", 0),
                    "following": data.get("follows_count", 0),
                    "posts": data.get("media_count", 0)
                })
            except Exception:
                pass

        return summary

    # =========================================================================
    # ACCOUNT INSIGHTS
    # =========================================================================

    async def get_account_insights(
        self,
        period: InsightsPeriod = InsightsPeriod.DAYS_28,
        use_cache: bool = True
    ) -> AccountInsights:
        """
        Ottiene metriche account Instagram.

        Args:
            period: Periodo per metriche (day, week, days_28)
            use_cache: Se usare cache (5 minuti)

        Returns:
            AccountInsights con tutte le metriche
        """
        # Check cache
        if use_cache and self._account_cache and self._cache_expiry:
            if datetime.utcnow() < self._cache_expiry:
                return self._account_cache

        # Get basic account info
        account_data = await self._make_request(
            f"/{self.account_id}",
            params={
                "fields": "id,username,followers_count,follows_count,media_count"
            }
        )

        insights = AccountInsights(
            account_id=account_data.get("id", self.account_id),
            username=account_data.get("username", ""),
            followers_count=account_data.get("followers_count", 0),
            follows_count=account_data.get("follows_count", 0),
            media_count=account_data.get("media_count", 0)
        )

        # Get insights metrics
        metrics = [
            "reach",
            "impressions",
            "profile_views",
            "website_clicks",
            "email_contacts",
            "phone_call_clicks",
            "text_message_clicks",
            "get_directions_clicks"
        ]

        try:
            insights_data = await self._make_request(
                f"/{self.account_id}/insights",
                params={
                    "metric": ",".join(metrics),
                    "period": period.value,
                    "metric_type": "total_value"
                }
            )

            for metric in insights_data.get("data", []):
                name = metric.get("name")
                values = metric.get("total_value", {})
                value = values.get("value", 0) if isinstance(values, dict) else 0

                if hasattr(insights, name):
                    setattr(insights, name, value)

        except InstagramAPIError as e:
            # Some metrics may not be available for all account types
            logger.warning("instagram_insights_partial", error=str(e))

        # Update cache
        self._account_cache = insights
        self._cache_expiry = datetime.utcnow() + timedelta(minutes=5)

        logger.info(
            "instagram_account_insights_fetched",
            followers=insights.followers_count,
            reach=insights.reach
        )

        return insights

    # =========================================================================
    # MEDIA INSIGHTS
    # =========================================================================

    async def get_media_list(
        self,
        limit: int = 50,
        media_type: Optional[MediaType] = None
    ) -> List[Dict[str, Any]]:
        """
        Ottiene lista media recenti.

        Args:
            limit: Numero massimo di media (max 100)
            media_type: Filtra per tipo media

        Returns:
            Lista di media con info base
        """
        limit = min(limit, 100)

        data = await self._make_request(
            f"/{self.account_id}/media",
            params={
                "fields": "id,media_type,permalink,caption,timestamp,thumbnail_url,media_url,like_count,comments_count",
                "limit": limit
            }
        )

        media_list = data.get("data", [])

        if media_type:
            media_list = [m for m in media_list if m.get("media_type") == media_type.value]

        return media_list

    async def get_media_insights(self, media_id: str) -> MediaInsights:
        """
        Ottiene insights per singolo media.

        Args:
            media_id: ID del media Instagram

        Returns:
            MediaInsights con tutte le metriche
        """
        # Get media info
        media_data = await self._make_request(
            f"/{media_id}",
            params={
                "fields": "id,media_type,permalink,caption,timestamp,thumbnail_url,media_url,like_count,comments_count"
            }
        )

        media_type = media_data.get("media_type", "IMAGE")

        insights = MediaInsights(
            media_id=media_id,
            media_type=media_type,
            permalink=media_data.get("permalink"),
            caption=media_data.get("caption"),
            thumbnail_url=media_data.get("thumbnail_url"),
            media_url=media_data.get("media_url"),
            likes=media_data.get("like_count", 0),
            comments=media_data.get("comments_count", 0)
        )

        # Parse timestamp
        ts = media_data.get("timestamp")
        if ts:
            try:
                insights.timestamp = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                pass

        # Get detailed insights based on media type
        if media_type in ["IMAGE", "CAROUSEL_ALBUM"]:
            metrics = ["reach", "impressions", "saved", "shares"]
        elif media_type == "VIDEO":
            metrics = ["reach", "impressions", "saved", "shares", "video_views"]
        elif media_type == "REELS":
            metrics = ["reach", "impressions", "saved", "shares", "plays", "comments", "likes"]
        else:
            metrics = ["reach", "impressions"]

        try:
            insights_data = await self._make_request(
                f"/{media_id}/insights",
                params={"metric": ",".join(metrics)}
            )

            for metric in insights_data.get("data", []):
                name = metric.get("name")
                values = metric.get("values", [{}])
                value = values[0].get("value", 0) if values else 0

                if name == "saved":
                    insights.saves = value
                elif name == "shares":
                    insights.shares = value
                elif name == "reach":
                    insights.reach = value
                elif name == "impressions":
                    insights.impressions = value
                elif name == "video_views":
                    insights.video_views = value
                elif name == "plays":
                    insights.plays = value

        except InstagramAPIError as e:
            logger.warning("instagram_media_insights_error", media_id=media_id, error=str(e))

        # Calculate engagement rate
        account = await self.get_account_insights(use_cache=True)
        insights.calculate_engagement_rate(account.followers_count)

        return insights

    async def get_all_media_insights(
        self,
        limit: int = 50
    ) -> List[MediaInsights]:
        """
        Ottiene insights per tutti i media recenti.

        Args:
            limit: Numero massimo di media

        Returns:
            Lista di MediaInsights
        """
        media_list = await self.get_media_list(limit=limit)
        insights_list = []

        for media in media_list:
            try:
                insights = await self.get_media_insights(media["id"])
                insights_list.append(insights)
            except Exception as e:
                logger.warning(
                    "instagram_media_insights_skip",
                    media_id=media.get("id"),
                    error=str(e)
                )

        # Sort by engagement rate
        insights_list.sort(key=lambda x: x.engagement_rate, reverse=True)

        logger.info(
            "instagram_all_media_insights_fetched",
            count=len(insights_list)
        )

        return insights_list

    # =========================================================================
    # STORY INSIGHTS
    # =========================================================================

    async def get_story_insights(self, story_id: str) -> StoryInsights:
        """
        Ottiene insights per singola story.

        Args:
            story_id: ID della story

        Returns:
            StoryInsights
        """
        insights = StoryInsights(story_id=story_id)

        try:
            data = await self._make_request(
                f"/{story_id}/insights",
                params={
                    "metric": "reach,impressions,replies,exits,taps_forward,taps_back"
                }
            )

            for metric in data.get("data", []):
                name = metric.get("name")
                values = metric.get("values", [{}])
                value = values[0].get("value", 0) if values else 0

                if hasattr(insights, name):
                    setattr(insights, name, value)

        except InstagramAPIError as e:
            logger.warning("instagram_story_insights_error", story_id=story_id, error=str(e))

        return insights

    async def get_stories_insights(self) -> List[StoryInsights]:
        """
        Ottiene insights per tutte le stories attive.

        Returns:
            Lista di StoryInsights
        """
        try:
            data = await self._make_request(
                f"/{self.account_id}/stories",
                params={"fields": "id,media_type,timestamp"}
            )

            stories = data.get("data", [])
            insights_list = []

            for story in stories:
                insights = await self.get_story_insights(story["id"])
                insights.timestamp = story.get("timestamp")
                insights_list.append(insights)

            return insights_list

        except InstagramAPIError as e:
            logger.warning("instagram_stories_fetch_error", error=str(e))
            return []

    # =========================================================================
    # AUDIENCE DEMOGRAPHICS
    # =========================================================================

    async def get_audience_demographics(self) -> AudienceDemographics:
        """
        Ottiene dati demografici audience.

        NOTA: Richiede almeno 100 followers per funzionare.

        Returns:
            AudienceDemographics
        """
        demographics = AudienceDemographics(account_id=self.account_id)

        # Age/Gender breakdown
        try:
            data = await self._make_request(
                f"/{self.account_id}/insights",
                params={
                    "metric": "follower_demographics",
                    "period": "lifetime",
                    "metric_type": "total_value",
                    "breakdown": "age,gender"
                }
            )

            for metric in data.get("data", []):
                if metric.get("name") == "follower_demographics":
                    breakdown = metric.get("total_value", {}).get("breakdowns", [{}])
                    if breakdown:
                        results = breakdown[0].get("results", [])
                        for result in results:
                            dims = result.get("dimension_values", [])
                            if len(dims) >= 2:
                                key = f"{dims[1]}.{dims[0]}"  # "M.18-24"
                                demographics.age_gender[key] = result.get("value", 0)

        except InstagramAPIError:
            pass  # Demographics may not be available

        # Top cities
        try:
            data = await self._make_request(
                f"/{self.account_id}/insights",
                params={
                    "metric": "follower_demographics",
                    "period": "lifetime",
                    "metric_type": "total_value",
                    "breakdown": "city"
                }
            )

            for metric in data.get("data", []):
                if metric.get("name") == "follower_demographics":
                    breakdown = metric.get("total_value", {}).get("breakdowns", [{}])
                    if breakdown:
                        results = breakdown[0].get("results", [])
                        for result in results[:10]:  # Top 10
                            dims = result.get("dimension_values", [])
                            if dims:
                                demographics.top_cities[dims[0]] = result.get("value", 0)

        except InstagramAPIError:
            pass

        # Top countries
        try:
            data = await self._make_request(
                f"/{self.account_id}/insights",
                params={
                    "metric": "follower_demographics",
                    "period": "lifetime",
                    "metric_type": "total_value",
                    "breakdown": "country"
                }
            )

            for metric in data.get("data", []):
                if metric.get("name") == "follower_demographics":
                    breakdown = metric.get("total_value", {}).get("breakdowns", [{}])
                    if breakdown:
                        results = breakdown[0].get("results", [])
                        for result in results[:10]:  # Top 10
                            dims = result.get("dimension_values", [])
                            if dims:
                                demographics.top_countries[dims[0]] = result.get("value", 0)

        except InstagramAPIError:
            pass

        # Online followers (when followers are online)
        try:
            data = await self._make_request(
                f"/{self.account_id}/insights",
                params={
                    "metric": "online_followers",
                    "period": "lifetime"
                }
            )

            for metric in data.get("data", []):
                if metric.get("name") == "online_followers":
                    values = metric.get("values", [{}])
                    if values:
                        demographics.online_followers = values[0].get("value", {})

        except InstagramAPIError:
            pass

        logger.info(
            "instagram_demographics_fetched",
            cities=len(demographics.top_cities),
            countries=len(demographics.top_countries)
        )

        return demographics

    # =========================================================================
    # PERFORMANCE REPORTS
    # =========================================================================

    async def generate_performance_report(
        self,
        days: int = 30
    ) -> PerformanceReport:
        """
        Genera report performance completo.

        Args:
            days: Numero di giorni da analizzare

        Returns:
            PerformanceReport completo
        """
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=days)

        # Get account insights
        account_insights = await self.get_account_insights()

        # Get all media insights
        all_media = await self.get_all_media_insights(limit=100)

        # Filter by period
        period_media = [
            m for m in all_media
            if m.timestamp and m.timestamp >= period_start
        ]

        report = PerformanceReport(
            account_id=self.account_id,
            period_start=period_start,
            period_end=period_end,
            account_insights=account_insights,
            total_posts=len(period_media)
        )

        if period_media:
            # Calculate totals
            report.total_reach = sum(m.reach for m in period_media)
            report.total_impressions = sum(m.impressions for m in period_media)
            report.total_engagement = sum(
                m.likes + m.comments + m.saves + m.shares for m in period_media
            )

            # Average engagement rate
            report.avg_engagement_rate = round(
                sum(m.engagement_rate for m in period_media) / len(period_media), 2
            )

            # Top 5 posts
            report.top_posts = period_media[:5]

            # Content type breakdown
            type_stats: Dict[str, Dict[str, Any]] = {}
            for media in period_media:
                mtype = media.media_type
                if mtype not in type_stats:
                    type_stats[mtype] = {
                        "count": 0,
                        "total_reach": 0,
                        "total_engagement": 0
                    }
                type_stats[mtype]["count"] += 1
                type_stats[mtype]["total_reach"] += media.reach
                type_stats[mtype]["total_engagement"] += (
                    media.likes + media.comments + media.saves + media.shares
                )

            for mtype, stats in type_stats.items():
                if stats["count"] > 0:
                    stats["avg_reach"] = stats["total_reach"] // stats["count"]
                    stats["avg_engagement"] = stats["total_engagement"] // stats["count"]

            report.content_type_performance = type_stats

            # Best posting times
            hour_performance: Dict[int, List[float]] = {}
            day_performance: Dict[int, List[float]] = {}

            for media in period_media:
                if media.timestamp:
                    hour = media.timestamp.hour
                    day = media.timestamp.weekday()

                    if hour not in hour_performance:
                        hour_performance[hour] = []
                    hour_performance[hour].append(media.engagement_rate)

                    if day not in day_performance:
                        day_performance[day] = []
                    day_performance[day].append(media.engagement_rate)

            # Top 3 hours
            if hour_performance:
                sorted_hours = sorted(
                    hour_performance.items(),
                    key=lambda x: sum(x[1]) / len(x[1]),
                    reverse=True
                )
                report.best_posting_hours = [h for h, _ in sorted_hours[:3]]

            # Top 3 days
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if day_performance:
                sorted_days = sorted(
                    day_performance.items(),
                    key=lambda x: sum(x[1]) / len(x[1]),
                    reverse=True
                )
                report.best_posting_days = [day_names[d] for d, _ in sorted_days[:3]]

        logger.info(
            "instagram_performance_report_generated",
            posts=report.total_posts,
            avg_engagement=report.avg_engagement_rate
        )

        return report


# =============================================================================
# EXCEPTIONS
# =============================================================================


class InstagramAPIError(Exception):
    """Errore API Instagram."""

    def __init__(self, message: str, code: int = 0):
        super().__init__(message)
        self.code = code


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_instagram_service: Optional[InstagramInsightsService] = None


def get_instagram_insights_service() -> InstagramInsightsService:
    """Get singleton instance of InstagramInsightsService."""
    global _instagram_service
    if _instagram_service is None:
        _instagram_service = InstagramInsightsService()
    return _instagram_service
