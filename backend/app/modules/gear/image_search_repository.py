"""Database repository for image search engines."""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.modules.gear.db_models import ImageSearchEngineDB


class ImageSearchEngineRepository:
    """Repository for image search engine operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async SQLAlchemy session
        """
        self.db = db

    async def create(self, data: dict) -> ImageSearchEngineDB:
        """
        Create a new image search engine.

        Args:
            data: Engine data dictionary

        Returns:
            Created engine record
        """
        engine = ImageSearchEngineDB(id=generate_id(), **data)
        self.db.add(engine)
        await self.db.commit()
        await self.db.refresh(engine)
        return engine

    async def get_by_id(self, engine_id: str) -> ImageSearchEngineDB | None:
        """
        Get engine by ID.

        Args:
            engine_id: Engine ID

        Returns:
            Engine record if found, None otherwise
        """
        stmt = select(ImageSearchEngineDB).where(ImageSearchEngineDB.id == engine_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> ImageSearchEngineDB | None:
        """
        Get engine by name.

        Args:
            name: Engine name

        Returns:
            Engine record if found, None otherwise
        """
        stmt = select(ImageSearchEngineDB).where(ImageSearchEngineDB.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, active_only: bool = False) -> Sequence[ImageSearchEngineDB]:
        """
        Get all engines, optionally filtered by active status.

        Args:
            active_only: If True, only return active engines

        Returns:
            List of engine records
        """
        stmt = select(ImageSearchEngineDB)
        if active_only:
            stmt = stmt.where(ImageSearchEngineDB.is_active == True)  # noqa: E712
        stmt = stmt.order_by(ImageSearchEngineDB.priority, ImageSearchEngineDB.name)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_ids(self, engine_ids: list[str]) -> Sequence[ImageSearchEngineDB]:
        """
        Get engines by IDs.

        Args:
            engine_ids: List of engine IDs

        Returns:
            List of engine records
        """
        if not engine_ids:
            return []
        stmt = select(ImageSearchEngineDB).where(ImageSearchEngineDB.id.in_(engine_ids))
        stmt = stmt.order_by(ImageSearchEngineDB.priority)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, engine_id: str, data: dict) -> ImageSearchEngineDB | None:
        """
        Update an engine.

        Args:
            engine_id: Engine ID
            data: Update data dictionary

        Returns:
            Updated engine record if found, None otherwise
        """
        engine = await self.get_by_id(engine_id)
        if not engine:
            return None

        for key, value in data.items():
            setattr(engine, key, value)

        await self.db.commit()
        await self.db.refresh(engine)
        return engine

    async def delete(self, engine_id: str) -> bool:
        """
        Delete an engine.

        Args:
            engine_id: Engine ID

        Returns:
            True if deleted, False if not found
        """
        engine = await self.get_by_id(engine_id)
        if not engine:
            return False

        await self.db.delete(engine)
        await self.db.commit()
        return True
