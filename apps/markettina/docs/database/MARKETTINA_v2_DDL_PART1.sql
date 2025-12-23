-- ============================================================================
-- MARKETTINA v2.0 - DDL SQL COMPLETO - PARTE 1
-- ============================================================================
-- Database: PostgreSQL 16+
-- Encoding: UTF-8
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- SECTION 1: ACCOUNTS (Base Multi-Tenancy)
-- ============================================================================

CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan_tier VARCHAR(50) DEFAULT 'free',
    is_active BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_accounts_slug ON accounts(slug);
CREATE INDEX IF NOT EXISTS idx_accounts_active ON accounts(is_active) WHERE is_active = true;

-- ============================================================================
-- SECTION 2: IDENTITY CONTEXT - Estensioni
-- ============================================================================

-- 2.1 Social Accounts (multipli per piattaforma)
CREATE TABLE social_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    platform VARCHAR(50) NOT NULL,
    platform_user_id VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    handle VARCHAR(255),
    profile_image_url TEXT,

    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    token_scope TEXT[],

    is_active BOOLEAN DEFAULT true,
    is_primary BOOLEAN DEFAULT false,

    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,

    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(50) DEFAULT 'pending',
    sync_error TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1,

    CONSTRAINT uq_social_account_platform UNIQUE (account_id, platform, platform_user_id)
);

CREATE INDEX idx_social_accounts_account ON social_accounts(account_id);
CREATE INDEX idx_social_accounts_platform ON social_accounts(platform);
CREATE INDEX idx_social_accounts_active ON social_accounts(account_id, is_active) WHERE is_active = true;

-- 2.2 Social Account Health Check
CREATE TABLE social_account_health (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    social_account_id UUID NOT NULL REFERENCES social_accounts(id) ON DELETE CASCADE,

    status VARCHAR(50) NOT NULL,
    status_message TEXT,

    last_check_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    next_check_at TIMESTAMP WITH TIME ZONE,
    consecutive_failures INTEGER DEFAULT 0,

    rate_limit_remaining INTEGER,
    rate_limit_reset_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_social_health_account ON social_account_health(social_account_id);
CREATE INDEX idx_social_health_status ON social_account_health(status);

-- 2.3 User Permissions (granular)
CREATE TABLE user_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    permission VARCHAR(50) NOT NULL,

    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by INTEGER REFERENCES users(id),
    expires_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_user_permission UNIQUE (account_id, user_id, resource_type, resource_id, permission)
);

CREATE INDEX idx_user_permissions_user ON user_permissions(user_id);
CREATE INDEX idx_user_permissions_resource ON user_permissions(resource_type, resource_id);

-- ============================================================================
-- SECTION 3: BILLING CONTEXT - Estensioni
-- ============================================================================

-- 3.1 Service Pricing
CREATE TABLE service_pricing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    service_type VARCHAR(100) NOT NULL,
    service_subtype VARCHAR(100),
    token_cost INTEGER NOT NULL,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    is_active BOOLEAN DEFAULT true,
    effective_from DATE DEFAULT CURRENT_DATE,
    effective_to DATE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_service_pricing UNIQUE (service_type, service_subtype, effective_from)
);

CREATE INDEX idx_service_pricing_type ON service_pricing(service_type, service_subtype);
CREATE INDEX idx_service_pricing_active ON service_pricing(is_active, effective_from, effective_to);

-- Seed default pricing
INSERT INTO service_pricing (service_type, service_subtype, token_cost, name, description) VALUES
    ('text_generation', 'social_caption', 5, 'Caption Social', 'Generazione caption per social media'),
    ('text_generation', 'blog_post', 50, 'Blog Post', 'Generazione blog post (500-1000 parole)'),
    ('text_generation', 'email_copy', 20, 'Email Copy', 'Generazione copy email marketing'),
    ('image_generation', 'dalle3', 20, 'DALL-E 3', 'Generazione immagine con DALL-E 3'),
    ('image_generation', 'stable_diffusion', 10, 'Stable Diffusion', 'Generazione immagine con SD'),
    ('video_generation', 'short_video', 100, 'Video Breve', 'Generazione video 15-30 secondi'),
    ('social_publish', 'single_platform', 2, 'Pubblicazione Singola', 'Pubblicazione su singola piattaforma'),
    ('social_publish', 'cross_post', 5, 'Cross-Post', 'Pubblicazione multi-piattaforma'),
    ('analytics', 'sentiment_analysis', 5, 'Sentiment Analysis', 'Analisi sentiment commenti'),
    ('analytics', 'competitor_report', 30, 'Report Competitor', 'Analisi competitor completa'),
    ('lead_research', 'google_places', 3, 'Google Places', 'Ricerca lead da Google Places'),
    ('lead_research', 'enrichment', 10, 'Lead Enrichment', 'Arricchimento dati lead');

-- 3.2 Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    invoice_number VARCHAR(50) UNIQUE NOT NULL,

    subtotal_cents INTEGER NOT NULL,
    tax_cents INTEGER DEFAULT 0,
    total_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',

    status VARCHAR(50) DEFAULT 'draft',

    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE,
    paid_at TIMESTAMP WITH TIME ZONE,

    payment_method VARCHAR(50),
    payment_intent_id VARCHAR(255),

    billing_name VARCHAR(255),
    billing_email VARCHAR(255),
    billing_address TEXT,
    billing_vat_id VARCHAR(50),

    pdf_url TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_invoices_account ON invoices(account_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_date ON invoices(issue_date DESC);

-- 3.3 Invoice Items
CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,

    description TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit_price_cents INTEGER NOT NULL,
    total_cents INTEGER NOT NULL,

    service_type VARCHAR(100),
    resource_id UUID,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);

-- 3.4 Promo Codes
CREATE TABLE promo_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    code VARCHAR(50) UNIQUE NOT NULL,

    discount_type VARCHAR(50) NOT NULL,
    discount_value INTEGER NOT NULL,

    max_uses INTEGER,
    current_uses INTEGER DEFAULT 0,
    max_uses_per_user INTEGER DEFAULT 1,
    min_purchase_cents INTEGER,

    valid_from TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_to TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,

    applicable_packages UUID[],
    applicable_plans VARCHAR(50)[],

    description TEXT,
    internal_notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_promo_codes_code ON promo_codes(code);
CREATE INDEX idx_promo_codes_active ON promo_codes(is_active, valid_from, valid_to);

-- 3.5 Promo Redemptions
CREATE TABLE promo_redemptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    promo_code_id UUID NOT NULL REFERENCES promo_codes(id),
    account_id UUID NOT NULL REFERENCES accounts(id),
    user_id INTEGER REFERENCES users(id),

    transaction_id UUID,
    discount_amount INTEGER NOT NULL,

    redeemed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_promo_redemption UNIQUE (promo_code_id, account_id, transaction_id)
);

CREATE INDEX idx_promo_redemptions_code ON promo_redemptions(promo_code_id);
CREATE INDEX idx_promo_redemptions_account ON promo_redemptions(account_id);

-- 3.6 Referral Program
CREATE TABLE referral_program (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    referrer_account_id UUID NOT NULL REFERENCES accounts(id),
    referrer_user_id INTEGER REFERENCES users(id),
    referral_code VARCHAR(50) UNIQUE NOT NULL,

    referred_account_id UUID REFERENCES accounts(id),
    referred_user_id INTEGER REFERENCES users(id),

    referrer_bonus_tokens INTEGER DEFAULT 100,
    referred_bonus_tokens INTEGER DEFAULT 50,

    status VARCHAR(50) DEFAULT 'pending',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '30 days'
);

CREATE INDEX idx_referral_referrer ON referral_program(referrer_account_id);
CREATE INDEX idx_referral_code ON referral_program(referral_code);
CREATE INDEX idx_referral_status ON referral_program(status);
