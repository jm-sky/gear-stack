"""Pydantic schemas for user management endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.common.pagination import PaginatedResponse


class UserCreate(BaseModel):
    """User creation request schema with camelCase."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="user", pattern="^(user|admin|moderator)$")


class UserUpdate(BaseModel):
    """User update request schema with camelCase."""

    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, pattern="^(user|admin|moderator)$")
    isActive: Optional[bool] = None


class UserProfileUpdate(BaseModel):
    """Current user profile update schema."""

    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserResponse(BaseModel):
    """User response schema with camelCase."""

    id: str
    email: EmailStr
    name: str
    role: str
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class UserListResponse(PaginatedResponse[UserResponse]):
    """User list response with pagination metadata.

    Uses generic PaginatedResponse with consistent pagination fields:
    - data: list of users
    - total: total count
    - page: current page (0-based)
    - limit: items per page
    - hasMore: whether more pages exist
    """

    pass


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
