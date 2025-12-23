"""
Email Marketing Agent - Email Campaign Automation.

This agent specializes in email marketing campaign design, audience segmentation,
personalization, and performance optimization.

PRODUCTION-READY with real integrations:
- SendGrid API for email delivery and campaigns
- Contact management and list segmentation
- Real-time performance analytics

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

import logging
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field, EmailStr

from app.infrastructure.agents.base_agent import BaseAgent, AgentConfig
from app.infrastructure.email import SendGridClient, SendGridError
from app.core.config import settings

logger = logging.getLogger(__name__)


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
    cta_buttons: List[Dict[str, str]] = Field(
        default_factory=list, description="Call-to-action buttons"
    )
    personalization_tokens: List[str] = Field(
        default_factory=list, description="Personalization fields"
    )
    scheduled_send: Optional[datetime] = Field(
        default=None, description="Scheduled send time"
    )
    target_segments: List[str] = Field(
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
    filters: Dict[str, Any] = Field(..., description="Filter conditions")
    size: int = Field(..., ge=0, description="Segment size")
    characteristics: Dict[str, Any] = Field(
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
    personalization_data: Dict[str, Any] = Field(
        default_factory=dict, description="Personalization values"
    )
    recommended_products: List[Dict[str, Any]] = Field(
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
    issues: List[str] = Field(
        default_factory=list, description="Deliverability issues"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Improvement recommendations"
    )
    blacklist_status: List[Dict[str, str]] = Field(
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

    PRODUCTION-READY with SendGrid API integration for:
        - Real email delivery
        - Contact management
        - Campaign statistics
        - List management

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
        """Initialize Email Marketing Agent with SendGrid client."""
        super().__init__(config)

        self.campaigns: Dict[str, EmailCampaign] = {}
        self.segments: Dict[str, AudienceSegment] = {}
        self.performance_history: List[EmailPerformance] = []

        # Initialize SendGrid client
        self.sendgrid_client: Optional[SendGridClient] = None

    async def on_start(self) -> None:
        """Initialize SendGrid client."""
        await super().on_start()

        sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        if sendgrid_api_key:
            self.sendgrid_client = SendGridClient(
                api_key=sendgrid_api_key,
                from_email=getattr(settings, 'SENDGRID_FROM_EMAIL', 'noreply@studiocentos.it'),
                from_name=getattr(settings, 'SENDGRID_FROM_NAME', 'StudioCentos'),
            )
            logger.info("✅ SendGrid client initialized for Email Marketing Agent")
        else:
            logger.warning("⚠️ SendGrid API key not configured")

    async def design_campaign(
        self,
        campaign_type: EmailCampaignType,
        subject: str,
        goal: str,
        from_name: str = "Your Brand",
        from_email: str = "hello@yourbrand.com",
        content_guidelines: Optional[Dict[str, Any]] = None,
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
        filters: Dict[str, Any],
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
    # HELPER METHODS (Private) - PRODUCTION-READY with SendGrid
    # ========================================================================

    async def _generate_preview_text(self, subject: str, goal: str) -> str:
        """Generate email preview text using LLM."""
        prompt = f"""Generate a compelling email preview text (40-90 chars) for:
Subject: {subject}
Goal: {goal}

Preview text should complement the subject and encourage opens.
Return ONLY the preview text, no quotes or explanation."""

        try:
            response = await self.run(prompt)
            preview = response.data.strip().strip('"').strip("'")
            return preview[:90] if len(preview) > 90 else preview
        except Exception as e:
            logger.warning(f"LLM preview generation failed: {e}")
            return f"{subject} - Discover more inside"

    async def _generate_html_content(
        self, type_: EmailCampaignType, subject: str, goal: str, guidelines: Dict[str, Any]
    ) -> str:
        """Generate HTML email content using LLM."""
        prompt = f"""Generate a professional, responsive HTML email for:
Type: {type_.value}
Subject: {subject}
Goal: {goal}
Guidelines: {guidelines}

Requirements:
1. Mobile-responsive design
2. Include personalization tokens: {{{{first_name}}}}, {{{{company}}}}
3. Clear CTA button
4. Unsubscribe link placeholder
5. Professional, clean layout

Return ONLY valid HTML, no markdown or explanation."""

        try:
            response = await self.run(prompt)
            html = response.data.strip()
            # Ensure basic HTML structure
            if not html.startswith('<'):
                html = f"<html><body>{html}</body></html>"
            return html
        except Exception as e:
            logger.warning(f"LLM HTML generation failed: {e}")
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h1>Hello {{{{first_name}}}},</h1>
    <p>{subject}</p>
    <a href="{{{{cta_url}}}}" style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Learn More</a>
    <hr style="margin-top: 40px;">
    <p style="font-size: 12px; color: #666;">
        <a href="{{{{unsubscribe_url}}}}">Unsubscribe</a>
    </p>
</body>
</html>"""

    async def _generate_text_content(self, html: str) -> str:
        """Convert HTML to plain text."""
        import re
        # Remove script and style content
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Replace <br> and </p> with newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</h[1-6]>', '\n\n', text, flags=re.IGNORECASE)
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()

    def _extract_ctas(self, html: str) -> List[Dict[str, str]]:
        """Extract CTA buttons from HTML."""
        import re
        ctas = []
        # Find anchor tags that look like buttons (have button-like styling)
        button_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
        matches = re.findall(button_pattern, html, re.IGNORECASE)
        for url, text in matches:
            if any(kw in text.lower() for kw in ['learn', 'get', 'start', 'buy', 'shop', 'try', 'sign', 'register']):
                ctas.append({"url": url, "text": text.strip()})
        return ctas

    def _identify_tokens(self, html: str) -> List[str]:
        """Identify personalization tokens in template."""
        import re
        # Find {{token}} patterns
        pattern = r'\{\{(\w+)\}\}'
        tokens = list(set(re.findall(pattern, html)))
        return tokens

    async def _apply_segment_filters(
        self, criteria: SegmentCriteria, filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply segmentation filters to subscriber list using SendGrid."""
        if not self.sendgrid_client:
            logger.warning("SendGrid not configured, returning empty segment")
            return []

        try:
            # Get contacts from SendGrid
            contacts = await self.sendgrid_client.get_contacts()

            # Apply filters based on criteria
            filtered = []
            for contact in contacts:
                if criteria == SegmentCriteria.ENGAGEMENT:
                    # Filter by engagement metrics
                    min_opens = filters.get("min_opens", 0)
                    if contact.get("opens", 0) >= min_opens:
                        filtered.append(contact)
                elif criteria == SegmentCriteria.DEMOGRAPHICS:
                    # Filter by demographic fields
                    match = True
                    for key, value in filters.items():
                        if contact.get(key) != value:
                            match = False
                            break
                    if match:
                        filtered.append(contact)
                else:
                    # Default: include all
                    filtered.append(contact)

            return filtered
        except Exception as e:
            logger.error(f"Segment filter error: {e}")
            return []

    async def _analyze_segment(
        self, subscribers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze segment characteristics."""
        if not subscribers:
            return {}

        characteristics = {
            "total_count": len(subscribers),
            "has_first_name": sum(1 for s in subscribers if s.get("first_name")),
            "has_company": sum(1 for s in subscribers if s.get("company")),
            "avg_opens": 0.0,
            "avg_clicks": 0.0,
        }

        # Calculate engagement averages
        total_opens = sum(s.get("opens", 0) for s in subscribers)
        total_clicks = sum(s.get("clicks", 0) for s in subscribers)

        if len(subscribers) > 0:
            characteristics["avg_opens"] = total_opens / len(subscribers)
            characteristics["avg_clicks"] = total_clicks / len(subscribers)

        return characteristics

    def _calculate_engagement_score(
        self, subscribers: List[Dict[str, Any]]
    ) -> float:
        """Calculate average engagement score for segment."""
        if not subscribers:
            return 0.0

        scores = []
        for sub in subscribers:
            opens = sub.get("opens", 0)
            clicks = sub.get("clicks", 0)
            # Score: opens + clicks*2 (clicks are more valuable)
            score = min(100, opens * 5 + clicks * 10)
            scores.append(score)

        return sum(scores) / len(scores) if scores else 0.0

    async def _estimate_segment_value(
        self, subscribers: List[Dict[str, Any]]
    ) -> float:
        """Estimate segment lifetime value."""
        if not subscribers:
            return 0.0

        # Estimate based on engagement (more engaged = higher value)
        base_value = 10.0  # Base value per subscriber
        engagement_multiplier = self._calculate_engagement_score(subscribers) / 50

        return len(subscribers) * base_value * max(0.5, engagement_multiplier)

    async def _fetch_recipient_data(self, email: str) -> Dict[str, Any]:
        """Fetch recipient profile data from SendGrid."""
        if not self.sendgrid_client:
            return {"name": "Subscriber", "email": email}

        try:
            # Search for contact in SendGrid
            contacts = await self.sendgrid_client.search_contacts(email)
            if contacts:
                contact = contacts[0]
                return {
                    "name": f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip() or "Subscriber",
                    "first_name": contact.get("first_name", ""),
                    "last_name": contact.get("last_name", ""),
                    "email": email,
                    "company": contact.get("company", ""),
                    "custom_fields": contact.get("custom_fields", {}),
                }
        except Exception as e:
            logger.warning(f"Failed to fetch recipient data: {e}")

        return {"name": "Subscriber", "email": email}

    async def _personalize_subject(
        self, subject: str, data: Dict[str, Any]
    ) -> str:
        """Personalize subject line with recipient data."""
        personalized = subject
        for key, value in data.items():
            personalized = personalized.replace(f"{{{{{key}}}}}", str(value))
        return personalized

    async def _personalize_html(
        self, html: str, data: Dict[str, Any]
    ) -> str:
        """Personalize HTML content with recipient data."""
        personalized = html
        for key, value in data.items():
            personalized = personalized.replace(f"{{{{{key}}}}}", str(value))
        return personalized

    async def _personalize_text(
        self, text: str, data: Dict[str, Any]
    ) -> str:
        """Personalize text content with recipient data."""
        personalized = text
        for key, value in data.items():
            personalized = personalized.replace(f"{{{{{key}}}}}", str(value))
        return personalized

    async def _generate_recommendations(
        self, data: Dict[str, Any], type_: EmailCampaignType
    ) -> List[Dict[str, Any]]:
        """Generate product recommendations using LLM."""
        if type_ not in [EmailCampaignType.PROMOTIONAL, EmailCampaignType.ABANDONED_CART]:
            return []

        prompt = f"""Based on this customer profile, suggest 3 relevant products/services:
Customer: {data.get('name', 'Unknown')}
Company: {data.get('company', 'Unknown')}
Campaign Type: {type_.value}

Return JSON array with format:
[{{"name": "Product Name", "reason": "Why recommended", "priority": 1}}]"""

        try:
            response = await self.run(prompt)
            import json
            recommendations = json.loads(response.data)
            return recommendations[:3]
        except Exception:
            return []

    async def _fetch_engagement_history(self, email: str) -> List[Dict[str, Any]]:
        """Fetch recipient engagement history from SendGrid."""
        if not self.sendgrid_client:
            return []

        try:
            stats = await self.sendgrid_client.get_contact_activity(email)
            return stats
        except Exception as e:
            logger.warning(f"Failed to fetch engagement history: {e}")
            return []

    def _analyze_open_patterns(
        self, history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze when recipient opens emails."""
        if not history:
            return {"avg_open_rate": 20.0, "best_day": "Tuesday", "best_hour": 10}

        opens_by_day = {}
        opens_by_hour = {}
        total_opens = 0
        total_sent = len(history)

        for event in history:
            if event.get("event") == "open":
                total_opens += 1
                timestamp = event.get("timestamp")
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        day = dt.strftime("%A")
                        hour = dt.hour
                        opens_by_day[day] = opens_by_day.get(day, 0) + 1
                        opens_by_hour[hour] = opens_by_hour.get(hour, 0) + 1
                    except ValueError:
                        pass

        best_day = max(opens_by_day, key=opens_by_day.get) if opens_by_day else "Tuesday"
        best_hour = max(opens_by_hour, key=opens_by_hour.get) if opens_by_hour else 10

        return {
            "avg_open_rate": (total_opens / total_sent * 100) if total_sent > 0 else 20.0,
            "best_day": best_day,
            "best_hour": best_hour,
            "opens_by_day": opens_by_day,
            "opens_by_hour": opens_by_hour,
        }

    async def _detect_timezone(self, email: str) -> str:
        """Detect recipient timezone from profile or activity."""
        if not self.sendgrid_client:
            return "Europe/Rome"

        try:
            contacts = await self.sendgrid_client.search_contacts(email)
            if contacts and contacts[0].get("timezone"):
                return contacts[0]["timezone"]
        except Exception:
            pass

        return "Europe/Rome"

    def _calculate_optimal_time(
        self, patterns: Dict[str, Any]
    ) -> tuple:
        """Calculate optimal day and hour from patterns."""
        best_day = patterns.get("best_day", "Tuesday")
        best_hour = patterns.get("best_hour", 10)
        return (best_day, best_hour)

    def _get_next_occurrence(
        self, day: str, hour: int, timezone: str
    ) -> datetime:
        """Get next occurrence of day/hour."""
        day_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2,
            "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
        }

        now = datetime.utcnow()
        target_day = day_map.get(day, 1)
        days_ahead = target_day - now.weekday()

        if days_ahead <= 0:
            days_ahead += 7

        next_date = now + timedelta(days=days_ahead)
        return next_date.replace(hour=hour, minute=0, second=0, microsecond=0)

    def _calculate_confidence(self, patterns: Dict[str, Any]) -> float:
        """Calculate confidence in send time recommendation."""
        opens_by_day = patterns.get("opens_by_day", {})
        opens_by_hour = patterns.get("opens_by_hour", {})

        # More data points = higher confidence
        total_data_points = sum(opens_by_day.values()) + sum(opens_by_hour.values())

        if total_data_points < 5:
            return 40.0
        elif total_data_points < 20:
            return 60.0
        elif total_data_points < 50:
            return 75.0
        else:
            return 90.0

    async def _fetch_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Fetch campaign performance metrics from SendGrid."""
        if not self.sendgrid_client:
            logger.warning("SendGrid not configured, returning mock metrics")
            return {
                "sent": 0, "delivered": 0, "opens": 0, "unique_opens": 0,
                "clicks": 0, "unique_clicks": 0, "bounces": 0,
                "spam_reports": 0, "unsubscribes": 0, "conversions": 0, "revenue": 0.0,
            }

        try:
            stats = await self.sendgrid_client.get_campaign_stats(campaign_id)

            return {
                "sent": stats.get("requests", 0),
                "delivered": stats.get("delivered", 0),
                "opens": stats.get("opens", 0),
                "unique_opens": stats.get("unique_opens", 0),
                "clicks": stats.get("clicks", 0),
                "unique_clicks": stats.get("unique_clicks", 0),
                "bounces": stats.get("bounces", 0) + stats.get("bounce_drops", 0),
                "spam_reports": stats.get("spam_reports", 0),
                "unsubscribes": stats.get("unsubscribes", 0),
                "conversions": stats.get("conversions", 0),
                "revenue": stats.get("revenue", 0.0),
            }
        except Exception as e:
            logger.error(f"Failed to fetch campaign metrics: {e}")
            return {
                "sent": 0, "delivered": 0, "opens": 0, "unique_opens": 0,
                "clicks": 0, "unique_clicks": 0, "bounces": 0,
                "spam_reports": 0, "unsubscribes": 0, "conversions": 0, "revenue": 0.0,
            }

    async def _check_sender_reputation(self) -> float:
        """Check sender reputation score from SendGrid."""
        if not self.sendgrid_client:
            return 75.0

        try:
            # Get global stats to estimate reputation
            stats = await self.sendgrid_client.get_global_stats(days=30)

            total_sent = sum(s.get("requests", 0) for s in stats)
            total_bounces = sum(s.get("bounces", 0) for s in stats)
            total_spam = sum(s.get("spam_reports", 0) for s in stats)

            if total_sent == 0:
                return 80.0

            bounce_rate = (total_bounces / total_sent) * 100
            spam_rate = (total_spam / total_sent) * 100

            # Score: 100 - penalties
            score = 100 - (bounce_rate * 5) - (spam_rate * 20)
            return max(0, min(100, score))
        except Exception as e:
            logger.warning(f"Failed to check sender reputation: {e}")
            return 75.0

    async def _analyze_list_hygiene(self) -> float:
        """Analyze list quality from SendGrid."""
        if not self.sendgrid_client:
            return 80.0

        try:
            contacts = await self.sendgrid_client.get_contacts()

            if not contacts:
                return 100.0

            total = len(contacts)
            valid = sum(1 for c in contacts if c.get("email"))
            with_name = sum(1 for c in contacts if c.get("first_name"))

            # Score based on data completeness
            validity_score = (valid / total) * 50
            completeness_score = (with_name / total) * 50

            return validity_score + completeness_score
        except Exception as e:
            logger.warning(f"Failed to analyze list hygiene: {e}")
            return 75.0

    def _calculate_overall_engagement(self) -> float:
        """Calculate overall engagement rate from history."""
        if not self.performance_history:
            return 20.0

        recent = self.performance_history[-10:]  # Last 10 campaigns
        avg_open = sum(p.open_rate for p in recent) / len(recent)
        avg_click = sum(p.click_rate for p in recent) / len(recent)

        return (avg_open + avg_click * 2) / 3

    async def _get_bounce_rate(self) -> float:
        """Get recent bounce rate from SendGrid."""
        if not self.sendgrid_client:
            return 2.0

        try:
            stats = await self.sendgrid_client.get_global_stats(days=7)
            total_sent = sum(s.get("requests", 0) for s in stats)
            total_bounces = sum(s.get("bounces", 0) for s in stats)

            if total_sent == 0:
                return 0.0

            return (total_bounces / total_sent) * 100
        except Exception as e:
            logger.warning(f"Failed to get bounce rate: {e}")
            return 2.0

    async def _get_spam_rate(self) -> float:
        """Get spam complaint rate from SendGrid."""
        if not self.sendgrid_client:
            return 0.1

        try:
            stats = await self.sendgrid_client.get_global_stats(days=7)
            total_sent = sum(s.get("requests", 0) for s in stats)
            total_spam = sum(s.get("spam_reports", 0) for s in stats)

            if total_sent == 0:
                return 0.0

            return (total_spam / total_sent) * 100
        except Exception as e:
            logger.warning(f"Failed to get spam rate: {e}")
            return 0.1

    async def _check_blacklists(self) -> List[Dict[str, str]]:
        """Check if domain/IP is blacklisted."""
        # SendGrid handles this internally, but we can check suppressions
        if not self.sendgrid_client:
            return []

        try:
            # Get suppression lists
            suppressions = await self.sendgrid_client.get_suppressions()
            return [{"type": "suppression", "count": str(len(suppressions))}]
        except Exception:
            return []

    def _calculate_deliverability_score(
        self, rep: float, hygiene: float, eng: float, bounce: float, spam: float
    ) -> float:
        """Calculate overall deliverability score."""
        # Weighted calculation
        score = (
            rep * 0.3 +
            hygiene * 0.2 +
            eng * 0.2 +
            (100 - bounce * 10) * 0.15 +
            (100 - spam * 50) * 0.15
        )
        return max(0, min(100, score))

    def _identify_deliverability_issues(
        self, score: float, rep: float, hygiene: float, bounce: float, spam: float
    ) -> List[str]:
        """Identify deliverability issues."""
        issues = []

        if score < 70:
            issues.append("Overall deliverability score is low")
        if rep < 70:
            issues.append("Sender reputation needs improvement")
        if hygiene < 70:
            issues.append("List hygiene needs attention")
        if bounce > 3.0:
            issues.append("High bounce rate - clean your list")
        if bounce > 5.0:
            issues.append("Critical: Bounce rate exceeds 5%")
        if spam > 0.1:
            issues.append("Spam complaint rate needs monitoring")
        if spam > 0.5:
            issues.append("Critical: High spam complaint rate")

        return issues

    def _generate_deliverability_recommendations(
        self, issues: List[str]
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        for issue in issues:
            issue_lower = issue.lower()
            if "bounce" in issue_lower:
                recommendations.append("Implement double opt-in for new subscribers")
                recommendations.append("Use email verification service before adding contacts")
                recommendations.append("Remove hard bounces immediately from your list")
            if "spam" in issue_lower:
                recommendations.append("Review email content for spam trigger words")
                recommendations.append("Ensure clear unsubscribe link in all emails")
                recommendations.append("Verify opt-in process compliance")
            if "reputation" in issue_lower:
                recommendations.append("Warm up new sending domains gradually")
                recommendations.append("Maintain consistent sending volumes")
                recommendations.append("Authenticate with SPF, DKIM, and DMARC")
            if "hygiene" in issue_lower:
                recommendations.append("Run re-engagement campaign for inactive subscribers")
                recommendations.append("Remove contacts who haven't engaged in 12+ months")
                recommendations.append("Validate email addresses periodically")

        return list(set(recommendations))  # Remove duplicates
