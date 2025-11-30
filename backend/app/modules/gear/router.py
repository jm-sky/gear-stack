"""FastAPI router for gear management endpoints.

This module provides REST API endpoints for managing gear containers and items.
All endpoints require authentication.
"""

from typing import Annotated

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUser
from app.modules.auth.models import User
from app.modules.auth.repositories import get_user_repository
from app.modules.auth.types.repository import UserRepositoryInterface
from app.modules.settings.db_models import UserSettingsDB

from .repository import GearRepository
from .schemas import (
    BatchOrderUpdateRequest,
    ContainerCreate,
    ContainerResponse,
    ContainerUpdate,
    ContainerRatingCreate,
    ItemCreate,
    ItemResponse,
    ItemUpdate,
    ShareTokenCreate,
    ShareTokenResponse,
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

# Optional authentication for public endpoints
optional_security = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Security(optional_security),
    user_repository: Annotated[UserRepositoryInterface | None, Depends(get_user_repository)] = None,
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    if credentials is None:
        return None
    try:
        from app.modules.auth.dependencies import _verify_user_token

        token = credentials.credentials
        if user_repository is None:
            return None
        return await _verify_user_token(token, user_repository, None)
    except Exception:
        # If authentication fails, return None (endpoint is public)
        return None


OptionalUser = Annotated[User | None, Depends(get_optional_user)]


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
    "/containers",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all containers",
)
async def delete_all_containers(
    current_user: CurrentUser,
    service: GearServiceDep,
) -> None:
    """Delete all gear containers for the current user.

    Args:
        current_user: Authenticated user
        service: Gear service instance
    """
    await service.delete_all_containers(current_user.id)


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
    current_user: OptionalUser = None,
) -> list[ContainerResponse]:
    """Get all public containers from all users.

    Args:
        service: Gear service instance
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Optional authenticated user (for user rating data)

    Returns:
        List of public containers with author names
    """
    requesting_user_id = current_user.id if current_user else None
    return await service.get_public_containers(skip, limit, requesting_user_id)


@router.get(
    "/public/containers/{container_id}",
    response_model=ContainerResponse,
    summary="Get a public container by ID",
)
async def get_public_container(
    container_id: str,
    service: GearServiceDep,
    current_user: OptionalUser = None,
) -> ContainerResponse:
    """Get a public container by ID.

    Args:
        container_id: Container ID
        service: Gear service instance
        current_user: Optional authenticated user (for user rating data)

    Returns:
        Public container with author name

    Raises:
        HTTPException: If container not found or not public
    """
    requesting_user_id = current_user.id if current_user else None
    container = await service.get_public_container(container_id, requesting_user_id)
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


# Share token management endpoints (requires authentication)
@router.get(
    "/containers/{container_id}/share-tokens",
    response_model=list[ShareTokenResponse],
    summary="Get share tokens for a container",
)
async def get_container_share_tokens(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> list[ShareTokenResponse]:
    """Get all share tokens for a container.

    Args:
        container_id: Container ID
        current_user: Current authenticated user
        service: Gear service instance

    Returns:
        List of share tokens for the container

    Raises:
        HTTPException: If container not found or user doesn't own it
    """
    tokens = await service.get_share_tokens(container_id, current_user.id)
    return [ShareTokenResponse(**token) for token in tokens]


@router.post(
    "/containers/{container_id}/share-tokens",
    response_model=ShareTokenResponse,
    summary="Create a share token for a container",
)
async def create_container_share_token(
    container_id: str,
    current_user: CurrentUser,
    data: ShareTokenCreate,
    service: GearServiceDep,
) -> ShareTokenResponse:
    """Create a share token for a container.

    Args:
        container_id: Container ID
        current_user: Current authenticated user
        data: Share token creation data
        service: Gear service instance

    Returns:
        Created share token with share URL

    Raises:
        HTTPException: If container not found or user doesn't own it
    """
    token = await service.create_share_token(container_id, current_user.id, data.expiresAt)
    tokens = await service.get_share_tokens(container_id, current_user.id)
    # Find the newly created token
    token_data = next((t for t in tokens if t["token"] == token), None)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created token",
        )
    return ShareTokenResponse(**token_data)


@router.delete(
    "/containers/{container_id}/share-tokens/{token}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a share token",
)
async def revoke_container_share_token(
    container_id: str,
    token: str,
    current_user: CurrentUser,
    service: GearServiceDep,
) -> None:
    """Revoke a share token.

    Args:
        container_id: Container ID
        token: Share token to revoke
        current_user: Current authenticated user
        service: Gear service instance

    Raises:
        HTTPException: If token not found or user doesn't own it
    """
    revoked = await service.revoke_share_token(token, current_user.id)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share token not found or access denied",
        )


# Rating endpoints
@router.post("/containers/{container_id}/rating", response_model=dict, summary="Rate a container")
async def rate_container(
    container_id: str,
    rating_data: ContainerRatingCreate,
    current_user: CurrentUser,
    service: GearServiceDep,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Rate a container (create or update rating).

    Supports two rating types:
    - 'owner': Rating by container owner (only if current_user is owner)
    - 'user': Rating by other users (only for public containers)
    """
    repository = GearRepository(db)

    # Verify container exists
    container = await repository.get_container(container_id, current_user.id)
    if not container:
        # Try public container
        container = await repository.get_public_container(container_id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")

    # Validate rating type
    is_owner = container.user_id == current_user.id

    if rating_data.ratingType == "owner" and not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only container owner can set owner rating")

    if rating_data.ratingType == "user" and is_owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Container owner should use 'owner' rating type")

    if rating_data.ratingType == "user" and not container.is_public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User ratings are only allowed for public containers")

    # Upsert rating
    rating = await repository.upsert_container_rating(container_id=container_id, user_id=current_user.id, rating=rating_data.rating, rating_type=rating_data.ratingType)
    await db.commit()

    # Get updated stats
    if rating_data.ratingType == "owner":
        owner_rating: int | None = rating.rating
        avg_user_rating = await repository.get_container_average_user_rating(container_id)
        user_rating_count = await repository.get_container_user_rating_count(container_id)
    else:
        owner_rating = await repository.get_container_owner_rating(container_id)
        avg_user_rating = await repository.get_container_average_user_rating(container_id)
        user_rating_count = await repository.get_container_user_rating_count(container_id)

    return {"rating": rating.rating, "ratingType": rating.rating_type, "ownerRating": owner_rating, "averageUserRating": float(avg_user_rating) if avg_user_rating else None, "userRatingCount": user_rating_count}


@router.delete("/containers/{container_id}/rating", summary="Delete container rating")
async def delete_container_rating(
    container_id: str,
    current_user: CurrentUser,
    service: GearServiceDep,
    rating_type: str = Query(default="user", description="Type of rating to delete: 'owner' or 'user'"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete user's rating for a container."""
    repository = GearRepository(db)

    # Verify container exists
    container = await repository.get_container(container_id, current_user.id)
    if not container:
        container = await repository.get_public_container(container_id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")

    # Validate rating type
    is_owner = container.user_id == current_user.id

    if rating_type == "owner" and not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only container owner can delete owner rating")

    # Delete rating
    deleted = await repository.delete_container_rating(container_id, current_user.id, rating_type)
    await db.commit()

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")

    # Get updated stats
    owner_rating = await repository.get_container_owner_rating(container_id)
    avg_user_rating = await repository.get_container_average_user_rating(container_id)
    user_rating_count = await repository.get_container_user_rating_count(container_id)

    return {"message": "Rating deleted", "ownerRating": owner_rating, "averageUserRating": float(avg_user_rating) if avg_user_rating else None, "userRatingCount": user_rating_count}
