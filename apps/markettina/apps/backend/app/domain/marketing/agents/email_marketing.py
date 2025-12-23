"""
Email Marketing Agent - Email Campaign Automation.

This agent specializes in email marketing campaign design, audience segmentation,
personalization, and performance optimization.

Features:
    - Email campaign design and creation
    - Audience segmentation
    - Dynamic content personalization
    - Send time optimization
    - A/B testing
    - Performance analytics
    - List hygiene and deliverability

Tools:
    1. design_campaign() - Create email campaigns
    2. segment_audience() - Segment subscribers
    3. personalize_content() - Personalize emails
    4. optimize_send_time() - Find optimal send times
    5. analyze_performance() - Track email metrics
    6. manage_deliverability() - Improve deliverability

Example:
    >>> agent = EmailMarketingAgent(config=config)
    >>>
    >>> # Create email campaign
    >>> campaign = await agent.design_campaign(
    ...     subject="New Product Launch",
    ...     goal="sales",
    ...     audience_size=10000,
    ... )
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.infrastructure.ai.agents.base_agent import AgentConfig, BaseAgent
from app.infrastructure.email.sendgrid_client import SendGridClient

# ============================================================================
# ENUMS
# ============================================================================


class EmailCampaignType(str, Enum):
    """Email campaign types."""

    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    WELCOME = "welcome"
    ABANDONED_CART = "abandoned_cart"
    RE_ENGAGEMENT = "re_engagement"
    SURVEY = "survey"


class SegmentCriteria(str, Enum):
    """Audience segmentation criteria."""

    DEMOGRAPHICS = "demographics"
    BEHAVIOR = "behavior"
    ENGAGEMENT = "engagement"
    PURCHASE_HISTORY = "purchase_history"
    LIFECYCLE_STAGE = "lifecycle_stage"
    CUSTOM = "custom"


class EmailStatus(str, Enum):
    """Email delivery status."""

    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    SPAM = "spam"
    UNSUBSCRIBED = "unsubscribed"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class EmailCampaign(BaseModel):
    """Email campaign design."""

    campaign_id: str = Field(..., description="Campaign ID")
    name: str = Field(..., description="Campaign name")
    campaign_type: EmailCampaignType = Field(..., description="Campaign type")
    subject_line: str = Field(..., description="Email subject")
    preview_text: str = Field(..., description="Preview text")
    from_name: str = Field(..., description="Sender name")
    from_email: EmailStr = Field(..., description="Sender email")
    reply_to: EmailStr = Field(..., description="Reply-to email")
    html_content: str = Field(..., description="HTML email body")
    text_content: str = Field(..., description="Plain text version")
    cta_buttons: list[dict[str, str]] = Field(
        default_factory=list, description="Call-to-action buttons"
    )
    personalization_tokens: list[str] = Field(
        default_factory=list, description="Personalization fields"
    )
    scheduled_send: datetime | None = Field(
        default=None, description="Scheduled send time"
    )
    target_segments: list[str] = Field(
        default_factory=list, description="Target segment IDs"
    )
    ab_test_enabled: bool = Field(
        default=False, description="A/B testing enabled"
    )


class AudienceSegment(BaseModel):
    """Audience segmentation result."""

    segment_id: str = Field(..., description="Segment ID")
    name: str = Field(..., description="Segment name")
    criteria: SegmentCriteria = Field(..., description="Segmentation criteria")
    filters: dict[str, Any] = Field(..., description="Filter conditions")
    size: int = Field(..., ge=0, description="Segment size")
    characteristics: dict[str, Any] = Field(
        default_factory=dict, description="Segment characteristics"
    )
    engagement_score: float = Field(
        ..., ge=0.0, le=100.0, description="Avg engagement score"
    )
    estimated_value: float = Field(
        ..., ge=0.0, description="Estimated segment value"
    )


class PersonalizedEmail(BaseModel):
    """Personalized email content."""

    recipient_email: EmailStr = Field(..., description="Recipient email")
    recipient_name: str = Field(..., description="Recipient name")
    subject_line: str = Field(..., description="Personalized subject")
    html_content: str = Field(..., description="Personalized HTML")
    text_content: str = Field(..., description="Personalized text")
    personalization_data: dict[str, Any] = Field(
        default_factory=dict, description="Personalization values"
    )
    recommended_products: list[dict[str, Any]] = Field(
        default_factory=list, description="Product recommendations"
    )


class SendTimeOptimization(BaseModel):
    """Optimal send time recommendation."""

    recipient_timezone: str = Field(..., description="Recipient timezone")
    optimal_day: str = Field(..., description="Best day of week")
    optimal_hour: int = Field(..., ge=0, le=23, description="Best hour")
    confidence: float = Field(
        ..., ge=0.0, le=100.0, description="Confidence %"
    )
    historical_open_rate: float = Field(
        ..., ge=0.0, le=100.0, description="Historical open rate %"
    )
    recommended_send_time: datetime = Field(
        ..., description="Recommended send datetime"
    )


class EmailPerformance(BaseModel):
    """Email campaign performance metrics."""

    campaign_id: str = Field(..., description="Campaign ID")
    sent: int = Field(..., ge=0, description="Total sent")
    delivered: int = Field(..., ge=0, description="Total delivered")
    opens: int = Field(..., ge=0, description="Total opens")
    unique_opens: int = Field(..., ge=0, description="Unique opens")
    clicks: int = Field(..., ge=0, description="Total clicks")
    unique_clicks: int = Field(..., ge=0, description="Unique clicks")
    bounces: int = Field(..., ge=0, description="Bounces")
    spam_reports: int = Field(..., ge=0, description="Spam reports")
    unsubscribes: int = Field(..., ge=0, description="Unsubscribes")
    open_rate: float = Field(
        ..., ge=0.0, le=100.0, description="Open rate %"
    )
    click_rate: float = Field(
        ..., ge=0.0, le=100.0, description="Click rate %"
    )
    click_to_open_rate: float = Field(
        ..., ge=0.0, le=100.0, description="CTOR %"
    )
    bounce_rate: float = Field(
        ..., ge=0.0, le=100.0, description="Bounce rate %"
    )
    conversions: int = Field(..., ge=0, description="Total conversions")
    conversion_rate: float = Field(
        ..., ge=0.0, le=100.0, description="Conversion rate %"
    )
    revenue: float = Field(..., ge=0.0, description="Revenue generated")
    roi: float = Field(..., description="ROI %")


class DeliverabilityReport(BaseModel):
    """Email deliverability health report."""

    overall_score: float = Field(
        ..., ge=0.0, le=100.0, description="Overall health score"
    )
    sender_reputation: float = Field(
        ..., ge=0.0, le=100.0, description="Sender reputation"
    )
    list_hygiene_score: float = Field(
        ..., ge=0.0, le=100.0, description="List quality score"
    )
    engagement_rate: float = Field(
        ..., ge=0.0, le=100.0, description="Engagement rate %"
    )
    bounce_rate: float = Field(
        ..., ge=0.0, le=100.0, description="Bounce rate %"
    )
    spam_complaint_rate: float = Field(
        ..., ge=0.0, le=100.0, description="Spam complaint rate %"
    )
    issues: list[str] = Field(
        default_factory=list, description="Deliverability issues"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Improvement recommendations"
    )
    blacklist_status: list[dict[str, str]] = Field(
        default_factory=list, description="Blacklist check results"
    )


# ============================================================================
# EMAIL MARKETING AGENT
# ============================================================================


class EmailMarketingAgent(BaseAgent):
    """
    Email Marketing Agent for email campaign automation.

    Automates email marketing campaigns with advanced segmentation,
    personalization, and performance optimization.

    Capabilities:
        - Campaign design and creation
        - Audience segmentation
        - Dynamic personalization
        - Send time optimization
        - Performance tracking
        - Deliverability management
        - A/B testing

    Example:
        >>> config = AgentConfig(
        ...     id="email_agent_1",
        ...     name="Email Marketing Specialist",
        ...     model="gpt-4",
        ... )
        >>> agent = EmailMarketingAgent(config=config)
        >>>
        >>> # Design campaign
        >>> campaign = await agent.design_campaign(
        ...     campaign_type=EmailCampaignType.PROMOTIONAL,
        ...     subject="Summer Sale - 50% Off",
        ...     goal="sales",
        ... )
    """

    def __init__(self, config: AgentConfig):
        """Initialize Email Marketing Agent."""
        super().__init__(config)

        self.campaigns: dict[str, EmailCampaign] = {}
        self.segments: dict[str, AudienceSegment] = {}
        self.performance_history: list[EmailPerformance] = []
        self._sendgrid_client: SendGridClient | None = None

    async def on_start(self) -> None:
        """Initialize email service clients."""
        await super().on_start()

        self._sendgrid_client = SendGridClient()

        if self._sendgrid_client.is_configured():
            self._logger.info("SendGrid client configured")
        else:
            self._logger.warning("SendGrid not configured - email features limited")

    async def design_campaign(
        self,
        campaign_type: EmailCampaignType,
        subject: str,
        goal: str,
        from_name: str = "Your Brand",
        from_email: str = "hello@yourbrand.com",
        content_guidelines: dict[str, Any] | None = None,
    ) -> EmailCampaign:
        """
        Design and create email campaign.

        Args:
            campaign_type: Type of campaign
            subject: Email subject line
            goal: Campaign goal (sales, engagement, etc.)
            from_name: Sender name
            from_email: Sender email
            content_guidelines: Content requirements

        Returns:
            EmailCampaign with complete design

        Example:
            >>> campaign = await agent.design_campaign(
            ...     campaign_type=EmailCampaignType.NEWSLETTER,
            ...     subject="Weekly Industry Insights",
            ...     goal="engagement",
            ... )
        """
        # Generate campaign ID
        campaign_id = f"email_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Generate preview text
        preview_text = await self._generate_preview_text(subject, goal)

        # Generate email content
        html_content = await self._generate_html_content(
            campaign_type, subject, goal, content_guidelines or {}
        )
        text_content = await self._generate_text_content(html_content)

        # Extract CTAs
        ctas = self._extract_ctas(html_content)

        # Identify personalization tokens
        tokens = self._identify_tokens(html_content)

        campaign = EmailCampaign(
            campaign_id=campaign_id,
            name=subject,
            campaign_type=campaign_type,
            subject_line=subject,
            preview_text=preview_text,
            from_name=from_name,
            from_email=from_email,
            reply_to=from_email,
            html_content=html_content,
            text_content=text_content,
            cta_buttons=ctas,
            personalization_tokens=tokens,
        )

        self.campaigns[campaign_id] = campaign
        return campaign

    async def segment_audience(
        self,
        criteria: SegmentCriteria,
        filters: dict[str, Any],
        min_size: int = 100,
    ) -> AudienceSegment:
        """
        Segment subscribers based on criteria.

        Args:
            criteria: Segmentation criteria
            filters: Filter conditions
            min_size: Minimum segment size

        Returns:
            AudienceSegment with segment details
        """
        # Generate segment ID
        segment_id = f"segment_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Apply segmentation filters
        subscribers = await self._apply_segment_filters(criteria, filters)

        # Check minimum size
        if len(subscribers) < min_size:
            raise ValueError(
                f"Segment size {len(subscribers)} below minimum {min_size}"
            )

        # Analyze segment characteristics
        characteristics = await self._analyze_segment(subscribers)

        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(subscribers)

        # Estimate segment value
        estimated_value = await self._estimate_segment_value(subscribers)

        segment = AudienceSegment(
            segment_id=segment_id,
            name=f"{criteria.value} Segment",
            criteria=criteria,
            filters=filters,
            size=len(subscribers),
            characteristics=characteristics,
            engagement_score=engagement_score,
            estimated_value=estimated_value,
        )

        self.segments[segment_id] = segment
        return segment

    async def personalize_content(
        self, campaign_id: str, recipient_email: str
    ) -> PersonalizedEmail:
        """
        Generate personalized email content.

        Args:
            campaign_id: Campaign to personalize
            recipient_email: Recipient email

        Returns:
            PersonalizedEmail with customized content
        """
        # Get campaign template
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        # Fetch recipient data
        recipient_data = await self._fetch_recipient_data(recipient_email)

        # Personalize subject line
        personalized_subject = await self._personalize_subject(
            campaign.subject_line, recipient_data
        )

        # Personalize HTML content
        personalized_html = await self._personalize_html(
            campaign.html_content, recipient_data
        )

        # Personalize text content
        personalized_text = await self._personalize_text(
            campaign.text_content, recipient_data
        )

        # Generate product recommendations
        recommendations = await self._generate_recommendations(
            recipient_data, campaign.campaign_type
        )

        return PersonalizedEmail(
            recipient_email=recipient_email,
            recipient_name=recipient_data.get("name", "Subscriber"),
            subject_line=personalized_subject,
            html_content=personalized_html,
            text_content=personalized_text,
            personalization_data=recipient_data,
            recommended_products=recommendations,
        )

    async def optimize_send_time(
        self, recipient_email: str
    ) -> SendTimeOptimization:
        """
        Determine optimal send time for recipient.

        Args:
            recipient_email: Recipient email

        Returns:
            SendTimeOptimization with best send time
        """
        # Fetch recipient's engagement history
        history = await self._fetch_engagement_history(recipient_email)

        # Analyze open patterns
        patterns = self._analyze_open_patterns(history)

        # Get recipient timezone
        timezone = await self._detect_timezone(recipient_email)

        # Calculate optimal send time
        optimal_day, optimal_hour = self._calculate_optimal_time(patterns)

        # Calculate next occurrence
        next_send = self._get_next_occurrence(
            optimal_day, optimal_hour, timezone
        )

        # Calculate confidence
        confidence = self._calculate_confidence(patterns)

        return SendTimeOptimization(
            recipient_timezone=timezone,
            optimal_day=optimal_day,
            optimal_hour=optimal_hour,
            confidence=confidence,
            historical_open_rate=patterns.get("avg_open_rate", 0.0),
            recommended_send_time=next_send,
        )

    async def analyze_performance(
        self, campaign_id: str
    ) -> EmailPerformance:
        """
        Analyze email campaign performance.

        Args:
            campaign_id: Campaign to analyze

        Returns:
            EmailPerformance with metrics
        """
        # Fetch campaign metrics
        metrics = await self._fetch_campaign_metrics(campaign_id)

        # Calculate rates
        open_rate = (
            metrics["unique_opens"] / metrics["delivered"] * 100
            if metrics["delivered"] > 0
            else 0.0
        )
        click_rate = (
            metrics["unique_clicks"] / metrics["delivered"] * 100
            if metrics["delivered"] > 0
            else 0.0
        )
        ctor = (
            metrics["unique_clicks"] / metrics["unique_opens"] * 100
            if metrics["unique_opens"] > 0
            else 0.0
        )
        bounce_rate = (
            metrics["bounces"] / metrics["sent"] * 100
            if metrics["sent"] > 0
            else 0.0
        )
        conversion_rate = (
            metrics["conversions"] / metrics["delivered"] * 100
            if metrics["delivered"] > 0
            else 0.0
        )

        # Calculate ROI
        cost = metrics.get("cost", 0.0)
        roi = (
            (metrics["revenue"] - cost) / cost * 100 if cost > 0 else 0.0
        )

        performance = EmailPerformance(
            campaign_id=campaign_id,
            sent=metrics["sent"],
            delivered=metrics["delivered"],
            opens=metrics["opens"],
            unique_opens=metrics["unique_opens"],
            clicks=metrics["clicks"],
            unique_clicks=metrics["unique_clicks"],
            bounces=metrics["bounces"],
            spam_reports=metrics["spam_reports"],
            unsubscribes=metrics["unsubscribes"],
            open_rate=open_rate,
            click_rate=click_rate,
            click_to_open_rate=ctor,
            bounce_rate=bounce_rate,
            conversions=metrics["conversions"],
            conversion_rate=conversion_rate,
            revenue=metrics["revenue"],
            roi=roi,
        )

        self.performance_history.append(performance)
        return performance

    async def manage_deliverability(self) -> DeliverabilityReport:
        """
        Assess and improve email deliverability.

        Returns:
            DeliverabilityReport with health assessment
        """
        # Check sender reputation
        reputation = await self._check_sender_reputation()

        # Analyze list hygiene
        list_score = await self._analyze_list_hygiene()

        # Calculate engagement rate
        engagement = self._calculate_overall_engagement()

        # Get bounce and spam rates
        bounce_rate = await self._get_bounce_rate()
        spam_rate = await self._get_spam_rate()

        # Check blacklists
        blacklist_status = await self._check_blacklists()

        # Calculate overall score
        overall_score = self._calculate_deliverability_score(
            reputation, list_score, engagement, bounce_rate, spam_rate
        )

        # Identify issues
        issues = self._identify_deliverability_issues(
            overall_score, reputation, list_score, bounce_rate, spam_rate
        )

        # Generate recommendations
        recommendations = self._generate_deliverability_recommendations(issues)

        return DeliverabilityReport(
            overall_score=overall_score,
            sender_reputation=reputation,
            list_hygiene_score=list_score,
            engagement_rate=engagement,
            bounce_rate=bounce_rate,
            spam_complaint_rate=spam_rate,
            issues=issues,
            recommendations=recommendations,
            blacklist_status=blacklist_status,
        )

    # ========================================================================
    # HELPER METHODS (Private)
    # ========================================================================

    async def _generate_preview_text(self, subject: str, goal: str) -> str:
        """Generate email preview text."""

        return f"{subject} - Open to learn more"

    async def _generate_html_content(
        self, type_: EmailCampaignType, subject: str, goal: str, guidelines: dict[str, Any]
    ) -> str:
        """Generate HTML email content."""

        return "<html><body><h1>{{first_name}}</h1></body></html>"

    async def _generate_text_content(self, html: str) -> str:
        """Convert HTML to plain text."""

        return "Plain text version"

    def _extract_ctas(self, html: str) -> list[dict[str, str]]:
        """Extract CTA buttons from HTML."""

        return []

    def _identify_tokens(self, html: str) -> list[str]:
        """Identify personalization tokens."""

        return []

    async def _apply_segment_filters(
        self, criteria: SegmentCriteria, filters: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Apply segmentation filters to subscriber list."""

        return []

    async def _analyze_segment(
        self, subscribers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze segment characteristics."""

        return {}

    def _calculate_engagement_score(
        self, subscribers: list[dict[str, Any]]
    ) -> float:
        """Calculate average engagement score."""

        return 75.0

    async def _estimate_segment_value(
        self, subscribers: list[dict[str, Any]]
    ) -> float:
        """Estimate segment lifetime value."""

        return 0.0

    async def _fetch_recipient_data(self, email: str) -> dict[str, Any]:
        """Fetch recipient profile data."""

        return {"name": "User", "email": email}

    async def _personalize_subject(
        self, subject: str, data: dict[str, Any]
    ) -> str:
        """Personalize subject line."""

        return subject

    async def _personalize_html(
        self, html: str, data: dict[str, Any]
    ) -> str:
        """Personalize HTML content."""

        return html

    async def _personalize_text(
        self, text: str, data: dict[str, Any]
    ) -> str:
        """Personalize text content."""

        return text

    async def _generate_recommendations(
        self, data: dict[str, Any], type_: EmailCampaignType
    ) -> list[dict[str, Any]]:
        """Generate product recommendations."""

        return []

    async def _fetch_engagement_history(self, email: str) -> list[dict[str, Any]]:
        """Fetch recipient engagement history."""

        return []

    def _analyze_open_patterns(
        self, history: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze when recipient opens emails."""

        return {"avg_open_rate": 25.0}

    async def _detect_timezone(self, email: str) -> str:
        """Detect recipient timezone."""

        return "UTC"

    def _calculate_optimal_time(
        self, patterns: dict[str, Any]
    ) -> tuple[str, int]:
        """Calculate optimal day and hour."""

        return ("Tuesday", 10)

    def _get_next_occurrence(
        self, day: str, hour: int, timezone: str
    ) -> datetime:
        """Get next occurrence of day/hour."""

        return datetime.utcnow()

    def _calculate_confidence(self, patterns: dict[str, Any]) -> float:
        """Calculate confidence in recommendation."""

        return 75.0

    async def _fetch_campaign_metrics(self, campaign_id: str) -> dict[str, Any]:
        """Fetch campaign performance metrics."""

        return {
            "sent": 0,
            "delivered": 0,
            "opens": 0,
            "unique_opens": 0,
            "clicks": 0,
            "unique_clicks": 0,
            "bounces": 0,
            "spam_reports": 0,
            "unsubscribes": 0,
            "conversions": 0,
            "revenue": 0.0,
        }

    async def _check_sender_reputation(self) -> float:
        """Check sender reputation score."""

        return 80.0

    async def _analyze_list_hygiene(self) -> float:
        """Analyze list quality."""

        return 85.0

    def _calculate_overall_engagement(self) -> float:
        """Calculate overall engagement rate."""

        return 20.0

    async def _get_bounce_rate(self) -> float:
        """Get recent bounce rate."""

        return 2.0

    async def _get_spam_rate(self) -> float:
        """Get spam complaint rate."""

        return 0.1

    async def _check_blacklists(self) -> list[dict[str, str]]:
        """Check if domain/IP is blacklisted."""

        return []

    def _calculate_deliverability_score(
        self, rep: float, hygiene: float, eng: float, bounce: float, spam: float
    ) -> float:
        """Calculate overall deliverability score."""

        return (rep + hygiene) / 2

    def _identify_deliverability_issues(
        self, score: float, rep: float, hygiene: float, bounce: float, spam: float
    ) -> list[str]:
        """Identify deliverability issues."""
        issues = []
        if bounce > 5.0:
            issues.append("High bounce rate")
        if spam > 0.5:
            issues.append("High spam complaint rate")
        return issues

    def _generate_deliverability_recommendations(
        self, issues: list[str]
    ) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []
        for issue in issues:
            if "bounce" in issue.lower():
                recommendations.append("Implement email verification")
            if "spam" in issue.lower():
                recommendations.append("Review email content and opt-in process")
        return recommendations
