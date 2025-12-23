-- ============================================================================
-- MARKETTINA v2.0 - DDL SQL COMPLETO - PARTE 4
-- ============================================================================

-- ============================================================================
-- SECTION 8: WORKFLOW CONTEXT - Estensioni
-- ============================================================================

-- 8.1 Workflows (persistenza DB)
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    trigger_type VARCHAR(50) NOT NULL,
    trigger_config JSONB NOT NULL,

    actions JSONB NOT NULL DEFAULT '[]',

    status VARCHAR(50) DEFAULT 'draft',

    execution_count INTEGER DEFAULT 0,
    last_executed_at TIMESTAMP WITH TIME ZONE,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,

    is_template BOOLEAN DEFAULT false,
    template_category VARCHAR(100),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_workflows_account ON workflows(account_id);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_trigger ON workflows(trigger_type);
CREATE INDEX idx_workflows_template ON workflows(is_template) WHERE is_template = true;

-- 8.2 Workflow Executions
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    status VARCHAR(50) DEFAULT 'pending',

    current_action_index INTEGER DEFAULT 0,
    current_action_id VARCHAR(100),

    trigger_context JSONB,
    execution_context JSONB DEFAULT '{}',

    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    next_action_at TIMESTAMP WITH TIME ZONE,

    error_message TEXT,
    error_action_id VARCHAR(100),

    triggered_by VARCHAR(50),
    triggered_by_user INTEGER REFERENCES users(id)
);

CREATE INDEX idx_workflow_exec_workflow ON workflow_executions(workflow_id);
CREATE INDEX idx_workflow_exec_account ON workflow_executions(account_id);
CREATE INDEX idx_workflow_exec_status ON workflow_executions(status);
CREATE INDEX idx_workflow_exec_next ON workflow_executions(next_action_at) WHERE status = 'waiting';

-- 8.3 Workflow Logs
CREATE TABLE workflow_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,

    action_id VARCHAR(100),
    action_type VARCHAR(50),
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_workflow_logs_exec ON workflow_logs(execution_id);
CREATE INDEX idx_workflow_logs_level ON workflow_logs(level);

-- 8.4 Workflow Schedules
CREATE TABLE workflow_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,

    cron_expression VARCHAR(100) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'Europe/Rome',

    is_active BOOLEAN DEFAULT true,

    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    run_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_workflow_schedules_workflow ON workflow_schedules(workflow_id);
CREATE INDEX idx_workflow_schedules_next ON workflow_schedules(next_run_at) WHERE is_active = true;

-- 8.5 Approval Workflows
CREATE TABLE approval_workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    steps JSONB NOT NULL,

    content_types TEXT[],

    is_default BOOLEAN DEFAULT false,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_approval_workflows_account ON approval_workflows(account_id);

-- 8.6 Content Approvals
CREATE TABLE content_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    content_type VARCHAR(50) NOT NULL,
    content_id UUID NOT NULL,

    workflow_id UUID REFERENCES approval_workflows(id),

    current_step INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'pending',

    approvals JSONB DEFAULT '[]',

    delegated_to INTEGER REFERENCES users(id),
    delegation_expires_at TIMESTAMP WITH TIME ZONE,

    due_date TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_content_approval UNIQUE (content_type, content_id)
);

CREATE INDEX idx_content_approvals_account ON content_approvals(account_id);
CREATE INDEX idx_content_approvals_content ON content_approvals(content_type, content_id);
CREATE INDEX idx_content_approvals_status ON content_approvals(status);

-- ============================================================================
-- SECTION 9: KNOWLEDGE BASE CONTEXT
-- ============================================================================

-- 9.1 Document Categories (prima per FK)
CREATE TABLE document_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    parent_id UUID REFERENCES document_categories(id),

    icon VARCHAR(50),
    color VARCHAR(7),
    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_doc_categories_account ON document_categories(account_id);
CREATE INDEX idx_doc_categories_parent ON document_categories(parent_id);

-- 9.2 Knowledge Documents
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    title VARCHAR(500) NOT NULL,
    description TEXT,

    source_type VARCHAR(50) NOT NULL,
    source_url TEXT,
    original_filename VARCHAR(255),

    content_text TEXT,
    content_hash VARCHAR(64),

    file_size_bytes BIGINT,
    mime_type VARCHAR(100),

    processing_status VARCHAR(50) DEFAULT 'pending',
    chunks_count INTEGER DEFAULT 0,

    vector_store VARCHAR(50),
    namespace VARCHAR(255),

    category_id UUID REFERENCES document_categories(id),

    tags TEXT[],

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_knowledge_docs_account ON knowledge_documents(account_id);
CREATE INDEX idx_knowledge_docs_status ON knowledge_documents(processing_status);
CREATE INDEX idx_knowledge_docs_category ON knowledge_documents(category_id);

-- 9.3 Document Chunks
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,

    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_size INTEGER NOT NULL,

    embedding_id VARCHAR(255),
    embedding_model VARCHAR(100),

    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_document_chunk UNIQUE (document_id, chunk_index)
);

CREATE INDEX idx_doc_chunks_document ON document_chunks(document_id);

-- 9.4 Search History
CREATE TABLE search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),

    query_text TEXT NOT NULL,
    query_type VARCHAR(50),

    results_count INTEGER,
    top_results JSONB,

    was_helpful BOOLEAN,
    selected_result_id UUID,

    response_time_ms INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_search_history_account ON search_history(account_id);
CREATE INDEX idx_search_history_user ON search_history(user_id);
CREATE INDEX idx_search_history_date ON search_history(created_at DESC);

-- ============================================================================
-- SECTION 10: SHARED KERNEL (Cross-Cutting Concerns)
-- ============================================================================

-- 10.1 Domain Events (Event Sourcing con Partitioning)
CREATE TABLE domain_events (
    id UUID DEFAULT gen_random_uuid(),

    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,

    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,

    metadata JSONB DEFAULT '{}',

    aggregate_version INTEGER NOT NULL,

    account_id UUID NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMP WITH TIME ZONE,

    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE domain_events_2024_12 PARTITION OF domain_events
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');
CREATE TABLE domain_events_2025_01 PARTITION OF domain_events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE domain_events_2025_02 PARTITION OF domain_events
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE domain_events_2025_03 PARTITION OF domain_events
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE INDEX idx_events_aggregate ON domain_events(aggregate_type, aggregate_id);
CREATE INDEX idx_events_account ON domain_events(account_id);
CREATE INDEX idx_events_type ON domain_events(event_type);
CREATE INDEX idx_events_unprocessed ON domain_events(processed, created_at) WHERE processed = false;

-- 10.2 Feature Flags
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    feature_name VARCHAR(100) NOT NULL,
    description TEXT,

    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,

    enabled BOOLEAN DEFAULT false,

    config JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),

    CONSTRAINT uq_feature_flag UNIQUE (account_id, feature_name)
);

CREATE INDEX idx_feature_flags_name ON feature_flags(feature_name);
CREATE INDEX idx_feature_flags_account ON feature_flags(account_id);

-- 10.3 Webhooks
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    url TEXT NOT NULL,

    secret VARCHAR(255),

    events TEXT[] NOT NULL,

    is_active BOOLEAN DEFAULT true,

    retry_count INTEGER DEFAULT 3,
    retry_delay_seconds INTEGER DEFAULT 60,

    total_deliveries INTEGER DEFAULT 0,
    successful_deliveries INTEGER DEFAULT 0,
    failed_deliveries INTEGER DEFAULT 0,
    last_delivery_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_webhooks_account ON webhooks(account_id);
CREATE INDEX idx_webhooks_active ON webhooks(is_active) WHERE is_active = true;

-- 10.4 Webhook Deliveries
CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,

    event_type VARCHAR(100) NOT NULL,
    event_id UUID,

    payload JSONB NOT NULL,

    status VARCHAR(50) DEFAULT 'pending',

    response_code INTEGER,
    response_body TEXT,
    response_time_ms INTEGER,

    attempts INTEGER DEFAULT 0,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    last_error TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_webhook_deliveries_webhook ON webhook_deliveries(webhook_id);
CREATE INDEX idx_webhook_deliveries_status ON webhook_deliveries(status);
CREATE INDEX idx_webhook_deliveries_retry ON webhook_deliveries(next_retry_at) WHERE status = 'pending';

-- 10.5 API Rate Limits
CREATE TABLE api_rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    endpoint VARCHAR(200) NOT NULL,

    limit_per_minute INTEGER,
    limit_per_hour INTEGER,
    limit_per_day INTEGER,

    current_minute_count INTEGER DEFAULT 0,
    current_hour_count INTEGER DEFAULT 0,
    current_day_count INTEGER DEFAULT 0,

    reset_minute_at TIMESTAMP WITH TIME ZONE,
    reset_hour_at TIMESTAMP WITH TIME ZONE,
    reset_day_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_rate_limit UNIQUE (account_id, endpoint)
);

CREATE INDEX idx_rate_limits_account ON api_rate_limits(account_id);
CREATE INDEX idx_rate_limits_endpoint ON api_rate_limits(endpoint);

-- 10.6 Idempotency Keys
CREATE TABLE idempotency_keys (
    key VARCHAR(255) PRIMARY KEY,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    endpoint VARCHAR(200) NOT NULL,
    request_hash VARCHAR(64),

    response_data JSONB,
    status_code INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '24 hours'
);

CREATE INDEX idx_idempotency_account ON idempotency_keys(account_id);
CREATE INDEX idx_idempotency_expiry ON idempotency_keys(expires_at);

-- 10.7 Async Jobs (generic job queue)
CREATE TABLE async_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    job_type VARCHAR(100) NOT NULL,

    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,

    input_data JSONB NOT NULL,
    result_data JSONB,

    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    scheduled_at TIMESTAMP WITH TIME ZONE,

    created_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_async_jobs_account ON async_jobs(account_id);
CREATE INDEX idx_async_jobs_status ON async_jobs(status);
CREATE INDEX idx_async_jobs_queue ON async_jobs(status, priority, created_at) WHERE status = 'pending';
CREATE INDEX idx_async_jobs_scheduled ON async_jobs(scheduled_at) WHERE status = 'pending' AND scheduled_at IS NOT NULL;
