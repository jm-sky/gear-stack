"""Service for handling image uploads with proper error handling and transaction safety."""

import logging
import uuid
from io import BytesIO

import httpx
from fastapi import HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

# Optional import for MIME type detection
try:
    import magic

    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    logger = logging.getLogger(__name__)
    logger.warning("python-magic not available, will use Pillow for MIME type detection")

from app.common.id_utils import generate_id
from app.core.config import settings
from app.core.storage.factory import get_storage_adapter
from app.core.storage.image_processor import ImageProcessor
from app.modules.gear.item_image_repository import ItemImageRepository

logger = logging.getLogger(__name__)

# MIME type to extension mapping (centralized constant)
MIME_TO_EXTENSION = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


class ImageUploadService:
    """Service for handling image uploads."""

    def __init__(self, db: AsyncSession):
        """
        Initialize image upload service.

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
        self.max_file_size = settings.storage.max_file_size
        self.allowed_mime_types = settings.storage.allowed_mime_types
        self.repository = ItemImageRepository(db)

    async def validate_upload(self, file: UploadFile, item_id: str) -> None:
        """
        Validate file upload constraints.

        Args:
            file: Uploaded file
            item_id: Item ID to upload image for

        Raises:
            HTTPException: If validation fails
        """
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset

        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {self.max_file_size / 1024 / 1024:.1f} MB",
            )

        # Check MIME type (preliminary check based on content-type header)
        if file.content_type not in self.allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(self.allowed_mime_types)}",
            )

        # Check number of existing images for item
        existing_count = await self.repository.count_by_item(item_id)
        if existing_count >= settings.storage.max_files_per_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {settings.storage.max_files_per_item} images per item",
            )

        # Check available storage space (for local storage)
        if settings.storage.type == "local":
            available_space = await self.storage.get_available_space()
            if available_space and available_space < file_size:
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail="Insufficient storage space",
                )

    async def upload_image(self, file: UploadFile, item_id: str, user_id: str, is_primary: bool = False) -> dict:
        """
        Upload and process image with transaction safety.

        Args:
            file: Uploaded file
            item_id: Item ID
            user_id: User ID (uploader)
            is_primary: Whether this should be the primary image

        Returns:
            Image metadata dictionary

        Raises:
            HTTPException: If upload or processing fails
        """
        # Read file content
        content = await file.read()
        original_filename = file.filename or "uploaded-image"

        return await self._process_and_store_image(
            content=content,
            item_id=item_id,
            user_id=user_id,
            original_filename=original_filename,
            is_primary=is_primary,
        )

    async def delete_image(self, image_id: str, user_id: str) -> bool:
        """
        Delete image by ID.

        Args:
            image_id: Image ID
            user_id: User ID (for authorization check)

        Returns:
            True if deleted successfully, False if not found
        """
        image = await self.repository.get_by_id(image_id)

        if not image:
            return False

        # Delete from storage (continue even if this fails)
        try:
            await self.storage.delete(image.file_path)
        except Exception as e:
            logger.error(f"Failed to delete file from storage: {e}")

        # Delete from database
        await self.repository.delete(image_id)

        return True

    async def reorder_images(self, item_id: str, image_orders: list[dict]) -> bool:
        """
        Reorder images for an item.

        Args:
            item_id: Item ID
            image_orders: List of {"id": "uuid", "order": 0} dictionaries

        Returns:
            True if successful
        """
        for item in image_orders:
            await self.repository.update(item["id"], {"order": item["order"]})
        return True

    async def set_primary_image(self, item_id: str, image_id: str) -> bool:
        """
        Set image as primary for item.

        Args:
            item_id: Item ID
            image_id: Image ID to set as primary

        Returns:
            True if successful
        """
        # Unset current primary
        await self.repository.unset_primary_for_item(item_id)

        # Set new primary
        await self.repository.update(image_id, {"is_primary": True})

        return True

    async def get_item_images(self, item_id: str) -> list[dict]:
        """
        Get all images for an item with URLs.

        Args:
            item_id: Item ID

        Returns:
            List of image dictionaries with URLs
        """
        images = await self.repository.get_by_item(item_id)

        result = []
        for img in images:
            url = await self.storage.get_url(img.file_path)
            result.append(
                {
                    "id": img.id,
                    "item_id": img.item_id,
                    "user_id": img.user_id,
                    "url": url,
                    "file_name": img.file_name,
                    "file_size": img.file_size,
                    "mime_type": img.mime_type,
                    "width": img.width,
                    "height": img.height,
                    "is_primary": img.is_primary,
                    "order": img.order,
                    "created_at": img.created_at.isoformat(),
                    "updated_at": img.updated_at.isoformat(),
                }
            )

        return result

    async def upload_image_from_url(self, image_url: str, item_id: str, user_id: str, is_primary: bool = False) -> dict:
        """
        Download image from external URL and create item image.

        Args:
            image_url: External image URL
            item_id: Item ID
            user_id: User ID (uploader)
            is_primary: Whether this should be the primary image

        Returns:
            Image metadata dictionary

        Raises:
            HTTPException: If download or processing fails
        """
        # Check max images per item
        existing_count = await self.repository.count_by_item(item_id)
        if existing_count >= settings.storage.max_files_per_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {settings.storage.max_files_per_item} images per item",
            )

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()

                content = response.content
        except httpx.HTTPError as exc:
            logger.error("Failed to download image from URL %s: %s", image_url, exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to download image from URL",
            ) from exc

        # Enforce max file size
        file_size = len(content)
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {self.max_file_size / 1024 / 1024:.1f} MB",
            )

        # Check available storage for local adapter
        if settings.storage.type == "local":
            available_space = await self.storage.get_available_space()
            if available_space and available_space < file_size:
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail="Insufficient storage space",
                )

        # Use last part of URL as original filename, if possible
        original_filename = image_url.rsplit("/", 1)[-1] or "remote-image"

        return await self._process_and_store_image(
            content=content,
            item_id=item_id,
            user_id=user_id,
            original_filename=original_filename,
            is_primary=is_primary,
        )

    async def _process_and_store_image(
        self,
        content: bytes,
        item_id: str,
        user_id: str,
        original_filename: str,
        is_primary: bool,
    ) -> dict:
        """Shared implementation for processing, storing and persisting image metadata."""
        # Validate MIME type using python-magic (magic numbers) or Pillow as fallback
        detected_mime = None
        if HAS_MAGIC:
            try:
                mime = magic.Magic(mime=True)
                detected_mime = mime.from_buffer(content)
            except Exception as e:  # pragma: no cover - defensive logging
                logger.warning("Failed to detect MIME type with magic: %s, falling back to Pillow", e)
                detected_mime = None

        # Fallback to Pillow if magic is not available or failed
        if not detected_mime:
            try:
                import asyncio

                img = await asyncio.to_thread(Image.open, BytesIO(content))
                format_lower = img.format.lower() if img.format else None
                # Map Pillow format to MIME type
                format_to_mime = {
                    "jpeg": "image/jpeg",
                    "jpg": "image/jpeg",
                    "png": "image/png",
                    "webp": "image/webp",
                    "gif": "image/gif",
                }
                detected_mime = format_to_mime.get(format_lower) if format_lower else None
                if not detected_mime:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to detect file type",
                    )
            except Exception as e:
                logger.error("Failed to detect MIME type with Pillow: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to detect file type",
                ) from e

        if detected_mime not in self.allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Invalid file type. Detected: {detected_mime}",
            )

        # Validate image integrity
        if not await self.processor.validate_image(content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or corrupted image file",
            )

        original_size = len(content)

        # Process image if enabled
        if settings.storage.enable_processing:
            content, detected_mime, width, height = await self.processor.process_image(content, detected_mime)
            processed_size = len(content)
        else:
            # Get dimensions without processing (run in thread pool)
            import asyncio

            img = await asyncio.to_thread(Image.open, BytesIO(content))
            width, height = img.size
            processed_size = original_size

        # Generate unique filename
        file_ext = MIME_TO_EXTENSION.get(detected_mime, ".jpg")
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        destination_path = f"items/{item_id}/{unique_filename}"

        # Upload to storage with rollback on failure
        stored_path = None
        try:
            stored_path = await self.storage.upload(
                content,
                destination_path,
                detected_mime,
                metadata={
                    "item_id": item_id,
                    "user_id": user_id,
                    "original_filename": original_filename,
                },
            )

            # If this is primary or no primary exists, unset other primaries
            if is_primary:
                await self.repository.unset_primary_for_item(item_id)
            else:
                # Check if any primary exists
                existing_primary = await self.repository.get_primary_image(item_id)
                if not existing_primary:
                    # First image should be primary
                    is_primary = True

            # Create database record
            image_record = await self.repository.create(
                {
                    "item_id": item_id,
                    "user_id": user_id,
                    "storage_type": settings.storage.type,
                    "file_path": stored_path,
                    "file_name": original_filename,
                    "file_size": processed_size,
                    "mime_type": detected_mime,
                    "width": width,
                    "height": height,
                    "is_primary": is_primary,
                    "order": await self.repository.get_next_order(item_id),
                    "is_processed": settings.storage.enable_processing,
                    "original_file_size": (original_size if settings.storage.enable_processing else None),
                }
            )

            # Get accessible URL
            url = await self.storage.get_url(stored_path)

            return {
                "id": image_record.id,
                "url": url,
                "file_name": original_filename,
                "file_size": processed_size,
                "mime_type": detected_mime,
                "width": width,
                "height": height,
                "is_primary": is_primary,
                "order": image_record.order,
            }

        except Exception as e:  # pragma: no cover - defensive rollback path
            # Rollback: delete uploaded file if database insert failed
            if stored_path:
                try:
                    await self.storage.delete(stored_path)
                    logger.info("Rolled back uploaded file: %s", stored_path)
                except Exception as cleanup_error:
                    logger.error("Failed to cleanup uploaded file %s: %s", stored_path, cleanup_error)

            logger.error("Image upload failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image",
            ) from e
