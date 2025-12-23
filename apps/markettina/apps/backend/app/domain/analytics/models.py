"""
Analytics Models - Event tracking, Social Metrics, Sentiment Analysis, Competitor Tracking
MARKETTINA v2.0 - Market-ready analytics infrastructure
"""
import enum
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.infrastructure.database.session import Base


class AnalyticsEvent(Base):
    """
    Eventi analytics per tracking.

    Traccia tutte le interazioni utente per analytics.
    """
    __tablename__ = "analytics_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Tipo evento
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # page_view, project_click, service_click, booking_created, contact_form_submit

    # Risorsa
    resource_type: Mapped[str | None] = mapped_column(String(50), index=True)
    # project, service, booking, user
    resource_id: Mapped[int | None] = mapped_column(Integer, index=True)

    # User info
    user_id: Mapped[int | None] = mapped_column(Integer, index=True)
    session_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # Request info
    ip_address: Mapped[str] = mapped_column(String(50), nullable=False)
    user_agent: Mapped[str | None] = mapped_column(Text)
    referrer: Mapped[str | None] = mapped_column(String(500))

    # Metadata aggiuntivo (renamed from metadata to avoid SQLAlchemy conflict)
    event_metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    # Indexes per query performance
    __table_args__ = (
        Index("idx_event_resource", "event_type", "resource_type", "resource_id"),
        Index("idx_event_date", "event_type", "created_at"),
        Index("idx_session_date", "session_id", "created_at"),
    )


# ============================================================================
# SOCIAL METRICS
# ============================================================================

class MetricPeriod(str, enum.Enum):
    """Aggregation period for metrics."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class SocialMetrics(Base):
    """
    Social media metrics per platform.

    Tracks followers, engagement, reach, impressions for each social account.
    Aggregated at daily level for historical tracking.
    """
    __tablename__ = "social_metrics"
    __table_args__ = (
        Index("idx_social_metrics_account_date", "social_account_id", "metric_date"),
        Index("idx_social_metrics_period", "social_account_id", "period", "metric_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to social account
    social_account_id = mapped_column(UUID(as_uuid=True), ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Period
    period: Mapped[str] = mapped_column(SQLEnum(MetricPeriod), nullable=False, default=MetricPeriod.DAILY)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Follower metrics
    followers_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    followers_gained: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    followers_lost: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Content metrics
    posts_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stories_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reels_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Engagement metrics
    likes_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comments_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shares_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    saves_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clicks_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Reach & Impressions
    reach: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Calculated metrics (stored for performance)
    engagement_rate: Mapped[float] = mapped_column(Float, nullable=True)  # (likes+comments+shares)/followers * 100
    growth_rate: Mapped[float] = mapped_column(Float, nullable=True)  # (gained-lost)/followers * 100

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


# ============================================================================
# SENTIMENT ANALYSIS
# ============================================================================

class SentimentType(str, enum.Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class SentimentAnalysis(Base):
    """
    Sentiment analysis results for social content.

    Tracks sentiment of comments, mentions, and reviews for the account.
    """
    __tablename__ = "sentiment_analysis"
    __table_args__ = (
        Index("idx_sentiment_account_date", "account_id", "analysis_date"),
        Index("idx_sentiment_source", "account_id", "source_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to account
    account_id = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Source information
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # comment, mention, review, dm
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False)  # instagram, facebook, etc.
    source_id: Mapped[str] = mapped_column(String(255), nullable=True)  # Platform-specific ID

    # Content analyzed
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_language: Mapped[str] = mapped_column(String(10), nullable=True, default="it")

    # Sentiment results
    sentiment: Mapped[str] = mapped_column(SQLEnum(SentimentType), nullable=False)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)  # -1.0 to 1.0
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0

    # Entity extraction
    entities: Mapped[dict] = mapped_column(JSONB, nullable=True)  # {"topics": [], "brands": [], "products": []}
    keywords: Mapped[list] = mapped_column(JSONB, nullable=True)  # ["keyword1", "keyword2"]

    # Flags
    requires_response: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_urgent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# ============================================================================
# COMPETITOR TRACKING
# ============================================================================

class CompetitorProfile(Base):
    """
    Competitor profile for tracking.

    Stores competitor information and metrics for benchmarking.
    """
    __tablename__ = "competitor_profiles"
    __table_args__ = (
        Index("idx_competitor_account", "account_id", "is_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to account
    account_id = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Competitor info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website_url: Mapped[str] = mapped_column(String(500), nullable=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Social profiles (JSONB for flexibility)
    social_profiles: Mapped[dict] = mapped_column(JSONB, nullable=True)
    # {"instagram": "@handle", "facebook": "page_id", "linkedin": "company/name"}

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class CompetitorMetrics(Base):
    """
    Historical competitor metrics.

    Tracked periodically for benchmarking and trend analysis.
    """
    __tablename__ = "competitor_metrics"
    __table_args__ = (
        Index("idx_competitor_metrics_date", "competitor_id", "metric_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to competitor
    competitor_id: Mapped[int] = mapped_column(Integer, ForeignKey("competitor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Metrics date
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)

    # Follower metrics
    followers_count: Mapped[int] = mapped_column(Integer, nullable=True)
    following_count: Mapped[int] = mapped_column(Integer, nullable=True)

    # Content metrics
    posts_count: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_likes: Mapped[float] = mapped_column(Float, nullable=True)
    avg_comments: Mapped[float] = mapped_column(Float, nullable=True)

    # Engagement
    engagement_rate: Mapped[float] = mapped_column(Float, nullable=True)

    # Raw data
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# ============================================================================
# ANALYTICS AGGREGATES
# ============================================================================

class AnalyticsDailySummary(Base):
    """
    Pre-aggregated daily analytics summary.

    Materialized view equivalent for fast dashboard queries.
    """
    __tablename__ = "analytics_daily_summary"
    __table_args__ = (
        Index("idx_daily_summary_account", "account_id", "summary_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to account
    account_id = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Summary date
    summary_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Aggregated metrics
    total_followers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_engagement: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_reach: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Sentiment summary
    positive_mentions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    neutral_mentions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    negative_mentions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_sentiment_score: Mapped[float] = mapped_column(Float, nullable=True)

    # Content performance
    posts_published: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    best_performing_post_id: Mapped[str] = mapped_column(String(255), nullable=True)

    # Calculated
    overall_engagement_rate: Mapped[float] = mapped_column(Float, nullable=True)
    overall_growth_rate: Mapped[float] = mapped_column(Float, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
