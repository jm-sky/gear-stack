"""Business logic service for gear management.

This module contains business logic for gear containers and items,
including validation, calculations, and orchestration of repository operations.
"""

import asyncio
import logging
import secrets
from datetime import datetime
from typing import Any, Literal, Sequence, cast

from app.core.storage.factory import get_storage_adapter

from .item_image_repository import ItemImageRepository
from .repository import GearRepository
from .schemas import (
    BatchOrderUpdateRequest,
    ContainerCreate,
    ContainerInfo,
    ContainerResponse,
    ContainerUpdate,
    GlobalCatalogueItemCreate,
    GlobalCatalogueItemResponse,
    GlobalCatalogueItemSearchParams,
    GlobalCatalogueItemUpdate,
    ItemCreate,
    ItemResponse,
    ItemUpdate,
)
from .db_models import GearContainerDB, GearItemDB


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

    def _map_item_to_response(
        self,
        item: GearItemDB,
        primary_image_url: str | None = None,
        container: GearContainerDB | None = None,
    ) -> ItemResponse:
        """Map database item to response schema.

        Args:
            item: Database item model
            primary_image_url: Optional primary image URL for the item
            container: Optional container model (if not provided, will try to use item.container)

        Returns:
            Item response schema
        """
        # Use provided container or fallback to item.container if available
        container_obj = container or (item.container if hasattr(item, "container") and item.container else None)
        container_info = None
        if container_obj:
            container_info = ContainerInfo(
                id=container_obj.id,
                name=container_obj.name,
                type=container_obj.type,
                color=cast(ContainerColor | None, container_obj.color),
            )

        # Cast database string fields to their Literal types
        return ItemResponse(
            id=item.id,
            name=item.name,
            category=item.category,
            quantity=item.quantity,
            weight=item.weight,
            weightUnit=cast(WeightUnit, item.weight_unit),
            notes=item.notes,
            expirationDate=item.expiration_date,
            priority=cast(Priority, item.priority),
            status=cast(ItemStatus, item.status),
            containerId=item.nested_container_id,  # Reference to nested container if item is a container
            container=container_info,  # Information about parent container where item is located
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
            order=item.order,
            showOnContainer=item.show_on_container,
            primaryImageUrl=primary_image_url,
            createdAt=item.created_at,
            updatedAt=item.updated_at,
        )

    async def _map_container_to_response(self, container: GearContainerDB, ratings_data: dict[str, Any] | None = None) -> ContainerResponse:
        """Map database container to response schema.

        Args:
            container: Database container model
            ratings_data: Optional ratings data from repository

        Returns:
            Container response schema
        """
        # Access items through the relationship - mypy doesn't know about SQLAlchemy relationships
        container_items = container.items  # type: ignore[attr-defined]

        # Batch fetch primary images for all items
        item_ids = [item.id for item in container_items]
        primary_images = await self._image_repository.get_primary_images_by_items(item_ids)

        # Get URLs for all primary images
        image_urls: dict[str, str] = {}
        for item_id, image in primary_images.items():
            url = await self._storage.get_url(image.file_path)
            image_urls[item_id] = url

        # Map items to responses with primary image URLs and container information
        items = [self._map_item_to_response(item, image_urls.get(item.id), container=container) for item in container_items]

        # Map rating fields if provided
        owner_rating = None
        user_rating = None
        average_user_rating = None
        user_rating_count = 0

        if ratings_data:
            owner_rating = ratings_data.get("owner_rating")
            user_rating = ratings_data.get("user_rating")
            average_user_rating = ratings_data.get("average_user_rating")
            user_rating_count = ratings_data.get("user_rating_count", 0)

        # Cast database string fields to their Literal types
        return ContainerResponse(
            id=container.id,
            name=container.name,
            description=container.description,
            type=container.type,
            color=cast(ContainerColor | None, container.color),
            parentContainerId=container.parent_container_id,
            brand=container.brand,
            price=container.price,
            hideWhenNested=container.hide_when_nested,
            weight=container.weight,
            weightUnit=cast(WeightUnit | None, container.weight_unit),
            maxWeight=container.max_weight,
            maxWeightUnit=cast(WeightUnit | None, container.max_weight_unit),
            url=container.url,
            isPublic=container.is_public,
            favorite=container.favorite,
            showItemImages=container.show_item_images,
            authorName=None,  # Not populated for private containers
            authorId=None,  # Not populated for private containers (user already knows they own it)
            items=items,
            ownerRating=owner_rating,
            userRating=user_rating,
            averageUserRating=(float(average_user_rating) if average_user_rating else None),
            userRatingCount=user_rating_count,
            createdAt=container.created_at,
            updatedAt=container.updated_at,
        )

    async def _map_container_to_response_with_author(self, container: GearContainerDB, ratings_data: dict[str, Any] | None = None) -> ContainerResponse:
        """Map database container to response schema with author name.

        Args:
            container: Database container model (must have user relationship loaded)
            ratings_data: Optional ratings data from repository

        Returns:
            Container response schema with author name
        """
        # Access items through the relationship - mypy doesn't know about SQLAlchemy relationships
        container_items = container.items  # type: ignore[attr-defined]

        # Batch fetch primary images for all items
        item_ids = [item.id for item in container_items]
        primary_images = await self._image_repository.get_primary_images_by_items(item_ids)

        # Get URLs for all primary images
        image_urls: dict[str, str] = {}
        for item_id, image in primary_images.items():
            url = await self._storage.get_url(image.file_path)
            image_urls[item_id] = url

        # Map items to responses with primary image URLs and container information
        items = [self._map_item_to_response(item, image_urls.get(item.id), container=container) for item in container_items]

        # Filter nested containers - only show items if nested container is public
        filtered_items = []
        for item in items:
            if item.containerId:  # This is a nested container reference
                # We need to check if the nested container is public
                # For now, we'll include it and let the frontend handle filtering
                # In a full implementation, we'd join and check is_public
                filtered_items.append(item)
            else:
                filtered_items.append(item)

        # Get author name and ID from user relationship
        # For public containers, user relationship is always loaded via joinedload
        author_name = None
        author_id = None
        if hasattr(container, "user") and container.user:
            author_name = container.user.name
            author_id = container.user.id

        # Map rating fields if provided
        owner_rating = None
        user_rating = None
        average_user_rating = None
        user_rating_count = 0

        if ratings_data:
            owner_rating = ratings_data.get("owner_rating")
            user_rating = ratings_data.get("user_rating")
            average_user_rating = ratings_data.get("average_user_rating")
            user_rating_count = ratings_data.get("user_rating_count", 0)

        # Cast database string fields to their Literal types
        return ContainerResponse(
            id=container.id,
            name=container.name,
            description=container.description,
            type=container.type,
            color=cast(ContainerColor | None, container.color),
            parentContainerId=container.parent_container_id,
            brand=container.brand,
            price=container.price,
            hideWhenNested=container.hide_when_nested,
            weight=container.weight,
            weightUnit=cast(WeightUnit | None, container.weight_unit),
            maxWeight=container.max_weight,
            maxWeightUnit=cast(WeightUnit | None, container.max_weight_unit),
            url=container.url,
            isPublic=container.is_public,
            favorite=container.favorite,
            showItemImages=container.show_item_images,
            authorName=author_name,
            authorId=author_id,
            items=filtered_items,
            ownerRating=owner_rating,
            userRating=user_rating,
            averageUserRating=(float(average_user_rating) if average_user_rating else None),
            userRatingCount=user_rating_count,
            createdAt=container.created_at,
            updatedAt=container.updated_at,
        )

    async def create_container(self, user_id: str, data: ContainerCreate, default_public: bool = False) -> ContainerResponse:
        """Create a new gear container.

        Args:
            user_id: Owner user ID
            data: Container creation data
            default_public: Default public setting from user preferences

        Returns:
            Created container response
        """
        # Use default_public if isPublic is not explicitly set
        if data.isPublic is None:
            data.isPublic = default_public
        container = await self.repository.create_container(user_id, data)

        # New container has no ratings yet
        ratings_data = {
            "owner_rating": None,
            "user_rating": None,
            "average_user_rating": None,
            "user_rating_count": 0,
        }

        return await self._map_container_to_response(container, dict(ratings_data) if ratings_data else None)

    async def get_container(self, container_id: str, user_id: str) -> ContainerResponse | None:
        """Get a container by ID.

        Args:
            container_id: Container ID
            user_id: Owner user ID

        Returns:
            Container response if found, None otherwise
        """
        container = await self.repository.get_container(container_id, user_id)
        if not container:
            return None

        is_owner = container.user_id == user_id
        ratings_data = await self.repository.get_container_ratings_data(container_id, requesting_user_id=user_id, is_owner=is_owner)

        return await self._map_container_to_response(container, dict(ratings_data) if ratings_data else None)

    async def get_containers(self, user_id: str, skip: int = 0, limit: int = 100) -> list[ContainerResponse]:
        """Get all containers for a user.

        Args:
            user_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of container responses
        """
        containers = await self.repository.get_containers(user_id, skip, limit)
        results = []
        for container in containers:
            ratings_data = await self.repository.get_container_ratings_data(container.id, requesting_user_id=user_id, is_owner=True)
            results.append(await self._map_container_to_response(container, dict(ratings_data) if ratings_data else None))
        return results

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
            ratings_data = await self.repository.get_container_ratings_data(container.id, requesting_user_id=requesting_user_id, is_owner=False)
            results.append(await self._map_container_to_response_with_author(container, dict(ratings_data) if ratings_data else None))
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

        return await self._map_container_to_response_with_author(container, dict(ratings_data) if ratings_data else None)

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

        return await self._map_container_to_response_with_author(container, dict(ratings_data) if ratings_data else None)

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
        # Verify container ownership
        container = await self.repository.get_container(container_id, user_id)
        if not container:
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

    async def update_container(self, container_id: str, user_id: str, data: ContainerUpdate) -> ContainerResponse | None:
        """Update a container.

        Args:
            container_id: Container ID
            user_id: Owner user ID
            data: Update data

        Returns:
            Updated container response if found, None otherwise
        """
        container = await self.repository.update_container(container_id, user_id, data)
        if not container:
            return None

        ratings_data = await self.repository.get_container_ratings_data(container_id, requesting_user_id=user_id, is_owner=True)

        return await self._map_container_to_response(container, dict(ratings_data) if ratings_data else None)

    async def delete_container(self, container_id: str, user_id: str) -> bool:
        """Delete a container and all its items.

        Args:
            container_id: Container ID
            user_id: Owner user ID

        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete_container(container_id, user_id)

    async def delete_all_containers(self, user_id: str) -> int:
        """Delete all containers for a user.

        Args:
            user_id: Owner user ID

        Returns:
            Number of deleted containers
        """
        return await self.repository.delete_all_containers(user_id)

    async def create_item(self, container_id: str, user_id: str, data: ItemCreate) -> ItemResponse | None:
        """Create a new gear item in a container.

        Args:
            container_id: Parent container ID
            user_id: Owner user ID
            data: Item creation data

        Returns:
            Created item response if container exists, None otherwise
        """
        item = await self.repository.create_item(container_id, user_id, data)
        if not item:
            return None

        # Get primary image URL (if exists)
        primary_image = await self._image_repository.get_primary_image(item.id)
        primary_image_url = None
        if primary_image:
            # If external_url exists, use it. Otherwise, get URL from storage.
            if primary_image.external_url:
                primary_image_url = primary_image.external_url
            else:
                primary_image_url = await self._storage.get_url(primary_image.file_path)

        # Load container for the created item
        container = await self.repository.get_container(container_id, user_id)
        return self._map_item_to_response(item, primary_image_url, container=container)

    async def get_item(self, item_id: str, user_id: str) -> ItemResponse | None:
        """Get an item by ID.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            Item response if found, None otherwise (with container information)
        """
        item = await self.repository.get_item(item_id, user_id)
        if not item:
            return None

        # Get primary image URL
        primary_image = await self._image_repository.get_primary_image(item_id)
        primary_image_url = None
        if primary_image:
            # If external_url exists, use it. Otherwise, get URL from storage.
            if primary_image.external_url:
                primary_image_url = primary_image.external_url
            else:
                primary_image_url = await self._storage.get_url(primary_image.file_path)

        # Container is already loaded via joinedload in repository.get_item
        return self._map_item_to_response(item, primary_image_url, container=item.container)

    async def get_items(self, container_id: str, user_id: str, skip: int = 0, limit: int = 100) -> list[ItemResponse]:
        """Get all items in a container.

        Args:
            container_id: Parent container ID
            user_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of item responses with primary image URLs and container information
        """
        items = await self.repository.get_items(container_id, user_id, skip, limit)

        # Batch fetch primary images for all items
        item_ids = [item.id for item in items]
        primary_images = await self._image_repository.get_primary_images_by_items(item_ids)

        # Get URLs for all primary images
        image_urls: dict[str, str] = {}
        for item_id, image in primary_images.items():
            url = await self._storage.get_url(image.file_path)
            image_urls[item_id] = url

        # Map items to responses with primary image URLs and container information
        # Container is already loaded via joinedload in repository.get_items
        return [self._map_item_to_response(item, image_urls.get(item.id), container=item.container) for item in items]

    async def get_all_items(self, user_id: str, skip: int = 0, limit: int = 100) -> list[ItemResponse]:
        """Get all items for a user across all containers.

        Args:
            user_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of item responses with primary image URLs and container information
        """
        items = await self.repository.get_all_items(user_id, skip, limit)

        # Batch fetch primary images for all items
        item_ids = [item.id for item in items]
        primary_images = await self._image_repository.get_primary_images_by_items(item_ids)

        # Get URLs for all primary images
        image_urls: dict[str, str] = {}
        for item_id, image in primary_images.items():
            url = await self._storage.get_url(image.file_path)
            image_urls[item_id] = url

        # Map items to responses with primary image URLs and container information
        # Container is already loaded via joinedload in repository.get_all_items
        return [self._map_item_to_response(item, image_urls.get(item.id), container=item.container) for item in items]

    async def update_item(self, item_id: str, user_id: str, data: ItemUpdate) -> ItemResponse | None:
        """Update a gear item.

        Args:
            item_id: Item ID
            user_id: Owner user ID
            data: Update data

        Returns:
            Updated item response if found, None otherwise
        """
        item = await self.repository.update_item(item_id, user_id, data)
        if not item:
            return None

        # Get primary image URL (if exists)
        primary_image = await self._image_repository.get_primary_image(item_id)
        primary_image_url = None
        if primary_image:
            # If external_url exists, use it. Otherwise, get URL from storage.
            if primary_image.external_url:
                primary_image_url = primary_image.external_url
            else:
                primary_image_url = await self._storage.get_url(primary_image.file_path)

        # Container is already loaded via get_item in repository.update_item
        return self._map_item_to_response(item, primary_image_url, container=item.container)

    async def delete_item(self, item_id: str, user_id: str) -> bool:
        """Delete a gear item.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete_item(item_id, user_id)

    async def batch_update_item_order(self, user_id: str, data: BatchOrderUpdateRequest) -> list[ItemResponse]:
        """Batch update items' order values.

        Args:
            user_id: Owner user ID
            data: Batch order update request with list of item IDs and their new order values

        Returns:
            List of updated item responses

        Raises:
            ValueError: If any item ID is not found or doesn't belong to the user
        """
        items = await self.repository.batch_update_item_order(user_id, data)
        return [self._map_item_to_response(item) for item in items]

    def calculate_container_weight(self, container: ContainerResponse) -> dict[str, float]:
        """Calculate total weight of a container in grams and kilograms.

        Args:
            container: Container response with items

        Returns:
            Dictionary with weight in grams and kilograms
        """
        total_grams = 0.0
        for item in container.items:
            if item.weightUnit == "kg":
                total_grams += item.weight * 1000 * item.quantity
            elif item.weightUnit == "oz":
                # 1 oz = 28.3495 g
                total_grams += item.weight * 28.3495 * item.quantity
            elif item.weightUnit == "lb":
                # 1 lb = 453.592 g
                total_grams += item.weight * 453.592 * item.quantity
            else:  # g (default)
                total_grams += item.weight * item.quantity

        return {
            "grams": total_grams,
            "kilograms": total_grams / 1000,
        }

    def calculate_container_readiness(self, container: ContainerResponse) -> dict[str, int | float]:
        """Calculate container readiness statistics.

        Args:
            container: Container response with items

        Returns:
            Dictionary with readiness statistics
        """
        if not container.items:
            return {
                "totalItems": 0,
                "ownedItems": 0,
                "missingItems": 0,
                "toBuyItems": 0,
                "readinessPercentage": 0.0,
            }

        owned = sum(1 for item in container.items if item.status == "owned")
        missing = sum(1 for item in container.items if item.status == "missing")
        to_buy = sum(1 for item in container.items if item.status == "toBuy")
        total = len(container.items)

        return {
            "totalItems": total,
            "ownedItems": owned,
            "missingItems": missing,
            "toBuyItems": to_buy,
            "readinessPercentage": (owned / total * 100) if total > 0 else 0.0,
        }

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
            url = await self._storage.get_url(image.file_path)
            image_urls[item_id] = url

        # Map items to responses with primary image URLs
        results = []
        for item in items:
            item_dict = GlobalCatalogueItemResponse.model_validate(item).model_dump()
            item_dict["primaryImageUrl"] = image_urls.get(item.id)
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
            primary_image_url = await self._storage.get_url(primary_image.file_path)

        # Create response with image URL
        item_dict = GlobalCatalogueItemResponse.model_validate(item).model_dump()
        item_dict["primaryImageUrl"] = primary_image_url
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
        return GlobalCatalogueItemResponse.model_validate(item)

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
        return GlobalCatalogueItemResponse.model_validate(item)

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

        # Verify container belongs to user
        container = await self.repository.get_container(container_id, user_id)
        if not container:
            return None

        # Create item from catalogue data
        item_data = ItemCreate(  # type: ignore[call-arg]
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
        created_item = await self.create_item(container_id, user_id, item_data)
        if not created_item:
            return None

        # Copy images if requested
        if copy_image:
            await self._copy_catalogue_images_to_item(catalogue_item_id, created_item.id, user_id)

        return created_item

    async def _copy_catalogue_images_to_item(
        self,
        catalogue_item_id: str,
        item_id: str,
        user_id: str,
    ) -> None:
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
            return

        # Copy each image
        for idx, catalogue_image in enumerate(catalogue_images):
            try:
                # Download image from storage
                image_content = await self._storage.download(catalogue_image.file_path)

                # Create new file path for item image
                # Extract extension from original filename
                file_extension = ""
                if "." in catalogue_image.file_name:
                    file_extension = "." + catalogue_image.file_name.rsplit(".", 1)[1]
                new_filename = f"{generate_id()}{file_extension}"
                new_file_path = f"items/{item_id}/{new_filename}"

                # Upload image to new location
                await self._storage.upload(
                    image_content,
                    new_file_path,
                    catalogue_image.mime_type,
                    metadata={
                        "item_id": item_id,
                        "user_id": user_id,
                        "copied_from_catalogue_image": catalogue_image.id,
                    },
                )

                # Create ItemImageDB record
                # Unset primary for other images if this is primary
                if catalogue_image.is_primary:
                    await self._image_repository.unset_primary_for_item(item_id)

                # Get next order value
                next_order = await self._image_repository.get_next_order(item_id)

                new_image = ItemImageDB(
                    id=generate_id(),
                    item_id=item_id,
                    user_id=user_id,
                    storage_type=catalogue_image.storage_type,
                    file_path=new_file_path,
                    file_name=catalogue_image.file_name,
                    file_size=catalogue_image.file_size,
                    mime_type=catalogue_image.mime_type,
                    width=catalogue_image.width,
                    height=catalogue_image.height,
                    is_primary=catalogue_image.is_primary,
                    order=next_order,
                    is_processed=catalogue_image.is_processed,
                    original_file_size=catalogue_image.original_file_size,
                )

                self.repository.db.add(new_image)
                await self.repository.db.commit()
            except Exception as e:
                logger.error(
                    "Failed to copy image %s from catalogue item %s to item %s: %s",
                    catalogue_image.id,
                    catalogue_item_id,
                    item_id,
                    e,
                )
                # Continue copying other images even if one fails

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
        # Get user item
        item = await self.repository.get_item(item_id, user_id)
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
            fields = ["name", "description", "weight", "weightUnit", "price", "currency", "brand", "color", "category", "quality", "url"]

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
        update_data = ItemUpdate(**update_data_dict)
        return await self.update_item(item_id, user_id, update_data)

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
        # Verify item belongs to user
        item = await self.repository.get_item(item_id, user_id)
        if not item:
            return None

        # Verify catalogue item exists and is active
        catalogue_item = await self.repository.get_catalogue_item(catalogue_item_id)
        if not catalogue_item or not catalogue_item.is_active:
            return None

        # Set catalogue_item_id
        update_data = ItemUpdate(catalogueItemId=catalogue_item_id)  # type: ignore[call-arg]
        return await self.update_item(item_id, user_id, update_data)

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
        # Get user item
        item = await self.repository.get_item(item_id, user_id)
        if not item or not item.catalogue_item_id:
            return None

        # Get catalogue item to verify it exists and is active
        catalogue_item = await self.repository.get_catalogue_item(item.catalogue_item_id)
        if not catalogue_item or not catalogue_item.is_active:
            return None

        # Copy images from catalogue to item
        await self._copy_catalogue_images_to_item(item.catalogue_item_id, item_id, user_id)

        # Return updated item
        return await self.get_item(item_id, user_id)

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
        item = await self.repository.get_item(item_id, user_id)
        if not item:
            return None

        # Clear catalogue_item_id
        update_data = ItemUpdate(catalogueItemId=None)  # type: ignore[call-arg]
        return await self.update_item(item_id, user_id, update_data)
