"""Migration: Recreate container_share_tokens table, pointing at gear_items_v2.

Fixes docs/issues/2026-07-23--044--container-share-tokens-table-missing-prod.md: the
`container_share_tokens` table is absent on production despite migrations `032`/`036`
("add_container_share_tokens") being recorded as applied in `schema_migrations`. Both of those
migrations are idempotent `CREATE TABLE IF NOT EXISTS`-style scripts that also support being run
standalone as `python migrations/NNN_....py downgrade` outside the tracked runner — the most
likely explanation is that a manual `downgrade()` invocation dropped the table on production
without updating `schema_migrations`, since that's the only path that removes the table without
un-recording it. This migration does not attempt to prove that history; it simply restores the
table.

Unlike `032`/`036` (which pointed `container_id` at legacy `gear_containers`), this migration
targets `gear_items_v2` directly — the whole point of the V1->V2 unification plan
(docs/plans/2026-07-23-gear-backend-v1-v2-unification.md, Phase 1) is to avoid recreating a
V1-shaped table only to repoint it again in Phase 2. `ContainerShareTokenDB` in
`app/modules/gear/db_models.py` still declares `ForeignKey("gear_containers.id")` in the ORM;
that Python-level annotation is corrected in Phase 3 (it doesn't affect what constraint actually
exists in the database).

Idempotent: no-ops if the table already exists (e.g. the local dev DB, which never lost it).

Usage:
    python migrations/057_recreate_container_share_tokens.py upgrade
    python migrations/057_recreate_container_share_tokens.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database."""
    result = await conn.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Recreate container_share_tokens table, with container_id FK -> gear_items_v2."""
    print("Recreating container_share_tokens table (pointing at gear_items_v2)...")

    async with engine.begin() as conn:
        items_v2_exist = await table_exists(conn, "gear_items_v2")
        if not items_v2_exist:
            print("❌ Error: gear_items_v2 table does not exist. Run migration 050 first.")
            sys.exit(1)

        tokens_exist = await table_exists(conn, "container_share_tokens")
        if not tokens_exist:
            print("Creating container_share_tokens table...")
            await conn.execute(text("""
                    CREATE TABLE container_share_tokens (
                        token VARCHAR(255) PRIMARY KEY,
                        container_id VARCHAR(36) NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        expires_at TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        CONSTRAINT container_share_tokens_container_id_fkey
                            FOREIGN KEY (container_id)
                            REFERENCES gear_items_v2(id)
                            ON DELETE CASCADE,
                        CONSTRAINT container_share_tokens_user_id_fkey
                            FOREIGN KEY (user_id)
                            REFERENCES users(id)
                    );
                """))

            print("Creating indexes...")
            await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_container_share_tokens_token
                    ON container_share_tokens(token);
                """))
            await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_container_share_tokens_container_id
                    ON container_share_tokens(container_id);
                """))
            await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_container_share_tokens_user_id
                    ON container_share_tokens(user_id);
                """))
            await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_container_share_tokens_expires_at
                    ON container_share_tokens(expires_at);
                """))
            print("✓ Created container_share_tokens table (container_id -> gear_items_v2)")
        else:
            print("✓ container_share_tokens table already exists, skipping (no-op)")


async def downgrade() -> None:
    """Remove container_share_tokens table."""
    print("Dropping container_share_tokens table...")

    async with engine.begin() as conn:
        tokens_exist = await table_exists(conn, "container_share_tokens")
        if tokens_exist:
            await conn.execute(text("""
                    DROP TABLE IF EXISTS container_share_tokens CASCADE;
                """))
            print("✓ Dropped container_share_tokens table")
        else:
            print("✓ container_share_tokens table does not exist")


async def main() -> None:
    """Run migration based on command line argument."""
    if len(sys.argv) < 2:
        print("Usage: python migrations/057_recreate_container_share_tokens.py [upgrade|downgrade]")
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "upgrade":
        await upgrade()
    elif command == "downgrade":
        await downgrade()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python migrations/057_recreate_container_share_tokens.py [upgrade|downgrade]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
