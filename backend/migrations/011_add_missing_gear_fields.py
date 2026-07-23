"""Migration: Add missing fields to gear_containers and gear_items tables.

This migration adds the following fields:
- gear_containers: hide_when_nested, weight, weight_unit, max_weight, max_weight_unit, url
- gear_items: linked_item_id, wearable, consumable

Usage:
    python migrations/003_add_missing_gear_fields.py upgrade
    python migrations/003_add_missing_gear_fields.py downgrade

Note:
    The "table doesn't exist yet" fallback below originally created it via
    `GearContainerDB.metadata.create_all`/`GearItemDB.metadata.create_all` (SQLAlchemy ORM
    metadata). Rewritten to raw SQL as part of
    docs/plans/2026-07-23-gear-backend-v1-v2-unification.md Phase 5, which removes those classes
    from db_models.py entirely -- this migration must not depend on them to remain replayable on
    a fresh database. In practice this fallback is unreachable in a normal sequential replay
    (migration 010 always creates the tables first), but it must not reference deleted classes.
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
    # Use SQL query to check if table exists (works with async)
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
    """Add missing fields to gear tables."""
    print("Adding missing fields to gear tables...")

    async with engine.begin() as conn:
        # Check if tables exist, if not create them with all fields (using SQLAlchemy models)
        containers_exist = await table_exists(conn, "gear_containers")
        items_exist = await table_exists(conn, "gear_items")

        if not containers_exist:
            print("gear_containers table does not exist, creating it with all fields...")
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
            print("✓ gear_containers table created with all fields")
        else:
            print("gear_containers table exists, adding missing fields...")
            # Add fields to gear_containers
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS hide_when_nested BOOLEAN DEFAULT FALSE;
            """))
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS weight FLOAT;
            """))
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS weight_unit VARCHAR(5);
            """))
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS max_weight FLOAT;
            """))
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS max_weight_unit VARCHAR(5);
            """))
            await conn.execute(text("""
                ALTER TABLE gear_containers
                ADD COLUMN IF NOT EXISTS url TEXT;
            """))

        if not items_exist:
            print("gear_items table does not exist, creating it with all fields...")
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
                        priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                        status VARCHAR(20) NOT NULL DEFAULT 'owned',
                        nested_container_id VARCHAR(36) REFERENCES gear_containers(id),
                        price FLOAT,
                        currency VARCHAR(10),
                        url TEXT,
                        brand VARCHAR(255),
                        color VARCHAR(50),
                        quality VARCHAR(20),
                        linked_item_id VARCHAR(36),
                        wearable BOOLEAN DEFAULT FALSE,
                        consumable BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
                    );
                """))
            print("✓ gear_items table created with all fields")
        else:
            print("gear_items table exists, adding missing fields...")
            # Add fields to gear_items
            await conn.execute(text("""
                ALTER TABLE gear_items
                ADD COLUMN IF NOT EXISTS linked_item_id VARCHAR(36);
            """))
            await conn.execute(text("""
                ALTER TABLE gear_items
                ADD COLUMN IF NOT EXISTS wearable BOOLEAN DEFAULT FALSE;
            """))
            await conn.execute(text("""
                ALTER TABLE gear_items
                ADD COLUMN IF NOT EXISTS consumable BOOLEAN DEFAULT FALSE;
            """))

        # Add foreign key for linked_item_id (only if table exists and was modified, not created)
        if items_exist:
            # Check if constraint already exists using SQL
            try:
                result = await conn.execute(text("""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.table_constraints
                            WHERE constraint_schema = 'public'
                            AND table_name = 'gear_items'
                            AND constraint_name = 'fk_gear_items_linked_item_id'
                        );
                    """))
                constraint_exists = result.scalar() is True

                if not constraint_exists:
                    await conn.execute(text("""
                        ALTER TABLE gear_items
                        ADD CONSTRAINT fk_gear_items_linked_item_id
                        FOREIGN KEY (linked_item_id) REFERENCES gear_items(id) ON DELETE SET NULL;
                    """))
                    print("✓ Added foreign key constraint for linked_item_id")
                else:
                    print("✓ Foreign key constraint for linked_item_id already exists")
            except Exception as e:
                print(f"Note: Could not add foreign key constraint: {e}")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove added fields from gear tables."""
    print("Removing added fields from gear tables...")

    async with engine.begin() as conn:
        # Remove foreign key first
        try:
            await conn.execute(text("""
                ALTER TABLE gear_items
                DROP CONSTRAINT IF EXISTS fk_gear_items_linked_item_id;
            """))
        except Exception:
            pass

        # Remove fields from gear_items
        await conn.execute(text("""
            ALTER TABLE gear_items
            DROP COLUMN IF EXISTS consumable;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_items
            DROP COLUMN IF EXISTS wearable;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_items
            DROP COLUMN IF EXISTS linked_item_id;
        """))

        # Remove fields from gear_containers
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS url;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS max_weight_unit;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS max_weight;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS weight_unit;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS weight;
        """))
        await conn.execute(text("""
            ALTER TABLE gear_containers
            DROP COLUMN IF EXISTS hide_when_nested;
        """))

    print("✓ Removed added fields from gear_items")
    print("✓ Removed added fields from gear_containers")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add missing gear fields migration")
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
