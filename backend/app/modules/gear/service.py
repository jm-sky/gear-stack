"""Business logic service for gear management.

This module contains business logic for gear containers and items,
including validation, calculations, and orchestration of repository operations.
"""

import logging
from typing import Sequence

from .repository import GearRepository
from .schemas import (
    ContainerCreate,
    ContainerResponse,
    ContainerUpdate,
    ItemCreate,
    ItemResponse,
    ItemUpdate,
)
from .db_models import GearContainerDB, GearItemDB


logger = logging.getLogger(__name__)


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

    def _map_item_to_response(self, item: GearItemDB) -> ItemResponse:
        """Map database item to response schema.

        Args:
            item: Database item model

        Returns:
            Item response schema
        """
        return ItemResponse(
            id=item.id,
            name=item.name,
            category=item.category,
            quantity=item.quantity,
            weight=item.weight,
            weightUnit=item.weight_unit,
            notes=item.notes,
            expirationDate=item.expiration_date,
            priority=item.priority,
            status=item.status,
            containerId=item.nested_container_id,
            price=item.price,
            url=item.url,
            brand=item.brand,
            color=item.color,
            quality=item.quality,
            linkedItemId=item.linked_item_id,
            wearable=item.wearable,
            consumable=item.consumable,
            createdAt=item.created_at,
            updatedAt=item.updated_at,
        )

    def _map_container_to_response(self, container: GearContainerDB) -> ContainerResponse:
        """Map database container to response schema.

        Args:
            container: Database container model

        Returns:
            Container response schema
        """
        items = [self._map_item_to_response(item) for item in container.items]
        return ContainerResponse(
            id=container.id,
            name=container.name,
            description=container.description,
            type=container.type,
            color=container.color,
            parentContainerId=container.parent_container_id,
            brand=container.brand,
            price=container.price,
            hideWhenNested=container.hide_when_nested,
            weight=container.weight,
            weightUnit=container.weight_unit,
            maxWeight=container.max_weight,
            maxWeightUnit=container.max_weight_unit,
            url=container.url,
            isPublic=container.is_public,
            authorName=None,  # Will be populated for public containers
            items=items,
            createdAt=container.created_at,
            updatedAt=container.updated_at,
        )

    def _map_container_to_response_with_author(self, container: GearContainerDB) -> ContainerResponse:
        """Map database container to response schema with author name.

        Args:
            container: Database container model (must have user relationship loaded)

        Returns:
            Container response schema with author name
        """
        items = [self._map_item_to_response(item) for item in container.items]
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
        
        # Get author name from user relationship if available
        author_name = None
        if hasattr(container, 'user') and container.user:
            author_name = container.user.name
        
        return ContainerResponse(
            id=container.id,
            name=container.name,
            description=container.description,
            type=container.type,
            color=container.color,
            parentContainerId=container.parent_container_id,
            brand=container.brand,
            price=container.price,
            hideWhenNested=container.hide_when_nested,
            weight=container.weight,
            weightUnit=container.weight_unit,
            maxWeight=container.max_weight,
            maxWeightUnit=container.max_weight_unit,
            url=container.url,
            isPublic=container.is_public,
            authorName=author_name,
            items=filtered_items,
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
        return self._map_container_to_response(container)

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
        return self._map_container_to_response(container)

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
        return [self._map_container_to_response(container) for container in containers]

    async def get_public_containers(self, skip: int = 0, limit: int = 100) -> list[ContainerResponse]:
        """Get all public containers from all users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of public container responses with author names
        """
        containers = await self.repository.get_public_containers(skip, limit)
        return [self._map_container_to_response_with_author(container) for container in containers]

    async def get_public_container(self, container_id: str) -> ContainerResponse | None:
        """Get a public container by ID.

        Args:
            container_id: Container ID

        Returns:
            Container response with author name if found and public, None otherwise
        """
        container = await self.repository.get_public_container(container_id)
        if not container:
            return None
        return self._map_container_to_response_with_author(container)

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
        return self._map_container_to_response(container)

    async def delete_container(self, container_id: str, user_id: str) -> bool:
        """Delete a container and all its items.

        Args:
            container_id: Container ID
            user_id: Owner user ID

        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete_container(container_id, user_id)

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
        return self._map_item_to_response(item)

    async def get_item(self, item_id: str, user_id: str) -> ItemResponse | None:
        """Get an item by ID.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            Item response if found, None otherwise
        """
        item = await self.repository.get_item(item_id, user_id)
        if not item:
            return None
        return self._map_item_to_response(item)

    async def get_items(self, container_id: str, user_id: str, skip: int = 0, limit: int = 100) -> list[ItemResponse]:
        """Get all items in a container.

        Args:
            container_id: Parent container ID
            user_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of item responses
        """
        items = await self.repository.get_items(container_id, user_id, skip, limit)
        return [self._map_item_to_response(item) for item in items]

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
        return self._map_item_to_response(item)

    async def delete_item(self, item_id: str, user_id: str) -> bool:
        """Delete a gear item.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete_item(item_id, user_id)

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
            else:  # g
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
