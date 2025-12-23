"""
Social Media Manager Agent - Multi-Platform Social Media Management.

This agent specializes in managing social media presence across multiple
platforms with scheduling, analytics, engagement, and content optimization.

Features:
    - Multi-platform post scheduling (Twitter, Facebook, LinkedIn, Instagram)
    - Real-time engagement monitoring and auto-response
    - Social media analytics and reporting
    - Optimal posting time suggestions
    - Trend analysis and content recommendations
    - Hashtag optimization

Tools:
    1. schedule_post() - Schedule posts across platforms
    2. analyze_engagement() - Analyze post performance
    3. respond_to_comments() - Auto-respond to comments/mentions
    4. monitor_mentions() - Track brand mentions
    5. suggest_optimal_times() - Recommend posting times
    6. trend_analysis() - Identify trending topics

Author: StudioCentOS AI Team
Updated: December 2025 - Real API Integrations
"""

import os
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from app.infrastructure.agents.base_agent import BaseAgent, AgentConfig, AgentCapability
from app.infrastructure.agents.task import Task, TaskOutput
from app.domain.marketing.content_creator import SocialPlatform

# Import real social media clients
from app.infrastructure.social.twitter_client import TwitterClient
from app.infrastructure.social.facebook_client import FacebookClient
from app.infrastructure.social.linkedin_client import LinkedInClient
from app.infrastructure.social.instagram_client import InstagramClient
from app.infrastructure.social.base_client import OAuthTokens, SocialAPIError

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================


class EngagementType(str, Enum):
    """Types of social media engagement."""

    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    RETWEET = "retweet"
    MENTION = "mention"
    DIRECT_MESSAGE = "direct_message"


class PostStatus(str, Enum):
    """Post scheduling status."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class SocialPost(BaseModel):
    """Social media post model."""

    id: str = Field(..., description="Unique post ID")
    content: str = Field(..., description="Post content")
    platforms: List[SocialPlatform] = Field(..., description="Target platforms")
    status: PostStatus = Field(default=PostStatus.DRAFT, description="Post status")
    scheduled_time: Optional[datetime] = Field(
        default=None, description="Scheduled publish time"
    )
    published_time: Optional[datetime] = Field(
        default=None, description="Actual publish time"
    )
    media_urls: List[str] = Field(
        default_factory=list, description="Attached media URLs"
    )
    hashtags: List[str] = Field(default_factory=list, description="Hashtags")
    mentions: List[str] = Field(default_factory=list, description="User mentions")
    analytics: Dict[str, Any] = Field(
        default_factory=dict, description="Post analytics"
    )


class EngagementMetrics(BaseModel):
    """Social media engagement metrics."""

    platform: SocialPlatform = Field(..., description="Platform name")
    post_id: str = Field(..., description="Post ID")
    likes: int = Field(default=0, description="Number of likes")
    comments: int = Field(default=0, description="Number of comments")
    shares: int = Field(default=0, description="Number of shares")
    impressions: int = Field(default=0, description="Total impressions")
    reach: int = Field(default=0, description="Unique reach")
    engagement_rate: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Engagement rate %"
    )
    click_through_rate: float = Field(
        default=0.0, ge=0.0, le=100.0, description="CTR %"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Metrics timestamp"
    )


class OptimalPostingTime(BaseModel):
    """Optimal posting time recommendation."""

    platform: SocialPlatform = Field(..., description="Platform")
    day_of_week: str = Field(..., description="Day of week")
    hour: int = Field(..., ge=0, le=23, description="Hour (24h format)")
    expected_engagement: float = Field(
        ..., description="Expected engagement score"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score"
    )
    reason: str = Field(..., description="Recommendation reason")


class TrendingTopic(BaseModel):
    """Trending topic information."""

    topic: str = Field(..., description="Topic name")
    platform: SocialPlatform = Field(..., description="Platform")
    volume: int = Field(..., description="Mention volume")
    sentiment: float = Field(
        ..., ge=-1.0, le=1.0, description="Sentiment score"
    )
    trending_since: datetime = Field(..., description="Trending start time")
    relevance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Relevance to brand"
    )


class CommentResponse(BaseModel):
    """Auto-response to comment/mention."""

    original_comment: str = Field(..., description="Original comment")
    response: str = Field(..., description="Generated response")
    sentiment: str = Field(..., description="Comment sentiment")
    requires_human: bool = Field(
        default=False, description="Needs human review"
    )
    urgency: str = Field(default="low", description="Response urgency")


# ============================================================================
# SOCIAL MEDIA MANAGER AGENT
# ============================================================================


class SocialMediaManagerAgent(BaseAgent):
    """
    Social Media Manager Agent for multi-platform management.

    Manages social media presence across Twitter, Facebook, LinkedIn,
    Instagram with scheduling, analytics, and engagement automation.

    Capabilities:
        - Multi-platform post scheduling
        - Real-time engagement monitoring
        - Auto-response to comments/mentions
        - Analytics and reporting
        - Optimal posting time analysis
        - Trend identification

    Example:
        >>> config = AgentConfig(
        ...     id="social_manager_1",
        ...     name="Social Media Manager",
        ...     model="gpt-4",
        ... )
        >>> agent = SocialMediaManagerAgent(config=config)
        >>>
        >>> # Schedule cross-platform post
        >>> await agent.schedule_post(
        ...     content="New product launch!",
        ...     platforms=["twitter", "linkedin"],
        ...     scheduled_time=datetime.now() + timedelta(hours=2),
        ... )
    """

    def __init__(self, config: AgentConfig):
        """Initialize Social Media Manager Agent."""
        super().__init__(config)

        self.platform_clients: Dict[str, Any] = {}
        self.posting_schedule: List[SocialPost] = []
        self.engagement_history: List[EngagementMetrics] = []

        # Initialize clients lazily
        self._twitter_client: Optional[TwitterClient] = None
        self._facebook_client: Optional[FacebookClient] = None
        self._linkedin_client: Optional[LinkedInClient] = None
        self._instagram_client: Optional[InstagramClient] = None

    async def on_start(self) -> None:
        """Initialize platform API clients with real credentials."""
        await super().on_start()

        # Initialize Twitter client if credentials available
        twitter_access = os.getenv("TWITTER_ACCESS_TOKEN")
        if twitter_access:
            self._twitter_client = TwitterClient(
                tokens=OAuthTokens(
                    access_token=twitter_access,
                    refresh_token=os.getenv("TWITTER_REFRESH_TOKEN"),
                ),
            )
            self.platform_clients["twitter"] = self._twitter_client
            logger.info("Twitter client initialized")

        # Initialize Facebook client
        fb_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        if fb_token:
            self._facebook_client = FacebookClient(
                page_access_token=fb_token,
                page_id=os.getenv("FACEBOOK_PAGE_ID"),
            )
            self.platform_clients["facebook"] = self._facebook_client
            logger.info("Facebook client initialized")

        # Initialize LinkedIn client
        linkedin_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        if linkedin_token:
            self._linkedin_client = LinkedInClient(
                tokens=OAuthTokens(
                    access_token=linkedin_token,
                    refresh_token=os.getenv("LINKEDIN_REFRESH_TOKEN"),
                ),
                organization_id=os.getenv("LINKEDIN_ORGANIZATION_ID"),
            )
            self.platform_clients["linkedin"] = self._linkedin_client
            logger.info("LinkedIn client initialized")

        # Initialize Instagram client (uses Facebook token)
        ig_id = os.getenv("INSTAGRAM_BUSINESS_ID")
        if ig_id and fb_token:
            self._instagram_client = InstagramClient(
                page_access_token=fb_token,
                ig_user_id=ig_id,
            )
            self.platform_clients["instagram"] = self._instagram_client
            logger.info("Instagram client initialized")

        active_platforms = [p for p, c in self.platform_clients.items() if c]
        logger.info(f"Social Media Manager ready with platforms: {active_platforms}")

    def get_capabilities(self) -> List[AgentCapability]:
        """Get list of social media management capabilities."""
        return [
            AgentCapability(
                name="schedule_post",
                description="Schedule posts across multiple social platforms",
                input_schema={"content": "str", "platforms": "list", "scheduled_time": "datetime"},
                output_schema={"post_id": "str", "status": "str"},
            ),
            AgentCapability(
                name="analyze_engagement",
                description="Analyze post engagement metrics",
                input_schema={"post_id": "str", "platform": "str"},
                output_schema={"likes": "int", "comments": "int", "shares": "int"},
            ),
            AgentCapability(
                name="respond_to_comments",
                description="Auto-respond to comments with AI",
                input_schema={"platform": "str", "post_id": "str"},
                output_schema={"responses": "list"},
            ),
            AgentCapability(
                name="trend_analysis",
                description="Identify trending topics relevant to brand",
                input_schema={"platform": "str"},
                output_schema={"trends": "list"},
            ),
        ]

    async def execute(self, task: Task) -> TaskOutput:
        """Execute social media management task."""
        task_type = task.input.data.get("action", "schedule")

        try:
            if task_type == "schedule":
                platforms = [SocialPlatform(p) for p in task.input.data.get("platforms", ["twitter"])]
                result = await self.schedule_post(
                    content=task.input.data.get("content", ""),
                    platforms=platforms,
                    scheduled_time=datetime.fromisoformat(task.input.data.get("scheduled_time", datetime.utcnow().isoformat())),
                )
                return TaskOutput(
                    result={"post_id": result.id, "status": result.status.value},
                    metadata={"platforms": [p.value for p in result.platforms]}
                )
            elif task_type == "analyze":
                platform = SocialPlatform(task.input.data.get("platform", "twitter"))
                result = await self.analyze_engagement(
                    post_id=task.input.data.get("post_id", ""),
                    platform=platform
                )
                return TaskOutput(
                    result=result.model_dump(),
                    metadata={"platform": platform.value}
                )
            elif task_type == "trends":
                platform = SocialPlatform(task.input.data.get("platform", "twitter"))
                trends = await self.trend_analysis(platform=platform)
                return TaskOutput(
                    result={"trends": [t.model_dump() for t in trends]},
                    metadata={"platform": platform.value}
                )
            else:
                raise ValueError(f"Unknown action: {task_type}")

        except Exception as e:
            return TaskOutput(
                result={"error": str(e)},
                metadata={"status": "failed"}
            )

    async def schedule_post(
        self,
        content: str,
        platforms: List[SocialPlatform],
        scheduled_time: datetime,
        media_urls: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None,
    ) -> SocialPost:
        """
        Schedule post across multiple platforms.

        Args:
            content: Post content
            platforms: Target platforms
            scheduled_time: When to publish
            media_urls: Optional media attachments
            hashtags: Optional hashtags

        Returns:
            SocialPost with scheduling confirmation

        Example:
            >>> post = await agent.schedule_post(
            ...     content="Check out our new feature!",
            ...     platforms=[SocialPlatform.TWITTER, SocialPlatform.LINKEDIN],
            ...     scheduled_time=datetime.now() + timedelta(hours=2),
            ...     hashtags=["#AI", "#Tech"],
            ... )
        """
        # Generate unique post ID
        post_id = f"post_{datetime.utcnow().timestamp()}"

        # Optimize content per platform
        optimized_content = await self._optimize_for_platforms(
            content, platforms
        )

        # Create post object
        post = SocialPost(
            id=post_id,
            content=optimized_content,
            platforms=platforms,
            status=PostStatus.SCHEDULED,
            scheduled_time=scheduled_time,
            media_urls=media_urls or [],
            hashtags=hashtags or [],
        )

        # Schedule with each platform
        for platform in platforms:
            await self._schedule_platform_post(platform, post)

        # Add to schedule
        self.posting_schedule.append(post)

        return post

    async def analyze_engagement(
        self, post_id: str, platform: SocialPlatform
    ) -> EngagementMetrics:
        """
        Analyze engagement metrics for a post.

        Args:
            post_id: Post identifier
            platform: Platform to analyze

        Returns:
            EngagementMetrics with detailed analytics
        """
        # Fetch metrics from platform API
        metrics = await self._fetch_platform_metrics(platform, post_id)

        # Calculate engagement rate
        if metrics["impressions"] > 0:
            engagement_rate = (
                (metrics["likes"] + metrics["comments"] + metrics["shares"])
                / metrics["impressions"]
                * 100
            )
        else:
            engagement_rate = 0.0

        engagement = EngagementMetrics(
            platform=platform,
            post_id=post_id,
            likes=metrics.get("likes", 0),
            comments=metrics.get("comments", 0),
            shares=metrics.get("shares", 0),
            impressions=metrics.get("impressions", 0),
            reach=metrics.get("reach", 0),
            engagement_rate=engagement_rate,
            click_through_rate=metrics.get("ctr", 0.0),
        )

        # Store for analysis
        self.engagement_history.append(engagement)

        return engagement

    async def respond_to_comments(
        self, platform: SocialPlatform, post_id: str, limit: int = 10
    ) -> List[CommentResponse]:
        """
        Auto-respond to comments on a post.

        Args:
            platform: Platform to check
            post_id: Post ID
            limit: Max comments to process

        Returns:
            List of generated responses
        """
        # Fetch recent comments
        comments = await self._fetch_comments(platform, post_id, limit)

        responses = []
        for comment in comments:
            # Analyze sentiment
            sentiment = await self._analyze_sentiment(comment["text"])

            # Check if requires human intervention
            requires_human = await self._needs_human_review(
                comment["text"], sentiment
            )

            if not requires_human:
                # Generate response
                response_text = await self._generate_response(
                    comment["text"], sentiment
                )

                # Post response
                await self._post_comment_response(
                    platform, comment["id"], response_text
                )
            else:
                response_text = "[Flagged for human review]"

            responses.append(
                CommentResponse(
                    original_comment=comment["text"],
                    response=response_text,
                    sentiment=sentiment,
                    requires_human=requires_human,
                    urgency=self._determine_urgency(sentiment),
                )
            )

        return responses

    async def monitor_mentions(
        self, platform: SocialPlatform, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Monitor brand mentions on platform.

        Args:
            platform: Platform to monitor
            hours: Hours to look back

        Returns:
            List of mentions with metadata
        """
        since = datetime.utcnow() - timedelta(hours=hours)

        # Fetch mentions from platform API
        mentions = await self._fetch_mentions(platform, since)

        # Enrich with sentiment and priority
        enriched = []
        for mention in mentions:
            sentiment = await self._analyze_sentiment(mention["text"])
            priority = await self._calculate_priority(mention, sentiment)

            enriched.append(
                {
                    **mention,
                    "sentiment": sentiment,
                    "priority": priority,
                    "requires_response": priority in ["high", "urgent"],
                }
            )

        return enriched

    async def suggest_optimal_times(
        self, platform: SocialPlatform, days: int = 7
    ) -> List[OptimalPostingTime]:
        """
        Suggest optimal posting times based on historical data.

        Args:
            platform: Platform to analyze
            days: Days of history to analyze

        Returns:
            List of optimal posting times
        """
        # Analyze historical engagement data
        historical_data = await self._get_historical_engagement(
            platform, days
        )

        # Group by day of week and hour
        patterns = self._analyze_engagement_patterns(historical_data)

        # Generate recommendations
        recommendations = []
        for pattern in patterns[:5]:  # Top 5 times
            recommendations.append(
                OptimalPostingTime(
                    platform=platform,
                    day_of_week=pattern["day"],
                    hour=pattern["hour"],
                    expected_engagement=pattern["avg_engagement"],
                    confidence=pattern["confidence"],
                    reason=self._generate_recommendation_reason(pattern),
                )
            )

        return recommendations

    async def trend_analysis(
        self, platform: SocialPlatform, limit: int = 10
    ) -> List[TrendingTopic]:
        """
        Identify trending topics relevant to brand.

        Args:
            platform: Platform to analyze
            limit: Number of trends to return

        Returns:
            List of trending topics
        """
        # Fetch trending topics from platform
        trends = await self._fetch_trending_topics(platform)

        # Calculate relevance to brand
        relevant_trends = []
        for trend in trends:
            relevance = await self._calculate_brand_relevance(trend)

            if relevance > 0.3:  # Threshold for relevance
                relevant_trends.append(
                    TrendingTopic(
                        topic=trend["name"],
                        platform=platform,
                        volume=trend["volume"],
                        sentiment=trend["sentiment"],
                        trending_since=trend["started_at"],
                        relevance_score=relevance,
                    )
                )

        # Sort by relevance and return top N
        relevant_trends.sort(
            key=lambda x: x.relevance_score, reverse=True
        )
        return relevant_trends[:limit]

    # ========================================================================
    # HELPER METHODS (Private)
    # ========================================================================

    async def _optimize_for_platforms(
        self, content: str, platforms: List[SocialPlatform]
    ) -> str:
        """Optimize content for specific platforms using GROQ LLM."""
        try:
            from app.core.llm.groq_client import get_groq_client

            # If single platform, optimize specifically
            if len(platforms) == 1:
                platform = platforms[0]
                client = get_groq_client(model="llama-3.1-8b")

                platform_rules = {
                    SocialPlatform.TWITTER: "Max 280 caratteri, hashtag concisi, tono diretto",
                    SocialPlatform.LINKEDIN: "Tono professionale, può essere più lungo, focus su valore business",
                    SocialPlatform.INSTAGRAM: "Emoji appropriati, focus visuale, max 2200 caratteri",
                    SocialPlatform.FACEBOOK: "Tono conversazionale, può includere link, emoji moderati",
                    SocialPlatform.TIKTOK: "Ultra breve, catchy, gen-z friendly",
                }

                prompt = f"""Ottimizza questo contenuto per {platform.value}.

Contenuto originale: {content}

Regole per {platform.value}: {platform_rules.get(platform, 'Tono professionale')}

Contenuto ottimizzato:"""

                response = await client.generate(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=500
                )

                return response.strip()

            # Multiple platforms: return original, let each platform optimize individually
            return content

        except Exception:
            return content

    async def _schedule_platform_post(
        self, platform: SocialPlatform, post: SocialPost
    ) -> Dict[str, Any]:
        """Schedule/publish post with platform API."""
        client = self.platform_clients.get(platform.value)

        if not client:
            logger.warning(f"No client available for {platform.value}")
            return {"error": f"No client for {platform.value}", "scheduled": False}

        try:
            async with client:
                # Upload media if present
                media_ids = []
                for media_url in post.media_urls:
                    # For now, just pass the URL (platforms that support URL-based media)
                    media_ids.append(media_url)

                # Add hashtags to content
                content = post.content
                if post.hashtags:
                    hashtag_str = " ".join(f"#{tag.lstrip('#')}" for tag in post.hashtags)
                    content = f"{content}\n\n{hashtag_str}"

                # Post to platform
                if platform == SocialPlatform.TWITTER:
                    result = await client.post(content=content, media_ids=media_ids if media_ids else None)
                elif platform == SocialPlatform.FACEBOOK:
                    result = await client.post(content=content, media_ids=media_ids if media_ids else None)
                elif platform == SocialPlatform.LINKEDIN:
                    result = await client.post(content=content, media_ids=media_ids if media_ids else None)
                elif platform == SocialPlatform.INSTAGRAM:
                    if media_ids:
                        result = await client.post_image(image_url=media_ids[0], caption=content)
                    else:
                        raise SocialAPIError("Instagram requires media", platform.value)
                else:
                    result = {"error": "Unsupported platform"}

                logger.info(f"Posted to {platform.value}: {result.get('id', 'unknown')}")
                return {"platform": platform.value, "post_id": result.get("id"), "scheduled": True}

        except SocialAPIError as e:
            logger.error(f"Error posting to {platform.value}: {e}")
            return {"error": str(e), "platform": platform.value, "scheduled": False}
        except Exception as e:
            logger.error(f"Unexpected error posting to {platform.value}: {e}")
            return {"error": str(e), "platform": platform.value, "scheduled": False}

    async def _fetch_platform_metrics(
        self, platform: SocialPlatform, post_id: str
    ) -> Dict[str, Any]:
        """Fetch metrics from platform API."""
        client = self.platform_clients.get(platform.value)

        if not client:
            logger.warning(f"No client available for {platform.value}")
            return {
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "impressions": 0,
                "reach": 0,
                "ctr": 0.0,
                "error": f"No client for {platform.value}",
            }

        try:
            async with client:
                metrics = await client.get_metrics(post_id)
                return metrics
        except SocialAPIError as e:
            logger.error(f"Error fetching metrics from {platform.value}: {e}")
            return {
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "impressions": 0,
                "reach": 0,
                "ctr": 0.0,
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching metrics: {e}")
            return {
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "impressions": 0,
                "reach": 0,
                "ctr": 0.0,
                "error": str(e),
            }

    async def _fetch_comments(
        self, platform: SocialPlatform, post_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Fetch comments from platform."""
        client = self.platform_clients.get(platform.value)

        if not client:
            logger.warning(f"No client available for {platform.value}")
            return []

        try:
            async with client:
                comments = await client.get_comments(post_id, limit=limit)
                return comments
        except SocialAPIError as e:
            logger.error(f"Error fetching comments from {platform.value}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching comments: {e}")
            return []

    async def _analyze_sentiment(self, text: str) -> str:
        """Analyze text sentiment using GROQ LLM."""
        try:
            from app.core.llm.groq_client import get_groq_client

            client = get_groq_client(model="llama-3.1-8b")  # Fast model for sentiment

            prompt = f"""Analizza il sentiment del seguente testo e rispondi SOLO con una parola: 'positive', 'neutral', o 'negative'.

Testo: {text}

Sentiment:"""

            response = await client.generate(
                prompt=prompt,
                temperature=0.1,
                max_tokens=10
            )

            sentiment = response.strip().lower()
            if sentiment in ["positive", "neutral", "negative"]:
                return sentiment
            return "neutral"

        except Exception:
            return "neutral"

    async def _needs_human_review(
        self, text: str, sentiment: str
    ) -> bool:
        """Determine if comment needs human review."""
        # Negative sentiment always needs review
        if sentiment == "negative":
            return True

        # Check for complaint keywords
        complaint_keywords = [
            "reclamo", "complaint", "refund", "rimborso",
            "denuncia", "avvocato", "lawyer", "legal",
            "truffa", "scam", "fraud", "frode",
            "vergogna", "schifo", "disgusting", "terrible",
            "mai più", "never again", "worst", "peggio",
        ]
        text_lower = text.lower()
        for keyword in complaint_keywords:
            if keyword in text_lower:
                return True

        # Check for legal/compliance concerns
        legal_keywords = [
            "gdpr", "privacy", "dati personali", "personal data",
            "garanzia", "warranty", "diritto", "right",
            "consumatore", "consumer", "autorità", "authority",
        ]
        for keyword in legal_keywords:
            if keyword in text_lower:
                return True

        # Check for urgent language
        urgent_patterns = [
            "urgente", "urgent", "immediately", "subito",
            "help", "aiuto", "emergency", "emergenza",
        ]
        for pattern in urgent_patterns:
            if pattern in text_lower:
                return True

        return False

    async def _generate_response(
        self, comment: str, sentiment: str
    ) -> str:
        """Generate appropriate response to comment using GROQ LLM."""
        try:
            from app.core.llm.groq_client import get_groq_client

            client = get_groq_client(model="llama-3.3-70b")

            tone_guide = {
                "positive": "entusiasta e riconoscente",
                "neutral": "professionale e cordiale",
                "negative": "empatico, comprensivo e orientato alla soluzione"
            }

            prompt = f"""Genera una risposta breve e professionale per questo commento social media.

Commento: {comment}
Sentiment rilevato: {sentiment}
Tono da usare: {tone_guide.get(sentiment, 'professionale')}

Regole:
- Max 2-3 frasi
- In italiano
- Professionale ma friendly
- Se negativo, offri aiuto concreto

Risposta:"""

            response = await client.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=150
            )

            return response.strip()

        except Exception:
            # Fallback responses based on sentiment
            fallbacks = {
                "positive": "Grazie mille per il tuo feedback positivo! 🙏",
                "neutral": "Grazie per il tuo commento! Siamo a disposizione.",
                "negative": "Ci dispiace per l'inconveniente. Contattaci per risolvere insieme."
            }
            return fallbacks.get(sentiment, "Grazie per il tuo feedback!")

    async def _post_comment_response(
        self, platform: SocialPlatform, comment_id: str, response: str, post_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Post response to comment using platform API."""
        client = self.platform_clients.get(platform.value)

        if not client:
            logger.warning(f"No client available for {platform.value}")
            return {"error": f"No client for {platform.value}", "posted": False}

        try:
            async with client:
                if platform == SocialPlatform.LINKEDIN and post_id:
                    result = await client.reply_to_comment(comment_id, response, post_id=post_id)
                else:
                    result = await client.reply_to_comment(comment_id, response)
                logger.info(f"Replied to comment {comment_id} on {platform.value}")
                return {"posted": True, "result": result}
        except SocialAPIError as e:
            logger.error(f"Error replying on {platform.value}: {e}")
            return {"error": str(e), "posted": False}
        except Exception as e:
            logger.error(f"Unexpected error replying: {e}")
            return {"error": str(e), "posted": False}

    def _determine_urgency(self, sentiment: str) -> str:
        """Determine response urgency based on sentiment."""
        if sentiment == "negative":
            return "high"
        elif sentiment == "positive":
            return "low"
        return "medium"

    async def _fetch_mentions(
        self, platform: SocialPlatform, since: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch brand mentions since timestamp."""
        client = self.platform_clients.get(platform.value)

        if not client:
            logger.warning(f"No client available for {platform.value}")
            return []

        try:
            async with client:
                if platform == SocialPlatform.TWITTER and hasattr(client, 'get_mentions'):
                    mentions = await client.get_mentions(limit=100)
                    # Filter by since timestamp
                    return [m for m in mentions if m.get('created_at', '') >= since.isoformat()]
                else:
                    logger.info(f"Mentions not supported for {platform.value}")
                    return []
        except SocialAPIError as e:
            logger.error(f"Error fetching mentions from {platform.value}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching mentions: {e}")
            return []

    async def _calculate_priority(
        self, mention: Dict[str, Any], sentiment: str
    ) -> str:
        """Calculate mention priority based on sentiment and engagement."""
        # High priority for negative sentiment
        if sentiment == "negative":
            return "urgent"

        # Check engagement metrics
        likes = mention.get("likes", 0) or mention.get("like_count", 0)

        # High engagement = high priority
        if likes > 100:
            return "high"
        elif likes > 20:
            return "medium"

        return "low"

    async def _get_historical_engagement(
        self, platform: SocialPlatform, days: int
    ) -> List[Dict[str, Any]]:
        """Get historical engagement data from local history."""
        # Filter engagement history by platform and time
        cutoff = datetime.utcnow() - timedelta(days=days)

        return [
            {
                "platform": m.platform.value,
                "likes": m.likes,
                "comments": m.comments,
                "shares": m.shares,
                "engagement_rate": m.engagement_rate,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in self.engagement_history
            if m.platform == platform and m.timestamp >= cutoff
        ]

    def _analyze_engagement_patterns(
        self, data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze engagement patterns by time."""
        if not data:
            return []

        # Group by day of week and hour
        patterns: Dict[str, Dict[str, Any]] = {}

        for entry in data:
            try:
                ts = datetime.fromisoformat(entry["timestamp"])
                day = ts.strftime("%A")
                hour = ts.hour
                key = f"{day}_{hour}"

                if key not in patterns:
                    patterns[key] = {
                        "day": day,
                        "hour": hour,
                        "total_engagement": 0,
                        "count": 0,
                    }

                engagement = entry.get("likes", 0) + entry.get("comments", 0) + entry.get("shares", 0)
                patterns[key]["total_engagement"] += engagement
                patterns[key]["count"] += 1
            except Exception:
                continue

        # Calculate averages and confidence
        result = []
        for key, pattern in patterns.items():
            if pattern["count"] > 0:
                avg_engagement = pattern["total_engagement"] / pattern["count"]
                # Confidence based on sample size
                confidence = min(1.0, pattern["count"] / 10.0)

                result.append({
                    "day": pattern["day"],
                    "hour": pattern["hour"],
                    "avg_engagement": avg_engagement,
                    "confidence": confidence,
                    "sample_size": pattern["count"],
                })

        # Sort by avg engagement
        result.sort(key=lambda x: x["avg_engagement"], reverse=True)
        return result

    def _generate_recommendation_reason(
        self, pattern: Dict[str, Any]
    ) -> str:
        """Generate human-readable recommendation reason."""
        day = pattern.get('day', 'Unknown')
        hour = pattern.get('hour', 0)
        engagement = pattern.get('avg_engagement', 0)
        confidence = pattern.get('confidence', 0)

        time_str = f"{hour}:00"
        if hour < 12:
            time_str = f"{hour}:00 AM"
        elif hour == 12:
            time_str = "12:00 PM"
        else:
            time_str = f"{hour-12}:00 PM"

        confidence_str = "alta" if confidence > 0.7 else "media" if confidence > 0.4 else "bassa"

        return f"Engagement medio {engagement:.0f} osservato il {day} alle {time_str} (confidenza {confidence_str})"

    async def _fetch_trending_topics(
        self, platform: SocialPlatform
    ) -> List[Dict[str, Any]]:
        """Fetch trending topics from platform."""
        client = self.platform_clients.get(platform.value)

        if not client:
            logger.warning(f"No client available for {platform.value}")
            return []

        try:
            async with client:
                # Twitter has trending topics API
                if platform == SocialPlatform.TWITTER:
                    # Note: Twitter API v2 trending requires elevated access
                    # For now, return empty - would need Twitter API v1.1 trends endpoint
                    logger.info("Twitter trends requires elevated API access")
                    return []
                elif platform == SocialPlatform.INSTAGRAM:
                    # Instagram doesn't have public trending API
                    # Could potentially use hashtag search for popular tags
                    return []
                else:
                    return []
        except SocialAPIError as e:
            logger.error(f"Error fetching trends from {platform.value}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching trends: {e}")
            return []

    async def _calculate_brand_relevance(
        self, trend: Dict[str, Any]
    ) -> float:
        """Calculate trend relevance to brand using GROQ LLM."""
        try:
            from app.core.llm.groq_client import get_groq_client

            client = get_groq_client(model="llama-3.1-8b")

            prompt = f"""Valuta la rilevanza di questo trend per StudioCentOS, una software house italiana specializzata in:
- Sviluppo web enterprise (React, FastAPI)
- App mobile
- E-commerce
- AI & Automazione
- Consulenza tecnologica

Trend: {trend.get('name', '')}
Descrizione: {trend.get('description', '')}

Rispondi SOLO con un numero da 0.0 a 1.0 che indica la rilevanza (1.0 = molto rilevante, 0.0 = non rilevante):"""

            response = await client.generate(
                prompt=prompt,
                temperature=0.1,
                max_tokens=10
            )

            # Parse float from response
            try:
                score = float(response.strip())
                return max(0.0, min(1.0, score))
            except ValueError:
                return 0.5

        except Exception:
            return 0.5
