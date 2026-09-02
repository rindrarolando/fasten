-- =============================================================================
-- template_pgsql.00.sql — Database & user creation for PostgreSQL
-- Copy this file, rename it (e.g. my_service.00.sql), and replace every
-- occurrence of <service_name> with your actual service name (e.g. product).
-- =============================================================================

CREATE DATABASE <service_name>_db ENCODING 'UTF8';

CREATE USER <service_name>_user WITH PASSWORD 'change_me';

GRANT ALL PRIVILEGES ON DATABASE <service_name>_db TO <service_name>_user;

-- Grant schema privileges for proper permission inheritance
ALTER DATABASE <service_name>_db OWNER TO <service_name>_user;

\c <service_name>_db

GRANT ALL PRIVILEGES ON SCHEMA public TO <service_name>_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO <service_name>_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO <service_name>_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO <service_name>_user;

-- Create the update_updated_at_column function (used by all tables in this DB)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
