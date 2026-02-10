-- =============================================================================
-- CyberGuardX — PostgreSQL Initialization Script
-- =============================================================================
-- Auto-executed by PostgreSQL Docker entrypoint on first run.
-- Creates all tables, indexes, and grants required by the application.
--
-- Tables:
--   scan_history   — email / URL scan audit log
--   website_scans  — comprehensive website security assessments
--   scan_progress  — real-time progress tracking for long-running scans

-- ---------------------------------------------------------------------------
-- 1. scan_history
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scan_history (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL,
    email_breached  BOOLEAN      NOT NULL,
    phishing_score  FLOAT,
    risk_level      VARCHAR(50)  NOT NULL,
    scanned_at      TIMESTAMP    NOT NULL DEFAULT NOW(),

    -- Enhanced breach information (v2.0)
    pwned_count     INTEGER      DEFAULT 0,
    breach_details  TEXT,
    breach_source   VARCHAR(50),
    last_checked    TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_scan_history_id
    ON scan_history (id);
CREATE INDEX IF NOT EXISTS idx_scan_history_email
    ON scan_history (email);
CREATE INDEX IF NOT EXISTS idx_scan_history_timestamp
    ON scan_history (scanned_at DESC);

-- ---------------------------------------------------------------------------
-- 2. website_scans
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS website_scans (
    id                    SERIAL PRIMARY KEY,
    url                   VARCHAR(2048) NOT NULL,
    client_ip             VARCHAR(45)   NOT NULL,

    -- Overall risk assessment
    risk_score            INTEGER       NOT NULL,
    risk_level            VARCHAR(50)   NOT NULL,
    overall_grade         VARCHAR(2)    NOT NULL,

    -- Individual scan results (JSON)
    http_scan_json        TEXT,
    ssl_scan_json         TEXT,
    dns_scan_json         TEXT,
    tech_scan_json        TEXT,
    owasp_assessment_json TEXT,

    -- Metadata
    scan_duration_ms      INTEGER,
    scanned_at            TIMESTAMP     NOT NULL DEFAULT NOW(),

    -- Legal / safety tracking
    permission_confirmed  BOOLEAN DEFAULT FALSE,
    owner_confirmed       BOOLEAN DEFAULT FALSE,
    legal_accepted        BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS ix_website_scans_id
    ON website_scans (id);
CREATE INDEX IF NOT EXISTS ix_website_scans_url
    ON website_scans (url);

-- ---------------------------------------------------------------------------
-- 3. scan_progress
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scan_progress (
    id                           SERIAL PRIMARY KEY,
    scan_id                      VARCHAR(36) NOT NULL UNIQUE,
    url                          VARCHAR(2048) NOT NULL,

    -- Progress tracking
    current_step                 VARCHAR(100) NOT NULL,
    progress_percentage          INTEGER      NOT NULL DEFAULT 0,
    step_details                 TEXT,

    -- Timing
    start_time                   TIMESTAMP NOT NULL DEFAULT NOW(),
    last_update                  TIMESTAMP NOT NULL DEFAULT NOW(),
    estimated_seconds_remaining  INTEGER,

    -- Status flags
    is_complete                  BOOLEAN DEFAULT FALSE,
    has_error                    BOOLEAN DEFAULT FALSE,
    error_message                VARCHAR(500),
    is_cancelled                 BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS ix_scan_progress_id
    ON scan_progress (id);
CREATE INDEX IF NOT EXISTS ix_scan_progress_scan_id
    ON scan_progress (scan_id);

-- ---------------------------------------------------------------------------
-- Done
-- ---------------------------------------------------------------------------
SELECT 'CyberGuardX database initialized successfully' AS status;
