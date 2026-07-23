"""Migration: Add visualization fields to gear_settings table.

This migration adds two columns to gear_settings for the container
visualization drag-and-drop feature:
- visualization_custom_zones (JSON) - user-defined zones (id, name, iconKey)
- visualization_placements (JSON) - containerId -> zoneId override map

Usage:
    python migrations/056_add_visualization_to_gear_settings.py upgrade
    python migrations/056_add_visualization_to_gear_settings.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table (PostgreSQL compatible).

    Args:
        conn: Database connection
        table_name: Name of the table
        column_name: Name of the column

    Returns:
        True if column exists, False otherwise
    """
    result = await conn.execute(
        text("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = :table_name
                AND column_name = :column_name
            );
        """),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Add visualization columns to gear_settings table."""
    print("Adding visualization fields to gear_settings table...")

    async with engine.begin() as conn:
        if not await column_exists(conn, "gear_settings", "visualization_custom_zones"):
            print("Adding visualization_custom_zones column to gear_settings table...")
            await conn.execute(text("""
                    ALTER TABLE gear_settings
                    ADD COLUMN visualization_custom_zones JSON NOT NULL DEFAULT '[]';
                """))
            print("✓ Added visualization_custom_zones column")
        else:
            print("visualization_custom_zones column already exists, skipping...")

        if not await column_exists(conn, "gear_settings", "visualization_placements"):
            print("Adding visualization_placements column to gear_settings table...")
            await conn.execute(text("""
                    ALTER TABLE gear_settings
                    ADD COLUMN visualization_placements JSON NOT NULL DEFAULT '{}';
                """))
            print("✓ Added visualization_placements column")
        else:
            print("visualization_placements column already exists, skipping...")

    print("✓ Migration completed successfully")


async def downgrade() -> None:
    """Remove visualization columns from gear_settings table."""
    print("Removing visualization fields from gear_settings table...")

    async with engine.begin() as conn:
        if await column_exists(conn, "gear_settings", "visualization_placements"):
            print("Removing visualization_placements column from gear_settings table...")
            await conn.execute(text("""
                    ALTER TABLE gear_settings
                    DROP COLUMN IF EXISTS visualization_placements;
                """))
            print("✓ Removed visualization_placements column")
        else:
            print("visualization_placements column does not exist, skipping...")

        if await column_exists(conn, "gear_settings", "visualization_custom_zones"):
            print("Removing visualization_custom_zones column from gear_settings table...")
            await conn.execute(text("""
                    ALTER TABLE gear_settings
                    DROP COLUMN IF EXISTS visualization_custom_zones;
                """))
            print("✓ Removed visualization_custom_zones column")
        else:
            print("visualization_custom_zones column does not exist, skipping...")

    print("✓ Downgrade completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Add visualization fields to gear_settings migration")
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
