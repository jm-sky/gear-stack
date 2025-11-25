"""FastAPI router for admin endpoints.

This module provides admin-only endpoints for managing users, containers, and items.
All endpoints require admin authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.repositories import (
    UserRepository as AuthUserRepository,
    get_user_repository as get_auth_user_repository,
)
from app.modules.users.dependencies import AdminUser
from app.modules.users.repositories import UserRepository, get_user_repository
from app.modules.users.schemas import UserUpdate

from .repository import AdminRepository
from .schemas import AdminUserResponse, AdminContainerResponse, AdminItemResponse
from .service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


def get_admin_repository(db: AsyncSession = Depends(get_db)) -> AdminRepository:
    """Dependency to get admin repository instance."""
    return AdminRepository(db)


def get_admin_service(
    repository: AdminRepository = Depends(get_admin_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    auth_user_repository: AuthUserRepository = Depends(get_auth_user_repository),
) -> AdminService:
    """Dependency to get admin service instance."""
    return AdminService(repository, user_repository, auth_user_repository)


# Users endpoints
@router.get(
    "/users",
    response_model=list[AdminUserResponse],
    summary="Get all users (admin only)",
    description="Get list of all users with pagination",
)
async def get_all_users(
    _: AdminUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
) -> list[AdminUserResponse]:
    """Get all users (admin only)."""
    return await service.get_all_users(skip=skip, limit=limit)


@router.get(
    "/users/{user_id}",
    response_model=AdminUserResponse,
    summary="Get user by ID (admin only)",
    description="Get a specific user by their ID",
)
async def get_user_by_id(
    user_id: str,
    _: AdminUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> AdminUserResponse:
    """Get user by ID (admin only)."""
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    return user


@router.patch(
    "/users/{user_id}",
    response_model=AdminUserResponse,
    summary="Update user (admin only)",
    description="Update user information",
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    _: AdminUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> AdminUserResponse:
    """Update user (admin only)."""
    user = await service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    return user


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user (admin only)",
    description="Delete a user (soft delete - sets isActive to false)",
)
async def delete_user(
    user_id: str,
    _: AdminUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> None:
    """Delete user (admin only)."""
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")


# Containers endpoints
@router.get(
    "/containers",
    response_model=list[AdminContainerResponse],
    summary="Get all containers (admin only)",
    description="Get list of all containers from all users",
)
async def get_all_containers(
    _: AdminUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
) -> list[AdminContainerResponse]:
    """Get all containers (admin only)."""
    return await service.get_all_containers(skip=skip, limit=limit)


@router.get(
    "/containers/{container_id}",
    response_model=AdminContainerResponse,
    summary="Get container by ID (admin only)",
    description="Get a specific container by its ID",
)
async def get_container_by_id(
    container_id: str,
    _: AdminUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> AdminContainerResponse:
    """Get container by ID (admin only)."""
    container = await service.get_container_by_id(container_id)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found",
        )
    return container


@router.delete(
    "/containers/{container_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete container (admin only)",
    description="Delete a container and all its items",
)
async def delete_container(
    container_id: str,
    _: AdminUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> None:
    """Delete container (admin only)."""
    success = await service.delete_container(container_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found",
        )


# Items endpoints
@router.get(
    "/items",
    response_model=list[AdminItemResponse],
    summary="Get all items (admin only)",
    description="Get list of all items from all containers",
)
async def get_all_items(
    _: AdminUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
) -> list[AdminItemResponse]:
    """Get all items (admin only)."""
    return await service.get_all_items(skip=skip, limit=limit)


@router.get(
    "/items/{item_id}",
    response_model=AdminItemResponse,
    summary="Get item by ID (admin only)",
    description="Get a specific item by its ID",
)
async def get_item_by_id(
    item_id: str,
    _: AdminUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> AdminItemResponse:
    """Get item by ID (admin only)."""
    item = await service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )
    return item


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item (admin only)",
    description="Delete an item",
)
async def delete_item(
    item_id: str,
    _: AdminUser,
    service: Annotated[AdminService, Depends(get_admin_service)],
) -> None:
    """Delete item (admin only)."""
    success = await service.delete_item(item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )
