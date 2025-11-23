"""Database repository implementation for gear management.

This module provides async repository for managing gear containers and items
using SQLAlchemy 2.0+.
"""

import logging
from typing import Sequence

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.common.id_utils import generate_id
from app.common.search import SearchMixin
from app.modules.auth.db_models import UserDB

from .db_models import GearContainerDB, GearItemDB
from .schemas import ContainerCreate, ContainerUpdate, ItemCreate, ItemUpdate


logger = logging.getLogger(__name__)


class GearRepository(SearchMixin):
    """Repository for gear containers and items.

    Provides async database operations for managing gear containers and items.
    Supports search across container names and item names.
    """

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db
        # Configure SearchMixin for gear search
        self._search_columns = [GearContainerDB.name, GearItemDB.name]
        self._case_sensitive = False

    # Container operations
    async def create_container(self, user_id: str, data: ContainerCreate) -> GearContainerDB:
        """Create a new gear container.

        Args:
            user_id: Owner user ID
            data: Container creation data

        Returns:
            Created container
        """
        container = GearContainerDB(
            id=generate_id(),
            user_id=user_id,
            name=data.name,
            description=data.description,
            type=data.type,
            color=data.color,
            parent_container_id=data.parentContainerId,
            brand=data.brand,
            price=data.price,
            hide_when_nested=data.hideWhenNested,
            weight=data.weight,
            weight_unit=data.weightUnit,
            max_weight=data.maxWeight,
            max_weight_unit=data.maxWeightUnit,
            url=data.url,
            is_public=data.isPublic if data.isPublic is not None else False,
        )
        self.db.add(container)
        await self.db.commit()
        await self.db.refresh(container)
        # Reload container with items relationship to avoid lazy loading issues
        # For a newly created container, items will be empty, but we need to load the relationship
        stmt = select(GearContainerDB).where(GearContainerDB.id == container.id).options(selectinload(GearContainerDB.items))
        result = await self.db.execute(stmt)
        container = result.scalar_one()
        return container

    async def get_container(self, container_id: str, user_id: str) -> GearContainerDB | None:
        """Get a container by ID for a specific user.

        Args:
            container_id: Container ID
            user_id: Owner user ID

        Returns:
            Container if found, None otherwise
        """
        stmt = select(GearContainerDB).where(and_(GearContainerDB.id == container_id, GearContainerDB.user_id == user_id)).options(selectinload(GearContainerDB.items))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_containers(self, user_id: str, skip: int = 0, limit: int = 100) -> Sequence[GearContainerDB]:
        """Get all containers for a user.

        Args:
            user_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of containers
        """
        stmt = select(GearContainerDB).where(GearContainerDB.user_id == user_id).options(selectinload(GearContainerDB.items)).offset(skip).limit(limit).order_by(GearContainerDB.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_public_containers(self, skip: int = 0, limit: int = 100) -> Sequence[GearContainerDB]:
        """Get all public containers from all users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of public containers with user relationship loaded
        """
        stmt = (
            select(GearContainerDB)
            .where(GearContainerDB.is_public == True)  # noqa: E712
            .options(selectinload(GearContainerDB.items), joinedload(GearContainerDB.user))
            .offset(skip)
            .limit(limit)
            .order_by(GearContainerDB.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_public_container(self, container_id: str) -> GearContainerDB | None:
        """Get a public container by ID.

        Args:
            container_id: Container ID

        Returns:
            Container if found and public, None otherwise (with user relationship loaded)
        """
        stmt = (
            select(GearContainerDB)
            .where(
                and_(
                    GearContainerDB.id == container_id,
                    GearContainerDB.is_public == True,  # noqa: E712
                )
            )
            .options(selectinload(GearContainerDB.items), joinedload(GearContainerDB.user))
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def update_container(self, container_id: str, user_id: str, data: ContainerUpdate) -> GearContainerDB | None:
        """Update a container.

        Args:
            container_id: Container ID
            user_id: Owner user ID
            data: Update data

        Returns:
            Updated container if found, None otherwise
        """
        container = await self.get_container(container_id, user_id)
        if not container:
            return None

        update_data = data.model_dump(exclude_unset=True)
        # Map camelCase to snake_case
        field_mapping = {
            "parentContainerId": "parent_container_id",
            "hideWhenNested": "hide_when_nested",
            "weightUnit": "weight_unit",
            "maxWeight": "max_weight",
            "maxWeightUnit": "max_weight_unit",
            "isPublic": "is_public",
        }

        for key, value in update_data.items():
            db_key = field_mapping.get(key, key)
            if hasattr(container, db_key):
                setattr(container, db_key, value)

        await self.db.commit()
        await self.db.refresh(container)
        # Reload container with items relationship to avoid lazy loading issues
        stmt = select(GearContainerDB).where(GearContainerDB.id == container.id).options(selectinload(GearContainerDB.items))
        result = await self.db.execute(stmt)
        container = result.scalar_one()
        return container

    async def delete_container(self, container_id: str, user_id: str) -> bool:
        """Delete a container and all its items.

        Args:
            container_id: Container ID
            user_id: Owner user ID

        Returns:
            True if deleted, False if not found
        """
        container = await self.get_container(container_id, user_id)
        if not container:
            return False

        await self.db.delete(container)
        await self.db.commit()
        return True

    # Item operations
    async def create_item(self, container_id: str, user_id: str, data: ItemCreate) -> GearItemDB | None:
        """Create a new gear item in a container.

        Args:
            container_id: Parent container ID
            user_id: Owner user ID
            data: Item creation data

        Returns:
            Created item if container exists, None otherwise
        """
        # Verify container exists and belongs to user
        container = await self.get_container(container_id, user_id)
        if not container:
            return None

        item = GearItemDB(
            id=generate_id(),
            container_id=container_id,
            name=data.name,
            category=data.category,
            quantity=data.quantity,
            weight=data.weight,
            weight_unit=data.weightUnit,
            notes=data.notes,
            expiration_date=data.expirationDate,
            priority=data.priority,
            status=data.status,
            nested_container_id=data.containerId,
            price=data.price,
            url=data.url,
            brand=data.brand,
            color=data.color,
            quality=data.quality,
            linked_item_id=data.linkedItemId,
            wearable=data.wearable,
            consumable=data.consumable,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_item(self, item_id: str, user_id: str) -> GearItemDB | None:
        """Get an item by ID for a specific user.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            Item if found, None otherwise
        """
        stmt = select(GearItemDB).join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id).where(and_(GearItemDB.id == item_id, GearContainerDB.user_id == user_id))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_items(self, container_id: str, user_id: str, skip: int = 0, limit: int = 100) -> Sequence[GearItemDB]:
        """Get all items in a container.

        Args:
            container_id: Parent container ID
            user_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of items
        """
        # Verify container belongs to user
        container = await self.get_container(container_id, user_id)
        if not container:
            return []

        stmt = select(GearItemDB).where(GearItemDB.container_id == container_id).offset(skip).limit(limit).order_by(GearItemDB.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_item(self, item_id: str, user_id: str, data: ItemUpdate) -> GearItemDB | None:
        """Update a gear item.

        Args:
            item_id: Item ID
            user_id: Owner user ID
            data: Update data

        Returns:
            Updated item if found, None otherwise
        """
        item = await self.get_item(item_id, user_id)
        if not item:
            return None

        update_data = data.model_dump(exclude_unset=True)
        # Map camelCase to snake_case
        field_mapping = {
            "weightUnit": "weight_unit",
            "expirationDate": "expiration_date",
            "containerId": "nested_container_id",
            "linkedItemId": "linked_item_id",
        }

        for key, value in update_data.items():
            db_key = field_mapping.get(key, key)
            if hasattr(item, db_key):
                setattr(item, db_key, value)

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_item(self, item_id: str, user_id: str) -> bool:
        """Delete a gear item.

        Args:
            item_id: Item ID
            user_id: Owner user ID

        Returns:
            True if deleted, False if not found
        """
        item = await self.get_item(item_id, user_id)
        if not item:
            return False

        await self.db.delete(item)
        await self.db.commit()
        return True
