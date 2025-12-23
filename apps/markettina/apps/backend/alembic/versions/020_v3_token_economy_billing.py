"""
020_v3_token_economy_billing.py
MARKETTINA v3.0 - Token Economy & Enterprise Billing Schema

Creates:
- subscription_plans (dynamic SaaS plans)
- subscriptions (account-plan link)
- token_wallets (user token balance)
- token_packages (purchasable token bundles)
- token_transactions (immutable ledger)

Revision ID: 020_v3_token_economy
Revises: 019_workflow_persistence
Create Date: 2025-12-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic
revision = '020_v3_token_economy'
down_revision = '019_workflow_persistence'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =====================================================================
    # 1. SUBSCRIPTION PLANS
    # =====================================================================
    op.create_table(
        'subscription_plans',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('billing_interval', sa.Enum('monthly', 'annual', name='billinginterval'), nullable=False),
        sa.Column('price_cents', sa.Integer, nullable=False, server_default='0'),
        sa.Column('included_users', sa.Integer, nullable=False, server_default='1'),
        sa.Column('included_tokens', sa.Integer, nullable=False, server_default='0'),
        sa.Column('max_social_accounts', sa.Integer, nullable=True),
        sa.Column('max_campaigns', sa.Integer, nullable=True),
        sa.Column('features', JSONB, nullable=False, server_default='{}'),
        sa.Column('limits', JSONB, nullable=True),
        sa.Column('trial_days', sa.Integer, nullable=True, server_default='14'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # =====================================================================
    # 2. SUBSCRIPTIONS (Account <-> Plan)
    # =====================================================================
    op.create_table(
        'subscriptions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('account_id', UUID(as_uuid=True), sa.ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
        sa.Column('plan_id', sa.String(50), sa.ForeignKey('subscription_plans.id'), nullable=False, index=True),
        sa.Column('status', sa.Enum('trialing', 'active', 'past_due', 'cancelled', 'unpaid', 'incomplete', name='subscriptionstatus'), nullable=False, server_default='trialing'),
        sa.Column('quantity', sa.Integer, nullable=False, server_default='1'),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('trial_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(255), unique=True, nullable=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('version', sa.Integer, nullable=False, server_default='1'),
    )
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])

    # =====================================================================
    # 3. TOKEN PACKAGES
    # =====================================================================
    op.create_table(
        'token_packages',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('badge', sa.String(50), nullable=True),
        sa.Column('tokens', sa.Integer, nullable=False),
        sa.Column('bonus_tokens', sa.Integer, nullable=False, server_default='0'),
        sa.Column('price_usd', sa.Numeric(8, 2), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # =====================================================================
    # 4. TOKEN WALLETS
    # =====================================================================
    op.create_table(
        'token_wallets',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('account_id', UUID(as_uuid=True), sa.ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('balance', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_purchased', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_used', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_bonus', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_refunded', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_spent_usd', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('last_purchase_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_usage_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('version', sa.Integer, nullable=False, server_default='1'),
        sa.UniqueConstraint('user_id', 'account_id', name='uq_user_account_wallet'),
        sa.CheckConstraint('balance >= 0', name='ck_wallet_balance_positive'),
    )

    # =====================================================================
    # 5. TOKEN TRANSACTIONS (Ledger)
    # =====================================================================
    op.create_table(
        'token_transactions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('wallet_id', UUID(as_uuid=True), sa.ForeignKey('token_wallets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('account_id', UUID(as_uuid=True), sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('type', sa.Enum('purchase', 'usage', 'bonus', 'refund', 'adjustment', 'subscription_renewal', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('balance_before', sa.Integer, nullable=False),
        sa.Column('balance_after', sa.Integer, nullable=False),
        sa.Column('package_id', sa.String(50), sa.ForeignKey('token_packages.id'), nullable=True),
        sa.Column('price_usd', sa.Numeric(10, 2), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
        sa.Column('usage_context', sa.Enum('ai_generation', 'image_generation', 'video_generation', 'analytics', 'storage', 'other', name='usagecontext'), nullable=True),
        sa.Column('ai_provider', sa.Enum('openai', 'anthropic', 'stability', 'replicate', 'google', 'qwen', 'llama', 'other', name='aiprovider'), nullable=True),
        sa.Column('ai_model', sa.String(100), nullable=True),
        sa.Column('related_resource_id', UUID(as_uuid=True), nullable=True),
        sa.Column('related_resource_type', sa.String(100), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_token_tx_wallet_created', 'token_transactions', ['wallet_id', 'created_at'])
    op.create_index('ix_token_tx_account_type', 'token_transactions', ['account_id', 'type'])

    # =====================================================================
    # 6. SEED DEFAULT PLANS
    # =====================================================================
    op.execute("""
        INSERT INTO subscription_plans (id, name, description, billing_interval, price_cents, included_users, included_tokens, features, is_active, sort_order) VALUES
        ('tier_free', 'Free', 'Get started with Markettina', 'monthly', 0, 1, 1000, '{"api_access": false, "advanced_analytics": false}', true, 0),
        ('tier_starter_monthly', 'Starter', 'For small businesses', 'monthly', 2900, 3, 50000, '{"api_access": true, "advanced_analytics": false}', true, 1),
        ('tier_pro_monthly', 'Pro', 'For growing teams', 'monthly', 7900, 10, 200000, '{"api_access": true, "advanced_analytics": true}', true, 2),
        ('tier_enterprise_monthly', 'Enterprise', 'Custom solutions', 'monthly', 0, 999, 1000000, '{"api_access": true, "advanced_analytics": true, "custom_integrations": true}', true, 3);
    """)

    # =====================================================================
    # 7. SEED DEFAULT TOKEN PACKAGES
    # =====================================================================
    op.execute("""
        INSERT INTO token_packages (id, name, slug, description, tokens, bonus_tokens, price_usd, badge, is_active, sort_order) VALUES
        ('pack_starter_10k', 'Starter Pack', 'starter-pack', '10,000 tokens to get started', 10000, 0, 9.99, NULL, true, 0),
        ('pack_growth_50k', 'Growth Pack', 'growth-pack', '50,000 tokens + 5,000 bonus', 50000, 5000, 39.99, 'POPULAR', true, 1),
        ('pack_pro_200k', 'Pro Pack', 'pro-pack', '200,000 tokens + 25,000 bonus', 200000, 25000, 129.99, 'BEST VALUE', true, 2),
        ('pack_enterprise_1m', 'Enterprise Pack', 'enterprise-pack', '1,000,000 tokens + 150,000 bonus', 1000000, 150000, 499.99, NULL, true, 3);
    """)


def downgrade() -> None:
    op.drop_table('token_transactions')
    op.drop_table('token_wallets')
    op.drop_table('token_packages')
    op.drop_table('subscriptions')
    op.drop_table('subscription_plans')
    op.execute("DROP TYPE IF EXISTS transactiontype")
    op.execute("DROP TYPE IF EXISTS usagecontext")
    op.execute("DROP TYPE IF EXISTS aiprovider")
    op.execute("DROP TYPE IF EXISTS subscriptionstatus")
    op.execute("DROP TYPE IF EXISTS billinginterval")
