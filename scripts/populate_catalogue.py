#!/usr/bin/env python3
"""Script to populate the catalogue with items from markdown file."""

import re
import sys
from pathlib import Path

import httpx

# API configuration
API_URL = "http://localhost:8000/api"
CATALOGUE_MD = Path(__file__).parent.parent / "docs" / "plans" / "global-catalogue-items.md"

# Category mapping from Polish to English
CATEGORY_MAP = {
    "Ogień": "fire",
    "Noże / Narzędzia tnące / Uzupełnienie": "blades",
    "Narzędzia wielofunkcyjne": "tools",
    "Narzędzia / Siekiery": "tools",
    "Narzędzia / Liny": "tools",
    "Narzędzia / Naprawa": "tools",
    "Narzędzia": "tools",
    "Woda": "water",
    "Schronienie": "shelter",
    "Light": "light",
    "First Aid": "firstAid",
    "Container": "other",
    "Food": "food",
    "Navigation": "navigation",
    "Communication": "communication",
    "Communication / zasilanie": "communication",
    "Communication / zasilanie / sygnały": "communication",
}

# Price tier mapping
PRICE_TIER_MAP = {
    "low": "budget",
    "medium": "mid",
    "high": "premium",
}

# Quality mapping
QUALITY_MAP = {
    "basic": "medium",
    "value": "medium",
    "solid": "high",
    "durable": "high",
    "reliable": "high",
    "premium": "high",
}


def parse_markdown_file(filepath: Path) -> list[dict]:
    """Parse catalogue items from markdown file.

    Args:
        filepath: Path to markdown file

    Returns:
        List of item dictionaries
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    items = []
    current_category = None
    current_item = None

    lines = content.split("\n")
    for line in lines:
        # Check for category header (## Category)
        if line.startswith("## "):
            current_category = line[3:].strip()
            continue

        # Check for item name (- **Item Name**)
        if line.startswith("- **") and line.endswith("**"):
            if current_item:
                items.append(current_item)

            name = line[4:-2]  # Remove "- **" and "**"
            current_item = {
                "name": name,
                "category_raw": current_category,
                "weightUnit": "g",
            }
            continue

        # Parse item properties
        if current_item and line.strip().startswith("- *"):
            # Extract property (e.g., "- *kategoria:* value")
            match = re.match(r"\s*- \*([^:]+):\*\s*(.+)?", line)
            if match:
                prop_name = match.group(1).strip()
                prop_value = match.group(2).strip() if match.group(2) else ""

                if prop_name == "kategoria":
                    current_item["category_from_item"] = prop_value
                elif prop_name == "firma":
                    current_item["brand"] = prop_value
                elif prop_name == "model":
                    current_item["model"] = prop_value
                elif prop_name == "opis":
                    current_item["notes"] = prop_value
                elif prop_name == "półka cenowa":
                    current_item["price_tier_raw"] = prop_value
                elif prop_name == "klasa":
                    current_item["quality_raw"] = prop_value
                elif prop_name == "website":
                    if prop_value:
                        current_item["url"] = prop_value

    # Add last item
    if current_item:
        items.append(current_item)

    # Process items: map categories, price tiers, quality
    for item in items:
        # Map category
        category_key = item.get("category_from_item") or item.get("category_raw", "")
        item["category"] = CATEGORY_MAP.get(category_key, "other")

        # Map price tier
        price_tier_raw = item.get("price_tier_raw", "medium")
        item["priceTier"] = PRICE_TIER_MAP.get(price_tier_raw, "mid")

        # Map quality
        quality_raw = item.get("quality_raw", "basic")
        item["quality"] = QUALITY_MAP.get(quality_raw, "medium")

        # Clean up temporary fields
        item.pop("category_raw", None)
        item.pop("category_from_item", None)
        item.pop("price_tier_raw", None)
        item.pop("quality_raw", None)

    return items


async def get_auth_token(email: str, password: str) -> str:
    """Get authentication token.

    Args:
        email: User email
        password: User password

    Returns:
        JWT token
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        return data["accessToken"]


async def create_catalogue_item(token: str, item_data: dict) -> dict:
    """Create a catalogue item via API.

    Args:
        token: JWT authentication token
        item_data: Item data dictionary

    Returns:
        Created item response
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/gear/catalogue/items",
            json=item_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


async def main():
    """Main function to populate catalogue."""
    if len(sys.argv) < 3:
        print("Usage: python populate_catalogue.py <email> <password>")
        print("Example: python populate_catalogue.py admin@example.com password123")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    print("📖 Reading catalogue items from markdown...")
    items = parse_markdown_file(CATALOGUE_MD)
    print(f"   Found {len(items)} items")

    print("\n🔐 Authenticating...")
    try:
        token = await get_auth_token(email, password)
        print("   ✓ Authentication successful")
    except Exception as e:
        print(f"   ✗ Authentication failed: {e}")
        sys.exit(1)

    print(f"\n📦 Creating {len(items)} catalogue items...")
    created_count = 0
    failed_count = 0

    for i, item in enumerate(items, 1):
        try:
            result = await create_catalogue_item(token, item)
            created_count += 1
            print(f"   [{i}/{len(items)}] ✓ Created: {item['name']}")
        except Exception as e:
            failed_count += 1
            print(f"   [{i}/{len(items)}] ✗ Failed: {item['name']} - {e}")

    print(f"\n✨ Done!")
    print(f"   Created: {created_count}")
    print(f"   Failed: {failed_count}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
