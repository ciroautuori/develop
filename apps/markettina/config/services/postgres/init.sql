-- ============================================================================
-- markettina - PostgreSQL Initialization Script
-- ============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS content;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS ai;

-- Set default search path
ALTER DATABASE markettina SET search_path TO public, auth, content, analytics, ai;

-- Create roles
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'markettina_readonly') THEN
        CREATE ROLE markettina_readonly;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'markettina_readwrite') THEN
        CREATE ROLE markettina_readwrite;
    END IF;
END
$$;

-- Grant permissions
GRANT CONNECT ON DATABASE markettina TO markettina_readonly;
GRANT USAGE ON SCHEMA public, auth, content, analytics, ai TO markettina_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public, auth, content, analytics, ai TO markettina_readonly;

GRANT CONNECT ON DATABASE markettina TO markettina_readwrite;
GRANT USAGE, CREATE ON SCHEMA public, auth, content, analytics, ai TO markettina_readwrite;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public, auth, content, analytics, ai TO markettina_readwrite;

-- Create audit log function
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.created_at = NOW();
        NEW.updated_at = NOW();
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'markettina database initialized successfully';
END
$$;
