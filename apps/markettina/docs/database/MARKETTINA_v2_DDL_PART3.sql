-- ============================================================================
-- MARKETTINA v2.0 - DDL SQL COMPLETO - PARTE 3
-- ============================================================================

-- ============================================================================
-- SECTION 6: SOCIAL CONTEXT - Estensioni
-- ============================================================================

-- 6.1 Cross-Post Configurations
CREATE TABLE cross_post_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    social_account_ids UUID[] NOT NULL,

    auto_adapt_dimensions BOOLEAN DEFAULT true,
    auto_adapt_caption_length BOOLEAN DEFAULT true,
    auto_adapt_hashtags BOOLEAN DEFAULT true,
    auto_adapt_mentions BOOLEAN DEFAULT true,

    platform_rules JSONB DEFAULT '{}',

    is_default BOOLEAN DEFAULT false,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_cross_post_configs_account ON cross_post_configs(account_id);

-- 6.2 Cross Posts
CREATE TABLE cross_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    original_post_id INTEGER NOT NULL,
    config_id UUID REFERENCES cross_post_configs(id),

    platform_posts JSONB NOT NULL DEFAULT '[]',

    status VARCHAR(50) DEFAULT 'pending',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_cross_posts_original ON cross_posts(original_post_id);
CREATE INDEX idx_cross_posts_account ON cross_posts(account_id);
CREATE INDEX idx_cross_posts_status ON cross_posts(status);

-- 6.3 Social Comments
CREATE TABLE social_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    post_id INTEGER NOT NULL,
    social_account_id UUID REFERENCES social_accounts(id),
    platform VARCHAR(50) NOT NULL,

    platform_comment_id VARCHAR(255) NOT NULL,
    parent_comment_id VARCHAR(255),

    author_name VARCHAR(255),
    author_handle VARCHAR(255),
    author_profile_url TEXT,
    comment_text TEXT NOT NULL,
    comment_date TIMESTAMP WITH TIME ZONE,

    likes_count INTEGER DEFAULT 0,
    replies_count INTEGER DEFAULT 0,

    our_reply_id VARCHAR(255),
    our_reply_text TEXT,
    replied_at TIMESTAMP WITH TIME ZONE,
    replied_by INTEGER REFERENCES users(id),

    status VARCHAR(50) DEFAULT 'new',
    requires_attention BOOLEAN DEFAULT false,

    sentiment_label VARCHAR(20),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_social_comments_post ON social_comments(post_id);
CREATE INDEX idx_social_comments_account ON social_comments(account_id);
CREATE INDEX idx_social_comments_status ON social_comments(status);
CREATE INDEX idx_social_comments_attention ON social_comments(requires_attention) WHERE requires_attention = true;

-- 6.4 Social Mentions
CREATE TABLE social_mentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255),
    platform_post_url TEXT,

    author_name VARCHAR(255),
    author_handle VARCHAR(255),
    author_followers INTEGER,

    mention_text TEXT,
    mention_date TIMESTAMP WITH TIME ZONE,

    mention_type VARCHAR(50),
    matched_keyword VARCHAR(255),

    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,

    sentiment_label VARCHAR(20),
    sentiment_score DECIMAL(5,4),

    status VARCHAR(50) DEFAULT 'new',

    response_post_id INTEGER,
    responded_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_mentions_account ON social_mentions(account_id);
CREATE INDEX idx_mentions_platform ON social_mentions(platform);
CREATE INDEX idx_mentions_date ON social_mentions(mention_date DESC);
CREATE INDEX idx_mentions_status ON social_mentions(status);

-- ============================================================================
-- SECTION 7: AI SERVICES CONTEXT - Estensioni
-- ============================================================================

-- 7.1 AI Jobs (queue asincrona)
CREATE TABLE ai_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    job_type VARCHAR(100) NOT NULL,

    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,

    input_data JSONB NOT NULL,
    result_data JSONB,

    error_message TEXT,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    tokens_consumed INTEGER DEFAULT 0,

    created_by INTEGER REFERENCES users(id),

    idempotency_key VARCHAR(255) UNIQUE
);

CREATE INDEX idx_ai_jobs_account ON ai_jobs(account_id);
CREATE INDEX idx_ai_jobs_status ON ai_jobs(status);
CREATE INDEX idx_ai_jobs_queue ON ai_jobs(status, priority, created_at) WHERE status IN ('pending', 'processing');
CREATE INDEX idx_ai_jobs_type ON ai_jobs(job_type);

-- 7.2 AI Job Logs
CREATE TABLE ai_job_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES ai_jobs(id) ON DELETE CASCADE,

    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_job_logs_job ON ai_job_logs(job_id);
CREATE INDEX idx_ai_job_logs_level ON ai_job_logs(level);

-- 7.3 Content Generations
CREATE TABLE content_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    job_id UUID REFERENCES ai_jobs(id),

    content_type VARCHAR(50) NOT NULL,

    prompt TEXT NOT NULL,
    context JSONB,

    generated_content TEXT NOT NULL,
    alternatives JSONB,

    ai_provider VARCHAR(50) NOT NULL,
    ai_model VARCHAR(100) NOT NULL,
    temperature DECIMAL(3,2),

    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,

    quality_score DECIMAL(5,4),
    user_rating INTEGER,
    user_feedback TEXT,

    was_used BOOLEAN DEFAULT false,
    used_in_post_id INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_content_gen_account ON content_generations(account_id);
CREATE INDEX idx_content_gen_type ON content_generations(content_type);
CREATE INDEX idx_content_gen_date ON content_generations(created_at DESC);

-- 7.4 Image Generations
CREATE TABLE image_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    job_id UUID REFERENCES ai_jobs(id),

    prompt TEXT NOT NULL,
    negative_prompt TEXT,
    style VARCHAR(100),

    width INTEGER,
    height INTEGER,
    aspect_ratio VARCHAR(20),

    image_url TEXT NOT NULL,
    thumbnail_url TEXT,

    ai_provider VARCHAR(50) NOT NULL,
    ai_model VARCHAR(100) NOT NULL,

    seed BIGINT,

    quality_score DECIMAL(5,4),
    user_rating INTEGER,

    was_used BOOLEAN DEFAULT false,
    used_in_post_id INTEGER,
    media_asset_id UUID REFERENCES media_assets(id),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_image_gen_account ON image_generations(account_id);
CREATE INDEX idx_image_gen_date ON image_generations(created_at DESC);

-- 7.5 Video Generations
CREATE TABLE video_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    job_id UUID REFERENCES ai_jobs(id),

    prompt TEXT NOT NULL,
    script TEXT,
    style VARCHAR(100),

    duration_seconds INTEGER,
    aspect_ratio VARCHAR(20),
    resolution VARCHAR(20),

    video_url TEXT,
    thumbnail_url TEXT,

    ai_provider VARCHAR(50) NOT NULL,
    ai_model VARCHAR(100) NOT NULL,

    status VARCHAR(50) DEFAULT 'pending',
    progress_percent INTEGER DEFAULT 0,

    quality_score DECIMAL(5,4),
    user_rating INTEGER,

    was_used BOOLEAN DEFAULT false,
    used_in_post_id INTEGER,
    media_asset_id UUID REFERENCES media_assets(id),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_video_gen_account ON video_generations(account_id);
CREATE INDEX idx_video_gen_status ON video_generations(status);

-- 7.6 Brand DNA
CREATE TABLE brand_dna (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID UNIQUE NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    company_name VARCHAR(255),
    tagline TEXT,
    mission TEXT,
    vision TEXT,
    brand_story TEXT,

    tone_of_voice VARCHAR(50),
    writing_style JSONB,

    primary_color VARCHAR(7),
    secondary_colors VARCHAR(7)[],
    accent_color VARCHAR(7),
    font_family VARCHAR(100),
    logo_url TEXT,

    core_values TEXT[],

    target_demographics JSONB,
    target_psychographics JSONB,
    target_industries TEXT[],
    target_company_sizes TEXT[],
    target_regions TEXT[],

    keywords TEXT[],
    competitor_ids UUID[],
    usp TEXT,
    sector VARCHAR(100),

    preferred_languages VARCHAR(10)[],
    default_hashtags TEXT[],
    cta_templates TEXT[],
    emoji_usage VARCHAR(20),

    ai_persona TEXT,
    forbidden_words TEXT[],
    typical_customer_journey TEXT,
    pain_points_addressed TEXT[],

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_brand_dna_account ON brand_dna(account_id);

-- 7.7 Brand DNA Versions
CREATE TABLE brand_dna_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_dna_id UUID NOT NULL REFERENCES brand_dna(id) ON DELETE CASCADE,

    version_number INTEGER NOT NULL,

    snapshot JSONB NOT NULL,

    change_summary TEXT,
    changed_fields TEXT[],

    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    changed_by INTEGER REFERENCES users(id),

    CONSTRAINT uq_brand_dna_version UNIQUE (brand_dna_id, version_number)
);

CREATE INDEX idx_brand_dna_versions_dna ON brand_dna_versions(brand_dna_id);
