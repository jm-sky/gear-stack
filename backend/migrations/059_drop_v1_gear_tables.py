"""Migration: Drop legacy V1 gear tables (gear_containers, gear_items).

Final step of docs/plans/2026-07-23-gear-backend-v1-v2-unification.md. By this point:
- gear_items_v2 is the sole read/write path for every gear feature (Phase 3).
- The dead V1 CRUD endpoints/repository methods/service methods have been removed (Phase 4).
- All ancillary tables (item_images, container_ratings, container_share_tokens,
  item_promotions, content_reports) have their FK pointed at gear_items_v2, not these tables
  (Phase 2, migration 058).

This migration verifies no *other* table still has a live FK into gear_containers/gear_items
before dropping them -- if anything unexpected does, it aborts rather than silently cascading
into data no one has audited. This is not a bulk data migration: gear_items_v2 already contains
everything (migrated by 051); these two tables are dropped as-is.

**This is the only destructive step in the whole plan.** Take a fresh database backup
immediately before running this on production -- downgrade() recreates the (empty) tables, it
does not restore data.

Usage:
    python migrations/059_drop_v1_gear_tables.py upgrade
    python migrations/059_drop_v1_gear_tables.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine

V1_TABLES = ("gear_items", "gear_containers")


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


async def get_external_referencing_fks(conn) -> list[tuple[str, str, str]]:
    """Find any FK from a table OTHER than gear_items/gear_containers into either of them.

    Returns a list of (referencing_table, constraint_name, referenced_table). Self-references
    from gear_items/gear_containers onto each other are expected and drop via CASCADE; anything
    else means some table wasn't repointed at gear_items_v2 and this migration must not proceed.
    """
    result = await conn.execute(text("""
            SELECT tc.table_name AS referencing_table, tc.constraint_name, ccu.table_name AS referenced_table
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
                AND tc.table_schema = ccu.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
                AND ccu.table_name IN ('gear_items', 'gear_containers')
                AND tc.table_name NOT IN ('gear_items', 'gear_containers');
        """))
    return [(row.referencing_table, row.constraint_name, row.referenced_table) for row in result.fetchall()]


async def get_row_count(conn, table_name: str) -> int:
    """Get row count for a table."""
    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table_name};"))  # noqa: S608 -- table name from V1_TABLES only
    return result.scalar() or 0


async def upgrade() -> None:
    """Drop gear_items and gear_containers, after verifying it's safe to do so."""
    print("Preparing to drop legacy V1 gear tables...")

    async with engine.begin() as conn:
        existing = [t for t in V1_TABLES if await table_exists(conn, t)]
        if not existing:
            print("✓ gear_items/gear_containers already absent, nothing to do")
            return

        # Safety gate: no other table may still reference these.
        external_fks = await get_external_referencing_fks(conn)
        if external_fks:
            print("❌ Error: found external foreign keys still referencing V1 tables:")
            for referencing_table, constraint_name, referenced_table in external_fks:
                print(f"   {referencing_table}.{constraint_name} -> {referenced_table}")
            print("These must be repointed at gear_items_v2 first (see Phase 2, migration 058) " "before V1 tables can be safely dropped.")
            sys.exit(1)

        for table in existing:
            count = await get_row_count(conn, table)
            print(f"  {table}: {count} row(s) -- gear_items_v2 already has this data (migration 051)")

        for table in V1_TABLES:
            if await table_exists(conn, table):
                await conn.execute(text(f"DROP TABLE {table} CASCADE;"))  # noqa: S608 -- table name from V1_TABLES only
                print(f"✓ Dropped {table}")

    print("✓ V1 gear tables removed. gear_items_v2 is now the sole backend gear data model.")


async def downgrade() -> None:
    """Recreate empty gear_containers/gear_items tables (best-effort; data is NOT restored).

    Real recovery from a mistaken drop is the pre-migration backup, not this downgrade -- it
    only recreates the schema so the app doesn't hard-fail on a missing table, matching the
    shape from migrations 010/011.
    """
    print("Recreating empty gear_containers/gear_items tables (schema only, no data)...")

    async with engine.begin() as conn:
        if not await table_exists(conn, "gear_containers"):
            await conn.execute(text("""
                    CREATE TABLE gear_containers (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        type VARCHAR(50) NOT NULL,
                        color VARCHAR(20) DEFAULT 'default',
                        parent_container_id VARCHAR(36) REFERENCES gear_containers(id),
                        brand VARCHAR(255),
                        price FLOAT,
                        hide_when_nested BOOLEAN DEFAULT FALSE,
                        weight FLOAT,
                        weight_unit VARCHAR(5),
                        max_weight FLOAT,
                        max_weight_unit VARCHAR(5),
                        url TEXT,
                        is_public BOOLEAN NOT NULL DEFAULT FALSE,
                        is_hidden_by_reports BOOLEAN NOT NULL DEFAULT FALSE,
                        favorite BOOLEAN NOT NULL DEFAULT FALSE,
                        show_item_images BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
                    );
                """))
            print("✓ Recreated empty gear_containers table")

        if not await table_exists(conn, "gear_items"):
            await conn.execute(text("""
                    CREATE TABLE gear_items (
                        id VARCHAR(36) PRIMARY KEY,
                        container_id VARCHAR(36) NOT NULL REFERENCES gear_containers(id),
                        name VARCHAR(255) NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        quantity INTEGER NOT NULL DEFAULT 1,
                        weight FLOAT NOT NULL,
                        weight_unit VARCHAR(5) NOT NULL DEFAULT 'g',
                        notes TEXT,
                        expiration_date TIMESTAMP WITH TIME ZONE,
                        shelf_life JSONB,
                        priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                        status VARCHAR(20) NOT NULL DEFAULT 'owned',
                        nested_container_id VARCHAR(36) REFERENCES gear_containers(id),
                        price FLOAT,
                        currency VARCHAR(10),
                        url TEXT,
                        brand VARCHAR(255),
                        color VARCHAR(50),
                        quality VARCHAR(20),
                        linked_item_id VARCHAR(36) REFERENCES gear_items(id),
                        catalogue_item_id VARCHAR(36) REFERENCES global_catalogue_items(id) ON DELETE SET NULL,
                        wearable BOOLEAN DEFAULT FALSE,
                        consumable BOOLEAN DEFAULT FALSE,
                        "order" INTEGER,
                        show_on_container BOOLEAN DEFAULT FALSE,
                        promote_count INTEGER NOT NULL DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
                    );
                """))
            print("✓ Recreated empty gear_items table")

    print("⚠️  Tables recreated empty -- data is NOT restored. Restore from backup if needed.")


async def main() -> None:
    """Run migration based on command line argument."""
    if len(sys.argv) < 2:
        print("Usage: python migrations/059_drop_v1_gear_tables.py [upgrade|downgrade]")
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "upgrade":
        await upgrade()
    elif command == "downgrade":
        await downgrade()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python migrations/059_drop_v1_gear_tables.py [upgrade|downgrade]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
