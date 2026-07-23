"""Migration: Add gear_containers and gear_items tables.

This migration creates the tables for gear management system.

Usage:
    python migrations/010_add_gear_tables.py upgrade
    python migrations/010_add_gear_tables.py downgrade

Note:
    Originally created via `GearContainerDB.metadata.create_all`/`GearItemDB.metadata.create_all`
    (SQLAlchemy ORM metadata). Rewritten to raw SQL as part of
    docs/plans/2026-07-23-gear-backend-v1-v2-unification.md Phase 5, which removes the
    GearContainerDB/GearItemDB classes from db_models.py entirely (V1 is fully retired) -- this
    migration must not depend on them to remain replayable on a fresh database. Shape reflects
    the tables as they stood immediately before migration 011 (which adds further columns).
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
    """Create gear_containers and gear_items tables."""
    print("Creating gear tables...")

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
                        is_public BOOLEAN NOT NULL DEFAULT FALSE,
                        is_hidden_by_reports BOOLEAN NOT NULL DEFAULT FALSE,
                        favorite BOOLEAN NOT NULL DEFAULT FALSE,
                        show_item_images BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
                    );
                """))
            print("✓ gear_containers table created")
        else:
            print("✓ gear_containers table already exists")

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
                        priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                        status VARCHAR(20) NOT NULL DEFAULT 'owned',
                        nested_container_id VARCHAR(36) REFERENCES gear_containers(id),
                        price FLOAT,
                        currency VARCHAR(10),
                        url TEXT,
                        brand VARCHAR(255),
                        color VARCHAR(50),
                        quality VARCHAR(20),
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
                    );
                """))
            print("✓ gear_items table created")
        else:
            print("✓ gear_items table already exists")


async def downgrade() -> None:
    """Drop gear_containers and gear_items tables."""
    print("Dropping gear tables...")

    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS gear_items CASCADE;"))
        print("✓ gear_items table dropped")
        await conn.execute(text("DROP TABLE IF EXISTS gear_containers CASCADE;"))
        print("✓ gear_containers table dropped")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Gear tables migration")
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
