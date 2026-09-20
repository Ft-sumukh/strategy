-- ==============================================================================
-- AEGIS INVEST — Initial Database Initialization Script
-- Executed on first PostgreSQL container startup by Docker entrypoint
-- ==============================================================================

-- Enable UUID generation extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for cryptographic functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Log database initialization
DO $$
BEGIN
    RAISE NOTICE 'AEGIS INVEST database initialized successfully at %', NOW();
END $$;
