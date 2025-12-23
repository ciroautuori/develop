"""
Marketing Agents - AI-powered marketing automation.

This module provides specialized agents for marketing tasks including
content creation, social media management, SEO, campaign management,
and email marketing.

Available Agents:
    - ContentCreatorAgent: Content generation and optimization
    - SocialMediaManagerAgent: Social media scheduling and analytics
    - SEOAgent: Search engine optimization and analysis
    - CampaignManagerAgent: Campaign planning and ROI tracking
    - EmailMarketingAgent: Email campaign automation
"""

from app.domain.marketing.content_creator import (
    ContentCreatorAgent,
    ContentType,
    ContentTone,
    SocialPlatform,
    BlogPostConfig,
    SocialPostConfig,
    AdCopyConfig,
    VideoScriptConfig,
    ContentResult,
)

from app.domain.marketing.social_media_manager import (
    SocialMediaManagerAgent,
    EngagementType,
    PostStatus,
    SocialPost,
    EngagementMetrics,
    OptimalPostingTime,
    TrendingTopic,
    CommentResponse,
)

from app.domain.marketing.seo_specialist import (
    SEOAgent,
    KeywordDifficulty,
    SEOIssueSeverity,
    Keyword,
    CompetitorAnalysis,
    SEOIssue,
    OnPageOptimization,
    RankingUpdate,
)

from app.domain.marketing.campaign_manager import (
    CampaignManagerAgent,
    CampaignObjective,
    CampaignStatus,
    AttributionModel,
    Channel,
    CampaignPlan,
    ROIMetrics,
    TouchPoint,
    AttributionResult,
    ABTestResult,
    BudgetAllocation,
    PerformanceForecast,
)

from app.domain.marketing.email_marketing import (
    EmailMarketingAgent,
    EmailCampaignType,
    SegmentCriteria,
    EmailStatus,
    EmailCampaign,
    AudienceSegment,
    PersonalizedEmail,
    SendTimeOptimization,
    EmailPerformance,
    DeliverabilityReport,
)

from app.domain.marketing.image_generator_agent import (
    ImageGenerationAgent,
    ImageProvider,
    ImageGenerationConfig,
    ImageResult,
)

__all__ = [
    # Agents
    "ContentCreatorAgent",
    "SocialMediaManagerAgent",
    "SEOAgent",
    "CampaignManagerAgent",
    "EmailMarketingAgent",
    "ImageGenerationAgent",
    # Content Creator
    "ContentType",
    "ContentTone",
    "SocialPlatform",
    "BlogPostConfig",
    "SocialPostConfig",
    "AdCopyConfig",
    "VideoScriptConfig",
    "ContentResult",
    # Social Media Manager
    "EngagementType",
    "PostStatus",
    "SocialPost",
    "EngagementMetrics",
    "OptimalPostingTime",
    "TrendingTopic",
    "CommentResponse",
    # SEO Specialist
    "KeywordDifficulty",
    "SEOIssueSeverity",
    "Keyword",
    "CompetitorAnalysis",
    "SEOIssue",
    "OnPageOptimization",
    "RankingUpdate",
    # Campaign Manager
    "CampaignObjective",
    "CampaignStatus",
    "AttributionModel",
    "Channel",
    "CampaignPlan",
    "ROIMetrics",
    "TouchPoint",
    "AttributionResult",
    "ABTestResult",
    "BudgetAllocation",
    "PerformanceForecast",
    # Email Marketing
    "EmailCampaignType",
    "SegmentCriteria",
    "EmailStatus",
    "EmailCampaign",
    "AudienceSegment",
    "PersonalizedEmail",
    "SendTimeOptimization",
    "EmailPerformance",
    "DeliverabilityReport",
    # Image Generation
    "ImageProvider",
    "ImageGenerationConfig",
    "ImageResult",
]
