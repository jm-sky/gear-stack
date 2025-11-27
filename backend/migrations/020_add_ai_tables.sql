-- AI Module Tables Migration for SQLite
-- Run with: sqlite3 backend/data/app.db < backend/migrations/020_add_ai_tables.sql

-- Create ai_user_settings table
CREATE TABLE IF NOT EXISTS ai_user_settings (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    use_own_token BOOLEAN NOT NULL DEFAULT 0,
    encrypted_api_token TEXT NULL,
    token_validated_at TIMESTAMP NULL,
    selected_model TEXT NOT NULL DEFAULT 'anthropic/claude-3.5-haiku',
    context_fields TEXT NOT NULL DEFAULT '["name", "category", "weight"]',
    monthly_token_limit INTEGER NULL,
    monthly_tokens_used INTEGER NOT NULL DEFAULT 0,
    monthly_cost_limit REAL NULL,
    monthly_cost_used REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_user_settings_user_id ON ai_user_settings(user_id);

-- Create ai_history table
CREATE TABLE IF NOT EXISTS ai_history (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    operation_type TEXT NOT NULL,
    final_prompt TEXT NOT NULL,
    context_data TEXT NULL,
    response_data TEXT NOT NULL,
    model TEXT NOT NULL,
    provider TEXT NOT NULL,
    tokens_input INTEGER NOT NULL,
    tokens_output INTEGER NOT NULL,
    tokens_total INTEGER NOT NULL,
    cost_input REAL NULL,
    cost_output REAL NULL,
    cost_total REAL NULL,
    duration_ms INTEGER NULL,
    used_own_token BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_history_user_id ON ai_history(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_history_created_at ON ai_history(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_history_operation_type ON ai_history(operation_type);

-- Create ai_cache table
CREATE TABLE IF NOT EXISTS ai_cache (
    id TEXT PRIMARY KEY,
    cache_key TEXT NOT NULL UNIQUE,
    operation_type TEXT NOT NULL,
    input_hash TEXT NOT NULL,
    model TEXT NOT NULL,
    response_data TEXT NOT NULL,
    hit_count INTEGER NOT NULL DEFAULT 0,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_cache_cache_key ON ai_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_ai_cache_expires_at ON ai_cache(expires_at);
