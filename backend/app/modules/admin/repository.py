"""Database repository implementation for admin operations.

This module provides async repository for admin-level data access
to users, containers, and items across all users.
"""

import logging

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, selectinload

from app.modules.auth.db_models import UserDB
from app.modules.gear.db_models_v2 import GearItemDBV2

logger = logging.getLogger(__name__)


class AdminRepository:
    """Repository for admin-level data access.

    Provides async database operations for admin users to access
    all users, containers, and items across the platform.
    """

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db

    # User operations
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[tuple[UserDB, UserDB | None]]:
        """Get all users with their auth data.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of tuples (UserDB, UserDB) - both refer to same user for consistency
        """
        stmt = select(UserDB).where(UserDB.deleted_at.is_(None)).offset(skip).limit(limit).order_by(UserDB.created_at.desc())
        result = await self.db.execute(stmt)
        users = result.scalars().all()

        # Return tuple format for consistency with service expectations
        users_with_auth: list[tuple[UserDB, UserDB | None]] = [(user, user) for user in users]

        return users_with_auth

    async def get_user_by_id(self, user_id: str) -> tuple[UserDB | None, UserDB | None]:
        """Get user by ID with auth data.

        Args:
            user_id: User ID

        Returns:
            Tuple of (UserDB, UserDB) or (None, None) if not found
        """
        # Get user
        stmt = select(UserDB).where(UserDB.id == user_id, UserDB.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return (None, None)

        return (user, user)

    # Container operations
    async def get_all_containers(self, skip: int = 0, limit: int = 100) -> list[tuple[GearItemDBV2, int]]:
        """Get all containers with item counts.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of tuples (GearItemDBV2, item_count)
        """
        children = aliased(GearItemDBV2)
        stmt = (
            select(GearItemDBV2, func.count(children.id).label("item_count"))
            .outerjoin(
                children,
                and_(children.parent_item_id == GearItemDBV2.id, children.item_type == "item"),
            )
            .where(GearItemDBV2.item_type == "container")
            .options(selectinload(GearItemDBV2.user))  # type: ignore[attr-defined]
            .group_by(GearItemDBV2.id)
            .offset(skip)
            .limit(limit)
            .order_by(GearItemDBV2.created_at.desc())
        )
        result = await self.db.execute(stmt)
        rows = result.unique().all()
        # Convert to list for type checker
        return [(row[0], row[1]) for row in rows]

    async def get_container_by_id(self, container_id: str) -> GearItemDBV2 | None:
        """Get container by ID with items and user.

        Args:
            container_id: Container ID

        Returns:
            Container if found, None otherwise
        """
        stmt = select(GearItemDBV2).where(GearItemDBV2.id == container_id, GearItemDBV2.item_type == "container").options(selectinload(GearItemDBV2.children), joinedload(GearItemDBV2.user))  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def update_container(self, container_id: str, data: dict) -> GearItemDBV2 | None:
        """Update container by ID (admin only).

        Args:
            container_id: Container ID
            data: Update data dictionary

        Returns:
            Updated container if found, None otherwise
        """
        stmt = select(GearItemDBV2).where(GearItemDBV2.id == container_id, GearItemDBV2.item_type == "container").options(selectinload(GearItemDBV2.children), joinedload(GearItemDBV2.user))  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        container_db = result.unique().scalar_one_or_none()

        if not container_db:
            return None

        # Update fields
        for key, value in data.items():
            if hasattr(container_db, key):
                setattr(container_db, key, value)

        await self.db.commit()
        # Limit refresh to plain columns -- refreshing without attribute_names would expire
        # (and force a lazy, sync-unsafe reload of) the eagerly-loaded .children/.user
        # relationships set up by the SELECT above.
        await self.db.refresh(container_db, attribute_names=["updated_at", *data.keys()])
        return container_db

    async def delete_container(self, container_id: str) -> bool:
        """Delete container by ID.

        Args:
            container_id: Container ID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(GearItemDBV2).where(GearItemDBV2.id == container_id, GearItemDBV2.item_type == "container")
        result = await self.db.execute(stmt)
        container_db = result.scalar_one_or_none()

        if not container_db:
            return False

        await self.db.delete(container_db)
        await self.db.commit()
        return True

    # Item operations
    async def get_all_items(self, skip: int = 0, limit: int = 100) -> list[tuple[GearItemDBV2, GearItemDBV2, UserDB]]:
        """Get all items with container and user data.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of tuples (GearItemDBV2, GearItemDBV2 [parent container], UserDB)
        """
        parent = aliased(GearItemDBV2)
        stmt = (
            select(GearItemDBV2, parent, UserDB)
            .join(parent, GearItemDBV2.parent_item_id == parent.id)
            .join(UserDB, GearItemDBV2.user_id == UserDB.id)
            .where(GearItemDBV2.item_type == "item")
            .offset(skip)
            .limit(limit)
            .order_by(GearItemDBV2.created_at.desc())
        )
        result = await self.db.execute(stmt)
        # Convert rows to typed tuples
        return [(row[0], row[1], row[2]) for row in result.all()]

    async def get_item_by_id(self, item_id: str) -> tuple[GearItemDBV2 | None, GearItemDBV2 | None, UserDB | None]:
        """Get item by ID with container and user data.

        Args:
            item_id: Item ID

        Returns:
            Tuple of (GearItemDBV2, GearItemDBV2 [parent container], UserDB) or (None, None, None)
        """
        parent = aliased(GearItemDBV2)
        stmt = select(GearItemDBV2, parent, UserDB).join(parent, GearItemDBV2.parent_item_id == parent.id).join(UserDB, GearItemDBV2.user_id == UserDB.id).where(GearItemDBV2.id == item_id, GearItemDBV2.item_type == "item")
        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            return (None, None, None)

        return tuple(row)

    async def delete_item(self, item_id: str) -> bool:
        """Delete item by ID.

        Args:
            item_id: Item ID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(GearItemDBV2).where(GearItemDBV2.id == item_id, GearItemDBV2.item_type == "item")
        result = await self.db.execute(stmt)
        item_db = result.scalar_one_or_none()

        if not item_db:
            return False

        await self.db.delete(item_db)
        await self.db.commit()
        return True
