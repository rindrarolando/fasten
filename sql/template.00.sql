-- =============================================================================
-- template.00.sql — Database & user creation
-- Copy this file, rename it (e.g. my_service.00.sql), and replace every
-- occurrence of <service_name> with your actual service name (e.g. product).
-- =============================================================================

-- --- MySQL / MariaDB ---
CREATE DATABASE IF NOT EXISTS <service_name>_db
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_0900_ai_ci;

SET time_zone = 'UTC';

CREATE USER IF NOT EXISTS '<service_name>_user'@'%' IDENTIFIED BY 'change_me';

GRANT ALL PRIVILEGES ON <service_name>_db.* TO '<service_name>_user'@'%';

FLUSH PRIVILEGES;


-- --- PostgreSQL equivalent (comment out MySQL block above and use this instead) ---
-- CREATE DATABASE <service_name>_db;
-- CREATE USER <service_name>_user WITH PASSWORD 'change_me';
-- GRANT ALL PRIVILEGES ON DATABASE <service_name>_db TO <service_name>_user;
