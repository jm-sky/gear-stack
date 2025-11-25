#!/usr/bin/env python3
"""Script to add Unsplash search engine configuration to database."""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.modules.gear.image_search_repository import ImageSearchEngineRepository


async def add_unsplash_engine():
    """Add Unsplash search engine configuration."""
    async with AsyncSessionLocal() as db:
        repo = ImageSearchEngineRepository(db)

        # Check if engine already exists
        existing = await repo.get_by_name("Unsplash")
        if existing:
            print(f"✓ Search engine 'Unsplash' already exists (ID: {existing.id})")
            print(f"  To update API key, use: UPDATE image_search_engines SET api_key = 'YOUR_KEY' WHERE id = '{existing.id}'")
            return

        # Get API key from environment or prompt
        api_key = os.getenv("UNSPLASH_API_KEY") or os.getenv("UNSPLASH_ACCESS_KEY")
        if not api_key:
            print("⚠️  UNSPLASH_API_KEY or UNSPLASH_ACCESS_KEY not found in environment variables.")
            print("   You can:")
            print("   1. Set UNSPLASH_API_KEY environment variable")
            print("   2. Get free API key from: https://unsplash.com/developers")
            print("   3. Register your app at: https://unsplash.com/oauth/applications")
            print("   4. Update the engine later with: UPDATE image_search_engines SET api_key = 'YOUR_KEY' WHERE id = 'ENGINE_ID'")
            api_key = "YOUR_UNSPLASH_ACCESS_KEY_HERE"  # Placeholder

        # Create engine configuration
        engine_data = {
            "name": "Unsplash",
            "type": "api",
            "base_url": "https://api.unsplash.com",
            "api_endpoint": "/search/photos",
            "api_key": api_key,
            "request_headers": {
                # Authorization header will be added automatically by service
            },
            "response_mapping": {
                "hits": "results",  # Unsplash uses "results" instead of "hits"
                "imageUrl": "urls.regular",  # urls.regular, urls.full, urls.raw
                "thumbnailUrl": "urls.thumb",  # urls.thumb, urls.small
                "sourceUrl": "links.html",  # Link to photo page on Unsplash
            },
            "is_active": True,
            "priority": 3,  # Lower priority than Pixabay
        }

        engine = await repo.create(engine_data)
        await db.commit()
        print(f"✓ Created search engine 'Unsplash' with ID: {engine.id}")
        print(f"  - Type: {engine.type}")
        print(f"  - Base URL: {engine.base_url}")
        print(f"  - API Endpoint: {engine.api_endpoint}")
        print(f"  - API Key: {'***' if api_key != 'YOUR_UNSPLASH_ACCESS_KEY_HERE' else 'YOUR_UNSPLASH_ACCESS_KEY_HERE (please update)'}")
        print(f"  - Active: {engine.is_active}")
        print(f"  - Priority: {engine.priority}")
        print(f"  - Response Mapping: {engine.response_mapping}")
        if api_key == "YOUR_UNSPLASH_ACCESS_KEY_HERE":
            print()
            print("⚠️  Remember to update the API key in the database!")
            print("   Unsplash uses 'Client-ID' in Authorization header, not a query parameter.")


if __name__ == "__main__":
    asyncio.run(add_unsplash_engine())
