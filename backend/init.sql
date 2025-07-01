-- backend/init.sql - ALVIN Database Initialization
-- This file initializes the PostgreSQL database for ALVIN

-- Create the main database (if not already created by environment)
-- The database 'alvin' should be created by environment variables
-- but we can ensure it exists and set up initial configuration

-- Set up extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create initial database user if needed (usually handled by environment)
-- DO $$ 
-- BEGIN
--    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'alvin_user') THEN
--       CREATE USER alvin_user WITH PASSWORD 'alvin_password';
--    END IF;
-- END
-- $$;

-- Grant permissions
-- GRANT ALL PRIVILEGES ON DATABASE alvin TO alvin_user;

-- Create a basic health check function
CREATE OR REPLACE FUNCTION health_check() 
RETURNS TEXT AS $$
BEGIN
    RETURN 'ALVIN Database is healthy - ' || NOW()::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Log initialization
SELECT 'ALVIN database initialization completed' AS status;