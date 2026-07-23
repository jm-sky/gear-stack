"""Database repository implementation for gear management.

This module provides async repository for managing gear containers and items
using SQLAlchemy 2.0+.
"""

import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypedDict

from sqlalchemy import and_, func, or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.common.id_utils import generate_id
from app.common.search import SearchMixin

from .db_models import (
    ContainerRatingDB,
    ContainerShareTokenDB,
    ContentReportDB,
    GearContainerDB,
    GearItemDB,
    GlobalCatalogueItemDB,
    ItemPromotionDB,
)
from .db_models_v2 import GearItemDBV2
from .schemas import (
    GlobalCatalogueItemCreate,
    GlobalCatalogueItemUpdate,
)

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
    async def count_user_containers(self, user_id: str) -> int:
        """Count all containers for a user.

        Args:
            user_id: Owner user ID

        Returns:
            Number of containers
        """
        stmt = select(func.count(GearItemDBV2.id)).where(
            GearItemDBV2.user_id == user_id,
            GearItemDBV2.item_type == "container",
        )
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def count_user_items(self, user_id: str) -> int:
        """Count all items for a user (across all containers).

        Args:
            user_id: Owner user ID

        Returns:
            Number of items
        """
        stmt = select(func.count(GearItemDBV2.id)).where(
            GearItemDBV2.user_id == user_id,
            GearItemDBV2.item_type == "item",
        )
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def get_public_containers(self, skip: int = 0, limit: int = 100) -> Sequence[GearItemDBV2]:
        """Get all public containers from all users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of public containers (gear_items_v2, item_type='container') with children and
            user relationships loaded
        """
        stmt = (
            select(GearItemDBV2)
            .where(
                and_(
                    GearItemDBV2.item_type == "container",
                    GearItemDBV2.is_public == True,  # noqa: E712
                    # is_hidden_by_reports is nullable on gear_items_v2 (unlike V1's NOT NULL
                    # default False) -- NULL means "never reported", i.e. not hidden.
                    or_(
                        GearItemDBV2.is_hidden_by_reports == False,  # noqa: E712
                        GearItemDBV2.is_hidden_by_reports.is_(None),
                    ),
                )
            )
            .options(
                selectinload(GearItemDBV2.children),
                joinedload(GearItemDBV2.user),  # type: ignore[attr-defined]
            )
            .offset(skip)
            .limit(limit)
            .order_by(GearItemDBV2.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_public_container(self, container_id: str) -> GearItemDBV2 | None:
        """Get a public container by ID.

        Args:
            container_id: Container ID

        Returns:
            Container if found and public, None otherwise (with children/user loaded)
        """
        stmt = (
            select(GearItemDBV2)
            .where(
                and_(
                    GearItemDBV2.id == container_id,
                    GearItemDBV2.item_type == "container",
                    GearItemDBV2.is_public == True,  # noqa: E712
                    or_(
                        GearItemDBV2.is_hidden_by_reports == False,  # noqa: E712
                        GearItemDBV2.is_hidden_by_reports.is_(None),
                    ),
                )
            )
            .options(
                selectinload(GearItemDBV2.children),
                joinedload(GearItemDBV2.user),  # type: ignore[attr-defined]
            )
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_public_container_for_reporting(self, container_id: str) -> GearItemDBV2 | None:
        """Get a public container by ID for reporting purposes.

        This method does NOT filter by is_hidden_by_reports, allowing reports
        even on containers that are already hidden.

        Args:
            container_id: Container ID

        Returns:
            Container if found and public, None otherwise
        """
        stmt = (
            select(GearItemDBV2)
            .where(
                and_(
                    GearItemDBV2.id == container_id,
                    GearItemDBV2.item_type == "container",
                    GearItemDBV2.is_public == True,  # noqa: E712
                )
            )
            .options(
                selectinload(GearItemDBV2.children),
                joinedload(GearItemDBV2.user),  # type: ignore[attr-defined]
            )
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_container_v2_owned_or_public(self, container_id: str, user_id: str) -> GearItemDBV2 | None:
        """Get a container (gear_items_v2) if the requesting user owns it, or it's public.

        Used by the rating endpoints: the owner may rate a container regardless of its
        visibility, other users only if it's public. Replaces the old two-step fallback of
        `get_container` (V1 ownership) then `get_public_container` (V2 public) -- that chain
        404'd for a private V2-only container even for its own owner, since get_container never
        found it in V1 (the same pattern as #043).

        Args:
            container_id: Container ID
            user_id: Requesting user ID

        Returns:
            Container if the user owns it or it's public, None otherwise
        """
        stmt = select(GearItemDBV2).where(
            GearItemDBV2.id == container_id,
            GearItemDBV2.item_type == "container",
            or_(GearItemDBV2.user_id == user_id, GearItemDBV2.is_public == True),  # noqa: E712
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # Item promotion operations
    async def get_promotion_by_item_and_user(self, item_id: str, user_id: str) -> ItemPromotionDB | None:
        """Get promotion record by item and user.

        Args:
            item_id: Item ID
            user_id: User ID

        Returns:
            Promotion record if found, None otherwise
        """
        stmt = select(ItemPromotionDB).where(
            and_(
                ItemPromotionDB.item_id == item_id,
                ItemPromotionDB.user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_promotion(self, item_id: str, user_id: str) -> ItemPromotionDB:
        """Create a new promotion record.

        Args:
            item_id: Item ID to promote
            user_id: User ID who is promoting

        Returns:
            Created promotion record
        """
        promotion = ItemPromotionDB(
            id=generate_id(),
            item_id=item_id,
            user_id=user_id,
        )
        self.db.add(promotion)
        await self.db.commit()
        await self.db.refresh(promotion)
        return promotion

    async def get_promotions_by_item(self, item_id: str) -> Sequence[ItemPromotionDB]:
        """Get all promotions for an item.

        Args:
            item_id: Item ID

        Returns:
            List of promotion records
        """
        stmt = select(ItemPromotionDB).where(ItemPromotionDB.item_id == item_id).order_by(ItemPromotionDB.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # Share token operations
    async def create_share_token(
        self,
        container_id: str,
        user_id: str,
        token: str,
        expires_at: datetime | None = None,
    ) -> ContainerShareTokenDB:
        """Create a share token for a container.

        Args:
            container_id: Container ID to share
            user_id: Owner user ID
            token: Unique share token
            expires_at: Optional expiration timestamp

        Returns:
            Created share token
        """
        share_token = ContainerShareTokenDB(
            token=token,
            container_id=container_id,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.db.add(share_token)
        await self.db.commit()
        await self.db.refresh(share_token)
        return share_token

    async def get_container_by_token(self, token: str) -> GearItemDBV2 | None:
        """Get a container by share token.

        Args:
            token: Share token

        Returns:
            Container if token is valid and not expired, None otherwise (with children/user
            relationships loaded)
        """
        # Check if token exists and is not expired
        token_stmt = (
            select(ContainerShareTokenDB)
            .where(ContainerShareTokenDB.token == token)
            .where(
                or_(
                    ContainerShareTokenDB.expires_at.is_(None),
                    ContainerShareTokenDB.expires_at > datetime.now(UTC),
                )
            )
        )
        token_result = await self.db.execute(token_stmt)
        share_token = token_result.scalar_one_or_none()

        if not share_token:
            return None

        # Get container with children and user relationship
        stmt = (
            select(GearItemDBV2)
            .where(GearItemDBV2.id == share_token.container_id)
            .options(
                selectinload(GearItemDBV2.children),
                joinedload(GearItemDBV2.user),  # type: ignore[attr-defined]
            )
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_share_tokens_by_container(self, container_id: str, user_id: str) -> Sequence[ContainerShareTokenDB]:
        """Get all share tokens for a container (only for owner).

        Args:
            container_id: Container ID
            user_id: Owner user ID

        Returns:
            List of share tokens for the container
        """
        # Verify container ownership against gear_items_v2 (the container may not have a
        # V1 gear_containers counterpart -- see #043/#044).
        owner_stmt = select(GearItemDBV2.id).where(
            GearItemDBV2.id == container_id,
            GearItemDBV2.user_id == user_id,
        )
        owner_result = await self.db.execute(owner_stmt)
        if owner_result.scalar_one_or_none() is None:
            return []

        stmt = select(ContainerShareTokenDB).where(ContainerShareTokenDB.container_id == container_id).order_by(ContainerShareTokenDB.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def revoke_share_token(self, token: str, user_id: str) -> bool:
        """Revoke a share token (only by owner).

        Args:
            token: Share token to revoke
            user_id: Owner user ID

        Returns:
            True if token was revoked, False otherwise
        """
        token_stmt = select(ContainerShareTokenDB).where(ContainerShareTokenDB.token == token)
        token_result = await self.db.execute(token_stmt)
        share_token = token_result.scalar_one_or_none()

        if not share_token or share_token.user_id != user_id:
            return False

        await self.db.delete(share_token)
        await self.db.commit()
        return True

    # Rating operations
    async def get_container_rating(self, container_id: str, user_id: str, rating_type: str = "user") -> ContainerRatingDB | None:
        """Get user's rating for a container by type.

        Args:
            container_id: Container ID
            user_id: User ID
            rating_type: Rating type ('owner' or 'user')

        Returns:
            Rating if found, None otherwise
        """
        result = await self.db.execute(select(ContainerRatingDB).where(ContainerRatingDB.container_id == container_id).where(ContainerRatingDB.user_id == user_id).where(ContainerRatingDB.rating_type == rating_type))
        return result.scalar_one_or_none()

    async def upsert_container_rating(self, container_id: str, user_id: str, rating: int, rating_type: str = "user") -> ContainerRatingDB:
        """Create or update user's rating for a container.

        Args:
            container_id: Container ID
            user_id: User ID
            rating: Rating value (1-5)
            rating_type: Rating type ('owner' or 'user')

        Returns:
            Created or updated rating
        """
        existing = await self.get_container_rating(container_id, user_id, rating_type)

        if existing:
            existing.rating = rating
            existing.updated_at = datetime.now(UTC)
            await self.db.flush()
            return existing

        new_rating = ContainerRatingDB(
            id=generate_id(),
            container_id=container_id,
            user_id=user_id,
            rating=rating,
            rating_type=rating_type,
        )
        self.db.add(new_rating)
        await self.db.flush()
        return new_rating

    async def delete_container_rating(self, container_id: str, user_id: str, rating_type: str = "user") -> bool:
        """Delete user's rating for a container.

        Args:
            container_id: Container ID
            user_id: User ID
            rating_type: Rating type ('owner' or 'user')

        Returns:
            True if deleted, False if not found
        """
        rating = await self.get_container_rating(container_id, user_id, rating_type)
        if rating:
            await self.db.delete(rating)
            await self.db.flush()
            return True
        return False

    async def get_container_average_user_rating(self, container_id: str) -> float | None:
        """Calculate average user rating for a container (excluding owner ratings).

        Args:
            container_id: Container ID

        Returns:
            Average rating or None if no ratings
        """
        result = await self.db.execute(select(func.avg(ContainerRatingDB.rating)).where(ContainerRatingDB.container_id == container_id).where(ContainerRatingDB.rating_type == "user"))
        avg = result.scalar()
        return float(avg) if avg is not None else None

    async def get_container_user_rating_count(self, container_id: str) -> int:
        """Get number of user ratings for a container (excluding owner ratings).

        Args:
            container_id: Container ID

        Returns:
            Number of user ratings
        """
        result = await self.db.execute(select(func.count(ContainerRatingDB.id)).where(ContainerRatingDB.container_id == container_id).where(ContainerRatingDB.rating_type == "user"))
        return result.scalar() or 0

    async def get_container_owner_rating(self, container_id: str) -> int | None:
        """Get owner's rating for a container.

        Args:
            container_id: Container ID

        Returns:
            Owner rating (1-5) or None if not set
        """
        result = await self.db.execute(select(ContainerRatingDB.rating).where(ContainerRatingDB.container_id == container_id).where(ContainerRatingDB.rating_type == "owner").limit(1))
        rating = result.scalar_one_or_none()
        return rating if rating else None

    class ContainerRatingsData(TypedDict):
        """Type for container ratings aggregated data."""

        owner_rating: int | None
        user_rating: int | None
        average_user_rating: float | None
        user_rating_count: int

    async def get_container_ratings_data(
        self,
        container_id: str,
        requesting_user_id: str | None = None,
        is_owner: bool = False,
    ) -> ContainerRatingsData:
        """Get all ratings data for a container.

        Args:
            container_id: Container ID
            requesting_user_id: ID of user requesting the data (for user_rating)
            is_owner: Whether requesting user is the owner

        Returns:
            Dictionary with all rating fields
        """
        # Load owner rating
        owner_rating = await self.get_container_owner_rating(container_id)

        # Load user rating (only if not owner and user_id provided)
        user_rating = None
        if requesting_user_id and not is_owner:
            user_rating_obj = await self.get_container_rating(container_id, requesting_user_id, rating_type="user")
            user_rating = user_rating_obj.rating if user_rating_obj else None

        # Calculate average user rating and count
        avg_user_rating = await self.get_container_average_user_rating(container_id)
        user_rating_count = await self.get_container_user_rating_count(container_id)

        return {
            "owner_rating": owner_rating,
            "user_rating": user_rating,
            "average_user_rating": avg_user_rating,
            "user_rating_count": user_rating_count,
        }

    # Global Catalogue Methods
    async def get_catalogue_items(
        self,
        query: str | None = None,
        category: str | None = None,
        brand: str | None = None,
        price_tier: str | None = None,
        quality: str | None = None,
        is_active: bool | None = True,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[GlobalCatalogueItemDB]:
        """Get global catalogue items with filtering and search.

        Args:
            query: Search query (searches in name, description, brand, model)
            category: Filter by category
            brand: Filter by brand
            price_tier: Filter by price tier
            quality: Filter by quality
            is_active: Filter by active status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of catalogue items
        """
        stmt = select(GlobalCatalogueItemDB)

        # Build filters
        conditions = []
        if is_active is not None:
            conditions.append(GlobalCatalogueItemDB.is_active == is_active)
        if category:
            conditions.append(GlobalCatalogueItemDB.category == category)
        if brand:
            conditions.append(GlobalCatalogueItemDB.brand == brand)
        if price_tier:
            conditions.append(GlobalCatalogueItemDB.price_tier == price_tier)
        if quality:
            conditions.append(GlobalCatalogueItemDB.quality == quality)

        # Full Text Search using PostgreSQL to_tsvector and to_tsquery
        if query:
            from sqlalchemy import func, text

            # Escape special characters in query for tsquery
            # Replace spaces with & (AND operator) and escape special characters
            query_escaped = query.replace("'", "''").replace("&", " ").replace("|", " ").replace("!", " ").replace("(", " ").replace(")", " ")
            # Split by spaces and join with & (AND) operator
            query_terms = " & ".join([term.strip() for term in query_escaped.split() if term.strip()])

            # Build tsvector from multiple columns (name, description, brand, model)
            # Use 'simple' dictionary for better matching (no language-specific stemming)
            # Concatenate columns with space separator using || operator
            tsvector_expr = func.to_tsvector(
                "simple",
                func.coalesce(GlobalCatalogueItemDB.name, "") + " " + func.coalesce(GlobalCatalogueItemDB.description, "") + " " + func.coalesce(GlobalCatalogueItemDB.brand, "") + " " + func.coalesce(GlobalCatalogueItemDB.model, ""),
            )
            tsquery_expr = func.to_tsquery("simple", query_terms)

            # Full text search condition using @@ operator (PostgreSQL full-text search)
            # Use text() with proper parameter binding for safety
            # Apply search condition directly to statement (not via conditions list)
            search_condition = text(
                "to_tsvector('simple', "
                "coalesce(global_catalogue_items.name, '') || ' ' || "
                "coalesce(global_catalogue_items.description, '') || ' ' || "
                "coalesce(global_catalogue_items.brand, '') || ' ' || "
                "coalesce(global_catalogue_items.model, '')) "
                "@@ to_tsquery('simple', :query_terms)"
            ).bindparams(query_terms=query_terms)
            stmt = stmt.where(search_condition)

            # Order by relevance (ts_rank) when searching
            rank_expr = func.ts_rank(tsvector_expr, tsquery_expr)
            stmt = stmt.order_by(rank_expr.desc(), GlobalCatalogueItemDB.name.asc())
        else:
            # Order by name when not searching
            stmt = stmt.order_by(GlobalCatalogueItemDB.name.asc())

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Load creator relationship
        stmt = stmt.options(joinedload(GlobalCatalogueItemDB.creator))

        # Pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_catalogue_item(self, item_id: str) -> GlobalCatalogueItemDB | None:
        """Get a single catalogue item by ID.

        Args:
            item_id: Catalogue item ID

        Returns:
            Catalogue item if found, None otherwise (with creator relationship loaded)
        """
        stmt = select(GlobalCatalogueItemDB).where(GlobalCatalogueItemDB.id == item_id).options(joinedload(GlobalCatalogueItemDB.creator))
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_catalogue_item(
        self,
        user_id: str,
        data: GlobalCatalogueItemCreate,
    ) -> GlobalCatalogueItemDB:
        """Create a new catalogue item.

        Args:
            user_id: User ID creating the item
            data: Item creation data

        Returns:
            Created catalogue item
        """
        item_id = generate_id()
        item = GlobalCatalogueItemDB(
            id=item_id,
            version=1,
            name=data.name,
            category=data.category,
            weight=data.weight,
            weight_unit=data.weightUnit,
            description=data.description,
            brand=data.brand,
            model=data.model,
            price_tier=data.priceTier,
            price=data.price,
            currency=data.currency,
            quality=data.quality,
            url=data.url,
            color=data.color,
            is_active=True,
            created_by=user_id,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def update_catalogue_item(
        self,
        item_id: str,
        user_id: str,
        data: GlobalCatalogueItemUpdate,
        is_admin: bool = False,
    ) -> GlobalCatalogueItemDB | None:
        """Update a catalogue item.

        Only the creator or admin can update items.

        Args:
            item_id: Catalogue item ID
            user_id: User ID updating the item
            data: Update data
            is_admin: Whether user is admin

        Returns:
            Updated item if found and user has permission, None otherwise
        """
        item = await self.get_catalogue_item(item_id)
        if not item:
            return None

        # Check permissions: creator or admin
        if not is_admin and item.created_by != user_id:
            return None

        # Update fields
        update_dict = data.model_dump(exclude_unset=True, by_alias=False)
        for key, value in update_dict.items():
            # Handle camelCase to snake_case conversion
            if key == "weightUnit":
                item.weight_unit = value
            elif key == "priceTier":
                item.price_tier = value
            elif key == "isActive":
                item.is_active = value
            else:
                setattr(item, key, value)

        # Increment version on update
        item.version += 1
        item.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_catalogue_item(
        self,
        item_id: str,
        user_id: str,
        is_admin: bool = False,
    ) -> bool:
        """Delete a catalogue item (soft delete by setting is_active=False).

        Only the creator or admin can delete items.

        Args:
            item_id: Catalogue item ID
            user_id: User ID deleting the item
            is_admin: Whether user is admin

        Returns:
            True if deleted, False otherwise
        """
        item = await self.get_catalogue_item(item_id)
        if not item:
            return False

        # Check permissions: creator or admin
        if not is_admin and item.created_by != user_id:
            return False

        # Soft delete
        item.is_active = False
        item.updated_at = datetime.now(UTC)
        await self.db.commit()
        return True

    # Content report operations
    async def create_container_report(
        self,
        container_id: str,
        reporter_user_id: str,
        reason: str,
        additional_info: str | None = None,
    ) -> ContentReportDB:
        """Create a new content report for a container.

        Args:
            container_id: Container ID being reported
            reporter_user_id: User ID reporting the container
            reason: Reason for report (spam_fraud, violence, sexual_content, profanity, other)
            additional_info: Optional additional information

        Returns:
            Created report

        Raises:
            IntegrityError: If report already exists (unique constraint violation)
        """
        report = ContentReportDB(
            id=generate_id(),
            container_id=container_id,
            reporter_user_id=reporter_user_id,
            reason=reason,
            additional_info=additional_info,
            status="pending",
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)

        # Reload with relationships
        stmt = (
            select(ContentReportDB)
            .options(
                joinedload(ContentReportDB.container),
                joinedload(ContentReportDB.reporter),
            )
            .where(ContentReportDB.id == report.id)
        )
        result = await self.db.execute(stmt)
        report_with_relations = result.unique().scalar_one()

        return report_with_relations

    async def get_reports_for_container(self, container_id: str) -> Sequence[ContentReportDB]:
        """Get all reports for a container.

        Args:
            container_id: Container ID

        Returns:
            List of reports for the container
        """
        stmt = select(ContentReportDB).where(ContentReportDB.container_id == container_id).order_by(ContentReportDB.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_active_reports_for_container(self, container_id: str) -> int:
        """Count active reports (pending + action_taken) for a container.

        Args:
            container_id: Container ID

        Returns:
            Number of active reports
        """
        stmt = select(func.count(ContentReportDB.id)).where(
            and_(
                ContentReportDB.container_id == container_id,
                or_(
                    ContentReportDB.status == "pending",
                    ContentReportDB.status == "action_taken",
                ),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def get_all_reports(
        self,
        status: str | None = None,
        container_id: str | None = None,
        reporter_user_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[ContentReportDB], int]:
        """Get all reports with optional filters.

        Args:
            status: Filter by status (pending, reviewed, dismissed, action_taken)
            container_id: Filter by container ID
            reporter_user_id: Filter by reporter user ID
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            Tuple of (reports list, total count)
        """
        conditions = []
        if status:
            conditions.append(ContentReportDB.status == status)
        if container_id:
            conditions.append(ContentReportDB.container_id == container_id)
        if reporter_user_id:
            conditions.append(ContentReportDB.reporter_user_id == reporter_user_id)

        where_clause = and_(*conditions) if conditions else true()

        # Get total count
        count_stmt = select(func.count(ContentReportDB.id)).where(where_clause)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get reports with eager loading of relationships
        stmt = (
            select(ContentReportDB)
            .options(
                joinedload(ContentReportDB.container),
                joinedload(ContentReportDB.reporter),
            )
            .where(where_clause)
            .order_by(ContentReportDB.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        reports = result.unique().scalars().all()

        return reports, total

    async def update_report_status(
        self,
        report_id: str,
        status: str,
        reviewed_by: str | None = None,
    ) -> ContentReportDB | None:
        """Update report status.

        Args:
            report_id: Report ID
            status: New status (pending, reviewed, dismissed, action_taken)
            reviewed_by: User ID who reviewed the report (for reviewed/action_taken statuses)

        Returns:
            Updated report if found, None otherwise
        """
        stmt = (
            select(ContentReportDB)
            .options(
                joinedload(ContentReportDB.container),
                joinedload(ContentReportDB.reporter),
            )
            .where(ContentReportDB.id == report_id)
        )
        result = await self.db.execute(stmt)
        report = result.unique().scalar_one_or_none()

        if not report:
            return None

        report.status = status
        if reviewed_by:
            report.reviewed_by = reviewed_by
        if status in ("reviewed", "dismissed", "action_taken"):
            report.reviewed_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def set_container_hidden_by_reports(self, container_id: str, is_hidden: bool) -> GearItemDBV2 | None:
        """Set is_hidden_by_reports flag for a container.

        Args:
            container_id: Container ID
            is_hidden: Whether container should be hidden

        Returns:
            Updated container if found, None otherwise
        """
        stmt = select(GearItemDBV2).where(GearItemDBV2.id == container_id, GearItemDBV2.item_type == "container")
        result = await self.db.execute(stmt)
        container = result.scalar_one_or_none()

        if not container:
            return None

        container.is_hidden_by_reports = is_hidden
        container.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(container)
        return container

    async def get_report_by_container_and_user(
        self,
        container_id: str,
        user_id: str,
    ) -> ContentReportDB | None:
        """Get report by container ID and user ID.

        Args:
            container_id: Container ID
            user_id: Reporter user ID

        Returns:
            Report if found, None otherwise
        """
        stmt = select(ContentReportDB).where(
            and_(
                ContentReportDB.container_id == container_id,
                ContentReportDB.reporter_user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_report(self, report_id: str) -> bool:
        """Delete a report.

        Args:
            report_id: Report ID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(ContentReportDB).where(ContentReportDB.id == report_id)
        result = await self.db.execute(stmt)
        report = result.scalar_one_or_none()

        if not report:
            return False

        await self.db.delete(report)
        await self.db.commit()
        return True
