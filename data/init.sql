-- Avaire Database Initialization Script
-- This script runs automatically when PostgreSQL container starts

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Database is already created via POSTGRES_DB environment variable
-- Tables are created by SQLAlchemy in the FastAPI application

-- Create a simple test function to verify database is ready
CREATE OR REPLACE FUNCTION database_initialized()
RETURNS TEXT AS $$
BEGIN
    RETURN 'Avaire database initialized successfully';
END;
$$ LANGUAGE plpgsql;

-- Verify function works
SELECT database_initialized();
