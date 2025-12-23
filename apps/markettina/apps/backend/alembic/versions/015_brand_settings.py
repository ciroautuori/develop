"""Add brand_settings table for Brand DNA persistence

Revision ID: 015_brand_settings
Revises: 014_toolai_posts
Create Date: 2025-12-04

Tables created:
- brand_settings: Brand identity configuration for AI agents
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '015_brand_settings'
down_revision = 'add_google_user_id'
branch_labels = None
depends_on = None


def upgrade():
    # Check if table already exists
    connection = op.get_bind()

    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'brand_settings')"
    ))
    table_exists = result.scalar()

    if table_exists:
        print("brand_settings table already exists, skipping creation")
        return

    # Create tone_of_voice enum type
    tone_enum = postgresql.ENUM(
        'professional',
        'casual',
        'enthusiastic',
        'formal',
        'friendly',
        'authoritative',
        name='toneofvoice',
        create_type=False
    )

    # Create the enum type if it doesn't exist
    connection.execute(sa.text(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'toneofvoice') THEN
                CREATE TYPE toneofvoice AS ENUM (
                    'professional', 'casual', 'enthusiastic',
                    'formal', 'friendly', 'authoritative'
                );
            END IF;
        END$$;
        """
    ))

    # Create brand_settings table
    op.create_table(
        'brand_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),

        # Logo & Visual Identity
        sa.Column('logo_url', sa.Text(), nullable=True),
        sa.Column('favicon_url', sa.Text(), nullable=True),

        # Brand Colors
        sa.Column('primary_color', sa.String(length=7), nullable=False, server_default='#D4AF37'),
        sa.Column('secondary_color', sa.String(length=7), nullable=False, server_default='#0A0A0A'),
        sa.Column('accent_color', sa.String(length=7), nullable=True, server_default='#FAFAFA'),

        # Company Info
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('tagline', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),

        # Voice & Tone (using String instead of Enum to avoid migration conflicts)
        sa.Column('tone_of_voice', sa.String(50), nullable=False, server_default='professional'),

        # Target & Positioning
        sa.Column('target_audience', sa.Text(), nullable=True),
        sa.Column('unique_value_proposition', sa.Text(), nullable=True),

        # Structured Data (JSONB)
        sa.Column('keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('values', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('competitors', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('content_pillars', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),

        # Social Presence
        sa.Column('social_handles', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),

        # AI Configuration
        sa.Column('ai_persona', sa.Text(), nullable=True),
        sa.Column('forbidden_words', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('preferred_hashtags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('admin_id', name='uq_brand_settings_admin_id')
    )

    # Create indexes
    op.create_index('ix_brand_settings_id', 'brand_settings', ['id'])
    op.create_index('ix_brand_settings_admin_id', 'brand_settings', ['admin_id'])

    print("✅ brand_settings table created successfully")


def downgrade():
    # Drop indexes
    op.drop_index('ix_brand_settings_admin_id', table_name='brand_settings')
    op.drop_index('ix_brand_settings_id', table_name='brand_settings')

    # Drop table
    op.drop_table('brand_settings')

    # Drop enum type
    connection = op.get_bind()
    connection.execute(sa.text("DROP TYPE IF EXISTS toneofvoice"))

    print("✅ brand_settings table dropped")
