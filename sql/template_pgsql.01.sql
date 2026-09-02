-- =============================================================================
-- template_pgsql.01.sql — Table definitions for PostgreSQL
-- Copy this file, rename it (e.g. my_service.01.sql), and customise the
-- table structure to match your domain models.
-- =============================================================================

-- NOTE: This assumes the update_updated_at_column() function was created in template_pgsql.00.sql
-- For additional tables in the same DB, only create the trigger (don't recreate the function)

-- \c <service_name>_db

SET search_path TO public;

-- -----------------------------------------------------------------------------
-- Table: example
-- Rename to your entity (e.g. product, order). Add/remove columns as needed.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS example (
    id         BIGSERIAL    PRIMARY KEY,
    uid        CHAR(32)     NOT NULL UNIQUE,          -- formatted UUID (no hyphens)
    name       VARCHAR(255) NOT NULL,
    meta       JSONB,                                 -- optional freeform payload
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
    -- Add indexes on foreign keys or frequently-filtered columns:
    -- CREATE INDEX ix_example_<col> ON example (<col>)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_example_uid ON example (uid);

-- Create trigger to auto-update the updated_at timestamp
CREATE TRIGGER tr_example_updated_at
BEFORE UPDATE ON example
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
