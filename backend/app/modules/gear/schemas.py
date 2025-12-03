"""Pydantic schemas for gear management endpoints.

This module defines request and response models for the gear API,
using camelCase for JSON field names to match frontend conventions.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# Type aliases matching frontend
GearContainerType = str  # Allows custom types: 'backpack', 'bag', 'pouch', etc.
GearItemStatus = Literal["owned", "missing", "toBuy"]
GearItemPriority = Literal["critical", "high", "medium", "low"]
GearItemQuality = Literal["low", "medium", "high"]
GearWeightUnit = Literal["g", "kg", "oz", "lb"]
RatingType = Literal["owner", "user"]
ContainerColor = Literal[
    # Current colors
    "default",
    "coyote",
    "khaki",
    "olive",
    "forestGreen",
    "tan",
    "brown",
    "black",
    "navy",
    "jeans",
    "gray",
    "orange",
    # Legacy colors (for backward compatibility - may exist in older data)
    "blue",
    "yellow",
    "green",
    "indigo",
    "pink",
    "purple",
    "red",
    "teal",
]
GearItemCategory = str  # Allows custom categories: 'water', 'food', 'shelter', etc.


# Container Schemas
class ContainerCreate(BaseModel):
    """Schema for creating a new gear container."""

    id: str | None = Field(
        None,
        description="Optional UUID for import/update workflow (when UUID is provided in markdown export)",
    )
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    type: GearContainerType
    color: ContainerColor | None = "default"
    parentContainerId: str | None = Field(None, alias="parentContainerId")
    brand: str | None = Field(None, max_length=255)
    price: float | None = Field(None, ge=0)
    hideWhenNested: bool | None = Field(default=None, alias="hideWhenNested")
    weight: float | None = Field(None, ge=0)
    weightUnit: GearWeightUnit | None = Field(None, alias="weightUnit")
    maxWeight: float | None = Field(None, ge=0, alias="maxWeight")
    maxWeightUnit: GearWeightUnit | None = Field(None, alias="maxWeightUnit")
    url: str | None = None
    isPublic: bool | None = Field(default=None, alias="isPublic")
    favorite: bool | None = Field(default=None)
    showItemImages: bool | None = Field(default=None, alias="showItemImages")

    model_config = {"populate_by_name": True}


class ContainerUpdate(BaseModel):
    """Schema for updating a gear container."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    type: GearContainerType | None = None
    color: ContainerColor | None = None
    parentContainerId: str | None = Field(None, alias="parentContainerId")
    brand: str | None = Field(None, max_length=255)
    price: float | None = Field(None, ge=0)
    hideWhenNested: bool | None = Field(None, alias="hideWhenNested")
    weight: float | None = Field(None, ge=0)
    weightUnit: GearWeightUnit | None = Field(None, alias="weightUnit")
    maxWeight: float | None = Field(None, ge=0, alias="maxWeight")
    maxWeightUnit: GearWeightUnit | None = Field(None, alias="maxWeightUnit")
    url: str | None = None
    isPublic: bool | None = Field(default=None, alias="isPublic")
    favorite: bool | None = Field(default=None)
    showItemImages: bool | None = Field(default=None, alias="showItemImages")

    model_config = {"populate_by_name": True}


class ItemResponse(BaseModel):
    """Schema for gear item response."""

    id: str
    name: str
    category: GearItemCategory
    quantity: int
    weight: float
    weightUnit: GearWeightUnit
    notes: str | None = None
    expirationDate: datetime | None = None
    priority: GearItemPriority
    status: GearItemStatus
    containerId: str | None = Field(None, alias="containerId")
    price: float | None = None
    currency: str | None = None
    url: str | None = None
    brand: str | None = None
    color: str | None = None
    quality: GearItemQuality | None = None
    linkedItemId: str | None = Field(None, alias="linkedItemId")
    catalogueItemId: str | None = Field(None, alias="catalogueItemId")
    wearable: bool | None = None
    consumable: bool | None = None
    order: int | None = Field(None, ge=0)
    showOnContainer: bool | None = Field(None, alias="showOnContainer")
    primaryImageUrl: str | None = Field(None, alias="primaryImageUrl")
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class ContainerResponse(BaseModel):
    """Schema for gear container response."""

    id: str
    name: str
    description: str | None = None
    type: GearContainerType
    color: ContainerColor | None = "default"
    parentContainerId: str | None = Field(None, alias="parentContainerId")
    brand: str | None = None
    price: float | None = None
    hideWhenNested: bool | None = None
    weight: float | None = None
    weightUnit: GearWeightUnit | None = Field(None, alias="weightUnit")
    maxWeight: float | None = None
    maxWeightUnit: GearWeightUnit | None = Field(None, alias="maxWeightUnit")
    url: str | None = None
    isPublic: bool
    favorite: bool
    showItemImages: bool | None = Field(None, alias="showItemImages")
    authorName: str | None = None  # Only populated for public containers
    authorId: str | None = Field(None, alias="authorId")  # Author user ID (only for public containers)
    items: list[ItemResponse] = []
    # Rating fields
    ownerRating: int | None = Field(None, alias="ownerRating")  # Owner's rating (1-5)
    userRating: int | None = Field(None, alias="userRating")  # Current user's rating (if logged in)
    averageUserRating: float | None = Field(None, alias="averageUserRating")  # Average of all user ratings
    userRatingCount: int = Field(default=0, alias="userRatingCount")  # Number of user ratings
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


# Item Schemas
class ItemCreate(BaseModel):
    """Schema for creating a new gear item."""

    id: str | None = Field(
        None,
        description="Optional UUID for import/update workflow (when UUID is provided in markdown export)",
    )
    name: str = Field(..., min_length=1, max_length=255)
    category: GearItemCategory
    quantity: int = Field(default=1, ge=1)
    weight: float = Field(..., ge=0)
    weightUnit: GearWeightUnit = Field(default="g")
    notes: str | None = None
    expirationDate: datetime | None = Field(None, alias="expirationDate")
    priority: GearItemPriority = Field(default="medium")
    status: GearItemStatus = Field(default="owned")
    containerId: str | None = Field(None, alias="containerId")
    price: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    url: str | None = None
    brand: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    quality: GearItemQuality | None = None
    linkedItemId: str | None = Field(None, alias="linkedItemId")
    catalogueItemId: str | None = Field(None, alias="catalogueItemId")
    wearable: bool | None = Field(default=None)
    consumable: bool | None = Field(default=None)
    order: int | None = Field(None, ge=0)
    showOnContainer: bool | None = Field(default=None, alias="showOnContainer")

    model_config = {"populate_by_name": True}


class ItemUpdate(BaseModel):
    """Schema for updating a gear item."""

    name: str | None = Field(None, min_length=1, max_length=255)
    category: GearItemCategory | None = None
    quantity: int | None = Field(None, ge=1)
    weight: float | None = Field(None, ge=0)
    weightUnit: GearWeightUnit | None = None
    notes: str | None = None
    expirationDate: datetime | None = Field(None, alias="expirationDate")
    priority: GearItemPriority | None = None
    status: GearItemStatus | None = None
    containerId: str | None = Field(None, alias="containerId")
    price: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    url: str | None = None
    brand: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    quality: GearItemQuality | None = None
    linkedItemId: str | None = Field(None, alias="linkedItemId")
    catalogueItemId: str | None = Field(None, alias="catalogueItemId")
    wearable: bool | None = None
    consumable: bool | None = None
    order: int | None = Field(None, ge=0)
    showOnContainer: bool | None = Field(None, alias="showOnContainer")

    model_config = {"populate_by_name": True}


class ItemOrderUpdate(BaseModel):
    """Schema for updating a single item's order."""

    id: str = Field(..., description="Item ID")
    order: int = Field(..., ge=0, description="New order value")


class BatchOrderUpdateRequest(BaseModel):
    """Schema for batch updating items' order."""

    items: list[ItemOrderUpdate] = Field(..., min_length=1, description="List of items with their new order values")

    model_config = {"populate_by_name": True}


# Share token schemas
class ShareTokenCreate(BaseModel):
    """Schema for creating a share token."""

    expiresAt: datetime | None = Field(None, alias="expiresAt", description="Optional expiration timestamp")

    model_config = {"populate_by_name": True}


class ShareTokenResponse(BaseModel):
    """Schema for share token response."""

    token: str = Field(..., description="Share token")
    containerId: str = Field(..., alias="containerId", description="Container ID")
    expiresAt: datetime | None = Field(None, alias="expiresAt", description="Expiration timestamp if set")
    createdAt: datetime = Field(..., alias="createdAt", description="Token creation timestamp")
    shareUrl: str = Field(..., alias="shareUrl", description="Full share URL")

    model_config = {"populate_by_name": True}


# Rating schemas
class ContainerRatingCreate(BaseModel):
    """Schema for creating/updating container rating."""

    rating: int = Field(..., ge=1, le=5, description="Rating value from 1 to 5")
    ratingType: RatingType = Field(
        default="user",
        alias="ratingType",
        description="Type of rating: 'owner' for owner rating, 'user' for user rating",
    )

    model_config = {"populate_by_name": True}


class ContainerRatingResponse(BaseModel):
    """Schema for container rating response."""

    id: str
    containerId: str = Field(alias="containerId")
    userId: str = Field(alias="userId")
    rating: int
    ratingType: RatingType = Field(alias="ratingType")
    createdAt: datetime = Field(alias="createdAt")
    updatedAt: datetime = Field(alias="updatedAt")

    model_config = {"from_attributes": True, "populate_by_name": True}


# Global Catalogue Schemas
class GlobalCatalogueItemBase(BaseModel):
    """Base schema for global catalogue items."""

    name: str = Field(..., min_length=1, max_length=255)
    category: GearItemCategory
    weight: float = Field(..., ge=0)
    weightUnit: GearWeightUnit = Field(default="g", alias="weightUnit")
    description: str | None = None
    brand: str | None = Field(None, max_length=255)
    model: str | None = Field(None, max_length=255)
    priceTier: Literal["low", "medium", "high"] | None = Field(None, alias="priceTier")
    quality: GearItemQuality | None = None
    url: str | None = None
    color: str | None = Field(None, max_length=50)

    model_config = {"populate_by_name": True}


class GlobalCatalogueItemCreate(GlobalCatalogueItemBase):
    """Schema for creating a global catalogue item."""

    pass


class GlobalCatalogueItemUpdate(BaseModel):
    """Schema for updating a global catalogue item."""

    name: str | None = Field(None, min_length=1, max_length=255)
    category: GearItemCategory | None = None
    weight: float | None = Field(None, gt=0)
    weightUnit: GearWeightUnit | None = Field(None, alias="weightUnit")
    description: str | None = None
    brand: str | None = Field(None, max_length=255)
    model: str | None = Field(None, max_length=255)
    priceTier: Literal["low", "medium", "high"] | None = Field(None, alias="priceTier")
    quality: GearItemQuality | None = None
    url: str | None = None
    color: str | None = Field(None, max_length=50)
    isActive: bool | None = Field(None, alias="isActive")

    model_config = {"populate_by_name": True}


class GlobalCatalogueItemResponse(GlobalCatalogueItemBase):
    """Schema for global catalogue item response."""

    id: str
    version: int
    isActive: bool = Field(alias="is_active")
    createdBy: str | None = Field(None, alias="created_by")
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")
    primaryImageUrl: str | None = Field(None, alias="primaryImageUrl")

    model_config = {"from_attributes": True, "populate_by_name": True}


class GlobalCatalogueItemSearchParams(BaseModel):
    """Schema for catalogue item search parameters."""

    query: str | None = None
    category: GearItemCategory | None = None
    brand: str | None = None
    priceTier: Literal["low", "medium", "high"] | None = Field(None, alias="priceTier")
    quality: GearItemQuality | None = None
    isActive: bool | None = Field(True, alias="isActive")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

    model_config = {"populate_by_name": True}
