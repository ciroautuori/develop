"""
018_analytics_advanced.py

MARKETTINA v2.0 - Advanced Analytics Migration
Creates social_metrics, sentiment_analysis, competitor tables.

Revision ID: 018
Revises: 017_identity_billing_context
Create Date: 2025-12-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '018_analytics_advanced'
down_revision = '017_identity_billing_context'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create advanced analytics tables."""

    # ========================================================================
    # SOCIAL METRICS
    # ========================================================================

    op.create_table(
        'social_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('social_account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Period
        sa.Column('period', sa.Enum('hourly', 'daily', 'weekly', 'monthly', name='metricperiod'), nullable=False, server_default='daily'),
        sa.Column('metric_date', sa.Date(), nullable=False, index=True),
        # Follower metrics
        sa.Column('followers_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('followers_gained', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('followers_lost', sa.Integer(), nullable=False, server_default='0'),
        # Content metrics
        sa.Column('posts_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('stories_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reels_count', sa.Integer(), nullable=False, server_default='0'),
        # Engagement metrics
        sa.Column('likes_total', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('comments_total', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('shares_total', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('saves_total', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('clicks_total', sa.Integer(), nullable=False, server_default='0'),
        # Reach & Impressions
        sa.Column('reach', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('impressions', sa.Integer(), nullable=False, server_default='0'),
        # Calculated
        sa.Column('engagement_rate', sa.Float(), nullable=True),
        sa.Column('growth_rate', sa.Float(), nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['social_account_id'], ['social_accounts.id'], ondelete='CASCADE')
    )
    op.create_index('idx_social_metrics_account_date', 'social_metrics', ['social_account_id', 'metric_date'])
    op.create_index('idx_social_metrics_period', 'social_metrics', ['social_account_id', 'period', 'metric_date'])

    # ========================================================================
    # SENTIMENT ANALYSIS
    # ========================================================================

    op.create_table(
        'sentiment_analysis',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Source
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_platform', sa.String(50), nullable=False),
        sa.Column('source_id', sa.String(255), nullable=True),
        # Content
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('content_language', sa.String(10), nullable=True, server_default='it'),
        # Sentiment
        sa.Column('sentiment', sa.Enum('positive', 'neutral', 'negative', 'mixed', name='sentimenttype'), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        # Entities
        sa.Column('entities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        # Flags
        sa.Column('requires_response', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_urgent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_processed', sa.Boolean(), nullable=False, server_default='true'),
        # Timestamps
        sa.Column('analysis_date', sa.Date(), nullable=False, index=True),
        sa.Column('source_created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE')
    )
    op.create_index('idx_sentiment_account_date', 'sentiment_analysis', ['account_id', 'analysis_date'])
    op.create_index('idx_sentiment_source', 'sentiment_analysis', ['account_id', 'source_type'])

    # ========================================================================
    # COMPETITOR TRACKING
    # ========================================================================

    op.create_table(
        'competitor_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('website_url', sa.String(500), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('social_profiles', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE')
    )
    op.create_index('idx_competitor_account', 'competitor_profiles', ['account_id', 'is_active'])

    op.create_table(
        'competitor_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('competitor_id', sa.Integer(), nullable=False, index=True),
        sa.Column('metric_date', sa.Date(), nullable=False, index=True),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('followers_count', sa.Integer(), nullable=True),
        sa.Column('following_count', sa.Integer(), nullable=True),
        sa.Column('posts_count', sa.Integer(), nullable=True),
        sa.Column('avg_likes', sa.Float(), nullable=True),
        sa.Column('avg_comments', sa.Float(), nullable=True),
        sa.Column('engagement_rate', sa.Float(), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['competitor_id'], ['competitor_profiles.id'], ondelete='CASCADE')
    )
    op.create_index('idx_competitor_metrics_date', 'competitor_metrics', ['competitor_id', 'metric_date'])

    # ========================================================================
    # ANALYTICS DAILY SUMMARY
    # ========================================================================

    op.create_table(
        'analytics_daily_summary',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('summary_date', sa.Date(), nullable=False, index=True),
        # Aggregated
        sa.Column('total_followers', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_engagement', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_reach', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_impressions', sa.Integer(), nullable=False, server_default='0'),
        # Sentiment
        sa.Column('positive_mentions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('neutral_mentions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('negative_mentions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_sentiment_score', sa.Float(), nullable=True),
        # Content
        sa.Column('posts_published', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('best_performing_post_id', sa.String(255), nullable=True),
        # Calculated
        sa.Column('overall_engagement_rate', sa.Float(), nullable=True),
        sa.Column('overall_growth_rate', sa.Float(), nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE')
    )
    op.create_index('idx_daily_summary_account', 'analytics_daily_summary', ['account_id', 'summary_date'])


def downgrade() -> None:
    """Drop advanced analytics tables."""
    op.drop_table('analytics_daily_summary')
    op.drop_table('competitor_metrics')
    op.drop_table('competitor_profiles')
    op.drop_table('sentiment_analysis')
    op.drop_table('social_metrics')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS metricperiod")
    op.execute("DROP TYPE IF EXISTS sentimenttype")
