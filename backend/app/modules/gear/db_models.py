"""SQLAlchemy database models for gear management.

This module provides SQLAlchemy ORM models for gear containers and items.
Designed to work with async SQLAlchemy sessions.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GearContainerDB(Base):
    """SQLAlchemy model for gear containers.

    Represents containers like backpacks, bags, or other storage units
    that hold gear items.

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        user_id: Owner of the container
        name: Container name
        description: Optional container description
        type: Container type (backpack, bag, pouch, etc.)
        color: Container color theme
        parent_container_id: Parent container ID for nested containers
        brand: Manufacturer/brand
        price: Container price
        created_at: Creation timestamp
        updated_at: Last update timestamp
        items: Relationship to gear items
    """

    __tablename__ = "gear_containers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True, default="default")
    parent_container_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("gear_containers.id"), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    hide_when_nested: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_unit: Mapped[str | None] = mapped_column(String(5), nullable=True)
    max_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_weight_unit: Mapped[str | None] = mapped_column(String(5), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<GearContainerDB(id={self.id}, name={self.name}, type={self.type})>"


class GearItemDB(Base):
    """SQLAlchemy model for gear items.

    Represents individual items stored in gear containers.

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        container_id: Parent container ID
        name: Item name
        category: Item category (water, food, shelter, etc.)
        quantity: Item quantity
        weight: Item weight value
        weight_unit: Weight unit (g or kg)
        notes: Optional notes
        expiration_date: Optional expiration date
        priority: Item priority (critical, high, medium, low)
        status: Item status (owned, missing, toBuy)
        nested_container_id: Optional reference to a nested container
        price: Item price
        url: Product URL
        brand: Manufacturer/brand
        color: Item color
        quality: Quality tier (low, medium, high)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "gear_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    container_id: Mapped[str] = mapped_column(String(36), ForeignKey("gear_containers.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    weight_unit: Mapped[str] = mapped_column(String(5), nullable=False, default="g")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    expiration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="owned")
    nested_container_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("gear_containers.id"), nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quality: Mapped[str | None] = mapped_column(String(20), nullable=True)
    linked_item_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("gear_items.id"), nullable=True)
    wearable: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    consumable: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    container: Mapped["GearContainerDB"] = relationship("GearContainerDB", back_populates="items", foreign_keys=[container_id])

    def __repr__(self) -> str:
        return f"<GearItemDB(id={self.id}, name={self.name}, category={self.category})>"


# Define relationship after both classes are defined
# This resolves the AmbiguousForeignKeysError by explicitly specifying
# which foreign key to use (container_id vs nested_container_id)
GearContainerDB.items = relationship(
    "GearItemDB",
    back_populates="container",
    foreign_keys=[GearItemDB.container_id],
    cascade="all, delete-orphan",
)

# Add user relationship for public containers
from app.modules.auth.db_models import UserDB  # noqa: E402

GearContainerDB.user = relationship("UserDB", foreign_keys=[GearContainerDB.user_id])
