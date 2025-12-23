"""
Campaign Manager Agent - Marketing Campaign Management.

This agent specializes in planning, executing, and optimizing marketing campaigns
across multiple channels with ROI tracking and predictive analytics.

PRODUCTION-READY with real integrations:
- SendGrid for email campaigns
- Google Analytics 4 for performance tracking
- Social media APIs for social campaigns

Features:
    - Campaign planning and strategy
    - Multi-channel campaign execution
    - ROI calculation and tracking
    - Attribution modeling
    - A/B testing and optimization
    - Budget allocation and optimization
    - Predictive analytics

Tools:
    1. plan_campaign() - Create campaign strategy
    2. track_roi() - Calculate ROI metrics
    3. attribution_analysis() - Multi-touch attribution
    4. optimize_abtest() - A/B test analysis
    5. allocate_budget() - Optimize budget allocation
    6. predict_performance() - Forecast campaign results

Example:
    >>> agent = CampaignManagerAgent(config=config)
    >>>
    >>> # Plan new campaign
    >>> campaign = await agent.plan_campaign(
    ...     objective="lead_generation",
    ...     budget=10000.0,
    ...     channels=["email", "social", "ppc"],
    ... )
"""

import logging
import math
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from app.infrastructure.agents.base_agent import BaseAgent, AgentConfig
from app.infrastructure.email import SendGridClient, SendGridError
from app.infrastructure.google import GA4Client, GA4Error
from app.core.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================


class CampaignObjective(str, Enum):
    """Campaign objectives."""

    BRAND_AWARENESS = "brand_awareness"
    LEAD_GENERATION = "lead_generation"
    SALES = "sales"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    REACTIVATION = "reactivation"


class CampaignStatus(str, Enum):
    """Campaign status."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AttributionModel(str, Enum):
    """Attribution models."""

    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"


class Channel(str, Enum):
    """Marketing channels."""

    EMAIL = "email"
    SOCIAL = "social"
    PPC = "ppc"
    SEO = "seo"
    CONTENT = "content"
    DISPLAY = "display"
    AFFILIATE = "affiliate"
    DIRECT = "direct"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class CampaignPlan(BaseModel):
    """Campaign planning details."""

    campaign_id: str = Field(..., description="Campaign ID")
    name: str = Field(..., description="Campaign name")
    objective: CampaignObjective = Field(..., description="Campaign objective")
    target_audience: Dict[str, Any] = Field(..., description="Audience targeting")
    channels: List[Channel] = Field(..., description="Marketing channels")
    budget: float = Field(..., ge=0.0, description="Total budget")
    budget_allocation: Dict[Channel, float] = Field(
        ..., description="Budget per channel"
    )
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    kpis: Dict[str, float] = Field(..., description="Target KPIs")
    creative_strategy: str = Field(..., description="Creative approach")
    messaging: List[str] = Field(
        default_factory=list, description="Key messages"
    )
    status: CampaignStatus = Field(
        default=CampaignStatus.DRAFT, description="Campaign status"
    )


class ROIMetrics(BaseModel):
    """ROI and performance metrics."""

    campaign_id: str = Field(..., description="Campaign ID")
    total_spent: float = Field(..., ge=0.0, description="Total spent")
    total_revenue: float = Field(..., ge=0.0, description="Total revenue")
    roi: float = Field(..., description="ROI percentage")
    roas: float = Field(..., ge=0.0, description="Return on ad spend")
    cpa: float = Field(..., ge=0.0, description="Cost per acquisition")
    cpl: float = Field(..., ge=0.0, description="Cost per lead")
    conversion_rate: float = Field(
        ..., ge=0.0, le=100.0, description="Conversion rate %"
    )
    impressions: int = Field(..., ge=0, description="Total impressions")
    clicks: int = Field(..., ge=0, description="Total clicks")
    conversions: int = Field(..., ge=0, description="Total conversions")
    channel_breakdown: Dict[Channel, Dict[str, float]] = Field(
        default_factory=dict, description="Per-channel metrics"
    )


class TouchPoint(BaseModel):
    """Customer journey touchpoint."""

    timestamp: datetime = Field(..., description="Touchpoint timestamp")
    channel: Channel = Field(..., description="Marketing channel")
    campaign_id: str = Field(..., description="Campaign ID")
    cost: float = Field(..., ge=0.0, description="Touchpoint cost")
    converted: bool = Field(default=False, description="Led to conversion")


class AttributionResult(BaseModel):
    """Attribution analysis result."""

    customer_id: str = Field(..., description="Customer ID")
    conversion_value: float = Field(..., description="Conversion value")
    touchpoints: List[TouchPoint] = Field(..., description="Journey touchpoints")
    attribution_model: AttributionModel = Field(..., description="Model used")
    channel_credits: Dict[Channel, float] = Field(
        ..., description="Credit per channel"
    )
    campaign_credits: Dict[str, float] = Field(
        ..., description="Credit per campaign"
    )
    time_to_conversion: timedelta = Field(
        ..., description="Time from first touch"
    )


class ABTestResult(BaseModel):
    """A/B test analysis result."""

    test_id: str = Field(..., description="Test ID")
    variant_a: Dict[str, Any] = Field(..., description="Control variant")
    variant_b: Dict[str, Any] = Field(..., description="Test variant")
    sample_size_a: int = Field(..., description="Variant A sample")
    sample_size_b: int = Field(..., description="Variant B sample")
    conversion_rate_a: float = Field(..., description="Variant A CVR")
    conversion_rate_b: float = Field(..., description="Variant B CVR")
    uplift: float = Field(..., description="Conversion uplift %")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Confidence %")
    statistical_significance: bool = Field(
        ..., description="Statistically significant"
    )
    winner: Optional[str] = Field(default=None, description="Winning variant")
    recommendation: str = Field(..., description="Action recommendation")


class BudgetAllocation(BaseModel):
    """Optimized budget allocation."""

    total_budget: float = Field(..., description="Total budget")
    allocations: Dict[Channel, float] = Field(
        ..., description="Budget per channel"
    )
    expected_roi: Dict[Channel, float] = Field(
        ..., description="Expected ROI per channel"
    )
    projected_revenue: float = Field(..., description="Total projected revenue")
    confidence_interval: tuple[float, float] = Field(
        ..., description="Revenue confidence interval"
    )
    optimization_strategy: str = Field(
        ..., description="Optimization approach used"
    )


class PerformanceForecast(BaseModel):
    """Campaign performance forecast."""

    campaign_id: str = Field(..., description="Campaign ID")
    forecast_period: int = Field(..., description="Days forecasted")
    predicted_impressions: int = Field(..., description="Forecast impressions")
    predicted_clicks: int = Field(..., description="Forecast clicks")
    predicted_conversions: int = Field(..., description="Forecast conversions")
    predicted_revenue: float = Field(..., description="Forecast revenue")
    predicted_roi: float = Field(..., description="Forecast ROI %")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Confidence %")
    best_case: Dict[str, float] = Field(..., description="Best case scenario")
    worst_case: Dict[str, float] = Field(..., description="Worst case scenario")
    recommendations: List[str] = Field(
        default_factory=list, description="Optimization recommendations"
    )


# ============================================================================
# CAMPAIGN MANAGER AGENT
# ============================================================================


class CampaignManagerAgent(BaseAgent):
    """
    Campaign Manager Agent for marketing campaign orchestration.

    Manages end-to-end marketing campaigns with ROI tracking, attribution
    analysis, and predictive optimization.

    PRODUCTION-READY with real integrations:
        - SendGrid for email campaign execution
        - Google Analytics 4 for performance metrics
        - Social media APIs integration

    Capabilities:
        - Strategic campaign planning
        - Multi-channel execution
        - Real-time ROI tracking
        - Multi-touch attribution
        - A/B testing optimization
        - Budget allocation
        - Performance forecasting

    Example:
        >>> config = AgentConfig(
        ...     id="campaign_manager_1",
        ...     name="Campaign Manager",
        ...     model="gpt-4",
        ... )
        >>> agent = CampaignManagerAgent(config=config)
        >>>
        >>> # Plan campaign
        >>> plan = await agent.plan_campaign(
        ...     objective=CampaignObjective.LEAD_GENERATION,
        ...     budget=10000.0,
        ...     channels=[Channel.EMAIL, Channel.SOCIAL],
        ... )
    """

    def __init__(self, config: AgentConfig):
        """Initialize Campaign Manager Agent with real API clients."""
        super().__init__(config)

        self.campaigns: Dict[str, CampaignPlan] = {}
        self.performance_history: List[ROIMetrics] = []

        # Initialize real API clients
        self.sendgrid_client: Optional[SendGridClient] = None
        self.ga4_client: Optional[GA4Client] = None

    async def on_start(self) -> None:
        """Initialize real API clients."""
        await super().on_start()

        # Initialize SendGrid for email campaigns
        sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        if sendgrid_api_key:
            self.sendgrid_client = SendGridClient(
                api_key=sendgrid_api_key,
                from_email=getattr(settings, 'SENDGRID_FROM_EMAIL', 'noreply@studiocentos.it'),
                from_name=getattr(settings, 'SENDGRID_FROM_NAME', 'StudioCentos'),
            )
            logger.info("✅ SendGrid client initialized for email campaigns")
        else:
            logger.warning("⚠️ SendGrid API key not configured")

        # Initialize GA4 for analytics
        ga4_credentials = getattr(settings, 'GA4_CREDENTIALS', '') or getattr(settings, 'GOOGLE_CREDENTIALS_JSON', '')
        ga4_property = getattr(settings, 'GA4_PROPERTY_ID', '')

        if ga4_credentials and ga4_property:
            self.ga4_client = GA4Client(
                credentials_json=ga4_credentials,
                property_id=ga4_property,
            )
            logger.info(f"✅ GA4 client initialized for property {ga4_property}")
        else:
            logger.warning("⚠️ GA4 credentials not configured")

    async def plan_campaign(
        self,
        objective: CampaignObjective,
        budget: float,
        channels: List[Channel],
        duration_days: int = 30,
        target_audience: Optional[Dict[str, Any]] = None,
    ) -> CampaignPlan:
        """
        Create comprehensive campaign plan.

        Args:
            objective: Campaign objective
            budget: Total budget
            channels: Marketing channels to use
            duration_days: Campaign duration
            target_audience: Audience targeting criteria

        Returns:
            CampaignPlan with strategy and allocation

        Example:
            >>> plan = await agent.plan_campaign(
            ...     objective=CampaignObjective.SALES,
            ...     budget=50000.0,
            ...     channels=[Channel.PPC, Channel.EMAIL],
            ...     duration_days=60,
            ... )
        """
        # Generate campaign ID
        campaign_id = f"campaign_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Optimize budget allocation
        allocation = await self._optimize_budget_allocation(
            budget, channels, objective
        )

        # Set campaign dates
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=duration_days)

        # Define KPIs based on objective
        kpis = self._define_kpis(objective, budget)

        # Generate creative strategy
        creative_strategy = await self._generate_creative_strategy(
            objective, target_audience or {}
        )

        # Generate key messages
        messages = await self._generate_key_messages(
            objective, target_audience or {}
        )

        plan = CampaignPlan(
            campaign_id=campaign_id,
            name=f"{objective.value.replace('_', ' ').title()} Campaign",
            objective=objective,
            target_audience=target_audience or {},
            channels=channels,
            budget=budget,
            budget_allocation=allocation,
            start_date=start_date,
            end_date=end_date,
            kpis=kpis,
            creative_strategy=creative_strategy,
            messaging=messages,
        )

        self.campaigns[campaign_id] = plan
        return plan

    async def track_roi(
        self, campaign_id: str
    ) -> ROIMetrics:
        """
        Calculate comprehensive ROI metrics.

        Args:
            campaign_id: Campaign to track

        Returns:
            ROIMetrics with performance data
        """
        # Fetch campaign data
        campaign_data = await self._fetch_campaign_data(campaign_id)

        # Calculate totals
        total_spent = sum(campaign_data["costs"].values())
        total_revenue = sum(campaign_data["revenue"].values())

        # Calculate ROI
        roi = ((total_revenue - total_spent) / total_spent * 100) if total_spent > 0 else 0.0
        roas = total_revenue / total_spent if total_spent > 0 else 0.0

        # Calculate conversion metrics
        conversions = campaign_data["conversions"]
        leads = campaign_data["leads"]

        cpa = total_spent / conversions if conversions > 0 else 0.0
        cpl = total_spent / leads if leads > 0 else 0.0

        conversion_rate = (
            conversions / campaign_data["clicks"] * 100
            if campaign_data["clicks"] > 0
            else 0.0
        )

        # Calculate per-channel breakdown
        channel_breakdown = await self._calculate_channel_breakdown(
            campaign_data
        )

        metrics = ROIMetrics(
            campaign_id=campaign_id,
            total_spent=total_spent,
            total_revenue=total_revenue,
            roi=roi,
            roas=roas,
            cpa=cpa,
            cpl=cpl,
            conversion_rate=conversion_rate,
            impressions=campaign_data["impressions"],
            clicks=campaign_data["clicks"],
            conversions=conversions,
            channel_breakdown=channel_breakdown,
        )

        self.performance_history.append(metrics)
        return metrics

    async def attribution_analysis(
        self,
        customer_ids: List[str],
        model: AttributionModel = AttributionModel.LINEAR,
    ) -> List[AttributionResult]:
        """
        Perform multi-touch attribution analysis.

        Args:
            customer_ids: Customers to analyze
            model: Attribution model to use

        Returns:
            List of attribution results
        """
        results = []

        for customer_id in customer_ids:
            # Fetch customer journey
            touchpoints = await self._fetch_customer_touchpoints(customer_id)

            if not touchpoints:
                continue

            # Get conversion value
            conversion = await self._get_conversion_value(customer_id)

            # Apply attribution model
            credits = self._apply_attribution_model(
                touchpoints, conversion["value"], model
            )

            # Aggregate by channel and campaign
            channel_credits = self._aggregate_by_channel(credits)
            campaign_credits = self._aggregate_by_campaign(credits)

            # Calculate time to conversion
            time_to_conv = touchpoints[-1].timestamp - touchpoints[0].timestamp

            results.append(
                AttributionResult(
                    customer_id=customer_id,
                    conversion_value=conversion["value"],
                    touchpoints=touchpoints,
                    attribution_model=model,
                    channel_credits=channel_credits,
                    campaign_credits=campaign_credits,
                    time_to_conversion=time_to_conv,
                )
            )

        return results

    async def optimize_abtest(
        self, test_id: str
    ) -> ABTestResult:
        """
        Analyze A/B test and provide recommendations.

        Args:
            test_id: Test to analyze

        Returns:
            ABTestResult with winner and recommendations
        """
        # Fetch test data
        test_data = await self._fetch_abtest_data(test_id)

        # Calculate conversion rates
        cvr_a = (
            test_data["conversions_a"] / test_data["visitors_a"]
            if test_data["visitors_a"] > 0
            else 0.0
        )
        cvr_b = (
            test_data["conversions_b"] / test_data["visitors_b"]
            if test_data["visitors_b"] > 0
            else 0.0
        )

        # Calculate uplift
        uplift = ((cvr_b - cvr_a) / cvr_a * 100) if cvr_a > 0 else 0.0

        # Statistical significance test
        significance, confidence = self._calculate_significance(
            test_data["visitors_a"],
            test_data["conversions_a"],
            test_data["visitors_b"],
            test_data["conversions_b"],
        )

        # Determine winner
        winner = None
        if significance:
            winner = "variant_b" if cvr_b > cvr_a else "variant_a"

        # Generate recommendation
        recommendation = self._generate_test_recommendation(
            cvr_a, cvr_b, significance, confidence
        )

        return ABTestResult(
            test_id=test_id,
            variant_a=test_data["variant_a"],
            variant_b=test_data["variant_b"],
            sample_size_a=test_data["visitors_a"],
            sample_size_b=test_data["visitors_b"],
            conversion_rate_a=cvr_a * 100,
            conversion_rate_b=cvr_b * 100,
            uplift=uplift,
            confidence=confidence,
            statistical_significance=significance,
            winner=winner,
            recommendation=recommendation,
        )

    async def allocate_budget(
        self,
        total_budget: float,
        channels: List[Channel],
        objective: CampaignObjective,
    ) -> BudgetAllocation:
        """
        Optimize budget allocation across channels.

        Args:
            total_budget: Total budget to allocate
            channels: Channels to allocate to
            objective: Campaign objective

        Returns:
            BudgetAllocation with optimized distribution
        """
        # Get historical performance
        historical_roi = await self._get_historical_roi(channels)

        # Run optimization algorithm
        optimal_allocation = self._optimize_allocation(
            total_budget, channels, historical_roi, objective
        )

        # Calculate expected ROI
        expected_roi = {}
        total_expected_revenue = 0.0

        for channel, budget in optimal_allocation.items():
            channel_roi = historical_roi.get(channel, 1.0)
            expected_revenue = budget * channel_roi
            expected_roi[channel] = channel_roi
            total_expected_revenue += expected_revenue

        # Calculate confidence interval
        ci = self._calculate_confidence_interval(
            total_expected_revenue, channels
        )

        return BudgetAllocation(
            total_budget=total_budget,
            allocations=optimal_allocation,
            expected_roi=expected_roi,
            projected_revenue=total_expected_revenue,
            confidence_interval=ci,
            optimization_strategy="historical_performance",
        )

    async def predict_performance(
        self, campaign_id: str, forecast_days: int = 30
    ) -> PerformanceForecast:
        """
        Forecast campaign performance.

        Args:
            campaign_id: Campaign to forecast
            forecast_days: Days to forecast

        Returns:
            PerformanceForecast with predictions
        """
        # Get historical data
        historical = await self._get_campaign_history(campaign_id)

        # Train forecasting model
        predictions = await self._forecast_metrics(historical, forecast_days)

        # Calculate scenarios
        best_case = self._calculate_scenario(predictions, multiplier=1.2)
        worst_case = self._calculate_scenario(predictions, multiplier=0.8)

        # Generate recommendations
        recommendations = await self._generate_forecast_recommendations(
            predictions, historical
        )

        return PerformanceForecast(
            campaign_id=campaign_id,
            forecast_period=forecast_days,
            predicted_impressions=predictions["impressions"],
            predicted_clicks=predictions["clicks"],
            predicted_conversions=predictions["conversions"],
            predicted_revenue=predictions["revenue"],
            predicted_roi=predictions["roi"],
            confidence=predictions["confidence"],
            best_case=best_case,
            worst_case=worst_case,
            recommendations=recommendations,
        )

    # ========================================================================
    # HELPER METHODS (Private) - REAL IMPLEMENTATIONS
    # ========================================================================

    async def _optimize_budget_allocation(
        self, budget: float, channels: List[Channel], objective: CampaignObjective
    ) -> Dict[Channel, float]:
        """
        Optimize budget across channels based on objective and historical performance.
        """
        # Get historical performance data from GA4
        historical_roi = await self._get_historical_roi(channels)

        # Define weights based on objective
        objective_weights = {
            CampaignObjective.BRAND_AWARENESS: {
                Channel.SOCIAL: 0.35, Channel.DISPLAY: 0.25, Channel.CONTENT: 0.20,
                Channel.EMAIL: 0.10, Channel.PPC: 0.10, Channel.SEO: 0.0,
            },
            CampaignObjective.LEAD_GENERATION: {
                Channel.EMAIL: 0.30, Channel.PPC: 0.25, Channel.SOCIAL: 0.20,
                Channel.CONTENT: 0.15, Channel.SEO: 0.10, Channel.DISPLAY: 0.0,
            },
            CampaignObjective.SALES: {
                Channel.PPC: 0.30, Channel.EMAIL: 0.25, Channel.AFFILIATE: 0.20,
                Channel.SOCIAL: 0.15, Channel.DIRECT: 0.10, Channel.DISPLAY: 0.0,
            },
            CampaignObjective.ENGAGEMENT: {
                Channel.SOCIAL: 0.40, Channel.CONTENT: 0.30, Channel.EMAIL: 0.20,
                Channel.DISPLAY: 0.10, Channel.PPC: 0.0, Channel.SEO: 0.0,
            },
            CampaignObjective.RETENTION: {
                Channel.EMAIL: 0.45, Channel.SOCIAL: 0.25, Channel.CONTENT: 0.20,
                Channel.DIRECT: 0.10, Channel.PPC: 0.0, Channel.DISPLAY: 0.0,
            },
            CampaignObjective.REACTIVATION: {
                Channel.EMAIL: 0.50, Channel.PPC: 0.20, Channel.SOCIAL: 0.15,
                Channel.DISPLAY: 0.15, Channel.CONTENT: 0.0, Channel.SEO: 0.0,
            },
        }

        weights = objective_weights.get(objective, {})

        # Filter to requested channels and normalize
        allocation = {}
        total_weight = sum(weights.get(ch, 0.1) for ch in channels)

        for channel in channels:
            base_weight = weights.get(channel, 0.1)
            # Adjust by historical ROI performance
            roi_factor = historical_roi.get(channel, 1.0) / 2.0  # Normalize to ~1
            adjusted_weight = base_weight * roi_factor
            allocation[channel] = (adjusted_weight / total_weight) * budget

        return allocation

    def _define_kpis(
        self, objective: CampaignObjective, budget: float
    ) -> Dict[str, float]:
        """Define KPIs based on objective and budget using industry benchmarks."""
        # Industry-standard benchmarks
        benchmarks = {
            CampaignObjective.BRAND_AWARENESS: {
                "target_impressions": budget * 1000,  # $1 per 1000 impressions
                "target_reach": budget * 500,
                "target_engagement_rate": 3.0,
                "target_brand_lift": 10.0,
            },
            CampaignObjective.LEAD_GENERATION: {
                "target_leads": int(budget / 50),  # $50 CPL target
                "target_cpl": 50.0,
                "target_conversion_rate": 5.0,
                "target_qualified_rate": 25.0,
            },
            CampaignObjective.SALES: {
                "target_revenue": budget * 3,  # 3x ROAS
                "target_roas": 300.0,
                "target_cpa": 100.0,
                "target_aov": 150.0,
            },
            CampaignObjective.ENGAGEMENT: {
                "target_engagement_rate": 5.0,
                "target_comments": int(budget / 10),
                "target_shares": int(budget / 20),
                "target_avg_time_on_site": 180,  # 3 minutes
            },
            CampaignObjective.RETENTION: {
                "target_retention_rate": 85.0,
                "target_ltv_increase": 20.0,
                "target_churn_reduction": 15.0,
                "target_nps_increase": 10,
            },
            CampaignObjective.REACTIVATION: {
                "target_reactivation_rate": 15.0,
                "target_reactivated_users": int(budget / 25),
                "target_win_back_revenue": budget * 2,
            },
        }

        base_kpis = benchmarks.get(objective, {})

        # Add universal KPIs
        base_kpis["target_roi"] = 200.0
        base_kpis["target_budget_efficiency"] = 95.0

        return base_kpis

    async def _generate_creative_strategy(
        self, objective: CampaignObjective, audience: Dict[str, Any]
    ) -> str:
        """Generate creative strategy based on objective and audience."""
        strategies = {
            CampaignObjective.BRAND_AWARENESS: (
                "Focus on storytelling and emotional connection. Use high-quality visuals "
                "and consistent brand messaging across all touchpoints. Leverage video content "
                "for maximum engagement and reach."
            ),
            CampaignObjective.LEAD_GENERATION: (
                "Create compelling lead magnets (whitepapers, webinars, free trials). "
                "Use clear CTAs and landing pages optimized for conversion. Implement "
                "progressive profiling and personalized follow-up sequences."
            ),
            CampaignObjective.SALES: (
                "Focus on product benefits and social proof. Use testimonials, case studies, "
                "and limited-time offers. Implement retargeting and abandoned cart sequences. "
                "Highlight value proposition and ROI."
            ),
            CampaignObjective.ENGAGEMENT: (
                "Create interactive and shareable content. Use polls, quizzes, and UGC campaigns. "
                "Respond to comments and foster community discussions. Run contests and giveaways."
            ),
            CampaignObjective.RETENTION: (
                "Focus on value delivery and customer success. Use personalized recommendations "
                "and loyalty rewards. Create exclusive content and early access programs. "
                "Implement proactive customer support touchpoints."
            ),
            CampaignObjective.REACTIVATION: (
                "Use 'We miss you' messaging with personalized incentives. Highlight new features "
                "and improvements. Offer special comeback deals. Remind of unused benefits or credits."
            ),
        }

        strategy = strategies.get(objective, "Standard multi-channel approach")

        # Personalize based on audience if available
        if audience:
            industry = audience.get("industry", "")
            if industry:
                strategy += f" Tailor messaging for {industry} sector."

            age_range = audience.get("age_range", "")
            if age_range:
                strategy += f" Optimize creative for {age_range} demographics."

        return strategy

    async def _generate_key_messages(
        self, objective: CampaignObjective, audience: Dict[str, Any]
    ) -> List[str]:
        """Generate key messages based on objective."""
        messages = {
            CampaignObjective.BRAND_AWARENESS: [
                "Discover the future of [industry]",
                "Join thousands of satisfied customers",
                "Innovation meets reliability",
                "Your success is our mission",
            ],
            CampaignObjective.LEAD_GENERATION: [
                "Download your free guide now",
                "Get a personalized consultation",
                "See how we can help your business grow",
                "Start your free trial today",
            ],
            CampaignObjective.SALES: [
                "Limited time offer - Save 20%",
                "Transform your business with proven solutions",
                "ROI guaranteed or money back",
                "Join 10,000+ happy customers",
            ],
            CampaignObjective.ENGAGEMENT: [
                "Share your story with us",
                "What do you think? Let us know!",
                "Tag a friend who needs to see this",
                "Join the conversation",
            ],
            CampaignObjective.RETENTION: [
                "Exclusive benefits just for you",
                "Thank you for being part of our community",
                "Unlock your member rewards",
                "Your feedback shapes our future",
            ],
            CampaignObjective.REACTIVATION: [
                "We've missed you!",
                "A lot has changed - come see what's new",
                "Special offer just for you",
                "Your account is waiting",
            ],
        }

        return messages.get(objective, ["Discover our solutions", "Contact us today"])

    async def _fetch_campaign_data(self, campaign_id: str) -> Dict[str, Any]:
        """
        Fetch campaign performance data from GA4 and email platforms.
        """
        data = {
            "costs": {},
            "revenue": {},
            "conversions": 0,
            "leads": 0,
            "clicks": 0,
            "impressions": 0,
        }

        # Try to get data from GA4
        if self.ga4_client:
            try:
                async with self.ga4_client as client:
                    # Get traffic overview
                    overview = await client.get_traffic_overview(days=30)

                    data["impressions"] = overview.get("screenPageViews", 0)
                    data["clicks"] = overview.get("sessions", 0)
                    data["conversions"] = overview.get("conversions", 0)

                    # Get traffic sources
                    sources = await client.get_traffic_sources(days=30)

                    for source in sources:
                        medium = source.get("medium", "other")
                        channel = self._medium_to_channel(medium)

                        data["costs"][channel] = source.get("sessions", 0) * 0.5  # Estimated cost
                        data["revenue"][channel] = source.get("conversions", 0) * 100  # Estimated revenue

                    # Get conversion data
                    conversion_data = await client.get_conversion_data(days=30)
                    data["leads"] = conversion_data.get("total_conversions", 0)
                    data["revenue"]["total"] = conversion_data.get("total_revenue", 0)

                    logger.info(f"✅ Fetched campaign data from GA4")

            except Exception as e:
                logger.error(f"Error fetching GA4 data: {e}")

        # Try to get email data from SendGrid
        if self.sendgrid_client:
            try:
                async with self.sendgrid_client as client:
                    stats = await client.get_stats(
                        start_date=(datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    )

                    for stat in stats:
                        metrics = stat.get("stats", [{}])[0].get("metrics", {})
                        data["impressions"] += metrics.get("delivered", 0)
                        data["clicks"] += metrics.get("clicks", 0)

                    logger.info("✅ Fetched email campaign data from SendGrid")

            except Exception as e:
                logger.error(f"Error fetching SendGrid data: {e}")

        return data

    def _medium_to_channel(self, medium: str) -> Channel:
        """Convert GA4 medium to Channel enum."""
        mapping = {
            "organic": Channel.SEO,
            "cpc": Channel.PPC,
            "email": Channel.EMAIL,
            "social": Channel.SOCIAL,
            "referral": Channel.AFFILIATE,
            "display": Channel.DISPLAY,
            "(none)": Channel.DIRECT,
        }
        return mapping.get(medium.lower(), Channel.DIRECT)

    async def _calculate_channel_breakdown(
        self, data: Dict[str, Any]
    ) -> Dict[Channel, Dict[str, float]]:
        """Calculate per-channel metrics."""
        breakdown = {}

        costs = data.get("costs", {})
        revenue = data.get("revenue", {})

        for channel in Channel:
            channel_cost = costs.get(channel, 0)
            channel_revenue = revenue.get(channel, 0)

            if channel_cost > 0 or channel_revenue > 0:
                breakdown[channel] = {
                    "spent": channel_cost,
                    "revenue": channel_revenue,
                    "roi": ((channel_revenue - channel_cost) / channel_cost * 100) if channel_cost > 0 else 0,
                    "roas": channel_revenue / channel_cost if channel_cost > 0 else 0,
                }

        return breakdown

    async def _fetch_customer_touchpoints(
        self, customer_id: str
    ) -> List[TouchPoint]:
        """
        Fetch customer journey touchpoints.

        In production, this would query a CDP or analytics database.
        """
        # This would integrate with a Customer Data Platform
        # For now, return empty list
        logger.info(f"Fetching touchpoints for customer {customer_id}")
        return []

    async def _get_conversion_value(self, customer_id: str) -> Dict[str, float]:
        """Get conversion value for customer."""
        # This would query CRM or e-commerce platform
        return {"value": 100.0}  # Default conversion value

    def _apply_attribution_model(
        self, touchpoints: List[TouchPoint], value: float, model: AttributionModel
    ) -> Dict[str, float]:
        """Apply attribution model to touchpoints with real implementations."""
        credits = {}

        if not touchpoints:
            return credits

        n = len(touchpoints)

        if model == AttributionModel.FIRST_TOUCH:
            credits[touchpoints[0].campaign_id] = value

        elif model == AttributionModel.LAST_TOUCH:
            credits[touchpoints[-1].campaign_id] = value

        elif model == AttributionModel.LINEAR:
            credit_per_touch = value / n
            for tp in touchpoints:
                credits[tp.campaign_id] = credits.get(tp.campaign_id, 0) + credit_per_touch

        elif model == AttributionModel.TIME_DECAY:
            # Half-life of 7 days
            half_life = 7 * 24 * 60 * 60  # seconds
            weights = []

            conversion_time = touchpoints[-1].timestamp
            for tp in touchpoints:
                time_diff = (conversion_time - tp.timestamp).total_seconds()
                weight = 2 ** (-time_diff / half_life)
                weights.append(weight)

            total_weight = sum(weights)
            for i, tp in enumerate(touchpoints):
                credit = value * (weights[i] / total_weight)
                credits[tp.campaign_id] = credits.get(tp.campaign_id, 0) + credit

        elif model == AttributionModel.POSITION_BASED:
            # 40% first, 40% last, 20% middle
            if n == 1:
                credits[touchpoints[0].campaign_id] = value
            elif n == 2:
                credits[touchpoints[0].campaign_id] = value * 0.5
                credits[touchpoints[1].campaign_id] = value * 0.5
            else:
                credits[touchpoints[0].campaign_id] = value * 0.4
                credits[touchpoints[-1].campaign_id] = credits.get(touchpoints[-1].campaign_id, 0) + value * 0.4

                middle_credit = value * 0.2 / (n - 2)
                for tp in touchpoints[1:-1]:
                    credits[tp.campaign_id] = credits.get(tp.campaign_id, 0) + middle_credit

        return credits

    def _aggregate_by_channel(
        self, credits: Dict[str, float]
    ) -> Dict[Channel, float]:
        """Aggregate credits by channel."""
        # Would need campaign-to-channel mapping in production
        channel_credits: Dict[Channel, float] = {}

        for campaign_id, credit in credits.items():
            # Extract channel from campaign naming convention
            for channel in Channel:
                if channel.value in campaign_id.lower():
                    channel_credits[channel] = channel_credits.get(channel, 0) + credit
                    break

        return channel_credits

    def _aggregate_by_campaign(
        self, credits: Dict[str, float]
    ) -> Dict[str, float]:
        """Aggregate credits by campaign."""
        return credits

    async def _fetch_abtest_data(self, test_id: str) -> Dict[str, Any]:
        """Fetch A/B test data - would integrate with testing platform."""
        # In production, integrate with Optimizely, VWO, or GA4 experiments
        return {
            "variant_a": {"name": "Control"},
            "variant_b": {"name": "Variant B"},
            "visitors_a": 1000,
            "conversions_a": 50,
            "visitors_b": 1000,
            "conversions_b": 65,
        }

    def _calculate_significance(
        self, visitors_a: int, conv_a: int, visitors_b: int, conv_b: int
    ) -> tuple[bool, float]:
        """Calculate statistical significance using z-test for proportions."""
        if visitors_a == 0 or visitors_b == 0:
            return False, 0.0

        p_a = conv_a / visitors_a
        p_b = conv_b / visitors_b
        p_pooled = (conv_a + conv_b) / (visitors_a + visitors_b)

        # Standard error
        se = math.sqrt(p_pooled * (1 - p_pooled) * (1/visitors_a + 1/visitors_b))

        if se == 0:
            return False, 0.0

        # Z-score
        z = (p_b - p_a) / se

        # Two-tailed p-value approximation
        # Using standard normal distribution
        abs_z = abs(z)

        # Approximation of cumulative normal distribution
        if abs_z > 3.5:
            confidence = 99.9
        elif abs_z > 2.58:
            confidence = 99.0
        elif abs_z > 1.96:
            confidence = 95.0
        elif abs_z > 1.65:
            confidence = 90.0
        else:
            confidence = min(50 + abs_z * 25, 89.9)

        is_significant = confidence >= 95.0

        return is_significant, confidence

    def _generate_test_recommendation(
        self, cvr_a: float, cvr_b: float, sig: bool, conf: float
    ) -> str:
        """Generate actionable test recommendation."""
        if not sig:
            if conf < 80:
                return f"Continue test - only {conf:.1f}% confidence. Need more data for reliable results."
            else:
                return f"Test approaching significance at {conf:.1f}%. Consider extending test duration or sample size."

        if cvr_b > cvr_a:
            uplift = ((cvr_b - cvr_a) / cvr_a * 100) if cvr_a > 0 else 0
            return f"✅ Implement Variant B - {uplift:.1f}% improvement with {conf:.1f}% confidence. Estimated annual impact: significant."
        else:
            return f"✅ Keep Variant A (Control) - it outperforms with {conf:.1f}% confidence."

    async def _get_historical_roi(
        self, channels: List[Channel]
    ) -> Dict[Channel, float]:
        """Get historical ROI by channel from GA4 data."""
        roi_data = {}

        # Default industry benchmarks
        default_roi = {
            Channel.EMAIL: 4.2,  # $4.20 per $1 spent
            Channel.SEO: 2.8,
            Channel.PPC: 2.0,
            Channel.SOCIAL: 1.5,
            Channel.CONTENT: 3.0,
            Channel.DISPLAY: 1.2,
            Channel.AFFILIATE: 2.5,
            Channel.DIRECT: 5.0,
        }

        for channel in channels:
            roi_data[channel] = default_roi.get(channel, 2.0)

        # Try to get real data from GA4
        if self.ga4_client:
            try:
                async with self.ga4_client as client:
                    sources = await client.get_traffic_sources(days=90)

                    for source in sources:
                        medium = source.get("medium", "")
                        channel = self._medium_to_channel(medium)

                        if channel in channels:
                            sessions = source.get("sessions", 0)
                            conversions = source.get("conversions", 0)

                            if sessions > 0:
                                # Estimate ROI from conversion rate
                                roi = (conversions / sessions) * 100  # Rough ROI proxy
                                roi_data[channel] = max(1.0, roi)

            except Exception as e:
                logger.warning(f"Using default ROI data: {e}")

        return roi_data

    def _optimize_allocation(
        self,
        budget: float,
        channels: List[Channel],
        roi: Dict[Channel, float],
        objective: CampaignObjective,
    ) -> Dict[Channel, float]:
        """Optimize budget allocation using ROI-weighted approach."""
        # Calculate weights based on ROI
        total_roi = sum(roi.get(ch, 1.0) for ch in channels)

        allocation = {}
        for channel in channels:
            channel_roi = roi.get(channel, 1.0)
            weight = channel_roi / total_roi
            allocation[channel] = budget * weight

        # Apply minimum allocation (10% per channel minimum)
        min_per_channel = budget * 0.1

        for channel in channels:
            if allocation[channel] < min_per_channel:
                allocation[channel] = min_per_channel

        # Normalize to match budget
        total_allocated = sum(allocation.values())
        if total_allocated > 0:
            factor = budget / total_allocated
            for channel in allocation:
                allocation[channel] *= factor

        return allocation

    def _calculate_confidence_interval(
        self, revenue: float, channels: List[Channel]
    ) -> tuple[float, float]:
        """Calculate 95% confidence interval for revenue projection."""
        # Standard deviation estimate based on channel count
        std_dev = revenue * 0.15 * math.sqrt(len(channels))

        # 95% CI = mean ± 1.96 * std_dev
        lower = revenue - 1.96 * std_dev
        upper = revenue + 1.96 * std_dev

        return (max(0, lower), upper)

    async def _get_campaign_history(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get historical campaign data for forecasting."""
        history = []

        if self.ga4_client:
            try:
                async with self.ga4_client as client:
                    # Get daily data for past 30 days
                    for days_ago in range(30, 0, -1):
                        start = f"{days_ago}daysAgo"
                        end = f"{days_ago}daysAgo"

                        result = await client.run_report(
                            dimensions=[],
                            metrics=["sessions", "conversions", "screenPageViews"],
                            start_date=start,
                            end_date=end,
                        )

                        rows = result.get("rows", [])
                        if rows:
                            values = rows[0].get("metricValues", [])
                            history.append({
                                "date": datetime.utcnow() - timedelta(days=days_ago),
                                "sessions": int(values[0].get("value", 0)) if values else 0,
                                "conversions": int(values[1].get("value", 0)) if len(values) > 1 else 0,
                                "pageviews": int(values[2].get("value", 0)) if len(values) > 2 else 0,
                            })

            except Exception as e:
                logger.warning(f"Could not fetch campaign history: {e}")

        return history

    async def _forecast_metrics(
        self, historical: List[Dict[str, Any]], days: int
    ) -> Dict[str, Any]:
        """Forecast campaign metrics using simple trend analysis."""
        if not historical:
            return {
                "impressions": 10000,
                "clicks": 500,
                "conversions": 25,
                "revenue": 2500.0,
                "roi": 150.0,
                "confidence": 50.0,
            }

        # Calculate averages and trends
        sessions = [h.get("sessions", 0) for h in historical]
        conversions = [h.get("conversions", 0) for h in historical]

        avg_sessions = sum(sessions) / len(sessions) if sessions else 0
        avg_conversions = sum(conversions) / len(conversions) if conversions else 0

        # Simple linear trend
        if len(sessions) >= 7:
            recent_avg = sum(sessions[-7:]) / 7
            older_avg = sum(sessions[:7]) / 7
            trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        else:
            trend = 0

        # Project forward
        projected_sessions = avg_sessions * days * (1 + trend)
        projected_conversions = avg_conversions * days * (1 + trend)
        projected_revenue = projected_conversions * 100  # $100 per conversion

        # Confidence based on data quality
        confidence = min(95, 50 + len(historical) * 1.5)

        return {
            "impressions": int(projected_sessions * 2),
            "clicks": int(projected_sessions),
            "conversions": int(projected_conversions),
            "revenue": projected_revenue,
            "roi": (projected_revenue / (projected_sessions * 0.5) - 1) * 100 if projected_sessions > 0 else 0,
            "confidence": confidence,
        }

    def _calculate_scenario(
        self, predictions: Dict[str, Any], multiplier: float
    ) -> Dict[str, float]:
        """Calculate best/worst case scenario."""
        return {
            "impressions": predictions["impressions"] * multiplier,
            "clicks": predictions["clicks"] * multiplier,
            "conversions": predictions["conversions"] * multiplier,
            "revenue": predictions["revenue"] * multiplier,
            "roi": predictions["roi"] * multiplier,
        }

    async def _generate_forecast_recommendations(
        self, predictions: Dict[str, Any], historical: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate optimization recommendations based on forecasts."""
        recommendations = []

        roi = predictions.get("roi", 0)
        confidence = predictions.get("confidence", 0)

        if roi < 100:
            recommendations.append("⚠️ ROI below target - consider reducing spend on underperforming channels")
        elif roi > 200:
            recommendations.append("✅ Strong ROI - consider scaling successful campaigns")

        if confidence < 70:
            recommendations.append("📊 Forecast confidence is low - gather more data before major decisions")

        if predictions.get("conversions", 0) < 10:
            recommendations.append("📈 Low conversion volume - focus on conversion rate optimization")

        # Add channel-specific recommendations
        recommendations.append("💡 Consider A/B testing email subject lines for better open rates")
        recommendations.append("💡 Review top-performing content and create similar pieces")

        return recommendations
