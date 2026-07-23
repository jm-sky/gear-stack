"""Business logic service for gear management.

This module contains business logic for gear containers and items,
including validation, calculations, and orchestration of repository operations.
"""

import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any, Literal, cast

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.config import get_settings
from app.core.storage.factory import get_storage_adapter
from app.modules.auth.db_models import UserDB
from app.modules.settings.db_models import UserSettingsDB

from .db_models import (
    GlobalCatalogueItemDB,
)
from .db_models_v2 import GearItemDBV2
from .item_image_repository import ItemImageRepository
from .repository import GearRepository
from .repository_v2 import GearRepositoryV2
from .schemas import (
    ContainerInfo,
    ContainerResponse,
    ContentReportListResponse,
    ContentReportResponse,
    GlobalCatalogueItemCreate,
    GlobalCatalogueItemResponse,
    GlobalCatalogueItemSearchParams,
    GlobalCatalogueItemUpdate,
    ItemPromotionStatus,
    ItemResponse,
    ReportReason,
    ReportStatus,
)
from .schemas_v2 import GearItemCreateV2, GearItemUpdateV2

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)

# Type aliases for Literal types
WeightUnit = Literal["g", "kg", "oz", "lb"]
Priority = Literal["critical", "high", "medium", "low"]
ItemStatus = Literal["owned", "missing", "toBuy"]
Quality = Literal["low", "medium", "high"]
ContainerColor = Literal[
    "default",
    "blue",
    "green",
    "red",
    "yellow",
    "purple",
    "orange",
    "pink",
    "teal",
    "indigo",
]


class GearService:
    """Service for gear management business logic.

    Handles container and item operations with business logic,
    validation, and weight calculations.
    """

    def __init__(self, repository: GearRepository):
        """Initialize service with repository.

        Args:
            repository: Gear repository instance
        """
        self.repository = repository
        self._image_repository = ItemImageRepository(repository.db)
        self._storage = get_storage_adapter()
        self._repository_v2 = GearRepositoryV2(repository.db)

    async def _delete_all_item_images(self, item_id: str) -> int:
        """Delete all images for an item from storage and database.

        This is a helper method used when deleting items.
        It deletes images from storage (S3/local) and database.

        Args:
            item_id: Item ID

        Returns:
            Number of images deleted
        """
        images = await self._image_repository.get_by_item(item_id)
        deleted_count = 0

        for image in images:
            # Delete from storage only if not external URL (continue even if this fails)
            if image.storage_type != "external" and image.file_path:
                try:
                    await self._storage.delete(image.file_path)
                except Exception as e:
                    logger.error(f"Failed to delete image file from storage (item_id={item_id}, image_id={image.id}): {e}")

            # Delete from database (cascade delete will handle this, but we do it explicitly for logging)
            try:
                await self._image_repository.delete(image.id)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete image record from database (item_id={item_id}, image_id={image.id}): {e}")

        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} image(s) for item {item_id}")

        return deleted_count

    async def delete_all_user_images(self, user_id: str) -> int:
        """Delete all images for a user from storage and database.

        This method is used when deleting a user account.
        It deletes all images belonging to the user across all items.

        Args:
            user_id: User ID

        Returns:
            Number of images deleted
        """
        images = await self._image_repository.get_all_by_user(user_id)
        deleted_count = 0

        for image in images:
            # Delete from storage only if not external URL (continue even if this fails)
            if image.storage_type != "external" and image.file_path:
                try:
                    await self._storage.delete(image.file_path)
                except Exception as e:
                    logger.error(f"Failed to delete image file from storage (user_id={user_id}, image_id={image.id}): {e}")

            # Delete from database
            try:
                await self._image_repository.delete(image.id)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete image record from database (user_id={user_id}, image_id={image.id}): {e}")

        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} image(s) for user {user_id}")

        return deleted_count

    async def _get_catalogue_item_creator_name(self, item: GlobalCatalogueItemDB) -> str | None:
        """Get creator name for catalogue item if profile is public.

        Args:
            item: Catalogue item with creator relationship loaded

        Returns:
            Creator name if profile is public, None otherwise
        """
        if not hasattr(item, "creator") or not item.creator:
            return None

        creator = item.creator
        # Check if creator has public profile
        settings_stmt = select(UserSettingsDB).where(UserSettingsDB.user_id == creator.id)
        settings_result = await self.repository.db.execute(settings_stmt)
        user_settings = settings_result.scalar_one_or_none()

        if user_settings and user_settings.is_public_profile:
            return creator.name

        return None

    def _map_item_v2_to_response(
        self,
        item: GearItemDBV2,
        primary_image_url: str | None = None,
        container: GearItemDBV2 | None = None,
    ) -> ItemResponse:
        """Map a gear_items_v2 item row to the (V1-shaped) ItemResponse schema.

        Counterpart to _map_item_to_response, for the public-browsing/share-token paths that
        have been repointed at gear_items_v2 (docs/plans/2026-07-23-gear-backend-v1-v2-unification.md,
        Phase 3b). Field names differ from GearItemDB in a few places (order_index vs order,
        container_type vs type); there is no V2 equivalent of the legacy nested_container_id
        field (V2 represents nested containers as ordinary child rows via parent_item_id, not a
        separate item field), so containerId is always None here.

        Args:
            item: gear_items_v2 row (item_type='item')
            primary_image_url: Optional primary image URL for the item
            container: Optional parent container row (item_type='container'), for ContainerInfo

        Returns:
            Item response schema
        """
        container_info = None
        if container is not None:
            container_info = ContainerInfo(
                id=container.id,
                name=container.name,
                type=cast(str, container.container_type),
                color=cast(ContainerColor | None, container.color),
            )

        # weight/weightUnit are nullable on gear_items_v2 (GearItemCreateV2 doesn't require or
        # default them, unlike category/quantity/status/priority) but required by the V1-shaped
        # ItemResponse schema -- default to "unknown weight" rather than raising a validation
        # error on every item created without one.
        return ItemResponse(
            id=item.id,
            name=item.name,
            category=cast(str, item.category),
            quantity=cast(int, item.quantity),
            weight=item.weight if item.weight is not None else 0.0,
            weightUnit=cast(WeightUnit, item.weight_unit) if item.weight_unit else "g",
            notes=item.notes,
            expirationDate=item.expiration_date,
            shelfLife=item.shelf_life,
            priority=cast(Priority, item.priority),
            status=cast(ItemStatus, item.status),
            containerId=None,  # No V2 equivalent of legacy nested_container_id
            container=container_info,
            price=item.price,
            currency=item.currency,
            url=item.url,
            brand=item.brand,
            color=item.color,
            quality=cast(Quality | None, item.quality),
            linkedItemId=item.linked_item_id,
            catalogueItemId=item.catalogue_item_id,
            wearable=item.wearable,
            consumable=item.consumable,
            order=item.order_index,
            showOnContainer=item.show_on_container,
            primaryImageUrl=primary_image_url,
            promote_count=item.promote_count or 0,
            createdAt=item.created_at,
            updatedAt=item.updated_at,
        )

    async def _map_container_v2_to_response_with_author(self, container: GearItemDBV2, ratings_data: dict[str, Any] | None = None) -> ContainerResponse:
        """Map a gear_items_v2 container row to ContainerResponse, with author name.

        Counterpart to _map_container_to_response_with_author, for the public-browsing/
        share-token paths repointed at gear_items_v2 (Phase 3b of
        docs/plans/2026-07-23-gear-backend-v1-v2-unification.md). `container.children` must be
        eager-loaded by the caller's query (selectinload) -- unlike GearContainerDB.items, it
        includes both nested sub-containers and items, so it's filtered to item_type='item' here
        to match the shape GearContainerDB.items always had.

        Args:
            container: gear_items_v2 row (item_type='container'), with .children and .user
                eager-loaded
            ratings_data: Optional ratings data from repository

        Returns:
            Container response schema with author name
        """
        container_items = [child for child in container.children if child.item_type == "item"]

        item_ids = [item.id for item in container_items]
        primary_images = await self._image_repository.get_primary_images_by_items(item_ids)

        image_urls: dict[str, str] = {}
        for item_id, image in primary_images.items():
            url = image.external_url or await self._storage.get_url(image.file_path)
            image_urls[item_id] = url

        items = [self._map_item_v2_to_response(item, image_urls.get(item.id), container=container) for item in container_items]

        author_name = None
        author_id = None
        if hasattr(container, "user") and container.user:
            settings_stmt = select(UserSettingsDB).where(UserSettingsDB.user_id == container.user.id)
            settings_result = await self.repository.db.execute(settings_stmt)
            user_settings = settings_result.scalar_one_or_none()

            if user_settings and user_settings.is_public_profile:
                author_name = container.user.name
                author_id = container.user.id

        owner_rating = None
        user_rating = None
        average_user_rating = None
        user_rating_count = 0

        if ratings_data:
            owner_rating = ratings_data.get("owner_rating")
            user_rating = ratings_data.get("user_rating")
            average_user_rating = ratings_data.get("average_user_rating")
            user_rating_count = ratings_data.get("user_rating_count", 0)

        return ContainerResponse(
            id=container.id,
            name=container.name,
            description=container.description,
            type=cast(str, container.container_type),
            color=cast(ContainerColor | None, container.color),
            parentContainerId=container.parent_item_id,
            brand=container.brand,
            price=container.price,
            hideWhenNested=container.hide_when_nested,
            weight=container.weight,
            weightUnit=cast(WeightUnit | None, container.weight_unit),
            maxWeight=container.max_weight,
            maxWeightUnit=cast(WeightUnit | None, container.max_weight_unit),
            url=container.url,
            isPublic=cast(bool, container.is_public),
            favorite=cast(bool, container.favorite),
            showItemImages=container.show_item_images,
            authorName=author_name,
            authorId=author_id,
            items=items,
            ownerRating=owner_rating,
            userRating=user_rating,
            averageUserRating=(float(average_user_rating) if average_user_rating else None),
            userRatingCount=user_rating_count,
            createdAt=container.created_at,
            updatedAt=container.updated_at,
        )

    async def get_public_containers(self, skip: int = 0, limit: int = 100, requesting_user_id: str | None = None) -> list[ContainerResponse]:
        """Get all public containers from all users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            requesting_user_id: Optional user ID for user rating data

        Returns:
            List of public container responses with author names
        """
        containers = await self.repository.get_public_containers(skip, limit)
        results = []
        for container in containers:
            try:
                ratings_data = await self.repository.get_container_ratings_data(container.id, requesting_user_id=requesting_user_id, is_owner=False)
                mapped = await self._map_container_v2_to_response_with_author(container, dict(ratings_data) if ratings_data else None)
                results.append(mapped)
            except Exception as e:
                # Log error but continue - one container error shouldn't prevent others from being returned
                logger.error(
                    f"Failed to map public container {container.id} to response: {e}",
                    exc_info=True,
                )
        return results

    async def get_public_container(self, container_id: str, requesting_user_id: str | None = None) -> ContainerResponse | None:
        """Get a public container by ID.

        Args:
            container_id: Container ID
            requesting_user_id: Optional user ID for user rating data

        Returns:
            Container response with author name if found and public, None otherwise
        """
        container = await self.repository.get_public_container(container_id)
        if not container:
            return None

        ratings_data = await self.repository.get_container_ratings_data(container_id, requesting_user_id=requesting_user_id, is_owner=False)

        return await self._map_container_v2_to_response_with_author(container, dict(ratings_data) if ratings_data else None)

    async def get_container_by_share_token(self, token: str, requesting_user_id: str | None = None) -> ContainerResponse | None:
        """Get a container by share token.

        Args:
            token: Share token
            requesting_user_id: Optional user ID for user rating data

        Returns:
            Container response with author name if token is valid and not expired, None otherwise
        """
        container = await self.repository.get_container_by_token(token)
        if not container:
            return None

        ratings_data = await self.repository.get_container_ratings_data(container.id, requesting_user_id=requesting_user_id, is_owner=False)

        return await self._map_container_v2_to_response_with_author(container, dict(ratings_data) if ratings_data else None)

    async def create_share_token(self, container_id: str, user_id: str, expires_at: datetime | None = None) -> str:
        """Create a share token for a container.

        Args:
            container_id: Container ID to share
            user_id: Owner user ID
            expires_at: Optional expiration timestamp

        Returns:
            Generated share token

        Raises:
            ValueError: If container not found or user doesn't own it
        """
        # Verify container ownership (gear_items_v2) -- checking legacy gear_containers here
        # would always fail for V2-native containers, i.e. any container created through
        # today's app (see #043).
        container = await self._repository_v2.get_item(container_id, user_id)
        if not container or container.item_type != "container":
            raise ValueError("Container not found or access denied")

        # Generate unique token
        token = secrets.token_urlsafe(32)

        # Create share token
        await self.repository.create_share_token(container_id, user_id, token, expires_at)

        return token

    async def get_share_tokens(self, container_id: str, user_id: str) -> list[dict]:
        """Get all share tokens for a container.

        Args:
            container_id: Container ID
            user_id: Owner user ID

        Returns:
            List of share token dictionaries with share URLs
        """
        tokens = await self.repository.get_share_tokens_by_container(container_id, user_id)
        result = []
        for token_db in tokens:
            # Construct share URL (frontend will handle the base URL)
            share_url = f"/shared/container/{token_db.token}"
            result.append(
                {
                    "token": token_db.token,
                    "containerId": token_db.container_id,
                    "expiresAt": token_db.expires_at,
                    "createdAt": token_db.created_at,
                    "shareUrl": share_url,
                }
            )
        return result

    async def revoke_share_token(self, token: str, user_id: str) -> bool:
        """Revoke a share token.

        Args:
            token: Share token to revoke
            user_id: Owner user ID

        Returns:
            True if token was revoked, False otherwise
        """
        return await self.repository.revoke_share_token(token, user_id)

    # Global Catalogue Methods
    async def get_catalogue_items(
        self,
        search_params: GlobalCatalogueItemSearchParams,
    ) -> list[GlobalCatalogueItemResponse]:
        """Get global catalogue items.

        Args:
            search_params: Search and filter parameters

        Returns:
            List of catalogue items
        """
        from app.modules.gear.catalogue_item_image_repository import (
            CatalogueItemImageRepository,
        )

        items = await self.repository.get_catalogue_items(
            query=search_params.query,
            category=search_params.category,
            brand=search_params.brand,
            price_tier=search_params.priceTier,
            quality=search_params.quality,
            is_active=search_params.isActive,
            skip=search_params.skip,
            limit=search_params.limit,
        )

        # Batch fetch primary images for all items
        catalogue_image_repo = CatalogueItemImageRepository(self.repository.db)
        item_ids = [item.id for item in items]
        primary_images = await catalogue_image_repo.get_primary_images_by_catalogue_items(item_ids)

        # Get URLs for all primary images
        image_urls: dict[str, str] = {}
        for item_id, image in primary_images.items():
            url = image.external_url or await self._storage.get_url(image.file_path)
            image_urls[item_id] = url

        # Map items to responses with primary image URLs and creator names
        results = []
        for item in items:
            item_dict = GlobalCatalogueItemResponse.model_validate(item).model_dump()
            item_dict["primaryImageUrl"] = image_urls.get(item.id)
            # Get creator name if profile is public
            creator_name = await self._get_catalogue_item_creator_name(item)
            item_dict["creatorName"] = creator_name
            results.append(GlobalCatalogueItemResponse(**item_dict))

        return results

    async def get_catalogue_item(self, item_id: str) -> GlobalCatalogueItemResponse | None:
        """Get a single catalogue item.

        Args:
            item_id: Catalogue item ID

        Returns:
            Catalogue item if found, None otherwise
        """
        from app.modules.gear.catalogue_item_image_repository import (
            CatalogueItemImageRepository,
        )

        item = await self.repository.get_catalogue_item(item_id)
        if not item:
            return None

        # Fetch primary image for this item
        catalogue_image_repo = CatalogueItemImageRepository(self.repository.db)
        primary_image = await catalogue_image_repo.get_primary_image(item_id)

        # Get URL for primary image if exists
        primary_image_url = None
        if primary_image:
            primary_image_url = primary_image.external_url or await self._storage.get_url(primary_image.file_path)

        # Create response with image URL and creator name
        item_dict = GlobalCatalogueItemResponse.model_validate(item).model_dump()
        item_dict["primaryImageUrl"] = primary_image_url
        # Get creator name if profile is public
        creator_name = await self._get_catalogue_item_creator_name(item)
        item_dict["creatorName"] = creator_name
        return GlobalCatalogueItemResponse(**item_dict)

    async def create_catalogue_item(
        self,
        user_id: str,
        data: GlobalCatalogueItemCreate,
    ) -> GlobalCatalogueItemResponse:
        """Create a new catalogue item.

        Args:
            user_id: User ID creating the item
            data: Item creation data

        Returns:
            Created catalogue item
        """
        item = await self.repository.create_catalogue_item(user_id, data)
        # Reload item with creator relationship

        reload_stmt = select(GlobalCatalogueItemDB).where(GlobalCatalogueItemDB.id == item.id).options(joinedload(GlobalCatalogueItemDB.creator))
        reload_result = await self.repository.db.execute(reload_stmt)
        item_with_creator = reload_result.unique().scalar_one()
        # Map to response with creator name
        item_dict = GlobalCatalogueItemResponse.model_validate(item_with_creator).model_dump()
        creator_name = await self._get_catalogue_item_creator_name(item_with_creator)
        item_dict["creatorName"] = creator_name
        return GlobalCatalogueItemResponse(**item_dict)

    async def update_catalogue_item(
        self,
        item_id: str,
        user_id: str,
        data: GlobalCatalogueItemUpdate,
        is_admin: bool = False,
    ) -> GlobalCatalogueItemResponse | None:
        """Update a catalogue item.

        Args:
            item_id: Catalogue item ID
            user_id: User ID updating the item
            data: Update data
            is_admin: Whether user is admin

        Returns:
            Updated item if found and user has permission, None otherwise
        """
        item = await self.repository.update_catalogue_item(item_id, user_id, data, is_admin)
        if not item:
            return None
        # Reload item with creator relationship

        reload_stmt = select(GlobalCatalogueItemDB).where(GlobalCatalogueItemDB.id == item.id).options(joinedload(GlobalCatalogueItemDB.creator))
        reload_result = await self.repository.db.execute(reload_stmt)
        item_with_creator = reload_result.unique().scalar_one()
        # Map to response with creator name
        item_dict = GlobalCatalogueItemResponse.model_validate(item_with_creator).model_dump()
        creator_name = await self._get_catalogue_item_creator_name(item_with_creator)
        item_dict["creatorName"] = creator_name
        return GlobalCatalogueItemResponse(**item_dict)

    async def delete_catalogue_item(
        self,
        item_id: str,
        user_id: str,
        is_admin: bool = False,
    ) -> bool:
        """Delete a catalogue item (soft delete).

        Args:
            item_id: Catalogue item ID
            user_id: User ID deleting the item
            is_admin: Whether user is admin

        Returns:
            True if deleted, False otherwise
        """
        return await self.repository.delete_catalogue_item(item_id, user_id, is_admin)

    async def add_catalogue_item_to_container(
        self,
        container_id: str,
        catalogue_item_id: str,
        user_id: str,
        quantity: int = 1,
        status: str = "owned",
        priority: str = "medium",
        copy_image: bool = False,
    ) -> ItemResponse | None:
        """Add a catalogue item to a user's container.

        Creates a new item in the container based on catalogue item data.
        The new item is independent (not linked to catalogue).

        Args:
            container_id: Target container ID
            catalogue_item_id: Catalogue item ID to copy
            user_id: User ID
            quantity: Item quantity (default: 1)
            status: Item status (default: "owned")
            priority: Item priority (default: "medium")
            copy_image: Whether to copy images from catalogue item (default: False)

        Returns:
            Created item if successful, None otherwise
        """
        # Get catalogue item
        catalogue_item = await self.repository.get_catalogue_item(catalogue_item_id)
        if not catalogue_item or not catalogue_item.is_active:
            return None

        # Verify container belongs to user (gear_items_v2) -- checking legacy gear_containers
        # here would always fail for V2-native containers, i.e. any container created through
        # today's app (see #043).
        container = await self._repository_v2.get_item(container_id, user_id)
        if not container or container.item_type != "container":
            return None

        # Create item from catalogue data
        item_data = GearItemCreateV2(  # type: ignore[call-arg]
            itemType="item",
            parentItemId=container_id,
            name=catalogue_item.name,
            category=catalogue_item.category,
            weight=catalogue_item.weight,
            weightUnit=cast(WeightUnit, catalogue_item.weight_unit),
            quantity=quantity,
            status=cast(ItemStatus, status),
            priority=cast(Priority, priority),
            brand=catalogue_item.brand,
            color=catalogue_item.color,
            url=catalogue_item.url,
            catalogueItemId=catalogue_item_id,
        )

        # Create item
        created_item_db = await self._repository_v2.create_item(user_id, item_data)
        created_item = self._map_item_v2_to_response(created_item_db)

        # Copy images if requested
        # Note: We copy images before verifying item exists to avoid transaction isolation issues
        # The create_item method already commits the transaction, so the item should be visible
        if copy_image:
            try:
                await self._copy_catalogue_images_to_item(catalogue_item_id, created_item.id, user_id)
            except Exception as e:
                logger.error(
                    "Failed to copy images for item %s: %s. Item was created successfully.",
                    created_item.id,
                    e,
                )
                # Return item even if image copy fails
                return created_item

        return created_item

    async def _copy_catalogue_images_to_item(
        self,
        catalogue_item_id: str,
        item_id: str,
        user_id: str,
    ) -> bool:
        """Copy images from catalogue item to user item.

        Args:
            catalogue_item_id: Source catalogue item ID
            item_id: Target item ID
            user_id: User ID (owner of the target item)
        """
        from app.common.id_utils import generate_id
        from app.modules.gear.catalogue_item_image_repository import (
            CatalogueItemImageRepository,
        )
        from app.modules.gear.db_models import ItemImageDB

        # Get catalogue images
        catalogue_image_repo = CatalogueItemImageRepository(self.repository.db)
        catalogue_images = await catalogue_image_repo.get_by_catalogue_item(catalogue_item_id)

        if not catalogue_images:
            return False

        # Verify item exists before starting to copy images
        # This is a safety check to ensure the item is in the database. item_images.item_id FK
        # targets gear_items_v2 (migration 058), so the check must too -- checking legacy
        # gear_items here would always fail for V2-native items (see #043).
        item_check_stmt = select(GearItemDBV2).where(GearItemDBV2.id == item_id)
        item_check_result = await self.repository.db.execute(item_check_stmt)
        initial_item_check = item_check_result.scalar_one_or_none()
        if not initial_item_check:
            logger.error(
                "Item %s does not exist in database. Cannot copy images.",
                item_id,
            )
            return False

        # Copy each image
        # Note: Item was already committed by create_item(), so it exists in the database
        for catalogue_image in catalogue_images:
            # Store catalogue_image attributes before try block to avoid accessing expired object in except
            catalogue_image_id = catalogue_image.id
            catalogue_image_file_path = catalogue_image.file_path
            catalogue_image_file_name = catalogue_image.file_name
            catalogue_image_mime_type = catalogue_image.mime_type
            catalogue_image_storage_type = catalogue_image.storage_type
            catalogue_image_file_size = catalogue_image.file_size
            catalogue_image_width = catalogue_image.width
            catalogue_image_height = catalogue_image.height
            catalogue_image_is_primary = catalogue_image.is_primary
            catalogue_image_is_processed = catalogue_image.is_processed
            catalogue_image_original_file_size = catalogue_image.original_file_size

            try:
                # Download image from storage
                image_content = await self._storage.download(catalogue_image_file_path)

                # Create new file path for item image
                # Extract extension from original filename
                file_extension = ""
                if "." in catalogue_image_file_name:
                    file_extension = "." + catalogue_image_file_name.rsplit(".", 1)[1]
                new_filename = f"{generate_id()}{file_extension}"
                new_file_path = f"items/{item_id}/{new_filename}"

                # Upload image to new location
                await self._storage.upload(
                    image_content,
                    new_file_path,
                    catalogue_image_mime_type,
                    metadata={
                        "item_id": item_id,
                        "user_id": user_id,
                        "copied_from_catalogue_image": catalogue_image_id,
                    },
                )

                # Create ItemImageDB record
                # Unset primary for other images if this is primary
                if catalogue_image_is_primary:
                    await self._image_repository.unset_primary_for_item(item_id)

                # Get next order value
                next_order = await self._image_repository.get_next_order(item_id)

                new_image = ItemImageDB(
                    id=generate_id(),
                    item_id=item_id,
                    user_id=user_id,
                    storage_type=catalogue_image_storage_type,
                    file_path=new_file_path,
                    file_name=catalogue_image_file_name,
                    file_size=catalogue_image_file_size,
                    mime_type=catalogue_image_mime_type,
                    width=catalogue_image_width,
                    height=catalogue_image_height,
                    is_primary=catalogue_image_is_primary,
                    order=next_order,
                    is_processed=catalogue_image_is_processed,
                    original_file_size=catalogue_image_original_file_size,
                )

                self.repository.db.add(new_image)
                await self.repository.db.flush()  # Flush first to catch errors early
                await self.repository.db.commit()

                logger.info(
                    "Successfully copied image %s from catalogue item %s to item %s",
                    catalogue_image_id,
                    catalogue_item_id,
                    item_id,
                )
            except Exception as e:
                logger.error(
                    "Failed to copy image %s from catalogue item %s to item %s: %s",
                    catalogue_image_id,
                    catalogue_item_id,
                    item_id,
                    e,
                )
                # Rollback on error to allow next image to be added
                try:
                    await self.repository.db.rollback()
                except Exception as rollback_error:
                    logger.error(
                        "Failed to rollback after image copy error: %s",
                        rollback_error,
                    )
                # Continue copying other images even if one fails

        # Return True if at least one image was copied successfully
        return True

    async def update_item_from_catalogue(
        self,
        item_id: str,
        user_id: str,
        fields: list[str] | None = None,
    ) -> ItemResponse | None:
        """Update an item with data from its linked catalogue item.

        Updates only specified fields from catalogue while preserving user-specific fields
        like quantity, status, priority, and notes.

        Args:
            item_id: Item ID to update
            user_id: User ID (must own the item)
            fields: List of field names to update. If None, updates all available fields.

        Returns:
            Updated item if successful, None otherwise
        """
        # Get user item (gear_items_v2)
        item = await self._repository_v2.get_item(item_id, user_id)
        if not item or not item.catalogue_item_id:
            return None

        # Get catalogue item
        catalogue_item = await self.repository.get_catalogue_item(item.catalogue_item_id)
        if not catalogue_item or not catalogue_item.is_active:
            return None

        # Build update data based on requested fields
        update_data_dict: dict[str, Any] = {}

        # If no fields specified, update all available fields
        if fields is None:
            fields = [
                "name",
                "description",
                "weight",
                "weightUnit",
                "price",
                "currency",
                "brand",
                "color",
                "category",
                "quality",
                "url",
            ]

        # Map field names and update only requested fields
        if "name" in fields:
            update_data_dict["name"] = catalogue_item.name
        if "description" in fields:
            update_data_dict["description"] = catalogue_item.description
        if "weight" in fields:
            update_data_dict["weight"] = catalogue_item.weight
        if "weightUnit" in fields or "weight_unit" in fields:
            update_data_dict["weightUnit"] = cast(WeightUnit, catalogue_item.weight_unit)
        if "price" in fields:
            update_data_dict["price"] = catalogue_item.price
        if "currency" in fields:
            update_data_dict["currency"] = catalogue_item.currency
        if "brand" in fields:
            update_data_dict["brand"] = catalogue_item.brand
        if "color" in fields:
            update_data_dict["color"] = catalogue_item.color
        if "category" in fields:
            update_data_dict["category"] = catalogue_item.category
        if "quality" in fields:
            update_data_dict["quality"] = catalogue_item.quality
        if "url" in fields:
            update_data_dict["url"] = catalogue_item.url

        # Preserve: quantity, status, priority, notes, expirationDate, etc.
        update_data = GearItemUpdateV2(**update_data_dict)
        updated_item = await self._repository_v2.update_item(item_id, user_id, update_data)
        if not updated_item:
            return None
        return self._map_item_v2_to_response(updated_item)

    async def link_item_to_catalogue(
        self,
        item_id: str,
        catalogue_item_id: str,
        user_id: str,
    ) -> ItemResponse | None:
        """Link an item to a catalogue item (set catalogue_item_id).

        Args:
            item_id: Item ID to link
            catalogue_item_id: Catalogue item ID to link to
            user_id: User ID (must own the item)

        Returns:
            Updated item if successful, None otherwise
        """
        # Verify item belongs to user (gear_items_v2)
        item = await self._repository_v2.get_item(item_id, user_id)
        if not item:
            return None

        # Verify catalogue item exists and is active
        catalogue_item = await self.repository.get_catalogue_item(catalogue_item_id)
        if not catalogue_item or not catalogue_item.is_active:
            return None

        # Set catalogue_item_id
        update_data = GearItemUpdateV2(catalogueItemId=catalogue_item_id)  # type: ignore[call-arg]
        updated_item = await self._repository_v2.update_item(item_id, user_id, update_data)
        if not updated_item:
            return None
        return self._map_item_v2_to_response(updated_item)

    async def fetch_images_from_catalogue(
        self,
        item_id: str,
        user_id: str,
    ) -> ItemResponse | None:
        """Fetch images from catalogue item and attach them to the gear item.

        Copies images from the linked catalogue item to the user's item.
        The item must be linked to a catalogue item (have catalogue_item_id).

        Args:
            item_id: Item ID to fetch images for
            user_id: User ID (must own the item)

        Returns:
            Updated item if successful, None otherwise
        """
        # Get user item (gear_items_v2) -- this doubles as the "item exists" check that used to
        # be a separate V1 query below (item is already committed by the time we get here).
        item = await self._repository_v2.get_item(item_id, user_id)
        if not item or not item.catalogue_item_id:
            return None

        # Get catalogue item to verify it exists and is active
        catalogue_item = await self.repository.get_catalogue_item(item.catalogue_item_id)
        if not catalogue_item or not catalogue_item.is_active:
            return None

        # Copy images from catalogue to item
        images_copied = await self._copy_catalogue_images_to_item(item.catalogue_item_id, item_id, user_id)

        if not images_copied:
            logger.warning(
                "No images were copied for item %s from catalogue item %s",
                item_id,
                item.catalogue_item_id,
            )

        # Return updated item
        refreshed_item = await self._repository_v2.get_item(item_id, user_id)
        if not refreshed_item:
            return None
        primary_image = await self._image_repository.get_primary_image(item_id)
        primary_image_url = None
        if primary_image:
            primary_image_url = primary_image.external_url or await self._storage.get_url(primary_image.file_path)
        return self._map_item_v2_to_response(refreshed_item, primary_image_url)

    async def unlink_item_from_catalogue(
        self,
        item_id: str,
        user_id: str,
    ) -> ItemResponse | None:
        """Unlink an item from the catalogue (clear catalogue_item_id).

        Args:
            item_id: Item ID to unlink
            user_id: User ID (must own the item)

        Returns:
            Updated item if successful, None otherwise
        """
        item = await self._repository_v2.get_item(item_id, user_id)
        if not item:
            return None

        # Clear catalogue_item_id
        update_data = GearItemUpdateV2(catalogueItemId=None)  # type: ignore[call-arg]
        updated_item = await self._repository_v2.update_item(item_id, user_id, update_data)
        if not updated_item:
            return None
        return self._map_item_v2_to_response(updated_item)

    # Item promotion methods
    def _can_user_promote(self, user: UserDB) -> tuple[bool, str]:
        """Check if user can promote items.

        Args:
            user: User database model

        Returns:
            Tuple of (can_promote: bool, reason: str)
        """
        if not user.created_at:
            return False, "User account creation date not found"

        # Check if account is older than 1 month
        one_month_ago = datetime.now(UTC) - timedelta(days=30)
        if user.created_at > one_month_ago:
            return False, "Account must be at least 1 month old"

        return True, ""

    async def _is_item_or_container_reported(self, item_id: str, container_id: str) -> bool:
        """Check if item or container has been reported for inappropriate content.

        This is a placeholder for future content reporting mechanism.
        Once reporting is implemented, this method should check if the item
        or its container has active reports.

        Args:
            item_id: Item ID to check
            container_id: Container ID to check

        Returns:
            True if item or container is reported, False otherwise
        """
        # TODO: Implement content reporting mechanism
        # This should check if item_id or container_id has active reports
        # Example:
        #   reports = await self.repository.get_active_reports(item_id, container_id)
        #   return len(reports) > 0
        return False

    async def can_promote_item(self, item_id: str, user_id: str) -> tuple[bool, str]:
        """Check if user can promote a specific item.

        Args:
            item_id: Item ID to promote
            user_id: User ID who wants to promote

        Returns:
            Tuple of (can_promote: bool, reason: str)
        """
        # Get user
        from sqlalchemy import select

        from app.modules.auth.db_models import UserDB as UserDBModel

        user_stmt = select(UserDBModel).where(UserDBModel.id == user_id)
        user_result = await self.repository.db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        if not user:
            return False, "User not found"

        # Get item (gear_items_v2) -- promotion isn't limited to items the requester owns;
        # eligibility for someone else's item is gated below by container.is_public.
        item_stmt = select(GearItemDBV2).where(GearItemDBV2.id == item_id, GearItemDBV2.item_type == "item")
        item_result = await self.repository.db.execute(item_stmt)
        item = item_result.scalar_one_or_none()
        if not item:
            return False, "Item not found"

        # Load container to check if it's public
        container_stmt = select(GearItemDBV2).where(GearItemDBV2.id == item.parent_item_id, GearItemDBV2.item_type == "container")
        container_result = await self.repository.db.execute(container_stmt)
        container = container_result.scalar_one_or_none()
        if not container:
            return False, "Container not found"

        # Check if user is admin or owner (app owner role)
        is_admin_or_owner = getattr(user, "is_admin", False) or getattr(user, "is_owner", False)

        # Check user account age (skip if admin or owner)
        if not is_admin_or_owner:
            can_promote, reason = self._can_user_promote(user)
            if not can_promote:
                return False, reason

        # Check if container is public
        if not container.is_public:
            return False, "Item must be in a public container to be promoted"

        # Check if container/item owner has account older than 1 month (skip if user is admin or owner)
        if not is_admin_or_owner:
            container_owner_stmt = select(UserDBModel).where(UserDBModel.id == container.user_id)
            container_owner_result = await self.repository.db.execute(container_owner_stmt)
            container_owner = container_owner_result.scalar_one_or_none()
            if not container_owner:
                return False, "Container owner not found"

            owner_can_promote, owner_reason = self._can_user_promote(container_owner)
            if not owner_can_promote:
                return (
                    False,
                    "Item owner account must be at least 1 month old to allow promotions",
                )

        # Check if item or container is reported for inappropriate content
        is_reported = await self._is_item_or_container_reported(item_id, container.id)
        if is_reported:
            return False, "Item or container has been reported and cannot be promoted"

        # Check if item is already in catalogue
        if item.catalogue_item_id:
            return False, "Item is already in the catalogue"

        # Check if user already promoted this item
        existing_promotion = await self.repository.get_promotion_by_item_and_user(item_id, user_id)
        if existing_promotion:
            return False, "You have already promoted this item"

        return True, ""

    async def promote_item(self, item_id: str, user_id: str) -> ItemResponse:
        """Promote an item to catalogue.

        Args:
            item_id: Item ID to promote
            user_id: User ID who is promoting

        Returns:
            Updated item response

        Raises:
            ValueError: If promotion is not allowed
        """
        # Check if user can promote
        can_promote, reason = await self.can_promote_item(item_id, user_id)
        if not can_promote:
            raise ValueError(reason)

        # Get item (gear_items_v2) -- promotion isn't limited to items the requester owns,
        # eligibility was already gated by can_promote_item() above.
        item_stmt = select(GearItemDBV2).where(GearItemDBV2.id == item_id, GearItemDBV2.item_type == "item")
        item_result = await self.repository.db.execute(item_stmt)
        item = item_result.scalar_one_or_none()
        if not item:
            raise ValueError("Item not found")

        # Create promotion record
        await self.repository.create_promotion(item_id, user_id)

        # Increment promote_count
        item.promote_count = (item.promote_count or 0) + 1
        await self.repository.db.commit()
        await self.repository.db.refresh(item)

        # Check if threshold reached
        settings = get_settings()
        threshold = settings.app.item_promotion_threshold
        if item.promote_count >= threshold:
            # Add to catalogue automatically
            await self._add_item_to_catalogue(item_id, user_id)

        # Return updated item
        return self._map_item_v2_to_response(item)

    async def get_promotion_status(self, item_id: str, user_id: str | None = None) -> ItemPromotionStatus:
        """Get promotion status for an item.

        Args:
            item_id: Item ID
            user_id: Optional user ID to check if user already promoted

        Returns:
            ItemPromotionStatus with promotion status
        """
        # Get item (gear_items_v2) -- visible to its owner regardless of container visibility,
        # otherwise only if the parent container is public.
        item_stmt = select(GearItemDBV2).where(GearItemDBV2.id == item_id, GearItemDBV2.item_type == "item")
        item_result = await self.repository.db.execute(item_stmt)
        item = item_result.scalar_one_or_none()

        if item and not (user_id and item.user_id == user_id):
            parent_stmt = select(GearItemDBV2.is_public).where(
                GearItemDBV2.id == item.parent_item_id,
                GearItemDBV2.item_type == "container",
            )
            parent_result = await self.repository.db.execute(parent_stmt)
            if not parent_result.scalar_one_or_none():
                item = None

        if not item:
            raise ValueError("Item not found")

        settings = get_settings()
        threshold = settings.app.item_promotion_threshold

        # Check if user already promoted
        user_promoted = False
        if user_id:
            existing_promotion = await self.repository.get_promotion_by_item_and_user(item_id, user_id)
            user_promoted = existing_promotion is not None

        # Check if user can promote
        can_promote = False
        if user_id:
            can_promote, _ = await self.can_promote_item(item_id, user_id)

        promote_count = item.promote_count or 0
        remaining = max(0, threshold - promote_count)
        percentage = (promote_count / threshold * 100) if threshold > 0 else 0

        return ItemPromotionStatus(
            promoteCount=promote_count,
            threshold=threshold,
            remaining=remaining,
            percentage=min(100, percentage),
            inCatalogue=item.catalogue_item_id is not None,
            userPromoted=user_promoted,
            canPromote=can_promote,
        )

    async def add_item_to_catalogue(self, item_id: str, admin_user_id: str) -> GlobalCatalogueItemResponse:
        """Add an item to catalogue (admin override - bypasses threshold).

        Args:
            item_id: Item ID to add to catalogue
            admin_user_id: Admin user ID who is adding the item

        Returns:
            Created catalogue item response
        """
        # Get item (gear_items_v2) -- not limited to items admin_user_id owns; admins can add
        # items from any user's (public) container to the catalogue.
        item_stmt = select(GearItemDBV2).where(GearItemDBV2.id == item_id, GearItemDBV2.item_type == "item")
        item_result = await self.repository.db.execute(item_stmt)
        item = item_result.scalar_one_or_none()
        if not item:
            raise ValueError("Item not found")

        # Check if already in catalogue
        if item.catalogue_item_id:
            # Return existing catalogue item
            catalogue_item = await self.repository.get_catalogue_item(item.catalogue_item_id)
            if catalogue_item:
                # Map to response with creator name
                item_dict = GlobalCatalogueItemResponse.model_validate(catalogue_item).model_dump()
                creator_name = await self._get_catalogue_item_creator_name(catalogue_item)
                item_dict["creatorName"] = creator_name
                return GlobalCatalogueItemResponse(**item_dict)
            # If catalogue item was deleted but reference remains, continue to create new one

        return await self._add_item_to_catalogue(item_id, admin_user_id)

    async def _add_item_to_catalogue(self, item_id: str, user_id: str) -> GlobalCatalogueItemResponse:
        """Internal method to add item to catalogue.

        Args:
            item_id: Item ID to add
            user_id: User ID performing the action (for operations like copying images)

        Returns:
            Created catalogue item response

        Note:
            The created_by field in the catalogue item is set to the owner of the container,
            not the user_id parameter (which may be an admin promoting the item).
        """
        # Get item (gear_items_v2) with its container to access container owner
        item_stmt = select(GearItemDBV2).where(GearItemDBV2.id == item_id, GearItemDBV2.item_type == "item")
        item_result = await self.repository.db.execute(item_stmt)
        item = item_result.scalar_one_or_none()
        if not item:
            raise ValueError("Item not found")

        # Get container owner ID (this is the actual creator of the item)
        container_stmt = select(GearItemDBV2).where(GearItemDBV2.id == item.parent_item_id, GearItemDBV2.item_type == "container")
        container_result = await self.repository.db.execute(container_stmt)
        container = container_result.scalar_one_or_none()
        if not container:
            raise ValueError("Item container not found")

        container_owner_id = container.user_id

        # Create catalogue item from user item
        from app.modules.gear.schemas import GearWeightUnit

        catalogue_data_dict = {
            "name": item.name,
            "category": item.category,
            "weight": item.weight,
            "weight_unit": (cast(GearWeightUnit, item.weight_unit) if item.weight_unit else "g"),
            "description": item.notes,
            "brand": item.brand,
            "model": None,
            "price_tier": None,
            "price": None,
            "currency": None,
            "quality": cast(Quality | None, item.quality),
            "url": item.url,
            "color": item.color,
        }
        catalogue_data = GlobalCatalogueItemCreate.model_validate(catalogue_data_dict)

        # Create catalogue item with container owner as creator
        catalogue_item = await self.repository.create_catalogue_item(container_owner_id, catalogue_data)

        # Link item to catalogue - use direct update to work with items from any user's public containers
        # (update_item requires ownership, but admin should be able to link items from public containers)
        from sqlalchemy import update as sql_update

        update_stmt = sql_update(GearItemDBV2).where(GearItemDBV2.id == item_id).values(catalogue_item_id=catalogue_item.id)
        await self.repository.db.execute(update_stmt)
        await self.repository.db.commit()
        # Refresh item to get updated catalogue_item_id
        await self.repository.db.refresh(item)

        # Copy images from item to catalogue item if they exist
        try:
            await self._copy_item_images_to_catalogue(item_id, catalogue_item.id, user_id)
        except Exception as e:
            logger.warning(f"Failed to copy images to catalogue item: {e}")

        # Reload catalogue item with creator relationship

        reload_stmt = select(GlobalCatalogueItemDB).where(GlobalCatalogueItemDB.id == catalogue_item.id).options(joinedload(GlobalCatalogueItemDB.creator))
        reload_result = await self.repository.db.execute(reload_stmt)
        item_with_creator = reload_result.unique().scalar_one()
        # Map to response with creator name
        item_dict = GlobalCatalogueItemResponse.model_validate(item_with_creator).model_dump()
        creator_name = await self._get_catalogue_item_creator_name(item_with_creator)
        item_dict["creatorName"] = creator_name
        return GlobalCatalogueItemResponse(**item_dict)

    async def _copy_item_images_to_catalogue(self, item_id: str, catalogue_item_id: str, user_id: str) -> None:
        """Copy images from user item to catalogue item.

        Args:
            item_id: Source item ID
            catalogue_item_id: Target catalogue item ID
            user_id: User ID (for image ownership)
        """
        from app.modules.gear.item_image_repository import ItemImageRepository

        # Get item images
        item_image_repo = ItemImageRepository(self.repository.db)
        item_images = await item_image_repo.get_by_item(item_id)

        if not item_images:
            return

        # Copy images to catalogue
        for idx, item_image in enumerate(item_images):
            # Download image from storage
            image_data = await self._storage.download(item_image.file_path)

            # Upload to catalogue item images location
            from app.common.id_utils import generate_id

            catalogue_image_path = f"catalogue-items/{catalogue_item_id}/{item_image.file_name}"
            await self._storage.upload(image_data, catalogue_image_path, item_image.mime_type)

            # Create catalogue image record
            from app.modules.gear.db_models import CatalogueItemImageDB

            catalogue_image = CatalogueItemImageDB(
                id=generate_id(),
                catalogue_item_id=catalogue_item_id,
                user_id=user_id,
                storage_type=item_image.storage_type,
                file_path=catalogue_image_path,
                file_name=item_image.file_name,
                file_size=item_image.file_size,
                mime_type=item_image.mime_type,
                width=item_image.width,
                height=item_image.height,
                is_primary=item_image.is_primary and idx == 0,  # First image is primary
                order=idx,
                is_processed=item_image.is_processed,
                original_file_size=item_image.original_file_size,
                external_url=item_image.external_url,
            )
            self.repository.db.add(catalogue_image)

        await self.repository.db.commit()

    # Content report operations
    async def report_container(
        self,
        container_id: str,
        reporter_user_id: str,
        reason: ReportReason,
        additional_info: str | None = None,
    ) -> ContentReportResponse:
        """Report a public container for inappropriate content.

        Args:
            container_id: Container ID being reported
            reporter_user_id: User ID reporting the container
            reason: Reason for report
            additional_info: Optional additional information

        Returns:
            Created report

        Raises:
            ValueError: If container doesn't exist or is not public
            IntegrityError: If report already exists (user already reported this container)
        """
        # Verify container exists and is public
        # Use get_public_container_for_reporting to allow reporting even if container is already hidden
        container = await self.repository.get_public_container_for_reporting(container_id)
        if not container:
            raise ValueError(f"Container {container_id} not found or is not public")

        # Create report
        report = await self.repository.create_container_report(
            container_id=container_id,
            reporter_user_id=reporter_user_id,
            reason=reason,
            additional_info=additional_info,
        )

        # Check if we need to auto-hide (≥3 active reports)
        active_count = await self.repository.count_active_reports_for_container(container_id)
        if active_count >= 3:
            await self.repository.set_container_hidden_by_reports(container_id, is_hidden=True)
            logger.info(f"Container {container_id} auto-hidden due to {active_count} active reports")

        # Map report with container and reporter names
        report_dict = {
            "id": report.id,
            "container_id": report.container_id,
            "containerName": report.container.name if report.container else None,
            "reporter_user_id": report.reporter_user_id,
            "reporterName": report.reporter.name if report.reporter else None,
            "reason": report.reason,
            "additional_info": report.additional_info,
            "status": report.status,
            "created_at": report.created_at,
            "reviewed_at": report.reviewed_at,
            "reviewed_by": report.reviewed_by,
        }

        return ContentReportResponse.model_validate(report_dict)

    async def get_reports(
        self,
        status: ReportStatus | None = None,
        container_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ContentReportListResponse:
        """Get content reports with optional filters.

        Args:
            status: Filter by status
            container_id: Filter by container ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of reports with pagination info
        """
        reports, total = await self.repository.get_all_reports(
            status=status,
            container_id=container_id,
            limit=limit,
            offset=offset,
        )

        # Map reports with container and reporter names
        report_responses = []
        for report in reports:
            report_dict = {
                "id": report.id,
                "container_id": report.container_id,
                "containerName": report.container.name if report.container else None,
                "reporter_user_id": report.reporter_user_id,
                "reporterName": report.reporter.name if report.reporter else None,
                "reason": report.reason,
                "additional_info": report.additional_info,
                "status": report.status,
                "created_at": report.created_at,
                "reviewed_at": report.reviewed_at,
                "reviewed_by": report.reviewed_by,
            }
            report_responses.append(ContentReportResponse.model_validate(report_dict))

        return ContentReportListResponse(
            reports=report_responses,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update_report_status(
        self,
        report_id: str,
        status: ReportStatus,
        reviewer_id: str,
    ) -> ContentReportResponse | None:
        """Update report status (admin only).

        Args:
            report_id: Report ID
            status: New status
            reviewer_id: Admin user ID reviewing the report

        Returns:
            Updated report if found, None otherwise
        """
        report = await self.repository.update_report_status(
            report_id=report_id,
            status=status,
            reviewed_by=reviewer_id,
        )

        if not report:
            return None

        # Map report with container and reporter names
        report_dict = {
            "id": report.id,
            "container_id": report.container_id,
            "containerName": report.container.name if report.container else None,
            "reporter_user_id": report.reporter_user_id,
            "reporterName": report.reporter.name if report.reporter else None,
            "reason": report.reason,
            "additional_info": report.additional_info,
            "status": report.status,
            "created_at": report.created_at,
            "reviewed_at": report.reviewed_at,
            "reviewed_by": report.reviewed_by,
        }

        # If status is dismissed, check if we should auto-unhide
        # (all reports for container are dismissed or reviewed, no pending/action_taken)
        if status == "dismissed":
            container_reports = await self.repository.get_reports_for_container(report.container_id)
            # Check if all reports are dismissed or reviewed (no pending or action_taken)
            all_resolved = all(r.status in ("dismissed", "reviewed") for r in container_reports)
            if all_resolved:
                await self.repository.set_container_hidden_by_reports(report.container_id, is_hidden=False)
                logger.info(f"Container {report.container_id} auto-unhidden - all reports resolved")

        return ContentReportResponse.model_validate(report_dict)

    async def get_user_report_status(
        self,
        container_id: str,
        user_id: str,
    ) -> bool:
        """Check if user has reported a container.

        Args:
            container_id: Container ID
            user_id: User ID

        Returns:
            True if user has reported the container, False otherwise
        """
        report = await self.repository.get_report_by_container_and_user(
            container_id=container_id,
            user_id=user_id,
        )
        return report is not None

    async def withdraw_report(
        self,
        container_id: str,
        user_id: str,
    ) -> bool:
        """Withdraw (delete) a user's report for a container.

        Args:
            container_id: Container ID
            user_id: User ID (reporter)

        Returns:
            True if report was deleted, False if not found

        Note:
            After withdrawal, checks if container should be auto-unhidden
            (if active reports count falls below 3)
        """
        # Find the user's report
        report = await self.repository.get_report_by_container_and_user(
            container_id=container_id,
            user_id=user_id,
        )

        if not report:
            return False

        # Delete the report
        deleted = await self.repository.delete_report(report.id)

        if deleted:
            # Check if we should auto-unhide (< 3 active reports)
            active_count = await self.repository.count_active_reports_for_container(container_id)
            if active_count < 3:
                # Get container to check if it's currently hidden
                container = await self.repository.get_public_container_for_reporting(container_id)
                if container and container.is_hidden_by_reports:
                    await self.repository.set_container_hidden_by_reports(container_id, is_hidden=False)
                    logger.info(f"Container {container_id} auto-unhidden - only {active_count} active reports")

        return deleted
