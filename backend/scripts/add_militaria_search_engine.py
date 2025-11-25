#!/usr/bin/env python3
"""Script to add militaria.pl search engine configuration to database."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.common.id_utils import generate_id
from app.core.database import AsyncSessionLocal
from app.modules.gear.image_search_repository import ImageSearchEngineRepository


async def add_militaria_engine():
    """Add militaria.pl search engine configuration."""
    async with AsyncSessionLocal() as db:
        repo = ImageSearchEngineRepository(db)

        # Check if engine already exists
        existing = await repo.get_by_name("Militaria.pl")
        if existing:
            print(f"✓ Search engine 'Militaria.pl' already exists (ID: {existing.id})")
            return

        # Create engine configuration
        engine_data = {
            "name": "Militaria.pl",
            "type": "html_scraper",
            "base_url": "https://militaria.pl",
            "search_template": "/szukaj?fraza={query}",
            "image_selectors": {
                "container": ".product-item, .product, [data-product-id], .item",
                "image": "img.product-image, img[data-src], img.lazy, img",
                "link": "a.product-link, a[href*='/p/'], a[href*='/product']",
            },
            "is_active": True,
            "priority": 1,
        }

        engine = await repo.create(engine_data)
        await db.commit()
        print(f"✓ Created search engine 'Militaria.pl' with ID: {engine.id}")
        print(f"  - Type: {engine.type}")
        print(f"  - Base URL: {engine.base_url}")
        print(f"  - Search Template: {engine.search_template}")
        print(f"  - Image Selectors: {engine.image_selectors}")
        print(f"  - Active: {engine.is_active}")
        print(f"  - Priority: {engine.priority}")


if __name__ == "__main__":
    asyncio.run(add_militaria_engine())
