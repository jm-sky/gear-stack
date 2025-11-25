"""Migration: Add image_search_engines table and extend item_images with source fields.

This migration:
1. Creates the image_search_engines table for configurable image search engines
2. Adds source attribution fields to item_images table (source_url, source_name, search_engine_id)

Usage:
    python migrations/020_add_image_search_engines.py upgrade
    python migrations/020_add_image_search_engines.py downgrade
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
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """
        ),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = :table_name
                AND column_name = :column_name
            );
        """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Create image_search_engines table and add source fields to item_images."""
    print("Creating image_search_engines table and extending item_images...")

    async with engine.begin() as conn:
        # 1. Create image_search_engines table
        if await table_exists(conn, "image_search_engines"):
            print("image_search_engines table already exists, skipping...")
        else:
            await conn.execute(
                text(
                    """
                    CREATE TABLE image_search_engines (
                        id VARCHAR(36) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        type VARCHAR(20) NOT NULL,
                        base_url VARCHAR(500) NOT NULL,
                        
                        -- HTML Scraper fields
                        search_template VARCHAR(500),
                        image_selectors JSONB,
                        
                        -- API fields
                        api_endpoint VARCHAR(500),
                        api_key TEXT,
                        request_headers JSONB,
                        response_mapping JSONB,
                        
                        -- Status
                        is_active BOOLEAN NOT NULL DEFAULT TRUE,
                        priority INTEGER NOT NULL DEFAULT 0,
                        
                        -- Timestamps
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """
                )
            )
            print("✓ image_search_engines table created successfully")

        # 2. Add source fields to item_images table
        if not await column_exists(conn, "item_images", "search_engine_id"):
            await conn.execute(
                text(
                    """
                    ALTER TABLE item_images
                    ADD COLUMN search_engine_id VARCHAR(36),
                    ADD COLUMN source_url TEXT,
                    ADD COLUMN source_name VARCHAR(255);
                """
                )
            )
            print("✓ Added source fields to item_images table")

            # Add foreign key constraint
            await conn.execute(
                text(
                    """
                    ALTER TABLE item_images
                    ADD CONSTRAINT fk_item_images_search_engine_id
                    FOREIGN KEY (search_engine_id)
                    REFERENCES image_search_engines(id)
                    ON DELETE SET NULL;
                """
                )
            )
            print("✓ Added foreign key constraint for search_engine_id")

            # Add index for search_engine_id
            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS ix_item_images_search_engine_id
                    ON item_images(search_engine_id);
                """
                )
            )
            print("✓ Added index for search_engine_id")
        else:
            print("Source fields already exist in item_images table, skipping...")

    print("\n✓ Migration completed successfully!")


async def downgrade() -> None:
    """Remove image_search_engines table and source fields from item_images."""
    print("Removing image_search_engines table and source fields from item_images...")

    async with engine.begin() as conn:
        # 1. Remove source fields from item_images
        if await column_exists(conn, "item_images", "search_engine_id"):
            # Drop foreign key constraint first
            await conn.execute(
                text(
                    """
                    ALTER TABLE item_images
                    DROP CONSTRAINT IF EXISTS fk_item_images_search_engine_id;
                """
                )
            )

            # Drop index
            await conn.execute(
                text(
                    """
                    DROP INDEX IF EXISTS ix_item_images_search_engine_id;
                """
                )
            )

            # Drop columns
            await conn.execute(
                text(
                    """
                    ALTER TABLE item_images
                    DROP COLUMN IF EXISTS search_engine_id,
                    DROP COLUMN IF EXISTS source_url,
                    DROP COLUMN IF EXISTS source_name;
                """
                )
            )
            print("✓ Removed source fields from item_images table")

        # 2. Drop image_search_engines table
        if await table_exists(conn, "image_search_engines"):
            await conn.execute(
                text(
                    """
                    DROP TABLE IF EXISTS image_search_engines;
                """
                )
            )
            print("✓ Dropped image_search_engines table")

    print("\n✓ Downgrade completed successfully!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrations/020_add_image_search_engines.py [upgrade|downgrade]")
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "upgrade":
        asyncio.run(upgrade())
    elif command == "downgrade":
        asyncio.run(downgrade())
    else:
        print(f"Unknown command: {command}")
        print("Usage: python migrations/020_add_image_search_engines.py [upgrade|downgrade]")
        sys.exit(1)
