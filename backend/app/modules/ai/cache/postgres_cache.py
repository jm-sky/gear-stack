"""PostgreSQL-based cache implementation using database models."""

import hashlib
import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db_models import AICacheDB
from .base import CacheService

logger = logging.getLogger(__name__)


class PostgresCacheService(CacheService):
    """PostgreSQL-based cache implementation."""

    def __init__(self, db: AsyncSession):
        """Initialize cache service.

        Args:
            db: Database session
        """
        self.db = db

    @staticmethod
    def generate_cache_key(operation_type: str, input_data: dict[str, Any], model: str) -> str:
        """Generate cache key from operation parameters.

        Args:
            operation_type: Type of operation (e.g., 'classify', 'embed')
            input_data: Input data dict
            model: Model identifier

        Returns:
            str: SHA256 hash as cache key
        """
        # Sort dict keys for consistent hashing
        input_str = json.dumps(input_data, sort_keys=True)
        hash_input = f"{operation_type}:{input_str}:{model}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    async def get(self, key: str) -> dict[str, Any] | None:
        """Get from PostgreSQL cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        try:
            result = await self.db.execute(select(AICacheDB).where(AICacheDB.cache_key == key).where(AICacheDB.expires_at > datetime.now(UTC)))
            cache = result.scalar_one_or_none()

            if cache:
                # Update hit count and last access
                cache.hit_count += 1
                cache.last_accessed_at = datetime.now(UTC)
                await self.db.commit()
                return cache.response_data

            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            await self.db.rollback()
            return None

    async def set(self, key: str, value: dict[str, Any], ttl_days: int) -> None:
        """Set in PostgreSQL cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_days: Time to live in days
        """
        try:
            expires_at = datetime.now(UTC) + timedelta(days=ttl_days)

            # Check if key exists (upsert logic)
            result = await self.db.execute(select(AICacheDB).where(AICacheDB.cache_key == key))
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing
                existing.response_data = value
                existing.expires_at = expires_at
                existing.last_accessed_at = datetime.now(UTC)
            else:
                # Create new
                cache = AICacheDB(
                    cache_key=key,
                    operation_type="",  # Will be set by caller
                    input_hash="",  # Will be set by caller
                    model="",  # Will be set by caller
                    response_data=value,
                    expires_at=expires_at,
                )
                self.db.add(cache)

            await self.db.commit()

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            await self.db.rollback()

    async def delete(self, key: str) -> None:
        """Delete from PostgreSQL cache.

        Args:
            key: Cache key
        """
        try:
            await self.db.execute(delete(AICacheDB).where(AICacheDB.cache_key == key))
            await self.db.commit()
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            await self.db.rollback()

    async def clear_expired(self) -> int:
        """Clear expired cache entries.

        Returns:
            Number of entries cleared
        """
        try:
            result = await self.db.execute(delete(AICacheDB).where(AICacheDB.expires_at < datetime.now(UTC)))
            await self.db.commit()
            return result.rowcount or 0
        except Exception as e:
            logger.error(f"Cache clear expired error: {e}")
            await self.db.rollback()
            return 0
