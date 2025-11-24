"""FastAPI router for admin endpoints.

This module provides admin-only endpoints for managing users, containers, and items.
All endpoints require admin authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.core.database import get_db
from app.modules.auth.db_models import UserDB
from app.modules.auth.repositories import UserRepository as AuthUserRepository, get_user_repository as get_auth_user_repository
from app.modules.gear.db_models import GearContainerDB, GearItemDB
from app.modules.gear.schemas import ContainerResponse, ItemResponse
from app.modules.gear.service import GearService
from app.modules.gear.repository import GearRepository
from app.modules.users.dependencies import AdminUser
from app.modules.users.repositories import UserRepository, get_user_repository
from app.modules.users.schemas import UserUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


def get_gear_repository(db: AsyncSession = Depends(get_db)) -> GearRepository:
    """Dependency to get gear repository instance."""
    return GearRepository(db)


def get_gear_service(
    repository: GearRepository = Depends(get_gear_repository),
) -> GearService:
    """Dependency to get gear service instance."""
    return GearService(repository)


# Users endpoints
@router.get(
    "/users",
    summary="Get all users (admin only)",
    description="Get list of all users with pagination",
)
async def get_all_users(
    _: AdminUser,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    auth_repo: Annotated[AuthUserRepository, Depends(get_auth_user_repository)],
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
) -> list[dict]:
    """Get all users (admin only)."""
    users = await repo.get_all_users(skip=skip, limit=limit, include_inactive=True)
    result = []
    for user in users:
        auth_user = await auth_repo.get_user_by_id(user.id)
        email_verified_at = auth_user.emailVerifiedAt if auth_user else None
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatarUrl": user.avatarUrl,
            "isActive": user.isActive,
            "isAdmin": user.role == "admin",
            "isEmailVerified": user.isEmailVerified,
            "emailVerifiedAt": email_verified_at.isoformat() if email_verified_at and hasattr(email_verified_at, "isoformat") else (str(email_verified_at) if email_verified_at else None),
            "createdAt": user.createdAt.isoformat() if hasattr(user.createdAt, "isoformat") else str(user.createdAt),
            "updatedAt": user.updatedAt.isoformat() if hasattr(user.updatedAt, "isoformat") else str(user.updatedAt),
        })
    return result


@router.get(
    "/users/{user_id}",
    summary="Get user by ID (admin only)",
    description="Get a specific user by their ID",
)
async def get_user_by_id(
    user_id: str,
    _: AdminUser,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    auth_repo: Annotated[AuthUserRepository, Depends(get_auth_user_repository)],
) -> dict:
    """Get user by ID (admin only)."""
    user = await repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    auth_user = await auth_repo.get_user_by_id(user_id)
    email_verified_at = auth_user.emailVerifiedAt if auth_user else None
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "avatarUrl": user.avatarUrl,
        "isActive": user.isActive,
        "isAdmin": user.role == "admin",
        "isEmailVerified": user.isEmailVerified,
        "emailVerifiedAt": email_verified_at.isoformat() if email_verified_at and hasattr(email_verified_at, "isoformat") else (str(email_verified_at) if email_verified_at else None),
        "createdAt": user.createdAt.isoformat() if hasattr(user.createdAt, "isoformat") else str(user.createdAt),
        "updatedAt": user.updatedAt.isoformat() if hasattr(user.updatedAt, "isoformat") else str(user.updatedAt),
    }


@router.patch(
    "/users/{user_id}",
    summary="Update user (admin only)",
    description="Update user information",
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    _: AdminUser,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    auth_repo: Annotated[AuthUserRepository, Depends(get_auth_user_repository)],
) -> dict:
    """Update user (admin only)."""
    # Map UserUpdate schema to repository method parameters
    update_kwargs = {}
    if user_data.email is not None:
        update_kwargs["email"] = user_data.email
    if user_data.name is not None:
        update_kwargs["name"] = user_data.name
    if user_data.isActive is not None:
        update_kwargs["is_active"] = user_data.isActive
    if user_data.role is not None:
        update_kwargs["role"] = user_data.role

    user = await repo.update_user(user_id, **update_kwargs)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    
    # Get auth user to check emailVerifiedAt
    auth_user = await auth_repo.get_user_by_id(user_id)
    email_verified_at = auth_user.emailVerifiedAt if auth_user else None
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "avatarUrl": user.avatarUrl,
        "isActive": user.isActive,
        "isAdmin": user.role == "admin",
        "isEmailVerified": user.isEmailVerified,
        "emailVerifiedAt": email_verified_at.isoformat() if email_verified_at and hasattr(email_verified_at, "isoformat") else (str(email_verified_at) if email_verified_at else None),
        "createdAt": user.createdAt.isoformat() if hasattr(user.createdAt, "isoformat") else str(user.createdAt),
        "updatedAt": user.updatedAt.isoformat() if hasattr(user.updatedAt, "isoformat") else str(user.updatedAt),
    }


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user (admin only)",
    description="Delete a user (soft delete - sets isActive to false)",
)
async def delete_user(
    user_id: str,
    _: AdminUser,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> None:
    """Delete user (admin only)."""
    success = await repo.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")


# Containers endpoints
@router.get(
    "/containers",
    response_model=list[dict],
    summary="Get all containers (admin only)",
    description="Get list of all containers from all users",
)
async def get_all_containers(
    _: AdminUser,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
) -> list[dict]:
    """Get all containers (admin only)."""
    # Get containers with user relationship and item count
    stmt = (
        select(GearContainerDB, func.count(GearItemDB.id).label("item_count"))
        .outerjoin(GearItemDB, GearContainerDB.id == GearItemDB.container_id)
        .options(joinedload(GearContainerDB.user))
        .group_by(GearContainerDB.id)
        .offset(skip)
        .limit(limit)
        .order_by(GearContainerDB.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.unique().all()

    containers = []
    for container_db, item_count in rows:
        author_name = container_db.user.name if container_db.user else None
        author_id = container_db.user.id if container_db.user else None

        containers.append({
            "id": container_db.id,
            "name": container_db.name,
            "description": container_db.description,
            "type": container_db.type,
            "color": container_db.color,
            "isPublic": container_db.is_public,
            "authorId": author_id,
            "authorName": author_name,
            "itemCount": item_count or 0,
            "createdAt": container_db.created_at.isoformat(),
            "updatedAt": container_db.updated_at.isoformat(),
        })

    return containers


@router.get(
    "/containers/{container_id}",
    response_model=dict,
    summary="Get container by ID (admin only)",
    description="Get a specific container by its ID",
)
async def get_container_by_id(
    container_id: str,
    _: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get container by ID (admin only)."""
    stmt = (
        select(GearContainerDB)
        .where(GearContainerDB.id == container_id)
        .options(selectinload(GearContainerDB.items), joinedload(GearContainerDB.user))
    )
    result = await db.execute(stmt)
    container_db = result.unique().scalar_one_or_none()

    if not container_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found",
        )

    author_name = container_db.user.name if container_db.user else None
    author_id = container_db.user.id if container_db.user else None

    return {
        "id": container_db.id,
        "name": container_db.name,
        "description": container_db.description,
        "type": container_db.type,
        "color": container_db.color,
        "isPublic": container_db.is_public,
        "authorId": author_id,
        "authorName": author_name,
        "itemCount": len(container_db.items),
        "createdAt": container_db.created_at.isoformat(),
        "updatedAt": container_db.updated_at.isoformat(),
    }


@router.delete(
    "/containers/{container_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete container (admin only)",
    description="Delete a container and all its items",
)
async def delete_container(
    container_id: str,
    _: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete container (admin only)."""
    stmt = select(GearContainerDB).where(GearContainerDB.id == container_id)
    result = await db.execute(stmt)
    container_db = result.scalar_one_or_none()

    if not container_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found",
        )

    await db.delete(container_db)
    await db.commit()


# Items endpoints
@router.get(
    "/items",
    response_model=list[dict],
    summary="Get all items (admin only)",
    description="Get list of all items from all containers",
)
async def get_all_items(
    _: AdminUser,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
) -> list[dict]:
    """Get all items (admin only)."""
    # Get items with container and user relationships
    stmt = (
        select(GearItemDB, GearContainerDB, UserDB)
        .join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id)
        .join(UserDB, GearContainerDB.user_id == UserDB.id)
        .offset(skip)
        .limit(limit)
        .order_by(GearItemDB.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for item_db, container_db, user_db in rows:
        items.append({
            "id": item_db.id,
            "name": item_db.name,
            "category": item_db.category,
            "quantity": item_db.quantity,
            "weight": item_db.weight,
            "weightUnit": item_db.weight_unit,
            "status": item_db.status,
            "priority": item_db.priority,
            "containerId": item_db.container_id,
            "containerName": container_db.name,
            "authorId": user_db.id,
            "authorName": user_db.name,
            "createdAt": item_db.created_at.isoformat(),
            "updatedAt": item_db.updated_at.isoformat(),
        })

    return items


@router.get(
    "/items/{item_id}",
    response_model=dict,
    summary="Get item by ID (admin only)",
    description="Get a specific item by its ID",
)
async def get_item_by_id(
    item_id: str,
    _: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get item by ID (admin only)."""
    stmt = (
        select(GearItemDB, GearContainerDB, UserDB)
        .join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id)
        .join(UserDB, GearContainerDB.user_id == UserDB.id)
        .where(GearItemDB.id == item_id)
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )

    item_db, container_db, user_db = row

    return {
        "id": item_db.id,
        "name": item_db.name,
        "category": item_db.category,
        "quantity": item_db.quantity,
        "weight": item_db.weight,
        "weightUnit": item_db.weight_unit,
        "status": item_db.status,
        "priority": item_db.priority,
        "containerId": item_db.container_id,
        "containerName": container_db.name,
        "authorId": user_db.id,
        "authorName": user_db.name,
        "createdAt": item_db.created_at.isoformat(),
        "updatedAt": item_db.updated_at.isoformat(),
    }


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item (admin only)",
    description="Delete an item",
)
async def delete_item(
    item_id: str,
    _: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete item (admin only)."""
    stmt = select(GearItemDB).where(GearItemDB.id == item_id)
    result = await db.execute(stmt)
    item_db = result.scalar_one_or_none()

    if not item_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )

    await db.delete(item_db)
    await db.commit()
