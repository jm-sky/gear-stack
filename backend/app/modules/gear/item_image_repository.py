"""Database repository for item images."""

from typing import Sequence

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.modules.gear.db_models import GearContainerDB, GearItemDB, ItemImageDB


class ItemImageRepository:
    """Repository for item image operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db

    async def create(self, data: dict) -> ItemImageDB:
        """
        Create a new item image.

        Args:
            data: Image data dictionary

        Returns:
            Created image record
        """
        image = ItemImageDB(id=generate_id(), **data)
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def get_by_id(self, image_id: str) -> ItemImageDB | None:
        """
        Get image by ID.

        Args:
            image_id: Image ID

        Returns:
            Image record if found, None otherwise
        """
        stmt = select(ItemImageDB).where(ItemImageDB.id == image_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_item(self, item_id: str) -> Sequence[ItemImageDB]:
        """
        Get all images for an item, ordered by order field.

        Args:
            item_id: Item ID

        Returns:
            List of images
        """
        stmt = (
            select(ItemImageDB)
            .where(ItemImageDB.item_id == item_id)
            .order_by(ItemImageDB.order)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_by_item(self, item_id: str) -> int:
        """
        Count images for an item.

        Args:
            item_id: Item ID

        Returns:
            Number of images
        """
        stmt = (
            select(func.count())
            .select_from(ItemImageDB)
            .where(ItemImageDB.item_id == item_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def update(self, image_id: str, data: dict) -> ItemImageDB | None:
        """
        Update image record.

        Args:
            image_id: Image ID
            data: Update data dictionary

        Returns:
            Updated image record if found, None otherwise
        """
        stmt = (
            update(ItemImageDB)
            .where(ItemImageDB.id == image_id)
            .values(**data)
            .returning(ItemImageDB)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete(self, image_id: str) -> bool:
        """
        Delete image record.

        Args:
            image_id: Image ID

        Returns:
            True if deleted, False if not found
        """
        image = await self.get_by_id(image_id)
        if image:
            await self.db.delete(image)
            await self.db.commit()
            return True
        return False

    async def get_next_order(self, item_id: str) -> int:
        """
        Get next order value for item images.

        Args:
            item_id: Item ID

        Returns:
            Next order value
        """
        stmt = select(func.max(ItemImageDB.order)).where(ItemImageDB.item_id == item_id)
        result = await self.db.execute(stmt)
        max_order = result.scalar()
        return (max_order or -1) + 1

    async def unset_primary_for_item(self, item_id: str) -> None:
        """
        Unset primary flag for all images of an item.

        Args:
            item_id: Item ID
        """
        stmt = (
            update(ItemImageDB)
            .where(ItemImageDB.item_id == item_id)
            .values(is_primary=False)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_primary_image(self, item_id: str) -> ItemImageDB | None:
        """
        Get primary image for an item.

        Args:
            item_id: Item ID

        Returns:
            Primary image if found, None otherwise
        """
        stmt = select(ItemImageDB).where(
            ItemImageDB.item_id == item_id, ItemImageDB.is_primary == True
        )  # noqa: E712
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_primary_images_by_items(
        self, item_ids: list[str]
    ) -> dict[str, ItemImageDB]:
        """
        Get primary images for multiple items in a single query.

        Args:
            item_ids: List of item IDs

        Returns:
            Dictionary mapping item_id to primary image (only items with primary images are included)
        """
        if not item_ids:
            return {}
        stmt = select(ItemImageDB).where(
            ItemImageDB.item_id.in_(item_ids), ItemImageDB.is_primary == True
        )  # noqa: E712
        result = await self.db.execute(stmt)
        images = result.scalars().all()
        return {img.item_id: img for img in images}

    async def get_user_storage_usage(self, user_id: str) -> int:
        """
        Get total storage usage in bytes for a user.

        Args:
            user_id: User ID

        Returns:
            Total storage usage in bytes
        """
        stmt = select(func.sum(ItemImageDB.file_size)).where(
            ItemImageDB.user_id == user_id
        )
        result = await self.db.execute(stmt)
        total = result.scalar()
        return total or 0

    async def get_item_owner_and_visibility(
        self, item_id: str
    ) -> tuple[str, bool] | None:
        """
        Resolve the owning user and public-visibility of an item's container.

        Args:
            item_id: Item ID

        Returns:
            Tuple of (owner_user_id, is_publicly_visible), or None if the item
            (or its container) does not exist. `is_publicly_visible` is True
            only if the container is public and not hidden by reports.
        """
        stmt = (
            select(
                GearContainerDB.user_id,
                GearContainerDB.is_public,
                GearContainerDB.is_hidden_by_reports,
            )
            .join(GearItemDB, GearItemDB.container_id == GearContainerDB.id)
            .where(GearItemDB.id == item_id)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if not row:
            return None
        owner_id, is_public, is_hidden = row
        return owner_id, bool(is_public) and not bool(is_hidden)

    async def get_item_owner_id(self, item_id: str) -> str | None:
        """
        Resolve the owning user_id of an item via its container.

        Args:
            item_id: Item ID

        Returns:
            Owner user_id, or None if the item does not exist.
        """
        visibility = await self.get_item_owner_and_visibility(item_id)
        return visibility[0] if visibility else None

    async def get_image_owner_id(self, image_id: str) -> str | None:
        """
        Resolve the owning user_id of an image via its item's container.

        Args:
            image_id: Image ID

        Returns:
            Owner user_id, or None if the image does not exist.
        """
        stmt = (
            select(GearContainerDB.user_id)
            .join(GearItemDB, GearItemDB.container_id == GearContainerDB.id)
            .join(ItemImageDB, ItemImageDB.item_id == GearItemDB.id)
            .where(ItemImageDB.id == image_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def image_belongs_to_item(self, image_id: str, item_id: str) -> bool:
        """
        Check whether an image belongs to the given item.

        Args:
            image_id: Image ID
            item_id: Item ID

        Returns:
            True if the image exists and belongs to item_id.
        """
        stmt = (
            select(func.count())
            .select_from(ItemImageDB)
            .where(ItemImageDB.id == image_id, ItemImageDB.item_id == item_id)
        )
        result = await self.db.execute(stmt)
        return (result.scalar() or 0) > 0

    async def get_all_by_user(self, user_id: str) -> Sequence[ItemImageDB]:
        """
        Get all images for a user (across all items).

        Args:
            user_id: User ID

        Returns:
            List of all images for the user
        """
        stmt = select(ItemImageDB).where(ItemImageDB.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
