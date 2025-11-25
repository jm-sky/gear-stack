#!/usr/bin/env python3
"""Test script to verify Pixabay API search works correctly."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.modules.gear.image_search_repository import ImageSearchEngineRepository
from app.modules.gear.image_search_service import ImageSearchService


async def test_pixabay_scraping():
    """Test Pixabay API search with a sample query."""
    async with AsyncSessionLocal() as db:
        repo = ImageSearchEngineRepository(db)
        service = ImageSearchService(db)

        # Get Pixabay engine
        engine = await repo.get_by_name("Pixabay")
        if not engine:
            print("❌ Pixabay engine not found!")
            print("   Run: python scripts/add_pixabay_search_engine.py")
            return

        print(f"✓ Found engine: {engine.name} (ID: {engine.id})")
        print(f"  - Type: {engine.type}")
        print(f"  - Base URL: {engine.base_url}")
        print(f"  - API Endpoint: {engine.api_endpoint}")
        print(f"  - API Key: {'***' if engine.api_key and engine.api_key != 'YOUR_PIXABAY_API_KEY_HERE' else 'NOT SET'}")
        print()

        # Check if API key is set
        if not engine.api_key or engine.api_key == "YOUR_PIXABAY_API_KEY_HERE":
            print("⚠️  API key not set!")
            print("   To set API key:")
            print("   1. Get free API key from: https://pixabay.com/api/docs/")
            print("   2. Update in database:")
            print(f"      UPDATE image_search_engines SET api_key = 'YOUR_KEY' WHERE id = '{engine.id}'")
            print("   3. Or set PIXABAY_API_KEY environment variable and re-run add script")
            return

        # Test search
        query = "knife"
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
                    print(f"     Thumbnail: {result.thumbnail_url[:80] if result.thumbnail_url else 'N/A'}...")
                    print(f"     Source URL: {result.source_url}")
                    print(f"     Source Name: {result.source_name}")
                    print()
            else:
                print("⚠️  No results found.")
        except Exception as e:
            print(f"❌ Error during API search: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_pixabay_scraping())
