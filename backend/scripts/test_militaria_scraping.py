#!/usr/bin/env python3
"""Test script to verify militaria.pl scraping works correctly."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.modules.gear.image_search_repository import ImageSearchEngineRepository
from app.modules.gear.image_search_service import ImageSearchService


async def test_militaria_scraping():
    """Test militaria.pl scraping with a sample query."""
    async with AsyncSessionLocal() as db:
        repo = ImageSearchEngineRepository(db)
        service = ImageSearchService(db)

        # Get militaria.pl engine
        engine = await repo.get_by_name("Militaria.pl")
        if not engine:
            print("❌ Militaria.pl engine not found!")
            return

        print(f"✓ Found engine: {engine.name} (ID: {engine.id})")
        print(f"  - Type: {engine.type}")
        print(f"  - Base URL: {engine.base_url}")
        print(f"  - Search Template: {engine.search_template}")
        print(f"  - Image Selectors: {engine.image_selectors}")
        print()

        # Test search
        query = "nóż"
        print(f"🔍 Testing search with query: '{query}'")
        print()

        try:
            results = await service.search_images_by_query(query, [engine.id])
            print(f"✓ Found {len(results)} results")
            print()

            if results:
                print("📸 Sample results:")
                for i, result in enumerate(results[:5], 1):
                    print(f"  {i}. Image URL: {result.image_url[:80]}...")
                    print(f"     Source URL: {result.source_url}")
                    print(f"     Source Name: {result.source_name}")
                    print()
            else:
                print("⚠️  No results found. This might indicate:")
                print("   - Selectors need adjustment")
                print("   - Website structure changed")
                print("   - Network/access issues")
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_militaria_scraping())
