"""Service for image search and fetching from external sources."""

import logging
from io import BytesIO
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.config import settings
from app.core.storage.factory import get_storage_adapter
from app.core.storage.image_processor import ImageProcessor
from app.modules.gear.db_models import GearItemDB, ImageSearchEngineDB
from app.modules.gear.image_search_repository import ImageSearchEngineRepository
from app.modules.gear.image_search_schemas import ImageSearchResult
from app.modules.gear.item_image_repository import ItemImageRepository

logger = logging.getLogger(__name__)


class ImageSearchService:
    """Service for searching and fetching images from external sources."""

    def __init__(self, db: AsyncSession):
        """
        Initialize image search service.

        Args:
            db: Database session
        """
        self.db = db
        self.storage = get_storage_adapter()
        self.processor = ImageProcessor(
            max_width=settings.storage.max_width,
            max_height=settings.storage.max_height,
            jpeg_quality=settings.storage.jpeg_quality,
            convert_to_webp=settings.storage.convert_to_webp,
        )
        self.engine_repo = ImageSearchEngineRepository(db)
        self.image_repo = ItemImageRepository(db)

    def _build_search_query(self, item: GearItemDB) -> str:
        """
        Build search query from item data.

        Args:
            item: Gear item

        Returns:
            Search query string
        """
        parts = []
        if item.brand:
            parts.append(item.brand)
        parts.append(item.name)
        if item.color:
            parts.append(item.color)

        query = " ".join(parts)
        logger.debug(f"Built search query for item {item.id} ({item.name}): '{query}'")
        return query

    async def _scrape_html_images(self, engine: ImageSearchEngineDB, query: str) -> list[ImageSearchResult]:
        """
        Scrape images from HTML source.

        Args:
            engine: Search engine configuration
            query: Search query

        Returns:
            List of image search results
        """
        if not engine.search_template or not engine.image_selectors:
            return []

        try:
            # Build search URL
            search_url = urljoin(engine.base_url, engine.search_template.format(query=query))

            # Fetch HTML with realistic browser headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(search_url, headers=headers)
                response.raise_for_status()
                html = response.text

            # Parse HTML
            soup = BeautifulSoup(html, "html.parser")

            # Find image containers
            container_selector = engine.image_selectors.get("container", "")
            if not container_selector:
                return []

            containers = soup.select(container_selector)[:10]  # Limit to 10 results

            results = []
            for container in containers:
                image_selector = engine.image_selectors.get("image", "")
                if not image_selector:
                    continue

                img_tag = container.select_one(image_selector)
                if not img_tag:
                    continue

                # Get image URL
                image_url = img_tag.get("src") or img_tag.get("data-src") or img_tag.get("data-lazy-src")
                if not image_url:
                    continue

                # Make absolute URL
                if image_url.startswith("/"):
                    image_url = urljoin(engine.base_url, image_url)
                elif not image_url.startswith("http"):
                    image_url = urljoin(engine.base_url, image_url)

                # Get source URL (product page)
                source_url = search_url
                link_selector = engine.image_selectors.get("link", "a")
                link_tag = container.select_one(link_selector)
                if link_tag:
                    href = link_tag.get("href")
                    if href:
                        if href.startswith("/"):
                            source_url = urljoin(engine.base_url, href)
                        elif href.startswith("http"):
                            source_url = href
                        else:
                            source_url = urljoin(engine.base_url, href)

                # Extract domain name for source_name
                parsed_url = urlparse(engine.base_url)
                source_name = parsed_url.netloc.replace("www.", "")

                results.append(
                    ImageSearchResult(
                        imageUrl=image_url,
                        thumbnailUrl=image_url,  # Use same URL if no thumbnail selector
                        sourceUrl=source_url,
                        sourceName=source_name,
                        searchEngineId=engine.id,
                        searchEngineName=engine.name,
                    )
                )

            return results

        except Exception as e:
            logger.error(f"Error scraping HTML from {engine.name}: {e}")
            return []

    async def _search_api_images(self, engine: ImageSearchEngineDB, query: str) -> list[ImageSearchResult]:
        """
        Search images via API.

        Args:
            engine: Search engine configuration
            query: Search query

        Returns:
            List of image search results
        """
        if not engine.api_endpoint or not engine.api_key:
            logger.warning(f"API endpoint or key not configured for {engine.name}")
            return []

        try:
            # Build API URL
            api_url = urljoin(engine.base_url, engine.api_endpoint)

            # Prepare request parameters
            max_results = 10  # Default limit per engine

            # Default parameters (can be overridden by response_mapping config)
            # For Pixabay: key, q, image_type, per_page, safesearch
            # For Unsplash: query, per_page (uses Authorization header instead of key param)
            params: dict[str, str | int] = {
                "per_page": min(max_results, 10),
            }

            # Add API key to params or headers based on engine type
            # Pixabay uses 'key' param, Unsplash uses 'Authorization' header
            if "pixabay" in engine.base_url.lower():
                params["key"] = engine.api_key
                params["q"] = query
                params["image_type"] = "photo"
                params["safesearch"] = "true"
            elif "unsplash" in engine.base_url.lower():
                # Unsplash uses 'query' param (not 'q') and Authorization header
                params["query"] = query
            else:
                # Default: try 'key' param and 'q' (for backward compatibility)
                params["key"] = engine.api_key
                params["q"] = query

            # Add custom headers if configured
            headers = engine.request_headers or {}

            # Add Authorization header for Unsplash
            if "unsplash" in engine.base_url.lower() and engine.api_key:
                headers["Authorization"] = f"Client-ID {engine.api_key}"

            # Make API request
            logger.debug(f"Searching {engine.name} API with query: '{query}', URL: {api_url}, params: {params}")
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(api_url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                logger.debug(f"Received {len(data.get('hits', data.get('results', [])))} results from {engine.name}")

            # Parse response using response_mapping if configured, otherwise use default structure
            if engine.response_mapping:
                # Use custom mapping
                hits_path = engine.response_mapping.get("hits", "hits")
                image_url_path = engine.response_mapping.get("imageUrl", "largeImageURL")
                thumbnail_url_path = engine.response_mapping.get("thumbnailUrl", "previewURL")
                source_url_path = engine.response_mapping.get("sourceUrl", "pageURL")

                # Navigate JSON path (simple dot notation for now)
                hits = data
                for key in hits_path.split("."):
                    hits = hits.get(key, [])

            else:
                # Default Pixabay structure
                hits = data.get("hits", [])
                image_url_path = "largeImageURL"
                thumbnail_url_path = "previewURL"
                source_url_path = "pageURL"

            # Extract image URLs
            results = []
            for hit in hits[:max_results]:
                # Get image URL (support dot notation for nested paths)
                image_url = hit
                for key in image_url_path.split("."):
                    image_url = image_url.get(key) if isinstance(image_url, dict) else None
                    if image_url is None:
                        break

                if not image_url:
                    continue

                # Get thumbnail URL
                thumbnail_url = hit
                for key in thumbnail_url_path.split("."):
                    thumbnail_url = thumbnail_url.get(key) if isinstance(thumbnail_url, dict) else None
                    if thumbnail_url is None:
                        break

                # Get source URL
                source_url = hit
                for key in source_url_path.split("."):
                    source_url = source_url.get(key) if isinstance(source_url, dict) else None
                    if source_url is None:
                        break

                # Extract domain name for source_name
                parsed_url = urlparse(engine.base_url)
                source_name = parsed_url.netloc.replace("www.", "")

                results.append(
                    ImageSearchResult(
                        imageUrl=image_url,
                        thumbnailUrl=thumbnail_url or image_url,
                        sourceUrl=source_url or engine.base_url,
                        sourceName=source_name,
                        searchEngineId=engine.id,
                        searchEngineName=engine.name,
                    )
                )

            return results

        except Exception as e:
            logger.error(f"Error searching API images from {engine.name}: {e}")
            return []

    async def search_images(self, item_id: str, query: str | None = None, engine_ids: list[str] | None = None) -> list[ImageSearchResult]:
        """
        Search for images for an item.

        Args:
            item_id: Item ID
            query: Optional custom search query (will be built from item if not provided)
            engine_ids: Optional list of engine IDs to use (uses all active if not provided)

        Returns:
            List of image search results
        """
        # Get item
        from sqlalchemy import select

        stmt = select(GearItemDB).where(GearItemDB.id == item_id)
        result = await self.db.execute(stmt)
        item = result.scalar_one_or_none()

        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

        # Build query if not provided
        if not query:
            query = self._build_search_query(item)

        # Get engines
        if engine_ids:
            engines = await self.engine_repo.get_by_ids(engine_ids)
        else:
            engines = await self.engine_repo.get_all(active_only=True)

        # Search with each engine
        all_results = []
        for engine in engines:
            if engine.type == "html_scraper":
                results = await self._scrape_html_images(engine, query)
            elif engine.type == "api":
                results = await self._search_api_images(engine, query)
            else:
                logger.warning(f"Unknown engine type: {engine.type}")
                continue

            all_results.extend(results)

        return all_results

    async def search_images_by_query(self, query: str, engine_ids: list[str] | None = None) -> list[ImageSearchResult]:
        """
        Search for images by query string only (without item_id).
        Useful for testing or direct search without an item context.

        Args:
            query: Search query string
            engine_ids: Optional list of engine IDs to use (uses all active if not provided)

        Returns:
            List of image search results
        """
        # Get engines
        if engine_ids:
            engines = await self.engine_repo.get_by_ids(engine_ids)
        else:
            engines = await self.engine_repo.get_all(active_only=True)

        # Search with each engine
        all_results = []
        for engine in engines:
            if engine.type == "html_scraper":
                results = await self._scrape_html_images(engine, query)
            elif engine.type == "api":
                results = await self._search_api_images(engine, query)
            else:
                logger.warning(f"Unknown engine type: {engine.type}")
                continue

            all_results.extend(results)

        return all_results

    async def download_and_add_image(
        self,
        item_id: str,
        user_id: str,
        image_url: str,
        source_url: str | None = None,
        source_name: str | None = None,
        search_engine_id: str | None = None,
        is_primary: bool = False,
    ) -> dict:
        """
        Download image from URL and add it to item gallery.

        Args:
            item_id: Item ID
            user_id: User ID (who is adding the image)
            image_url: URL of the image to download
            source_url: Original product page URL
            source_name: Display name of source (e.g., "militaria.pl")
            search_engine_id: Search engine ID that found this image
            is_primary: Whether this should be the primary image

        Returns:
            Image metadata dictionary

        Raises:
            HTTPException: If download or processing fails
        """
        try:
            # Download image
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(image_url, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
                content = response.content

            # Validate file size
            if len(content) > settings.storage.max_file_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Image size exceeds maximum allowed size of {settings.storage.max_file_size / 1024 / 1024:.1f} MB",
                )

            # Detect MIME type from content
            from PIL import Image
            import asyncio

            img = await asyncio.to_thread(Image.open, BytesIO(content))
            original_width, original_height = img.size

            # Detect MIME type
            format_lower = img.format.lower() if img.format else None
            format_to_mime = {
                "jpeg": "image/jpeg",
                "jpg": "image/jpeg",
                "png": "image/png",
                "webp": "image/webp",
                "gif": "image/gif",
            }
            mime_type = format_to_mime.get(format_lower, "image/jpeg")

            if mime_type not in settings.storage.allowed_mime_types:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=f"Image type {mime_type} not allowed",
                )

            # Check number of existing images
            existing_count = await self.image_repo.count_by_item(item_id)
            if existing_count >= settings.storage.max_files_per_item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum {settings.storage.max_files_per_item} images per item",
                )

            # Process and optimize image
            processed_bytes, processed_mime_type, processed_width, processed_height = await self.processor.process_image(content, mime_type)

            # MIME type to extension mapping
            mime_to_extension = {
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "image/webp": ".webp",
                "image/gif": ".gif",
            }

            # Generate file path
            file_ext = mime_to_extension.get(processed_mime_type, ".jpg")
            file_name = f"{generate_id()}{file_ext}"
            file_path = f"items/{item_id}/{file_name}"

            # Upload to storage
            await self.storage.upload_file(file_path, processed_bytes)

            # Get file size
            file_size = len(processed_bytes)

            # Get next order
            next_order = await self.image_repo.get_next_order(item_id)

            # Set as primary if requested (and unset others)
            if is_primary:
                await self.image_repo.unset_primary_images(item_id)

            # Create image record
            image_data = {
                "item_id": item_id,
                "user_id": user_id,
                "storage_type": settings.storage.type,
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_size,
                "mime_type": processed_mime_type,
                "width": processed_width,
                "height": processed_height,
                "is_primary": is_primary,
                "order": next_order,
                "is_processed": True,
                "original_file_size": len(content),
                "search_engine_id": search_engine_id,
                "source_url": source_url,
                "source_name": source_name,
            }

            image = await self.image_repo.create(image_data)

            # Build response
            return {
                "id": image.id,
                "itemId": image.item_id,
                "userId": image.user_id,
                "url": await self.storage.get_file_url(image.file_path),
                "fileName": image.file_name,
                "fileSize": image.file_size,
                "mimeType": image.mime_type,
                "width": image.width,
                "height": image.height,
                "isPrimary": image.is_primary,
                "order": image.order,
                "createdAt": image.created_at.isoformat(),
                "updatedAt": image.updated_at.isoformat(),
                "sourceUrl": image.source_url,
                "sourceName": image.source_name,
            }

        except httpx.HTTPError as e:
            logger.error(f"Error downloading image from {image_url}: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to download image: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Error processing image from {image_url}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process image: {str(e)}",
            )
