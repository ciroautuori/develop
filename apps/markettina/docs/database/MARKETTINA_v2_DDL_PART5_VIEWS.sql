-- ============================================================================
-- MARKETTINA v2.0 - DDL SQL COMPLETO - PARTE 5
-- MATERIALIZED VIEWS & TRIGGERS
-- ============================================================================

-- ============================================================================
-- SECTION 11: MATERIALIZED VIEWS (CQRS Read Models)
-- ============================================================================

-- 11.1 Dashboard KPIs
CREATE MATERIALIZED VIEW mv_dashboard_kpis AS
SELECT
    a.id as account_id,
    -- Leads
    COUNT(DISTINCT l.id) as total_leads,
    COUNT(DISTINCT CASE WHEN l.status = 'WON' THEN l.id END) as converted_leads,
    AVG(l.score) as avg_lead_score,
    -- Posts
    COUNT(DISTINCT sp.id) as total_posts,
    COUNT(DISTINCT CASE WHEN sp.status = 'published' THEN sp.id END) as published_posts,
    -- Campaigns
    COUNT(DISTINCT c.id) as total_campaigns,
    COUNT(DISTINCT CASE WHEN c.status = 'active' THEN c.id END) as active_campaigns,
    -- Token usage (last 30 days)
    COALESCE(SUM(CASE WHEN tt.type = 'usage' AND tt.created_at > NOW() - INTERVAL '30 days' THEN ABS(tt.amount) END), 0) as tokens_used_30d,
    -- Last activity
    MAX(GREATEST(l.created_at, sp.created_at, c.created_at)) as last_activity_at
FROM accounts a
LEFT JOIN leads l ON l.created_at > NOW() - INTERVAL '90 days'
LEFT JOIN scheduled_posts sp ON sp.created_at > NOW() - INTERVAL '90 days'
LEFT JOIN campaigns c ON c.account_id = a.id AND c.deleted_at IS NULL
LEFT JOIN token_transactions tt ON tt.created_at > NOW() - INTERVAL '30 days'
WHERE a.deleted_at IS NULL
GROUP BY a.id;

CREATE UNIQUE INDEX idx_mv_dashboard_kpis_account ON mv_dashboard_kpis(account_id);

-- 11.2 Social Performance per Platform
CREATE MATERIALIZED VIEW mv_social_performance AS
SELECT
    sm.account_id,
    sm.platform,
    DATE_TRUNC('day', sm.measured_at) as date,
    COUNT(DISTINCT sm.post_id) as posts_count,
    SUM(sm.impressions) as total_impressions,
    SUM(sm.reach) as total_reach,
    SUM(sm.engagement_count) as total_engagement,
    SUM(sm.clicks) as total_clicks,
    AVG(sm.engagement_rate) as avg_engagement_rate,
    AVG(sm.click_through_rate) as avg_ctr
FROM social_metrics sm
WHERE sm.measured_at > NOW() - INTERVAL '90 days'
GROUP BY sm.account_id, sm.platform, DATE_TRUNC('day', sm.measured_at);

CREATE INDEX idx_mv_social_perf_account ON mv_social_performance(account_id);
CREATE INDEX idx_mv_social_perf_date ON mv_social_performance(date DESC);

-- 11.3 Lead Funnel Stats
CREATE MATERIALIZED VIEW mv_lead_funnel AS
SELECT
    DATE_TRUNC('week', l.created_at) as week,
    l.source,
    COUNT(*) as total_leads,
    COUNT(CASE WHEN l.status = 'NEW' THEN 1 END) as status_new,
    COUNT(CASE WHEN l.status = 'CONTACTED' THEN 1 END) as status_contacted,
    COUNT(CASE WHEN l.status = 'QUALIFIED' THEN 1 END) as status_qualified,
    COUNT(CASE WHEN l.status = 'PROPOSAL_SENT' THEN 1 END) as status_proposal,
    COUNT(CASE WHEN l.status = 'NEGOTIATION' THEN 1 END) as status_negotiation,
    COUNT(CASE WHEN l.status = 'WON' THEN 1 END) as status_won,
    COUNT(CASE WHEN l.status = 'LOST' THEN 1 END) as status_lost,
    AVG(l.score) as avg_score,
    -- Conversion rate
    CASE
        WHEN COUNT(*) > 0
        THEN (COUNT(CASE WHEN l.status = 'WON' THEN 1 END)::DECIMAL / COUNT(*)) * 100
        ELSE 0
    END as conversion_rate
FROM leads l
WHERE l.created_at > NOW() - INTERVAL '1 year'
GROUP BY DATE_TRUNC('week', l.created_at), l.source;

CREATE INDEX idx_mv_lead_funnel_week ON mv_lead_funnel(week DESC);

-- 11.4 Content Performance Summary
CREATE MATERIALIZED VIEW mv_content_performance AS
SELECT
    sp.id as post_id,
    sp.account_id,
    sp.platforms,
    sp.status,
    sp.scheduled_at,
    sp.published_at,
    sp.ai_generated,
    -- Aggregated metrics
    COALESCE(SUM(sm.impressions), 0) as total_impressions,
    COALESCE(SUM(sm.engagement_count), 0) as total_engagement,
    COALESCE(AVG(sm.engagement_rate), 0) as avg_engagement_rate,
    COALESCE(SUM(sm.clicks), 0) as total_clicks,
    -- Sentiment
    COALESCE(AVG(sa.sentiment_score), 0) as avg_sentiment,
    COUNT(sa.id) as comments_analyzed
FROM scheduled_posts sp
LEFT JOIN social_metrics sm ON sm.post_id = sp.id
LEFT JOIN sentiment_analysis sa ON sa.post_id = sp.id
WHERE sp.status = 'published'
  AND sp.published_at > NOW() - INTERVAL '90 days'
GROUP BY sp.id, sp.account_id, sp.platforms, sp.status, sp.scheduled_at, sp.published_at, sp.ai_generated;

CREATE INDEX idx_mv_content_perf_account ON mv_content_performance(account_id);
CREATE INDEX idx_mv_content_perf_date ON mv_content_performance(published_at DESC);

-- 11.5 AI Usage Analytics
CREATE MATERIALIZED VIEW mv_ai_usage AS
SELECT
    cg.account_id,
    DATE_TRUNC('day', cg.created_at) as date,
    cg.content_type,
    cg.ai_provider,
    cg.ai_model,
    COUNT(*) as generation_count,
    SUM(cg.total_tokens) as total_tokens,
    AVG(cg.quality_score) as avg_quality,
    COUNT(CASE WHEN cg.was_used THEN 1 END) as used_count,
    -- Usage rate
    CASE
        WHEN COUNT(*) > 0
        THEN (COUNT(CASE WHEN cg.was_used THEN 1 END)::DECIMAL / COUNT(*)) * 100
        ELSE 0
    END as usage_rate
FROM content_generations cg
WHERE cg.created_at > NOW() - INTERVAL '90 days'
GROUP BY cg.account_id, DATE_TRUNC('day', cg.created_at), cg.content_type, cg.ai_provider, cg.ai_model;

CREATE INDEX idx_mv_ai_usage_account ON mv_ai_usage(account_id);
CREATE INDEX idx_mv_ai_usage_date ON mv_ai_usage(date DESC);

-- 11.6 Competitor Comparison
CREATE MATERIALIZED VIEW mv_competitor_comparison AS
SELECT
    cp.account_id,
    cp.id as competitor_id,
    cp.name as competitor_name,
    cm.platform,
    cm.followers_count as competitor_followers,
    cm.avg_engagement_rate as competitor_engagement,
    cm.posting_frequency as competitor_frequency,
    cm.our_followers_count,
    cm.our_avg_engagement_rate,
    cm.our_posting_frequency,
    -- Comparison
    CASE
        WHEN cm.followers_count > 0
        THEN ((cm.our_followers_count - cm.followers_count)::DECIMAL / cm.followers_count) * 100
        ELSE 0
    END as followers_diff_pct,
    CASE
        WHEN cm.avg_engagement_rate > 0
        THEN ((cm.our_avg_engagement_rate - cm.avg_engagement_rate) / cm.avg_engagement_rate) * 100
        ELSE 0
    END as engagement_diff_pct,
    cm.measured_at
FROM competitor_profiles cp
JOIN competitor_metrics cm ON cm.competitor_id = cp.id
WHERE cp.is_active = true
  AND cm.measured_at = (
      SELECT MAX(measured_at)
      FROM competitor_metrics
      WHERE competitor_id = cp.id AND platform = cm.platform
  );

CREATE INDEX idx_mv_competitor_account ON mv_competitor_comparison(account_id);

-- ============================================================================
-- SECTION 12: REFRESH FUNCTIONS
-- ============================================================================

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_kpis;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_social_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_lead_funnel;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_content_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ai_usage;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_competitor_comparison;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECTION 13: TRIGGERS
-- ============================================================================

-- 13.1 Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
          AND table_schema = 'public'
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS trigger_update_updated_at ON %I;
            CREATE TRIGGER trigger_update_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        ', t, t);
    END LOOP;
END;
$$;

-- 13.2 Auto-increment version for optimistic locking
CREATE OR REPLACE FUNCTION increment_version()
RETURNS TRIGGER AS $$
BEGIN
    NEW.version = COALESCE(OLD.version, 0) + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables with version column
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'version'
          AND table_schema = 'public'
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS trigger_increment_version ON %I;
            CREATE TRIGGER trigger_increment_version
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION increment_version();
        ', t, t);
    END LOOP;
END;
$$;

-- 13.3 Event Sourcing - Auto-create domain event on important changes
CREATE OR REPLACE FUNCTION create_domain_event()
RETURNS TRIGGER AS $$
DECLARE
    event_type TEXT;
    aggregate_type TEXT;
BEGIN
    aggregate_type := TG_TABLE_NAME;

    IF TG_OP = 'INSERT' THEN
        event_type := aggregate_type || '_created';
    ELSIF TG_OP = 'UPDATE' THEN
        event_type := aggregate_type || '_updated';
    ELSIF TG_OP = 'DELETE' THEN
        event_type := aggregate_type || '_deleted';
    END IF;

    INSERT INTO domain_events (
        aggregate_type,
        aggregate_id,
        event_type,
        event_data,
        metadata,
        aggregate_version,
        account_id,
        created_at
    ) VALUES (
        aggregate_type,
        COALESCE(NEW.id, OLD.id)::UUID,
        event_type,
        CASE
            WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD)
            ELSE to_jsonb(NEW)
        END,
        jsonb_build_object(
            'operation', TG_OP,
            'table', TG_TABLE_NAME,
            'timestamp', NOW()
        ),
        COALESCE(NEW.version, OLD.version, 1),
        COALESCE(NEW.account_id, OLD.account_id)::UUID,
        NOW()
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply event sourcing to critical tables
-- (Uncomment to enable - can generate many events)
/*
CREATE TRIGGER trigger_event_sourcing_leads
AFTER INSERT OR UPDATE OR DELETE ON leads
FOR EACH ROW EXECUTE FUNCTION create_domain_event();

CREATE TRIGGER trigger_event_sourcing_campaigns
AFTER INSERT OR UPDATE OR DELETE ON campaigns
FOR EACH ROW EXECUTE FUNCTION create_domain_event();

CREATE TRIGGER trigger_event_sourcing_brand_dna
AFTER INSERT OR UPDATE OR DELETE ON brand_dna
FOR EACH ROW EXECUTE FUNCTION create_domain_event();
*/

-- 13.4 Token balance update trigger
CREATE OR REPLACE FUNCTION update_token_balance()
RETURNS TRIGGER AS $$
BEGIN
    -- Update wallet balance after transaction
    UPDATE token_wallets
    SET
        balance = balance + NEW.amount,
        total_purchased = CASE WHEN NEW.type = 'purchase' THEN total_purchased + NEW.amount ELSE total_purchased END,
        total_used = CASE WHEN NEW.type = 'usage' THEN total_used + ABS(NEW.amount) ELSE total_used END,
        total_bonus = CASE WHEN NEW.type = 'bonus' THEN total_bonus + NEW.amount ELSE total_bonus END,
        total_refunded = CASE WHEN NEW.type = 'refund' THEN total_refunded + NEW.amount ELSE total_refunded END,
        last_purchase_at = CASE WHEN NEW.type = 'purchase' THEN NOW() ELSE last_purchase_at END,
        last_usage_at = CASE WHEN NEW.type = 'usage' THEN NOW() ELSE last_usage_at END,
        updated_at = NOW()
    WHERE id = NEW.wallet_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 13.5 Promo code usage counter
CREATE OR REPLACE FUNCTION increment_promo_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE promo_codes
    SET current_uses = current_uses + 1
    WHERE id = NEW.promo_code_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_promo_usage
AFTER INSERT ON promo_redemptions
FOR EACH ROW EXECUTE FUNCTION increment_promo_usage();

-- ============================================================================
-- SECTION 14: ROW LEVEL SECURITY (Multi-Tenancy)
-- ============================================================================

-- Enable RLS on all tenant tables
ALTER TABLE social_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE media_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhooks ENABLE ROW LEVEL SECURITY;

-- Create policies (example for social_accounts)
CREATE POLICY social_accounts_isolation ON social_accounts
    USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY campaigns_isolation ON campaigns
    USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY content_templates_isolation ON content_templates
    USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY media_assets_isolation ON media_assets
    USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY social_metrics_isolation ON social_metrics
    USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY competitor_profiles_isolation ON competitor_profiles
    USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY ai_jobs_isolation ON ai_jobs
    USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY workflows_isolation ON workflows
    USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY knowledge_documents_isolation ON knowledge_documents
    USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY webhooks_isolation ON webhooks
    USING (account_id = current_setting('app.current_account_id', true)::uuid);

-- ============================================================================
-- SECTION 15: SCHEDULED JOBS (pg_cron)
-- ============================================================================

-- Refresh materialized views every 15 minutes
-- SELECT cron.schedule('refresh_mv', '*/15 * * * *', 'SELECT refresh_all_materialized_views()');

-- Clean expired idempotency keys daily
-- SELECT cron.schedule('clean_idempotency', '0 3 * * *', 'DELETE FROM idempotency_keys WHERE expires_at < NOW()');

-- Archive old domain events monthly (move to cold storage)
-- SELECT cron.schedule('archive_events', '0 2 1 * *', 'DELETE FROM domain_events WHERE created_at < NOW() - INTERVAL ''6 months'' AND processed = true');

-- ============================================================================
-- END OF DDL
-- ============================================================================
