"""
MARKETTINA v2.0 - Marketing AI Agents

AI-powered marketing automation agents:
- ContentCreatorAgent: Content generation and optimization
- SocialMediaManagerAgent: Social media scheduling and analytics
- SEOAgent: Search engine optimization and analysis
- CampaignManagerAgent: Campaign planning and ROI tracking
- EmailMarketingAgent: Email campaign automation
- ImageGenerationAgent: AI image generation
"""

from .campaign_manager import (
    ABTestResult,
    AttributionModel,
    AttributionResult,
    BudgetAllocation,
    CampaignManagerAgent,
    CampaignObjective,
    CampaignPlan,
    CampaignStatus,
    Channel,
    PerformanceForecast,
    ROIMetrics,
    TouchPoint,
)
from .content_creator import (
    AdCopyConfig,
    BlogPostConfig,
    ContentCreatorAgent,
    ContentResult,
    ContentTone,
    ContentType,
    SocialPlatform,
    SocialPostConfig,
    VideoScriptConfig,
)
from .email_marketing import (
    AudienceSegment,
    DeliverabilityReport,
    EmailCampaign,
    EmailCampaignType,
    EmailMarketingAgent,
    EmailPerformance,
    EmailStatus,
    PersonalizedEmail,
    SegmentCriteria,
    SendTimeOptimization,
)
from .image_generator_agent import (
    ImageGenerationAgent,
    ImageGenerationConfig,
    ImageProvider,
    ImageResult,
)
from .seo_specialist import (
    CompetitorAnalysis,
    Keyword,
    KeywordDifficulty,
    OnPageOptimization,
    RankingUpdate,
    SEOAgent,
    SEOIssue,
    SEOIssueSeverity,
)
from .social_media_manager import (
    CommentResponse,
    EngagementMetrics,
    EngagementType,
    OptimalPostingTime,
    PostStatus,
    SocialMediaManagerAgent,
    SocialPost,
    TrendingTopic,
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
