"""
📊 Instagram Insights API Integration

Recupera metriche REALI da Instagram Business/Creator accounts:
- Post performance (reach, impressions, engagement)
- Account insights (followers, profile views)
- Stories performance
- Reels performance
- Audience demographics

Requires:
- Instagram Business/Creator Account connected to Facebook Page
- Facebook Access Token with instagram_basic, instagram_manage_insights permissions

API Docs: https://developers.facebook.com/docs/instagram-api/guides/insights
"""

import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import httpx
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


# =============================================================================
# MODELS
# =============================================================================

class MetricPeriod(str, Enum):
    """Periodo per metriche aggregate."""
    DAY = "day"
    WEEK = "week"
    DAYS_28 = "days_28"
    LIFETIME = "lifetime"


class MediaType(str, Enum):
    """Tipo di media Instagram."""
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    CAROUSEL_ALBUM = "CAROUSEL_ALBUM"
    REELS = "REELS"
    STORIES = "STORIES"


class PostInsights(BaseModel):
    """Insights di un singolo post."""
    media_id: str
    media_type: MediaType
    timestamp: datetime
    caption: Optional[str] = None
    permalink: Optional[str] = None

    # Metriche base
    impressions: int = 0
    reach: int = 0
    likes: int = 0
    comments: int = 0
    saves: int = 0
    shares: int = 0

    # Metriche engagement
    engagement_rate: float = 0.0

    # Video/Reels specific
    video_views: int = 0
    plays: int = 0

    # Calculated
    total_interactions: int = 0


class StoryInsights(BaseModel):
    """Insights di una story."""
    media_id: str
    timestamp: datetime

    impressions: int = 0
    reach: int = 0
    exits: int = 0
    replies: int = 0
    taps_forward: int = 0
    taps_back: int = 0

    # Calculated
    completion_rate: float = 0.0  # (impressions - exits) / impressions


class AccountInsights(BaseModel):
    """Insights account Instagram."""
    account_id: str
    username: str

    # Follower metrics
    followers_count: int = 0
    follows_count: int = 0

    # Growth (period-based)
    follower_growth: int = 0
    follower_growth_rate: float = 0.0

    # Engagement metrics
    profile_views: int = 0
    website_clicks: int = 0
    email_clicks: int = 0
    phone_clicks: int = 0
    get_directions_clicks: int = 0

    # Reach metrics
    reach: int = 0
    impressions: int = 0

    # Content metrics
    media_count: int = 0

    # Period
    period: MetricPeriod = MetricPeriod.DAYS_28


class AudienceDemographics(BaseModel):
    """Demographics del pubblico."""
    # Age-Gender breakdown
    age_gender: dict[str, int] = Field(default_factory=dict)

    # Top countries
    top_countries: dict[str, int] = Field(default_factory=dict)

    # Top cities
    top_cities: dict[str, int] = Field(default_factory=dict)

    # Gender breakdown
    gender_male: float = 0.0
    gender_female: float = 0.0
    gender_other: float = 0.0

    # Locale
    locales: dict[str, int] = Field(default_factory=dict)


class ContentPerformanceReport(BaseModel):
    """Report performance contenuti."""
    period_start: datetime
    period_end: datetime

    # Aggregate metrics
    total_posts: int = 0
    total_stories: int = 0
    total_reels: int = 0

    total_reach: int = 0
    total_impressions: int = 0
    total_engagement: int = 0

    avg_engagement_rate: float = 0.0

    # Best performing
    best_post: Optional[PostInsights] = None
    best_time_to_post: Optional[str] = None
    best_day_to_post: Optional[str] = None

    # Insights
    recommendations: list[str] = Field(default_factory=list)


# =============================================================================
# INSTAGRAM INSIGHTS SERVICE
# =============================================================================

class InstagramInsightsService:
    """
    Servizio per recuperare Instagram Insights via Facebook Graph API.

    Usa l'Instagram Graph API che richiede:
    1. Facebook Page collegata all'account Instagram Business
    2. Access Token con permessi appropriati
    """

    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(self):
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN") or os.getenv("META_ACCESS_TOKEN")
        self.instagram_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def is_configured(self) -> bool:
        """Verifica se il servizio è configurato."""
        return bool(self.access_token and self.instagram_account_id)

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[dict] = None
    ) -> dict[str, Any]:
        """Make authenticated request to Graph API."""
        if not self.is_configured:
            raise ValueError("Instagram Insights not configured. Set FACEBOOK_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID.")

        client = await self.get_client()

        request_params = params or {}
        request_params["access_token"] = self.access_token

        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = await client.get(url, params=request_params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "instagram_api_error",
                status=e.response.status_code,
                error=e.response.text[:200]
            )
            raise
        except Exception as e:
            logger.error("instagram_api_error", error=str(e))
            raise

    # =========================================================================
    # ACCOUNT INSIGHTS
    # =========================================================================

    async def get_account_info(self) -> dict[str, Any]:
        """Get basic account information."""
        fields = "id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url,website"

        data = await self._make_request(
            self.instagram_account_id,
            {"fields": fields}
        )

        logger.info("instagram_account_info_fetched", username=data.get("username"))
        return data

    async def get_account_insights(
        self,
        period: MetricPeriod = MetricPeriod.DAYS_28
    ) -> AccountInsights:
        """
        Get account-level insights.

        Metriche disponibili:
        - impressions, reach (day, week, days_28)
        - follower_count (day)
        - profile_views, website_clicks, etc.
        """
        # Get basic info first
        account_info = await self.get_account_info()

        # Define metrics based on period
        if period == MetricPeriod.DAY:
            metrics = "impressions,reach,profile_views,website_clicks,follower_count"
        else:
            metrics = "impressions,reach,profile_views,website_clicks"

        # Get insights
        data = await self._make_request(
            f"{self.instagram_account_id}/insights",
            {
                "metric": metrics,
                "period": period.value
            }
        )

        # Parse insights
        insights_data = {}
        for item in data.get("data", []):
            metric_name = item.get("name")
            values = item.get("values", [])
            if values:
                # Sum all values in period
                total = sum(v.get("value", 0) for v in values)
                insights_data[metric_name] = total

        # Calculate follower growth (if available)
        follower_growth = 0
        if period == MetricPeriod.DAY:
            follower_count_data = await self._get_follower_history(days=7)
            if len(follower_count_data) >= 2:
                follower_growth = follower_count_data[-1] - follower_count_data[0]

        return AccountInsights(
            account_id=self.instagram_account_id,
            username=account_info.get("username", ""),
            followers_count=account_info.get("followers_count", 0),
            follows_count=account_info.get("follows_count", 0),
            media_count=account_info.get("media_count", 0),
            follower_growth=follower_growth,
            follower_growth_rate=follower_growth / max(account_info.get("followers_count", 1), 1) * 100,
            profile_views=insights_data.get("profile_views", 0),
            website_clicks=insights_data.get("website_clicks", 0),
            reach=insights_data.get("reach", 0),
            impressions=insights_data.get("impressions", 0),
            period=period
        )

    async def _get_follower_history(self, days: int = 30) -> list[int]:
        """Get historical follower counts (requires stored data)."""
        # This would need historical data storage
        # For now, return empty
        return []

    # =========================================================================
    # MEDIA INSIGHTS
    # =========================================================================

    async def get_recent_media(self, limit: int = 25) -> list[dict]:
        """Get recent media posts."""
        fields = "id,media_type,timestamp,caption,permalink,thumbnail_url,media_url,like_count,comments_count"

        data = await self._make_request(
            f"{self.instagram_account_id}/media",
            {"fields": fields, "limit": limit}
        )

        return data.get("data", [])

    async def get_media_insights(self, media_id: str) -> PostInsights:
        """
        Get insights for a specific media post.

        Available metrics depend on media type:
        - IMAGE/CAROUSEL: impressions, reach, engagement, saved
        - VIDEO: impressions, reach, engagement, saved, video_views
        - REELS: plays, reach, likes, comments, shares, saved, total_interactions
        """
        # First get media info
        media_info = await self._make_request(
            media_id,
            {"fields": "id,media_type,timestamp,caption,permalink,like_count,comments_count"}
        )

        media_type = MediaType(media_info.get("media_type", "IMAGE"))

        # Define metrics based on type
        if media_type == MediaType.REELS:
            metrics = "plays,reach,likes,comments,shares,saved,total_interactions"
        elif media_type == MediaType.VIDEO:
            metrics = "impressions,reach,engagement,saved,video_views"
        else:
            metrics = "impressions,reach,engagement,saved"

        # Get insights
        try:
            insights_data = await self._make_request(
                f"{media_id}/insights",
                {"metric": metrics}
            )

            # Parse insights
            insights = {}
            for item in insights_data.get("data", []):
                name = item.get("name")
                values = item.get("values", [])
                if values:
                    insights[name] = values[0].get("value", 0)
        except Exception:
            # Some media types don't support all metrics
            insights = {}

        likes = media_info.get("like_count", 0) or insights.get("likes", 0)
        comments = media_info.get("comments_count", 0) or insights.get("comments", 0)
        saves = insights.get("saved", 0)
        shares = insights.get("shares", 0)
        reach = insights.get("reach", 0)
        impressions = insights.get("impressions", 0) or insights.get("plays", 0)

        total_interactions = likes + comments + saves + shares
        engagement_rate = (total_interactions / max(reach, 1)) * 100 if reach > 0 else 0

        return PostInsights(
            media_id=media_id,
            media_type=media_type,
            timestamp=datetime.fromisoformat(media_info.get("timestamp", "").replace("Z", "+00:00")),
            caption=media_info.get("caption"),
            permalink=media_info.get("permalink"),
            impressions=impressions,
            reach=reach,
            likes=likes,
            comments=comments,
            saves=saves,
            shares=shares,
            engagement_rate=engagement_rate,
            video_views=insights.get("video_views", 0),
            plays=insights.get("plays", 0),
            total_interactions=total_interactions
        )

    async def get_all_media_insights(self, limit: int = 25) -> list[PostInsights]:
        """Get insights for all recent media."""
        media_list = await self.get_recent_media(limit)

        insights = []
        for media in media_list:
            try:
                post_insight = await self.get_media_insights(media["id"])
                insights.append(post_insight)
            except Exception as e:
                logger.warning("media_insight_error", media_id=media["id"], error=str(e))

        return insights

    # =========================================================================
    # STORIES INSIGHTS
    # =========================================================================

    async def get_stories(self) -> list[dict]:
        """Get current stories (only available for 24 hours)."""
        data = await self._make_request(
            f"{self.instagram_account_id}/stories",
            {"fields": "id,media_type,timestamp,permalink"}
        )
        return data.get("data", [])

    async def get_story_insights(self, story_id: str) -> StoryInsights:
        """Get insights for a specific story."""
        # Get story info
        story_info = await self._make_request(
            story_id,
            {"fields": "id,timestamp"}
        )

        # Get story insights
        try:
            insights_data = await self._make_request(
                f"{story_id}/insights",
                {"metric": "impressions,reach,exits,replies,taps_forward,taps_back"}
            )

            insights = {}
            for item in insights_data.get("data", []):
                name = item.get("name")
                values = item.get("values", [])
                if values:
                    insights[name] = values[0].get("value", 0)
        except Exception:
            insights = {}

        impressions = insights.get("impressions", 0)
        exits = insights.get("exits", 0)
        completion_rate = ((impressions - exits) / max(impressions, 1)) * 100 if impressions > 0 else 0

        return StoryInsights(
            media_id=story_id,
            timestamp=datetime.fromisoformat(story_info.get("timestamp", "").replace("Z", "+00:00")),
            impressions=impressions,
            reach=insights.get("reach", 0),
            exits=exits,
            replies=insights.get("replies", 0),
            taps_forward=insights.get("taps_forward", 0),
            taps_back=insights.get("taps_back", 0),
            completion_rate=completion_rate
        )

    # =========================================================================
    # AUDIENCE INSIGHTS
    # =========================================================================

    async def get_audience_demographics(self) -> AudienceDemographics:
        """
        Get audience demographics.

        Requires Business account with 100+ followers.
        """
        try:
            data = await self._make_request(
                f"{self.instagram_account_id}/insights",
                {
                    "metric": "audience_city,audience_country,audience_gender_age,audience_locale",
                    "period": "lifetime"
                }
            )

            demographics = AudienceDemographics()

            for item in data.get("data", []):
                name = item.get("name")
                values = item.get("values", [])
                if not values:
                    continue

                value = values[0].get("value", {})

                if name == "audience_country":
                    demographics.top_countries = value
                elif name == "audience_city":
                    demographics.top_cities = value
                elif name == "audience_gender_age":
                    demographics.age_gender = value
                    # Calculate gender breakdown
                    male_total = sum(v for k, v in value.items() if k.startswith("M."))
                    female_total = sum(v for k, v in value.items() if k.startswith("F."))
                    other_total = sum(v for k, v in value.items() if k.startswith("U."))
                    total = male_total + female_total + other_total
                    if total > 0:
                        demographics.gender_male = (male_total / total) * 100
                        demographics.gender_female = (female_total / total) * 100
                        demographics.gender_other = (other_total / total) * 100
                elif name == "audience_locale":
                    demographics.locales = value

            return demographics

        except Exception as e:
            logger.warning("audience_demographics_error", error=str(e))
            return AudienceDemographics()

    # =========================================================================
    # REPORTS
    # =========================================================================

    async def generate_performance_report(
        self,
        days: int = 28
    ) -> ContentPerformanceReport:
        """
        Generate comprehensive performance report.

        Analizza:
        - Performance aggregata
        - Best performing content
        - Best times to post
        - Recommendations
        """
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=days)

        # Get all media insights
        media_insights = await self.get_all_media_insights(limit=50)

        # Filter to period
        period_media = [
            m for m in media_insights
            if m.timestamp >= period_start
        ]

        if not period_media:
            return ContentPerformanceReport(
                period_start=period_start,
                period_end=period_end,
                recommendations=["Non ci sono post nel periodo selezionato. Pubblica più contenuti!"]
            )

        # Aggregate metrics
        total_reach = sum(m.reach for m in period_media)
        total_impressions = sum(m.impressions for m in period_media)
        total_engagement = sum(m.total_interactions for m in period_media)

        # Count by type
        posts = [m for m in period_media if m.media_type in [MediaType.IMAGE, MediaType.CAROUSEL_ALBUM]]
        reels = [m for m in period_media if m.media_type == MediaType.REELS]

        # Find best performing
        best_post = max(period_media, key=lambda x: x.engagement_rate) if period_media else None

        # Analyze best times
        hour_performance: dict[int, list[float]] = {}
        day_performance: dict[int, list[float]] = {}

        for m in period_media:
            hour = m.timestamp.hour
            day = m.timestamp.weekday()

            if hour not in hour_performance:
                hour_performance[hour] = []
            hour_performance[hour].append(m.engagement_rate)

            if day not in day_performance:
                day_performance[day] = []
            day_performance[day].append(m.engagement_rate)

        # Find best hour
        best_hour = None
        if hour_performance:
            best_hour_num = max(hour_performance, key=lambda x: sum(hour_performance[x]) / len(hour_performance[x]))
            best_hour = f"{best_hour_num:02d}:00"

        # Find best day
        best_day = None
        day_names = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        if day_performance:
            best_day_num = max(day_performance, key=lambda x: sum(day_performance[x]) / len(day_performance[x]))
            best_day = day_names[best_day_num]

        # Generate recommendations
        recommendations = []

        avg_engagement = sum(m.engagement_rate for m in period_media) / len(period_media)

        if avg_engagement < 2:
            recommendations.append("📉 Engagement sotto la media. Prova contenuti più interattivi (domande, sondaggi).")
        elif avg_engagement > 5:
            recommendations.append("🎉 Ottimo engagement! Continua con questo tipo di contenuti.")

        if len(reels) < len(posts) * 0.3:
            recommendations.append("🎬 Pubblica più Reels! Hanno reach organico maggiore.")

        if best_hour:
            recommendations.append(f"⏰ Il tuo orario migliore è alle {best_hour}. Pubblica di più a quest'ora.")

        if best_day:
            recommendations.append(f"📅 Il giorno migliore è {best_day}. Concentra i contenuti importanti in questo giorno.")

        if total_reach < 1000:
            recommendations.append("📢 Reach basso. Usa più hashtag rilevanti e collabora con altri creator.")

        return ContentPerformanceReport(
            period_start=period_start,
            period_end=period_end,
            total_posts=len(posts),
            total_stories=0,  # Would need historical story data
            total_reels=len(reels),
            total_reach=total_reach,
            total_impressions=total_impressions,
            total_engagement=total_engagement,
            avg_engagement_rate=avg_engagement,
            best_post=best_post,
            best_time_to_post=best_hour,
            best_day_to_post=best_day,
            recommendations=recommendations
        )


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

instagram_insights = InstagramInsightsService()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def get_instagram_insights_summary() -> dict[str, Any]:
    """Quick summary for dashboard."""
    if not instagram_insights.is_configured:
        return {
            "configured": False,
            "error": "Instagram Insights not configured"
        }

    try:
        account = await instagram_insights.get_account_insights()
        recent_media = await instagram_insights.get_all_media_insights(limit=10)

        avg_engagement = 0
        if recent_media:
            avg_engagement = sum(m.engagement_rate for m in recent_media) / len(recent_media)

        return {
            "configured": True,
            "username": account.username,
            "followers": account.followers_count,
            "follower_growth": account.follower_growth,
            "reach_28d": account.reach,
            "impressions_28d": account.impressions,
            "avg_engagement_rate": round(avg_engagement, 2),
            "recent_posts_count": len(recent_media)
        }
    except Exception as e:
        logger.error("instagram_summary_error", error=str(e))
        return {
            "configured": True,
            "error": str(e)
        }
