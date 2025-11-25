"""Business logic service for admin operations.

This module contains business logic for admin-level operations,
including user, container, and item management across the platform.
"""

import logging

from app.modules.auth.repositories import UserRepository as AuthUserRepository
from app.modules.users.repositories import UserRepository
from app.modules.users.schemas import UserUpdate

from .repository import AdminRepository
from .schemas import AdminUserResponse, AdminContainerResponse, AdminItemResponse

logger = logging.getLogger(__name__)


class AdminService:
    """Service for admin-level business logic.

    Handles admin operations with business logic, validation,
    and coordination between repositories.
    """

    def __init__(
        self,
        repository: AdminRepository,
        user_repository: UserRepository,
        auth_user_repository: AuthUserRepository,
    ):
        """Initialize service with repositories.

        Args:
            repository: Admin repository instance
            user_repository: User repository instance
            auth_user_repository: Auth user repository instance
        """
        self.repository = repository
        self.user_repository = user_repository
        self.auth_user_repository = auth_user_repository

    def _serialize_datetime(self, dt: object) -> str | None:
        """Serialize datetime to ISO format string.

        Args:
            dt: Datetime object or string

        Returns:
            ISO format datetime string or None
        """
        if dt is None:
            return None
        if hasattr(dt, "isoformat"):
            return str(dt.isoformat())
        return str(dt)

    # User operations
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[AdminUserResponse]:
        """Get all users with admin metadata.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of admin user responses
        """
        users_with_auth = await self.repository.get_all_users(skip=skip, limit=limit)

        result = []
        for user, _ in users_with_auth:
            result.append(
                AdminUserResponse(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    avatarUrl=user.avatar_url,
                    isActive=user.is_active,
                    isAdmin=user.is_admin,
                    isEmailVerified=user.is_email_verified,
                    emailVerifiedAt=self._serialize_datetime(user.email_verified_at) or "",
                    createdAt=self._serialize_datetime(user.created_at) or "",
                    updatedAt=self._serialize_datetime(user.created_at) or "",  # UserDB doesn't have updated_at
                )
            )

        return result

    async def get_user_by_id(self, user_id: str) -> AdminUserResponse | None:
        """Get user by ID with admin metadata.

        Args:
            user_id: User ID

        Returns:
            Admin user response or None if not found
        """
        user, _ = await self.repository.get_user_by_id(user_id)

        if not user:
            return None

        return AdminUserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            avatarUrl=user.avatar_url,
            isActive=user.is_active,
            isAdmin=user.is_admin,
            isEmailVerified=user.is_email_verified,
            emailVerifiedAt=self._serialize_datetime(user.email_verified_at) or "",
            createdAt=self._serialize_datetime(user.created_at) or "",
            updatedAt=self._serialize_datetime(user.created_at) or "",  # UserDB doesn't have updated_at
        )

    async def update_user(self, user_id: str, user_data: UserUpdate) -> AdminUserResponse | None:
        """Update user information.

        Args:
            user_id: User ID
            user_data: User update data

        Returns:
            Updated admin user response or None if not found
        """
        # Update user via repository
        user_model = await self.user_repository.update_user(
            user_id=user_id,
            email=user_data.email,
            name=user_data.name,
            is_active=user_data.isActive,
            role=user_data.role,
        )
        if not user_model:
            return None

        # Fetch updated user from database
        updated_user, _ = await self.repository.get_user_by_id(user_id)
        if not updated_user:
            return None

        return AdminUserResponse(
            id=updated_user.id,
            name=updated_user.name,
            email=updated_user.email,
            avatarUrl=updated_user.avatar_url,
            isActive=updated_user.is_active,
            isAdmin=updated_user.is_admin,
            isEmailVerified=updated_user.is_email_verified,
            emailVerifiedAt=self._serialize_datetime(updated_user.email_verified_at) or "",
            createdAt=self._serialize_datetime(updated_user.created_at) or "",
            updatedAt=self._serialize_datetime(updated_user.created_at) or "",  # UserDB doesn't have updated_at
        )

    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete).

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        return await self.user_repository.delete_user(user_id)

    # Container operations
    async def get_all_containers(self, skip: int = 0, limit: int = 100) -> list[AdminContainerResponse]:
        """Get all containers with metadata.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of admin container responses
        """
        containers_with_counts = await self.repository.get_all_containers(skip=skip, limit=limit)

        result = []
        for container_db, item_count in containers_with_counts:
            author_name = container_db.user.name if hasattr(container_db, "user") and container_db.user else None
            author_id = container_db.user.id if hasattr(container_db, "user") and container_db.user else None

            result.append(
                AdminContainerResponse(
                    id=container_db.id,
                    name=container_db.name,
                    description=container_db.description,
                    type=container_db.type,
                    color=container_db.color,
                    isPublic=container_db.is_public,
                    authorId=author_id,
                    authorName=author_name,
                    itemCount=item_count or 0,
                    createdAt=container_db.created_at.isoformat(),
                    updatedAt=container_db.updated_at.isoformat(),
                )
            )

        return result

    async def get_container_by_id(self, container_id: str) -> AdminContainerResponse | None:
        """Get container by ID with metadata.

        Args:
            container_id: Container ID

        Returns:
            Admin container response or None if not found
        """
        container_db = await self.repository.get_container_by_id(container_id)

        if not container_db:
            return None

        author_name = container_db.user.name if hasattr(container_db, "user") and container_db.user else None
        author_id = container_db.user.id if hasattr(container_db, "user") and container_db.user else None
        items_count = len(container_db.items) if hasattr(container_db, "items") else 0

        return AdminContainerResponse(
            id=container_db.id,
            name=container_db.name,
            description=container_db.description,
            type=container_db.type,
            color=container_db.color,
            isPublic=container_db.is_public,
            authorId=author_id,
            authorName=author_name,
            itemCount=items_count,
            createdAt=container_db.created_at.isoformat(),
            updatedAt=container_db.updated_at.isoformat(),
        )

    async def delete_container(self, container_id: str) -> bool:
        """Delete container and all its items.

        Args:
            container_id: Container ID

        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete_container(container_id)

    # Item operations
    async def get_all_items(self, skip: int = 0, limit: int = 100) -> list[AdminItemResponse]:
        """Get all items with metadata.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of admin item responses
        """
        items_with_metadata = await self.repository.get_all_items(skip=skip, limit=limit)

        result = []
        for item_db, container_db, user_db in items_with_metadata:
            result.append(
                AdminItemResponse(
                    id=item_db.id,
                    name=item_db.name,
                    category=item_db.category,
                    quantity=item_db.quantity,
                    weight=item_db.weight,
                    weightUnit=item_db.weight_unit,
                    status=item_db.status,
                    priority=item_db.priority,
                    containerId=item_db.container_id,
                    containerName=container_db.name,
                    authorId=user_db.id,
                    authorName=user_db.name,
                    createdAt=item_db.created_at.isoformat(),
                    updatedAt=item_db.updated_at.isoformat(),
                )
            )

        return result

    async def get_item_by_id(self, item_id: str) -> AdminItemResponse | None:
        """Get item by ID with metadata.

        Args:
            item_id: Item ID

        Returns:
            Admin item response or None if not found
        """
        item_db, container_db, user_db = await self.repository.get_item_by_id(item_id)

        if not item_db:
            return None

        return AdminItemResponse(
            id=item_db.id,
            name=item_db.name,
            category=item_db.category,
            quantity=item_db.quantity,
            weight=item_db.weight,
            weightUnit=item_db.weight_unit,
            status=item_db.status,
            priority=item_db.priority,
            containerId=item_db.container_id,
            containerName=container_db.name if container_db else "",
            authorId=user_db.id if user_db else "",
            authorName=user_db.name if user_db else "",
            createdAt=item_db.created_at.isoformat(),
            updatedAt=item_db.updated_at.isoformat(),
        )

    async def delete_item(self, item_id: str) -> bool:
        """Delete item.

        Args:
            item_id: Item ID

        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete_item(item_id)
