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
GearWeightUnit = Literal["g", "kg"]
ContainerColor = Literal["default", "blue", "green", "red", "yellow", "purple", "orange", "pink", "teal", "indigo"]
GearItemCategory = str  # Allows custom categories: 'water', 'food', 'shelter', etc.


# Container Schemas
class ContainerCreate(BaseModel):
    """Schema for creating a new gear container."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    type: GearContainerType
    color: ContainerColor | None = "default"
    parentContainerId: str | None = Field(None, alias="parentContainerId")
    brand: str | None = Field(None, max_length=255)
    price: float | None = Field(None, ge=0)

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
    url: str | None = None
    brand: str | None = None
    color: str | None = None
    quality: GearItemQuality | None = None
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
    items: list[ItemResponse] = []
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


# Item Schemas
class ItemCreate(BaseModel):
    """Schema for creating a new gear item."""

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
    url: str | None = None
    brand: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    quality: GearItemQuality | None = None

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
    url: str | None = None
    brand: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    quality: GearItemQuality | None = None

    model_config = {"populate_by_name": True}
