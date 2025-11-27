"""Migration: Add AI module tables.

This migration adds three tables for AI functionality:
- ai_user_settings: User AI configuration (tokens, model selection, context preferences)
- ai_history: AI interaction history with full context and cost tracking
- ai_cache: Cache for AI responses to reduce API costs

Usage:
    python migrations/020_add_ai_tables.py upgrade
    python migrations/020_add_ai_tables.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database (PostgreSQL compatible)."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """
        ),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Create AI module tables."""
    print("Creating AI module tables...")

    async with engine.begin() as conn:
        # Check if tables already exist
        settings_exist = await table_exists(conn, "ai_user_settings")
        history_exist = await table_exists(conn, "ai_history")
        cache_exist = await table_exists(conn, "ai_cache")

        if settings_exist and history_exist and cache_exist:
            print("All AI tables already exist, skipping migration...")
            return

        # Create ai_user_settings table
        if not settings_exist:
            print("Creating ai_user_settings table...")
            await conn.execute(
                text(
                    """
                    CREATE TABLE ai_user_settings (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                        use_own_token BOOLEAN NOT NULL DEFAULT FALSE,
                        encrypted_api_token TEXT NULL,
                        token_validated_at TIMESTAMP WITH TIME ZONE NULL,
                        selected_model VARCHAR(255) NOT NULL DEFAULT 'anthropic/claude-3.5-haiku',
                        context_fields JSONB NOT NULL DEFAULT '["name", "category", "weight"]'::JSONB,
                        monthly_token_limit INTEGER NULL,
                        monthly_tokens_used INTEGER NOT NULL DEFAULT 0,
                        monthly_cost_limit NUMERIC(10,2) NULL,
                        monthly_cost_used NUMERIC(10,2) NOT NULL DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    )
                """
                )
            )
            await conn.execute(text("CREATE INDEX idx_ai_user_settings_user_id ON ai_user_settings(user_id)"))
            print("✓ Created ai_user_settings table")
        else:
            print("ai_user_settings table already exists, skipping...")

        # Create ai_history table
        if not history_exist:
            print("Creating ai_history table...")
            await conn.execute(
                text(
                    """
                    CREATE TABLE ai_history (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        operation_type VARCHAR(50) NOT NULL,
                        final_prompt TEXT NOT NULL,
                        context_data JSONB NULL,
                        response_data JSONB NOT NULL,
                        model VARCHAR(255) NOT NULL,
                        provider VARCHAR(100) NOT NULL,
                        tokens_input INTEGER NOT NULL,
                        tokens_output INTEGER NOT NULL,
                        tokens_total INTEGER NOT NULL,
                        cost_input NUMERIC(10,6) NULL,
                        cost_output NUMERIC(10,6) NULL,
                        cost_total NUMERIC(10,6) NULL,
                        duration_ms INTEGER NULL,
                        used_own_token BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    )
                """
                )
            )
            await conn.execute(text("CREATE INDEX idx_ai_history_user_id ON ai_history(user_id)"))
            await conn.execute(text("CREATE INDEX idx_ai_history_created_at ON ai_history(created_at)"))
            await conn.execute(text("CREATE INDEX idx_ai_history_operation_type ON ai_history(operation_type)"))
            await conn.execute(text("CREATE INDEX idx_ai_history_user_created ON ai_history(user_id, created_at)"))
            print("✓ Created ai_history table")
        else:
            print("ai_history table already exists, skipping...")

        # Create ai_cache table
        if not cache_exist:
            print("Creating ai_cache table...")
            await conn.execute(
                text(
                    """
                    CREATE TABLE ai_cache (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        cache_key VARCHAR(255) NOT NULL UNIQUE,
                        operation_type VARCHAR(50) NOT NULL,
                        input_hash VARCHAR(255) NOT NULL,
                        model VARCHAR(255) NOT NULL,
                        response_data JSONB NOT NULL,
                        hit_count INTEGER NOT NULL DEFAULT 0,
                        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        last_accessed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    )
                """
                )
            )
            await conn.execute(text("CREATE INDEX idx_ai_cache_cache_key ON ai_cache(cache_key)"))
            await conn.execute(text("CREATE INDEX idx_ai_cache_expires_at ON ai_cache(expires_at)"))
            print("✓ Created ai_cache table")
        else:
            print("ai_cache table already exists, skipping...")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Drop AI module tables."""
    print("Dropping AI module tables...")

    async with engine.begin() as conn:
        # Drop tables in reverse order (cache -> history -> settings)
        await conn.execute(text("DROP TABLE IF EXISTS ai_cache CASCADE"))
        print("✓ Dropped ai_cache table")

        await conn.execute(text("DROP TABLE IF EXISTS ai_history CASCADE"))
        print("✓ Dropped ai_history table")

        await conn.execute(text("DROP TABLE IF EXISTS ai_user_settings CASCADE"))
        print("✓ Dropped ai_user_settings table")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add AI module tables migration")
    parser.add_argument(
        "action",
        choices=["upgrade", "downgrade"],
        help="Migration action (upgrade or downgrade)",
    )
    args = parser.parse_args()

    if args.action == "upgrade":
        await upgrade()
    elif args.action == "downgrade":
        await downgrade()

    # Close database connections
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
