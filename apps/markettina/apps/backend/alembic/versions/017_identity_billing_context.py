"""
017_identity_billing_context.py

MARKETTINA v2.0 - Identity & Billing Context Migration
Creates accounts, social_accounts, billing tables for market-ready deployment.

Revision ID: 017
Revises: 016_whatsapp_messages
Create Date: 2025-12-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '017_identity_billing_context'
down_revision = '016_whatsapp_messages'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create Identity and Billing context tables."""

    # ========================================================================
    # IDENTITY CONTEXT
    # ========================================================================

    # accounts table - Multi-tenancy root
    op.create_table(
        'accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('plan_tier', sa.Enum('free', 'starter', 'pro', 'team', 'enterprise', name='plantier'), nullable=False, server_default='free'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True, unique=True),
        # TimestampMixin
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        # SoftDeleteMixin
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        # VersionMixin
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_accounts_slug', 'accounts', ['slug'])

    # social_accounts table - Connected social media
    op.create_table(
        'social_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        # Platform info
        sa.Column('platform', sa.Enum('facebook', 'instagram', 'linkedin', 'twitter', 'threads', 'tiktok', 'youtube', name='socialplatform'), nullable=False),
        sa.Column('platform_user_id', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('handle', sa.String(255), nullable=True),
        sa.Column('profile_url', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        # OAuth tokens
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sync_status', sa.Enum('active', 'syncing', 'error', 'expired', 'disconnected', name='syncstatus'), nullable=False, server_default='active'),
        # Metrics
        sa.Column('followers_count', sa.Integer(), nullable=True),
        sa.Column('following_count', sa.Integer(), nullable=True),
        sa.Column('posts_count', sa.Integer(), nullable=True),
        # Sync tracking
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        # Mixins
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('account_id', 'platform', 'platform_user_id', name='uq_social_account_platform')
    )
    op.create_index('ix_social_accounts_account_platform', 'social_accounts', ['account_id', 'platform'])

    # social_account_health table - Health monitoring
    op.create_table(
        'social_account_health',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('social_account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='healthy'),
        sa.Column('status_message', sa.Text(), nullable=True),
        sa.Column('last_check_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('consecutive_failures', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['social_account_id'], ['social_accounts.id'], ondelete='CASCADE')
    )

    # user_permissions table - Fine-grained RBAC
    op.create_table(
        'user_permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('permission', sa.String(50), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('granted_by', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id']),
        sa.UniqueConstraint('account_id', 'user_id', 'resource_type', 'resource_id', 'permission', name='uq_user_permission')
    )

    # ========================================================================
    # BILLING CONTEXT
    # ========================================================================

    # service_pricing table - Dynamic AI service pricing
    op.create_table(
        'service_pricing',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('service_type', sa.Enum('content_generation', 'image_generation', 'video_generation', 'sentiment_analysis', 'competitor_analysis', 'lead_enrichment', 'email_campaign', 'social_post', name='servicetype'), nullable=False),
        sa.Column('service_subtype', sa.String(100), nullable=True),
        sa.Column('token_cost', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('effective_from', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('service_type', 'service_subtype', 'effective_from', name='uq_service_pricing')
    )
    op.create_index('ix_service_pricing_active', 'service_pricing', ['service_type', 'is_active'])

    # invoices table - Billing records
    op.create_table(
        'invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('invoice_number', sa.String(50), nullable=False, unique=True),
        # Amounts in cents
        sa.Column('subtotal_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('discount_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tax_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(3), nullable=False, server_default='EUR'),
        # Status
        sa.Column('status', sa.Enum('draft', 'pending', 'paid', 'overdue', 'cancelled', 'refunded', name='invoicestatus'), nullable=False, server_default='draft'),
        # Dates
        sa.Column('issue_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        # Stripe
        sa.Column('stripe_invoice_id', sa.String(255), nullable=True, unique=True),
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
        # Billing info snapshot
        sa.Column('billing_name', sa.String(255), nullable=True),
        sa.Column('billing_email', sa.String(255), nullable=True),
        sa.Column('billing_address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        # Mixins
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE')
    )
    op.create_index('ix_invoices_account_status', 'invoices', ['account_id', 'status'])

    # token_packages table - For invoice items reference
    op.create_table(
        'token_packages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('tokens', sa.Integer(), nullable=False),
        sa.Column('price_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='EUR'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # invoice_items table - Line items
    op.create_table(
        'invoice_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('unit_price_cents', sa.Integer(), nullable=False),
        sa.Column('total_cents', sa.Integer(), nullable=False),
        sa.Column('token_package_id', sa.Integer(), nullable=True),
        sa.Column('tokens_amount', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['token_package_id'], ['token_packages.id'])
    )

    # promo_codes table - Discount codes
    op.create_table(
        'promo_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('discount_type', sa.Enum('percentage', 'fixed_amount', 'bonus_tokens', name='discounttype'), nullable=False),
        sa.Column('discount_value', sa.Numeric(10, 2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('valid_from', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('current_uses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_uses_per_account', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('min_purchase_cents', sa.Integer(), nullable=True),
        sa.Column('applicable_packages', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('campaign_name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('max_uses IS NULL OR current_uses <= max_uses', name='ck_promo_uses')
    )

    # promo_redemptions table - Usage tracking
    op.create_table(
        'promo_redemptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('promo_code_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('discount_applied_cents', sa.Integer(), nullable=False),
        sa.Column('redeemed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['promo_code_id'], ['promo_codes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('promo_code_id', 'account_id', 'invoice_id', name='uq_promo_redemption')
    )

    # referral_programs table - Referral tracking
    op.create_table(
        'referral_programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('referrer_account_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('referral_code', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('referrer_bonus_tokens', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('referee_bonus_tokens', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('total_referrals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('successful_referrals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens_earned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['referrer_account_id'], ['accounts.id'], ondelete='CASCADE')
    )

    # Insert default token packages
    op.execute("""
        INSERT INTO token_packages (name, tokens, price_cents, currency) VALUES
        ('Starter Pack', 1000, 990, 'EUR'),
        ('Growth Pack', 5000, 3990, 'EUR'),
        ('Pro Pack', 15000, 9990, 'EUR'),
        ('Enterprise Pack', 50000, 24990, 'EUR');
    """)

    # Insert default service pricing
    op.execute("""
        INSERT INTO service_pricing (service_type, name, token_cost, description) VALUES
        ('content_generation', 'Content Generation', 10, 'AI-generated marketing content'),
        ('image_generation', 'Image Generation', 50, 'AI-generated images with DALL-E'),
        ('video_generation', 'Video Generation', 200, 'AI-generated videos with HeyGen'),
        ('sentiment_analysis', 'Sentiment Analysis', 5, 'Social media sentiment analysis'),
        ('competitor_analysis', 'Competitor Analysis', 20, 'Competitor tracking and analysis'),
        ('lead_enrichment', 'Lead Enrichment', 15, 'Lead data enrichment with AI'),
        ('email_campaign', 'Email Campaign', 25, 'AI-powered email campaign'),
        ('social_post', 'Social Post', 10, 'AI-generated social media post');
    """)


def downgrade() -> None:
    """Drop Identity and Billing tables."""
    op.drop_table('referral_programs')
    op.drop_table('promo_redemptions')
    op.drop_table('promo_codes')
    op.drop_table('invoice_items')
    op.drop_table('token_packages')
    op.drop_table('invoices')
    op.drop_table('service_pricing')
    op.drop_table('user_permissions')
    op.drop_table('social_account_health')
    op.drop_table('social_accounts')
    op.drop_table('accounts')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS plantier")
    op.execute("DROP TYPE IF EXISTS socialplatform")
    op.execute("DROP TYPE IF EXISTS syncstatus")
    op.execute("DROP TYPE IF EXISTS servicetype")
    op.execute("DROP TYPE IF EXISTS invoicestatus")
    op.execute("DROP TYPE IF EXISTS discounttype")
