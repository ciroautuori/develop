-- ============================================================================
-- MARKETTINA v2.0 - DDL SQL COMPLETO - PARTE 2
-- ============================================================================

-- ============================================================================
-- SECTION 4: CONTENT CONTEXT - Estensioni
-- ============================================================================

-- 4.1 Campaigns (progetti multi-post)
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    start_date DATE,
    end_date DATE,

    status VARCHAR(50) DEFAULT 'planning',

    target_reach INTEGER,
    target_engagement INTEGER,
    target_conversions INTEGER,
    target_leads INTEGER,

    budget_tokens INTEGER,
    spent_tokens INTEGER DEFAULT 0,

    tags TEXT[],

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_campaigns_account ON campaigns(account_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_dates ON campaigns(start_date, end_date);

-- 4.2 Content Templates
CREATE TABLE content_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    content_type VARCHAR(50) NOT NULL,
    platform VARCHAR(50),
    template_content TEXT NOT NULL,

    variables JSONB DEFAULT '[]',

    tone_of_voice VARCHAR(50),
    target_audience TEXT,

    usage_count INTEGER DEFAULT 0,

    is_active BOOLEAN DEFAULT true,
    is_public BOOLEAN DEFAULT false,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_templates_account ON content_templates(account_id);
CREATE INDEX idx_templates_type ON content_templates(content_type, platform);
CREATE INDEX idx_templates_active ON content_templates(is_active);

-- 4.3 Content Versions (Event Sourcing per contenuti)
CREATE TABLE content_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    content_type VARCHAR(50) NOT NULL,
    content_id UUID NOT NULL,

    version_number INTEGER NOT NULL,

    content_snapshot JSONB NOT NULL,

    change_summary TEXT,
    changed_fields TEXT[],

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),

    CONSTRAINT uq_content_version UNIQUE (content_type, content_id, version_number)
);

CREATE INDEX idx_content_versions_ref ON content_versions(content_type, content_id);
CREATE INDEX idx_content_versions_date ON content_versions(created_at DESC);

-- 4.4 Content Variants (A/B Testing)
CREATE TABLE content_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    parent_content_type VARCHAR(50) NOT NULL,
    parent_content_id UUID NOT NULL,

    variant_name VARCHAR(100) NOT NULL,
    variant_content TEXT NOT NULL,

    traffic_percent DECIMAL(5,2) DEFAULT 50.00,

    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    engagement_score DECIMAL(10,4) DEFAULT 0,

    is_winner BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_variants_parent ON content_variants(parent_content_type, parent_content_id);
CREATE INDEX idx_variants_account ON content_variants(account_id);

-- 4.5 Media Assets Library
CREATE TABLE media_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    mime_type VARCHAR(100) NOT NULL,
    file_size_bytes BIGINT NOT NULL,

    storage_provider VARCHAR(50) DEFAULT 'local',
    storage_path TEXT NOT NULL,
    public_url TEXT,

    width INTEGER,
    height INTEGER,
    duration_seconds INTEGER,

    is_ai_generated BOOLEAN DEFAULT false,
    ai_prompt TEXT,
    ai_model VARCHAR(100),

    alt_text TEXT,
    description TEXT,

    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_media_account ON media_assets(account_id);
CREATE INDEX idx_media_type ON media_assets(mime_type);
CREATE INDEX idx_media_ai ON media_assets(is_ai_generated);

-- 4.6 Media Tags
CREATE TABLE media_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_asset_id UUID NOT NULL REFERENCES media_assets(id) ON DELETE CASCADE,

    tag VARCHAR(100) NOT NULL,
    tag_type VARCHAR(50) DEFAULT 'user',
    confidence DECIMAL(5,4),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_media_tag UNIQUE (media_asset_id, tag)
);

CREATE INDEX idx_media_tags_asset ON media_tags(media_asset_id);
CREATE INDEX idx_media_tags_tag ON media_tags(tag);

-- ============================================================================
-- SECTION 5: ANALYTICS CONTEXT - Estensioni
-- ============================================================================

-- 5.1 Social Metrics (per post)
CREATE TABLE social_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    post_id INTEGER NOT NULL,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255),

    impressions INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    engagement_count INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    video_views INTEGER DEFAULT 0,

    engagement_rate DECIMAL(10,6) DEFAULT 0,
    click_through_rate DECIMAL(10,6) DEFAULT 0,

    conversions INTEGER DEFAULT 0,
    conversion_value DECIMAL(10,2) DEFAULT 0,

    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_social_metrics UNIQUE (post_id, platform, measured_at)
);

CREATE INDEX idx_social_metrics_post ON social_metrics(post_id);
CREATE INDEX idx_social_metrics_account ON social_metrics(account_id);
CREATE INDEX idx_social_metrics_platform ON social_metrics(platform);
CREATE INDEX idx_social_metrics_date ON social_metrics(measured_at DESC);

-- 5.2 Sentiment Analysis
CREATE TABLE sentiment_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    post_id INTEGER NOT NULL,
    platform VARCHAR(50) NOT NULL,
    comment_id VARCHAR(255),

    comment_text TEXT,
    comment_author VARCHAR(255),
    comment_date TIMESTAMP WITH TIME ZONE,

    sentiment_score DECIMAL(5,4) NOT NULL,
    sentiment_label VARCHAR(20) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,

    emotions JSONB,
    keywords TEXT[],

    ai_model VARCHAR(100),

    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sentiment_post ON sentiment_analysis(post_id);
CREATE INDEX idx_sentiment_account ON sentiment_analysis(account_id);
CREATE INDEX idx_sentiment_label ON sentiment_analysis(sentiment_label);
CREATE INDEX idx_sentiment_date ON sentiment_analysis(analyzed_at DESC);

-- 5.3 Competitor Profiles
CREATE TABLE competitor_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    website VARCHAR(500),
    description TEXT,

    social_handles JSONB DEFAULT '{}',

    industry VARCHAR(100),
    company_size VARCHAR(50),

    track_social BOOLEAN DEFAULT true,
    track_content BOOLEAN DEFAULT true,
    track_seo BOOLEAN DEFAULT false,

    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_competitors_account ON competitor_profiles(account_id);
CREATE INDEX idx_competitors_active ON competitor_profiles(is_active);

-- 5.4 Competitor Metrics
CREATE TABLE competitor_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competitor_id UUID NOT NULL REFERENCES competitor_profiles(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,

    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,
    avg_engagement_rate DECIMAL(10,6) DEFAULT 0,
    posting_frequency DECIMAL(10,4) DEFAULT 0,

    top_hashtags TEXT[],
    content_themes TEXT[],
    posting_times JSONB,

    our_followers_count INTEGER,
    our_avg_engagement_rate DECIMAL(10,6),
    our_posting_frequency DECIMAL(10,4),

    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_competitor_metrics_competitor ON competitor_metrics(competitor_id);
CREATE INDEX idx_competitor_metrics_date ON competitor_metrics(measured_at DESC);

-- 5.5 Performance Predictions
CREATE TABLE performance_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    prediction_type VARCHAR(50) NOT NULL,

    content_type VARCHAR(50),
    content_id UUID,

    predicted_value DECIMAL(15,4),
    confidence_interval_low DECIMAL(15,4),
    confidence_interval_high DECIMAL(15,4),
    confidence_level DECIMAL(5,4),

    factors JSONB,
    recommendations JSONB,

    ai_model VARCHAR(100),

    valid_from TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_to TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_predictions_account ON performance_predictions(account_id);
CREATE INDEX idx_predictions_type ON performance_predictions(prediction_type);
