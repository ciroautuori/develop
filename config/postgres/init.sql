-- ISS Database Initialization Script
-- Innovazione Sociale Salernitana - Production Setup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom schemas
CREATE SCHEMA IF NOT EXISTS iss_core;
CREATE SCHEMA IF NOT EXISTS iss_analytics;
CREATE SCHEMA IF NOT EXISTS iss_logs;

-- Set default search path
ALTER DATABASE iss_wbs SET search_path TO iss_core, public;

-- Create performance monitoring view
CREATE OR REPLACE VIEW iss_analytics.query_performance AS
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_time DESC;

-- Create indexes for common queries
-- These will be created by Alembic migrations, but we prepare the structure

-- Grant permissions
GRANT USAGE ON SCHEMA iss_core TO postgres;
GRANT USAGE ON SCHEMA iss_analytics TO postgres;
GRANT USAGE ON SCHEMA iss_logs TO postgres;

-- Log successful initialization
INSERT INTO iss_logs.initialization_log (timestamp, message) 
VALUES (NOW(), 'ISS Database initialized successfully')
ON CONFLICT DO NOTHING;
