#!/usr/bin/env python3
"""Script to add Pixabay search engine configuration to database."""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.modules.gear.image_search_repository import ImageSearchEngineRepository


async def add_pixabay_engine():
    """Add Pixabay search engine configuration."""
    async with AsyncSessionLocal() as db:
        repo = ImageSearchEngineRepository(db)

        # Check if engine already exists
        existing = await repo.get_by_name("Pixabay")
        if existing:
            print(f"✓ Search engine 'Pixabay' already exists (ID: {existing.id})")
            print(f"  To update API key, use: UPDATE image_search_engines SET api_key = 'YOUR_KEY' WHERE id = '{existing.id}'")
            return

        # Get API key from environment or prompt
        api_key = os.getenv("PIXABAY_API_KEY")
        if not api_key:
            print("⚠️  PIXABAY_API_KEY not found in environment variables.")
            print("   You can:")
            print("   1. Set PIXABAY_API_KEY environment variable")
            print("   2. Get free API key from: https://pixabay.com/api/docs/")
            print("   3. Update the engine later with: UPDATE image_search_engines SET api_key = 'YOUR_KEY' WHERE id = 'ENGINE_ID'")
            api_key = "YOUR_PIXABAY_API_KEY_HERE"  # Placeholder

        # Create engine configuration
        engine_data = {
            "name": "Pixabay",
            "type": "api",
            "base_url": "https://pixabay.com",
            "api_endpoint": "/api/",
            "api_key": api_key,
            "request_headers": {},
            "response_mapping": {
                "hits": "hits",
                "imageUrl": "largeImageURL",
                "thumbnailUrl": "previewURL",
                "sourceUrl": "pageURL",
            },
            "is_active": True,
            "priority": 2,  # Lower priority than militaria.pl (if it worked)
        }

        engine = await repo.create(engine_data)
        await db.commit()
        print(f"✓ Created search engine 'Pixabay' with ID: {engine.id}")
        print(f"  - Type: {engine.type}")
        print(f"  - Base URL: {engine.base_url}")
        print(f"  - API Endpoint: {engine.api_endpoint}")
        print(f"  - API Key: {'***' if api_key != 'YOUR_PIXABAY_API_KEY_HERE' else 'YOUR_PIXABAY_API_KEY_HERE (please update)'}")
        print(f"  - Active: {engine.is_active}")
        print(f"  - Priority: {engine.priority}")
        if api_key == "YOUR_PIXABAY_API_KEY_HERE":
            print()
            print("⚠️  Remember to update the API key in the database!")


if __name__ == "__main__":
    asyncio.run(add_pixabay_engine())
