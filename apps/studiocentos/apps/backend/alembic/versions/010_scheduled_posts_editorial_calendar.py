"""Add scheduled_posts and editorial_calendars tables

Revision ID: 010_scheduled_posts
Revises: 009_booking_customer_integration
Create Date: 2025-11-28

Calendario editoriale per social media marketing automation.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create scheduled_posts table
    op.create_table(
        'scheduled_posts',
        sa.Column('id', sa.Integer(), nullable=False),

        # Content
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('hashtags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('mentions', sa.JSON(), nullable=False, server_default='[]'),

        # Media
        sa.Column('media_urls', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('media_type', sa.String(20), nullable=False, server_default='text'),

        # Targeting
        sa.Column('platforms', sa.JSON(), nullable=False, server_default='[]'),

        # Scheduling
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),

        # Status
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),

        # Results
        sa.Column('platform_results', sa.JSON(), nullable=False, server_default='{}'),

        # Error tracking
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),

        # AI metadata
        sa.Column('ai_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('ai_prompt', sa.Text(), nullable=True),
        sa.Column('ai_model', sa.String(100), nullable=True),

        # Linking
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),

        # Metrics
        sa.Column('metrics', sa.JSON(), nullable=False, server_default='{}'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['campaign_id'], ['email_campaigns.id'], ondelete='SET NULL'),
    )

    # Create indexes for scheduled_posts
    op.create_index('ix_scheduled_posts_id', 'scheduled_posts', ['id'])
    op.create_index('ix_scheduled_posts_scheduled_at', 'scheduled_posts', ['scheduled_at'])
    op.create_index('ix_scheduled_posts_status', 'scheduled_posts', ['status'])
    op.create_index('ix_scheduled_posts_status_scheduled', 'scheduled_posts', ['status', 'scheduled_at'])

    # Create editorial_calendars table
    op.create_table(
        'editorial_calendars',
        sa.Column('id', sa.Integer(), nullable=False),

        # Calendar info
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),

        # Period
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),

        # Settings
        sa.Column('default_platforms', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('posting_frequency', sa.String(50), nullable=True),
        sa.Column('optimal_times', sa.JSON(), nullable=False, server_default='[]'),

        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),

        # Stats
        sa.Column('total_posts_planned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_posts_published', sa.Integer(), nullable=False, server_default='0'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),

        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index('ix_editorial_calendars_id', 'editorial_calendars', ['id'])


def downgrade() -> None:
    op.drop_index('ix_editorial_calendars_id', table_name='editorial_calendars')
    op.drop_table('editorial_calendars')

    op.drop_index('ix_scheduled_posts_status_scheduled', table_name='scheduled_posts')
    op.drop_index('ix_scheduled_posts_status', table_name='scheduled_posts')
    op.drop_index('ix_scheduled_posts_scheduled_at', table_name='scheduled_posts')
    op.drop_index('ix_scheduled_posts_id', table_name='scheduled_posts')
    op.drop_table('scheduled_posts')
