"""SQLAlchemy database models for gear management.

This module provides SQLAlchemy ORM models for the ancillary gear-related tables that survive
the V1 unified-model migration: item images, container share tokens, container ratings, item
promotions, content reports, and the global catalogue. The core gear containers/items model is
`GearItemDBV2` in `db_models_v2.py` (docs/plans/2026-07-23-gear-backend-v1-v2-unification.md).
Designed to work with async SQLAlchemy sessions.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ItemImageDB(Base):
    """SQLAlchemy model for item images.

    Represents images uploaded for gear items.

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        item_id: Parent item ID
        user_id: Uploader user ID
        storage_type: Storage backend type (local or s3)
        file_path: Relative path for local storage, S3 key for S3
        file_name: Original filename
        file_size: File size in bytes
        mime_type: MIME type (image/jpeg, image/png, etc.)
        width: Image width in pixels
        height: Image height in pixels
        is_primary: Whether this is the primary image for the item
        order: Display order (0-based)
        is_processed: Whether image has been processed (resized/optimized)
        original_file_size: Original file size before processing
        created_at: Upload timestamp
        updated_at: Last update timestamp
        item: Relationship to gear item
        user: Relationship to user
    """

    __tablename__ = "item_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    item_id: Mapped[str] = mapped_column(
        String(36),
        # Points at gear_items_v2, not legacy gear_items -- see migration 058
        # (docs/plans/2026-07-23-gear-backend-v1-v2-unification.md, Phase 2/3a /
        # docs/issues/2026-07-23--043--gear-v1-v2-backend-duality-image-ownership-broken.md).
        ForeignKey("gear_items_v2.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Storage info
    storage_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    external_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)  # External URL if not hosted locally

    # Image metadata
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Processing flags
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    original_file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # No ORM relationship to the parent item -- item_id now targets gear_items_v2 (not
    # GearItemDB/V1), and nothing in this codebase navigates it; all lookups are explicit joins.

    def __repr__(self) -> str:
        return f"<ItemImageDB(id={self.id}, item_id={self.item_id}, file_name={self.file_name})>"


class ContainerShareTokenDB(Base):
    """SQLAlchemy model for container share tokens.

    Represents tokens that allow read-only access to containers via a shareable link.
    Tokens can have optional expiry dates and are used to share non-public containers.

    Attributes:
        token: Unique share token (URL-safe, 32+ chars)
        container_id: Container ID being shared
        user_id: Owner of the container (who created the token)
        expires_at: Optional expiration timestamp
        created_at: Token creation timestamp
        container: Relationship to gear container
    """

    __tablename__ = "container_share_tokens"

    token: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    container_id: Mapped[str] = mapped_column(
        String(36),
        # Points at gear_items_v2, not legacy gear_containers -- see migration 057
        # (docs/plans/2026-07-23-gear-backend-v1-v2-unification.md, Phase 1 /
        # docs/issues/2026-07-23--044--container-share-tokens-table-missing-prod.md).
        ForeignKey("gear_items_v2.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    def __repr__(self) -> str:
        return f"<ContainerShareTokenDB(token={self.token[:8]}..., container_id={self.container_id})>"


from app.modules.auth.db_models import UserDB  # noqa: E402
from app.modules.gear.db_models_v2 import GearItemDBV2  # noqa: E402

ItemImageDB.user = relationship("UserDB", foreign_keys=[ItemImageDB.user_id])

# Add relationships for share tokens
ContainerShareTokenDB.container = relationship("GearItemDBV2", foreign_keys=[ContainerShareTokenDB.container_id])
ContainerShareTokenDB.user = relationship("UserDB", foreign_keys=[ContainerShareTokenDB.user_id])


class ContainerRatingDB(Base):
    """SQLAlchemy model for container ratings.

    Supports two types of ratings:
    - 'owner': Rating given by container owner
    - 'user': Rating given by other users (for public containers)

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        container_id: Rated container ID
        user_id: User who gave the rating
        rating: Rating value (1-5)
        rating_type: Type of rating ('owner' or 'user')
        created_at: Rating timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "container_ratings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    container_id: Mapped[str] = mapped_column(
        String(36),
        # Points at gear_items_v2, not legacy gear_containers -- see migration 058
        # (docs/plans/2026-07-23-gear-backend-v1-v2-unification.md, Phase 2/3b).
        ForeignKey("gear_items_v2.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    rating_type: Mapped[str] = mapped_column(String(10), nullable=False, default="user")  # 'owner' or 'user'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Unique constraint: one rating per user per container per type
    # CHECK constraints for validation
    __table_args__ = (
        UniqueConstraint(
            "container_id",
            "user_id",
            "rating_type",
            name="uq_container_rating_user_type",
        ),
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
        CheckConstraint("rating_type IN ('owner', 'user')", name="check_rating_type"),
    )

    def __repr__(self) -> str:
        return f"<ContainerRatingDB(id={self.id}, container_id={self.container_id}, rating={self.rating}, rating_type={self.rating_type})>"


# Add relationships for container ratings
# One-way to GearItemDBV2 -- gear_items_v2 (not GearContainerDB/V1) owns ratings going forward,
# and nothing in this codebase navigates .container, so there's no back_populates to keep in sync.
ContainerRatingDB.container = relationship("GearItemDBV2", foreign_keys=[ContainerRatingDB.container_id])
ContainerRatingDB.user = relationship("UserDB", foreign_keys=[ContainerRatingDB.user_id])


class GlobalCatalogueItemDB(Base):
    """SQLAlchemy model for global catalogue items.

    Represents template items in the global catalogue that users can add to their containers.
    Items from the catalogue are copied (not linked) when added to user containers.

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        version: Version number for this item (for versioning support)
        name: Item name
        category: Item category (water, food, shelter, etc.)
        weight: Item weight value
        weight_unit: Weight unit (g, kg, oz, or lb)
        description: Item description
        brand: Manufacturer/brand
        model: Model name/number
        price_tier: Price tier (low, medium, high)
        quality: Quality tier (low, medium, high) - zgodne z GearItemQuality
        url: Product URL
        color: Item color (optional)
        shops: List of shop links with optional names (JSONB array of objects)
        is_active: Whether item is active in catalogue
        created_by: User ID who created this item (nullable for system items)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "global_catalogue_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    weight_unit: Mapped[str] = mapped_column(String(5), nullable=False, default="g")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price_tier: Mapped[str | None] = mapped_column(String(20), nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    quality: Mapped[str | None] = mapped_column(String(20), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    shops: Mapped[list[dict[str, str]]] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    creator: Mapped[UserDB | None] = relationship("UserDB", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<GlobalCatalogueItemDB(id={self.id}, name={self.name}, version={self.version})>"


class CatalogueItemImageDB(Base):
    """SQLAlchemy model for catalogue item images.

    Represents images uploaded for global catalogue items.
    Identical structure to ItemImageDB, but for catalogue items.

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        catalogue_item_id: Parent catalogue item ID
        user_id: Uploader user ID (admin)
        storage_type: Storage backend type (local or s3)
        file_path: Relative path for local storage, S3 key for S3
        file_name: Original filename
        file_size: File size in bytes
        mime_type: MIME type (image/jpeg, image/png, etc.)
        width: Image width in pixels
        height: Image height in pixels
        is_primary: Whether this is the primary image for the item
        order: Display order (0-based)
        is_processed: Whether image has been processed (resized/optimized)
        original_file_size: Original file size before processing
        external_url: External URL if not hosted locally
        created_at: Upload timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "catalogue_item_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    catalogue_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("global_catalogue_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Storage info
    storage_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    external_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Image metadata
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Processing flags
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    original_file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    catalogue_item: Mapped[GlobalCatalogueItemDB] = relationship("GlobalCatalogueItemDB", back_populates="images")
    user: Mapped[UserDB] = relationship("UserDB", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<CatalogueItemImageDB(id={self.id}, catalogue_item_id={self.catalogue_item_id}, file_name={self.file_name})>"


# Add images relationship to GlobalCatalogueItemDB
GlobalCatalogueItemDB.images = relationship(
    "CatalogueItemImageDB",
    back_populates="catalogue_item",
    cascade="all, delete-orphan",
    order_by="CatalogueItemImageDB.order",
)


class ItemPromotionDB(Base):
    """SQLAlchemy model for item promotions to catalogue.

    Tracks which users have promoted which items to be added to the global catalogue.
    Each user can promote an item only once.

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        item_id: Promoted item ID
        user_id: User who promoted the item
        created_at: Promotion timestamp
    """

    __tablename__ = "item_promotions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    item_id: Mapped[str] = mapped_column(
        String(36),
        # Points at gear_items_v2, not legacy gear_items -- see migration 058
        # (docs/plans/2026-07-23-gear-backend-v1-v2-unification.md, Phase 2/3b).
        ForeignKey("gear_items_v2.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    # One-way to GearItemDBV2 -- nothing in this codebase navigates .item, so there's no
    # back_populates target to keep in sync.
    item: Mapped[GearItemDBV2] = relationship("GearItemDBV2", foreign_keys=[item_id])
    user: Mapped[UserDB] = relationship("UserDB")

    # Unique constraint: user can promote item only once
    __table_args__ = (UniqueConstraint("item_id", "user_id", name="unique_item_user_promotion"),)

    def __repr__(self) -> str:
        return f"<ItemPromotionDB(id={self.id}, item_id={self.item_id}, user_id={self.user_id})>"


class ContentReportDB(Base):
    """SQLAlchemy model for content reports.

    Represents reports of inappropriate content in public containers.
    Supports automatic hiding of containers after reaching threshold of reports.

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        container_id: Reported container ID
        reporter_user_id: User who reported the content
        reason: Reason for report (spam_fraud, violence, sexual_content, profanity, other)
        additional_info: Optional additional information
        status: Report status (pending, reviewed, dismissed, action_taken)
        created_at: Report creation timestamp
        reviewed_at: Review timestamp (when status was changed)
        reviewed_by: Admin user ID who reviewed the report
    """

    __tablename__ = "content_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    container_id: Mapped[str] = mapped_column(
        String(36),
        # Points at gear_items_v2, not legacy gear_containers -- see migration 058
        # (docs/plans/2026-07-23-gear-backend-v1-v2-unification.md, Phase 2/3b).
        ForeignKey("gear_items_v2.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reporter_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reason: Mapped[str] = mapped_column(String(50), nullable=False)
    additional_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Unique constraint: one report per user per container
    __table_args__ = (
        UniqueConstraint("container_id", "reporter_user_id", name="unique_container_reporter"),
        CheckConstraint(
            "reason IN ('spam_fraud', 'violence', 'sexual_content', 'profanity', 'other')",
            name="check_report_reason",
        ),
        CheckConstraint(
            "status IN ('pending', 'reviewed', 'dismissed', 'action_taken')",
            name="check_report_status",
        ),
    )

    # Relationships
    # One-way to GearItemDBV2 -- nothing in this codebase navigates .container, so there's no
    # back_populates target to keep in sync.
    container: Mapped[GearItemDBV2] = relationship("GearItemDBV2", foreign_keys=[container_id])
    reporter: Mapped[UserDB] = relationship("UserDB", foreign_keys=[reporter_user_id])
    reviewer: Mapped[UserDB | None] = relationship("UserDB", foreign_keys=[reviewed_by])

    def __repr__(self) -> str:
        return f"<ContentReportDB(id={self.id}, container_id={self.container_id}, reason={self.reason}, status={self.status})>"
