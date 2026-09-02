-- =============================================================================
-- template_mysql.01.sql — Table definitions for MySQL / MariaDB
-- Copy this file, rename it (e.g. my_service.01.sql), and customise the
-- table structure to match your domain models.
-- =============================================================================

USE <service_name>_db;

-- -----------------------------------------------------------------------------
-- Table: example
-- Rename to your entity (e.g. product, order). Add/remove columns as needed.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS example (
    id         BIGINT       AUTO_INCREMENT PRIMARY KEY,
    uid        CHAR(32)     NOT NULL UNIQUE,          -- formatted UUID (no hyphens)
    name       VARCHAR(255) NOT NULL,
    meta       JSON,                                  -- optional freeform payload
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    -- Add indexes on foreign keys or frequently-filtered columns:
    -- INDEX ix_example_<col> (<col>)
);
