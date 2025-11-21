-- Migration: Add email_audit_log table
-- Created: 2025-11-13
-- Description: Create email_audit_log table for tracking all sent emails

-- For PostgreSQL:
CREATE TABLE IF NOT EXISTS email_audit_log (
    id VARCHAR(26) PRIMARY KEY,

    -- Recipients
    recipient_email VARCHAR(255) NOT NULL,
    sender_email VARCHAR(255),

    -- Content
    subject VARCHAR(500) NOT NULL,
    html_body TEXT,
    text_body TEXT,

    -- Template info
    template_name VARCHAR(100),
    template_context JSONB,

    -- Status & Tracking
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    adapter VARCHAR(50) NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,

    -- Error handling
    error_message TEXT,
    error_code VARCHAR(50),
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    -- Metadata
    extra_metadata JSONB,

    -- Related entities
    user_id VARCHAR(26),
    related_entity_type VARCHAR(50),
    related_entity_id VARCHAR(26)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_email_audit_recipient ON email_audit_log(recipient_email);
CREATE INDEX IF NOT EXISTS idx_email_audit_template ON email_audit_log(template_name);
CREATE INDEX IF NOT EXISTS idx_email_audit_status ON email_audit_log(status);
CREATE INDEX IF NOT EXISTS idx_email_audit_created ON email_audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_email_audit_user ON email_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_email_audit_status_created ON email_audit_log(status, created_at);
CREATE INDEX IF NOT EXISTS idx_email_audit_user_created ON email_audit_log(user_id, created_at);

-- For SQLite (alternative):
-- Note: SQLite doesn't support JSONB, use JSON instead
-- Also, TIMESTAMP WITH TIME ZONE becomes DATETIME
--
-- CREATE TABLE IF NOT EXISTS email_audit_log (
--     id VARCHAR(26) PRIMARY KEY,
--     recipient_email VARCHAR(255) NOT NULL,
--     sender_email VARCHAR(255),
--     subject VARCHAR(500) NOT NULL,
--     html_body TEXT,
--     text_body TEXT,
--     template_name VARCHAR(100),
--     template_context TEXT,  -- JSON stored as TEXT
--     status VARCHAR(20) NOT NULL DEFAULT 'pending',
--     adapter VARCHAR(50) NOT NULL,
--     created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     sent_at DATETIME,
--     failed_at DATETIME,
--     opened_at DATETIME,
--     clicked_at DATETIME,
--     error_message TEXT,
--     error_code VARCHAR(50),
--     retry_count INTEGER DEFAULT 0,
--     max_retries INTEGER DEFAULT 3,
--     extra_metadata TEXT,  -- JSON stored as TEXT
--     user_id VARCHAR(26),
--     related_entity_type VARCHAR(50),
--     related_entity_id VARCHAR(26)
-- );
