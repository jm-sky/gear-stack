"""FastAPI router for gear management endpoints.

This module provides REST API endpoints for managing gear containers and items.
All endpoints require authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUser
from app.modules.settings.db_models import UserSettingsDB

from .repository import GearRepository
from .schemas import (
    BatchOrderUpdateRequest,
    ContainerCreate,
    ContainerResponse,
    ContainerUpdate,
    ItemCreate,
    ItemResponse,
    ItemUpdate,
)
from .service import GearService
from .item_image_router import router as item_image_router

router = APIRouter(prefix="/gear", tags=["gear"])

# Include item images router
router.include_router(item_image_router)


def get_gear_repository(db: AsyncSession = Depends(get_db)) -> GearRepository:
    """Dependency to get gear repository instance.

    Args:
        db: Database session

    Returns:
        Gear repository instance
    """
    return GearRepository(db)


def get_gear_service(
    repository: GearRepository = Depends(get_gear_repository),
) -> GearService:
    """Dependency to get gear service instance.

    Args:
        repository: Gear repository instance

    Returns:
        Gear service instance
    """
    return GearService(repository)


GearServiceDep = Annotated[GearService, Depends(get_gear_service)]


# Container endpoints
@router.post(
    "/containers",
    response_model=ContainerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new gear container",
)
async def create_container(
    data: ContainerCreate,
    current_user: CurrentUser,
    service: GearServiceDep,
    db: AsyncSession = Depends(get_db),
) -> ContainerResponse:
    """Create a new gear container for the current user.

    Args:
        data: Container creation data
        current_user: Authenticated user
        service: Gear service instance
        db: Database session

    Returns:
        Created container

    Raises:
        HTTPException: If validation fails
    """
    # Get user settings for default public setting
    result = await db.execute(select(UserSettingsDB).where(UserSettingsDB.user_id == current_user.id))
    settings = result.scalars().first()
    default_public = settings.default_containers_public if settings else False

    return await service.create_container(current_user.id, data, default_public=default_public)


@router.get(
    "/containers",
    response_model=list[ContainerResponse],
    summary="Get all containers for the current user",
)
async def get_containers(
    current_user: CurrentUser,
    service: GearServiceDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
) -> list[ContainerResponse]:
    """Get all gear containers for the current user.

    Args:
        current_user: Authenticated user
        service: Gear service instance
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of containers
    """
    return await service.get_containers(current_user.id, skip, limit)


@router.get(
    "/containers/{container_id}",
    response_model=ContainerResponse,
    summary="Get a container by ID",
)
async def get_container(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ContainerResponse:
    """Get a gear container by ID.

    Args:
        container_id: Container ID
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Container

    Raises:
        HTTPException: If container not found
    """
    container = await service.get_container(container_id, current_user.id)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )
    return container


@router.patch(
    "/containers/{container_id}",
    response_model=ContainerResponse,
    summary="Update a container",
)
async def update_container(
    container_id: str,
    data: ContainerUpdate,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ContainerResponse:
    """Update a gear container.

    Args:
        container_id: Container ID
        data: Update data
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Updated container

    Raises:
        HTTPException: If container not found
    """
    container = await service.update_container(container_id, current_user.id, data)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )
    return container


@router.delete(
    "/containers/{container_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a container",
)
async def delete_container(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> None:
    """Delete a gear container and all its items.

    Args:
        container_id: Container ID
        current_user: Authenticated user
        service: Gear service instance

    Raises:
        HTTPException: If container not found
    """
    deleted = await service.delete_container(container_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )


# Item endpoints
@router.post(
    "/containers/{container_id}/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item in a container",
)
async def create_item(
    container_id: str,
    data: ItemCreate,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ItemResponse:
    """Create a new gear item in a container.

    Args:
        container_id: Parent container ID
        data: Item creation data
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Created item

    Raises:
        HTTPException: If container not found or validation fails
    """
    item = await service.create_item(container_id, current_user.id, data)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )
    return item


@router.get(
    "/containers/{container_id}/items",
    response_model=list[ItemResponse],
    summary="Get all items in a container",
)
async def get_items(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
) -> list[ItemResponse]:
    """Get all items in a container.

    Args:
        container_id: Parent container ID
        current_user: Authenticated user
        service: Gear service instance
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of items
    """
    return await service.get_items(container_id, current_user.id, skip, limit)


@router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    summary="Get an item by ID",
)
async def get_item(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ItemResponse:
    """Get a gear item by ID.

    Args:
        item_id: Item ID
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Item

    Raises:
        HTTPException: If item not found
    """
    item = await service.get_item(item_id, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    return item


@router.patch(
    "/items/{item_id}",
    response_model=ItemResponse,
    summary="Update an item",
)
async def update_item(
    item_id: str,
    data: ItemUpdate,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> ItemResponse:
    """Update a gear item.

    Args:
        item_id: Item ID
        data: Update data
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Updated item

    Raises:
        HTTPException: If item not found
    """
    item = await service.update_item(item_id, current_user.id, data)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    return item


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
)
async def delete_item(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> None:
    """Delete a gear item.

    Args:
        item_id: Item ID
        current_user: Authenticated user
        service: Gear service instance

    Raises:
        HTTPException: If item not found
    """
    deleted = await service.delete_item(item_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )


@router.patch(
    "/items/batch-order",
    response_model=list[ItemResponse],
    summary="Batch update items order",
)
async def batch_update_item_order(
    data: BatchOrderUpdateRequest,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> list[ItemResponse]:
    """Batch update items' order values.

    Args:
        data: Batch order update request with list of item IDs and their new order values
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        List of updated item responses

    Raises:
        HTTPException: If validation fails or items not found
    """
    try:
        return await service.batch_update_item_order(current_user.id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# Statistics endpoints
@router.get(
    "/containers/{container_id}/stats/weight",
    summary="Calculate container weight",
)
async def get_container_weight(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> dict[str, float]:
    """Calculate total weight of a container.

    Args:
        container_id: Container ID
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Dictionary with weight in grams and kilograms

    Raises:
        HTTPException: If container not found
    """
    container = await service.get_container(container_id, current_user.id)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )
    return service.calculate_container_weight(container)


@router.get(
    "/containers/{container_id}/stats/readiness",
    summary="Calculate container readiness",
)
async def get_container_readiness(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> dict[str, int | float]:
    """Calculate container readiness statistics.

    Args:
        container_id: Container ID
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Dictionary with readiness statistics

    Raises:
        HTTPException: If container not found
    """
    container = await service.get_container(container_id, current_user.id)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found",
        )
    return service.calculate_container_readiness(container)


# Public container endpoints (no authentication required)
@router.get(
    "/public/containers",
    response_model=list[ContainerResponse],
    summary="Get all public containers",
)
async def get_public_containers(
    service: GearServiceDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
) -> list[ContainerResponse]:
    """Get all public containers from all users.

    Args:
        service: Gear service instance
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of public containers with author names
    """
    return await service.get_public_containers(skip, limit)


@router.get(
    "/public/containers/{container_id}",
    response_model=ContainerResponse,
    summary="Get a public container by ID",
)
async def get_public_container(
    container_id: str,
    service: GearServiceDep,
) -> ContainerResponse:
    """Get a public container by ID.

    Args:
        container_id: Container ID
        service: Gear service instance

    Returns:
        Public container with author name

    Raises:
        HTTPException: If container not found or not public
    """
    container = await service.get_public_container(container_id)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public container not found",
        )
    return container


# Shared container endpoints (no authentication required, token-based access)
@router.get(
    "/shared/containers/{token}",
    response_model=ContainerResponse,
    summary="Get a shared container by token",
)
async def get_shared_container(
    token: str,
    service: GearServiceDep,
) -> ContainerResponse:
    """Get a container by share token.

    Args:
        token: Share token
        service: Gear service instance

    Returns:
        Shared container with author name

    Raises:
        HTTPException: If token is invalid, expired, or container not found
    """
    container = await service.get_container_by_share_token(token)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared container not found or token expired",
        )
    return container
