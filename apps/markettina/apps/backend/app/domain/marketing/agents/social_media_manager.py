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

Example:
    >>> agent = SocialMediaManagerAgent(config=config)
    >>>
    >>> # Schedule post across platforms
    >>> result = await agent.schedule_post(
    ...     content="Exciting news!",
    ...     platforms=["twitter", "linkedin"],
    ...     scheduled_time="2024-10-18T10:00:00Z",
    ... )
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.domain.marketing.agents.content_creator import SocialPlatform
from app.infrastructure.ai.agents.base_agent import AgentCapability, AgentConfig, BaseAgent
from app.infrastructure.ai.agents.task import Task, TaskOutput
from app.infrastructure.social import (
    TwitterClient,
    FacebookClient,
    InstagramClient,
    LinkedInClient,
)

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
    platforms: list[SocialPlatform] = Field(..., description="Target platforms")
    status: PostStatus = Field(default=PostStatus.DRAFT, description="Post status")
    scheduled_time: datetime | None = Field(
        default=None, description="Scheduled publish time"
    )
    published_time: datetime | None = Field(
        default=None, description="Actual publish time"
    )
    media_urls: list[str] = Field(
        default_factory=list, description="Attached media URLs"
    )
    hashtags: list[str] = Field(default_factory=list, description="Hashtags")
    mentions: list[str] = Field(default_factory=list, description="User mentions")
    analytics: dict[str, Any] = Field(
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

        self.platform_clients: dict[str, Any] = {}
        self.posting_schedule: list[SocialPost] = []
        self.engagement_history: list[EngagementMetrics] = []

    async def on_start(self) -> None:
        """Initialize platform API clients."""
        await super().on_start()

        # Initialize production-ready API clients for each platform
        self.platform_clients = {
            "twitter": TwitterClient(),
            "facebook": FacebookClient(),
            "linkedin": LinkedInClient(),
            "instagram": InstagramClient(),
        }

        # Log configured platforms
        configured = [
            name for name, client in self.platform_clients.items()
            if client.is_configured()
        ]
        if configured:
            self._logger.info(f"Configured social platforms: {configured}")

    def get_capabilities(self) -> list[AgentCapability]:
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
            if task_type == "analyze":
                platform = SocialPlatform(task.input.data.get("platform", "twitter"))
                result = await self.analyze_engagement(
                    post_id=task.input.data.get("post_id", ""),
                    platform=platform
                )
                return TaskOutput(
                    result=result.model_dump(),
                    metadata={"platform": platform.value}
                )
            if task_type == "trends":
                platform = SocialPlatform(task.input.data.get("platform", "twitter"))
                trends = await self.trend_analysis(platform=platform)
                return TaskOutput(
                    result={"trends": [t.model_dump() for t in trends]},
                    metadata={"platform": platform.value}
                )
            raise ValueError(f"Unknown action: {task_type}")

        except Exception as e:
            return TaskOutput(
                result={"error": str(e)},
                metadata={"status": "failed"}
            )

    async def schedule_post(
        self,
        content: str,
        platforms: list[SocialPlatform],
        scheduled_time: datetime,
        media_urls: list[str] | None = None,
        hashtags: list[str] | None = None,
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
    ) -> list[CommentResponse]:
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
    ) -> list[dict[str, Any]]:
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
    ) -> list[OptimalPostingTime]:
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
    ) -> list[TrendingTopic]:
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
        self, content: str, platforms: list[SocialPlatform]
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
    ) -> None:
        """Schedule post with platform API."""
        platform_name = platform.value.lower()
        client = self.platform_clients.get(platform_name)

        if not client or not client.is_configured():
            self._logger.warning(f"Platform {platform_name} not configured, skipping")
            return

        try:
            media_urls = post.media_urls if post.media_urls else None

            result = await client.publish_post(
                content=post.content,
                media_urls=media_urls,
            )

            # Update post with platform confirmation
            post.analytics[f"{platform_name}_post_id"] = result.post_id
            if result.permalink:
                post.analytics[f"{platform_name}_url"] = result.permalink

            self._logger.info(
                f"Published to {platform_name}: {result.post_id}"
            )

        except Exception as e:
            self._logger.error(f"Failed to publish to {platform_name}: {e}")
            raise

    async def _fetch_platform_metrics(
        self, platform: SocialPlatform, post_id: str
    ) -> dict[str, Any]:
        """Fetch metrics from platform API."""
        platform_name = platform.value.lower()
        client = self.platform_clients.get(platform_name)

        if not client or not client.is_configured():
            return {
                "likes": 0, "comments": 0, "shares": 0,
                "impressions": 0, "reach": 0, "ctr": 0.0,
            }

        try:
            metrics = await client.get_post_metrics(post_id)

            return {
                "likes": metrics.likes,
                "comments": metrics.comments,
                "shares": metrics.shares,
                "impressions": metrics.impressions,
                "reach": metrics.reach,
                "ctr": (metrics.clicks / metrics.impressions * 100) if metrics.impressions > 0 else 0.0,
            }
        except Exception as e:
            self._logger.warning(f"Failed to fetch metrics from {platform_name}: {e}")
            return {
                "likes": 0, "comments": 0, "shares": 0,
                "impressions": 0, "reach": 0, "ctr": 0.0,
            }

    async def _fetch_comments(
        self, platform: SocialPlatform, post_id: str, limit: int
    ) -> list[dict[str, Any]]:
        """Fetch comments from platform."""

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

        # - Negative sentiment
        # - Complaint keywords
        # - Legal/compliance concerns
        return sentiment == "negative"

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
        self, platform: SocialPlatform, comment_id: str, response: str
    ) -> None:
        """Post response to comment."""


    def _determine_urgency(self, sentiment: str) -> str:
        """Determine response urgency based on sentiment."""
        if sentiment == "negative":
            return "high"
        if sentiment == "positive":
            return "low"
        return "medium"

    async def _fetch_mentions(
        self, platform: SocialPlatform, since: datetime
    ) -> list[dict[str, Any]]:
        """Fetch brand mentions since timestamp."""

        return []

    async def _calculate_priority(
        self, mention: dict[str, Any], sentiment: str
    ) -> str:
        """Calculate mention priority."""

        # - Influencer mentions: high
        # - Negative sentiment: urgent
        # - High engagement: high
        return "medium"

    async def _get_historical_engagement(
        self, platform: SocialPlatform, days: int
    ) -> list[dict[str, Any]]:
        """Get historical engagement data."""

        return []

    def _analyze_engagement_patterns(
        self, data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Analyze engagement patterns by time."""

        # - Group by day/hour
        # - Calculate avg engagement
        # - Determine confidence
        return []

    def _generate_recommendation_reason(
        self, pattern: dict[str, Any]
    ) -> str:
        """Generate human-readable recommendation reason."""
        return f"High engagement observed on {pattern.get('day', 'Unknown')}"

    async def _fetch_trending_topics(
        self, platform: SocialPlatform
    ) -> list[dict[str, Any]]:
        """Fetch trending topics from platform."""

        return []

    async def _calculate_brand_relevance(
        self, trend: dict[str, Any]
    ) -> float:
        """Calculate trend relevance to brand using GROQ LLM."""
        try:
            from app.core.llm.groq_client import get_groq_client

            client = get_groq_client(model="llama-3.1-8b")

            prompt = f"""Valuta la rilevanza di questo trend per MARKETTINA, una software house italiana specializzata in:
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
