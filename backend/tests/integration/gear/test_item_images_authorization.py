"""Integration tests for item-image authorization (IDOR fix).

Covers docs/issues/2026-07-21--035--item-image-idor.md: item image endpoints
must enforce that the target item/image belongs to the caller, and the
unauthenticated read endpoint must only expose images for public containers.
"""

from datetime import UTC, datetime

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.auth_utils import get_password_hash
from app.modules.auth.db_models import UserDB
from app.modules.gear.image_upload_service import ImageUploadService
from app.modules.gear.item_image_repository import ItemImageRepository
from app.modules.gear.repository import GearRepository
from app.modules.gear.schemas import ContainerCreate, ItemCreate
from app.modules.gear.service import GearService

from .conftest import create_test_container, create_test_item


@pytest_asyncio.fixture
async def user_a(async_db_session: AsyncSession) -> UserDB:
    user = UserDB(
        id="user-a-id",
        email="user-a@example.com",
        name="User A",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_email_verified=True,
        is_premium=True,
        created_at=datetime.now(UTC),
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def user_b(async_db_session: AsyncSession) -> UserDB:
    user = UserDB(
        id="user-b-id",
        email="user-b@example.com",
        name="User B",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_email_verified=True,
        is_premium=True,
        created_at=datetime.now(UTC),
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user


async def _make_image(repository: ItemImageRepository, item_id: str, user_id: str, order: int = 0):
    return await repository.create(
        {
            "item_id": item_id,
            "user_id": user_id,
            "storage_type": "local",
            "file_path": f"items/{item_id}/test.jpg",
            "file_name": "test.jpg",
            "file_size": 100,
            "mime_type": "image/jpeg",
            "width": 10,
            "height": 10,
            "is_primary": False,
            "order": order,
            "is_processed": False,
            "original_file_size": None,
        }
    )


@pytest.mark.asyncio
async def test_delete_image_cross_user_returns_false(async_db_session: AsyncSession, user_a: UserDB, user_b: UserDB) -> None:
    gear_repository = GearRepository(async_db_session)
    gear_service = GearService(gear_repository)
    image_repository = ItemImageRepository(async_db_session)
    image_service = ImageUploadService(async_db_session)

    container_b = await create_test_container(gear_service, user_b.id)
    item_b = await create_test_item(gear_service, user_b.id, container_b["id"])
    image_b = await _make_image(image_repository, item_b["id"], user_b.id)

    # User A cannot delete User B's image.
    deleted = await image_service.delete_image(image_b.id, user_a.id)
    assert deleted is False

    # Image still exists for the owner.
    assert await image_repository.get_by_id(image_b.id) is not None

    # Owner can delete their own image.
    assert await image_service.delete_image(image_b.id, user_b.id) is True


@pytest.mark.asyncio
async def test_toggle_primary_cross_user_raises_404(async_db_session: AsyncSession, user_a: UserDB, user_b: UserDB) -> None:
    gear_repository = GearRepository(async_db_session)
    gear_service = GearService(gear_repository)
    image_repository = ItemImageRepository(async_db_session)
    image_service = ImageUploadService(async_db_session)

    container_b = await create_test_container(gear_service, user_b.id)
    item_b = await create_test_item(gear_service, user_b.id, container_b["id"])
    image_b = await _make_image(image_repository, item_b["id"], user_b.id)

    with pytest.raises(HTTPException) as exc_info:
        await image_service.toggle_primary_image(item_b["id"], image_b.id, user_a.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_reorder_images_cross_user_item_raises_404(async_db_session: AsyncSession, user_a: UserDB, user_b: UserDB) -> None:
    gear_repository = GearRepository(async_db_session)
    gear_service = GearService(gear_repository)
    image_repository = ItemImageRepository(async_db_session)
    image_service = ImageUploadService(async_db_session)

    container_b = await create_test_container(gear_service, user_b.id)
    item_b = await create_test_item(gear_service, user_b.id, container_b["id"])
    image_b = await _make_image(image_repository, item_b["id"], user_b.id)

    with pytest.raises(HTTPException) as exc_info:
        await image_service.reorder_images(item_b["id"], [{"id": image_b.id, "order": 5}], user_a.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_reorder_images_foreign_image_id_raises_404(async_db_session: AsyncSession, user_a: UserDB) -> None:
    """Owning item_id must not let a caller reorder an image from a different item."""
    gear_repository = GearRepository(async_db_session)
    gear_service = GearService(gear_repository)
    image_repository = ItemImageRepository(async_db_session)
    image_service = ImageUploadService(async_db_session)

    container_a = await create_test_container(gear_service, user_a.id)
    item_a1 = await create_test_item(gear_service, user_a.id, container_a["id"], name="Item 1")
    item_a2 = await create_test_item(gear_service, user_a.id, container_a["id"], name="Item 2")
    image_a2 = await _make_image(image_repository, item_a2["id"], user_a.id)

    # User A owns both items, but image_a2 belongs to item_a2, not item_a1.
    with pytest.raises(HTTPException) as exc_info:
        await image_service.reorder_images(item_a1["id"], [{"id": image_a2.id, "order": 5}], user_a.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_upload_validation_cross_user_item_raises_404(async_db_session: AsyncSession, user_a: UserDB, user_b: UserDB) -> None:
    gear_repository = GearRepository(async_db_session)
    gear_service = GearService(gear_repository)
    image_service = ImageUploadService(async_db_session)

    container_b = await create_test_container(gear_service, user_b.id)
    item_b = await create_test_item(gear_service, user_b.id, container_b["id"])

    class _FakeFile:
        content_type = "image/jpeg"

        class file:
            @staticmethod
            def seek(*_args, **_kwargs):
                return None

            @staticmethod
            def tell():
                return 100

    with pytest.raises(HTTPException) as exc_info:
        await image_service.validate_upload(_FakeFile(), item_b["id"], user_a.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_item_images_owner_succeeds(async_db_session: AsyncSession, user_a: UserDB) -> None:
    gear_repository = GearRepository(async_db_session)
    gear_service = GearService(gear_repository)
    image_repository = ItemImageRepository(async_db_session)
    image_service = ImageUploadService(async_db_session)

    container_a = await create_test_container(gear_service, user_a.id)
    item_a = await create_test_item(gear_service, user_a.id, container_a["id"])
    await _make_image(image_repository, item_a["id"], user_a.id)

    images = await image_service.get_item_images(item_a["id"], user_a.id)
    assert len(images) == 1


@pytest.mark.asyncio
async def test_get_item_images_private_container_unauthenticated_raises_404(async_db_session: AsyncSession, user_a: UserDB) -> None:
    gear_repository = GearRepository(async_db_session)
    gear_service = GearService(gear_repository)
    image_repository = ItemImageRepository(async_db_session)
    image_service = ImageUploadService(async_db_session)

    container_a = await create_test_container(gear_service, user_a.id)
    item_a = await create_test_item(gear_service, user_a.id, container_a["id"])
    await _make_image(image_repository, item_a["id"], user_a.id)

    with pytest.raises(HTTPException) as exc_info:
        await image_service.get_item_images(item_a["id"], None)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_item_images_private_container_other_user_raises_404(async_db_session: AsyncSession, user_a: UserDB, user_b: UserDB) -> None:
    gear_repository = GearRepository(async_db_session)
    gear_service = GearService(gear_repository)
    image_repository = ItemImageRepository(async_db_session)
    image_service = ImageUploadService(async_db_session)

    container_a = await create_test_container(gear_service, user_a.id)
    item_a = await create_test_item(gear_service, user_a.id, container_a["id"])
    await _make_image(image_repository, item_a["id"], user_a.id)

    with pytest.raises(HTTPException) as exc_info:
        await image_service.get_item_images(item_a["id"], user_b.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_item_images_public_container_visible_unauthenticated(async_db_session: AsyncSession, user_a: UserDB) -> None:
    gear_repository = GearRepository(async_db_session)
    gear_service = GearService(gear_repository)
    image_repository = ItemImageRepository(async_db_session)
    image_service = ImageUploadService(async_db_session)

    container = await gear_service.create_container(user_a.id, ContainerCreate(name="Public Container", type="backpack", isPublic=True))
    item = await gear_service.create_item(
        container.id,
        user_a.id,
        ItemCreate(name="Public Item", category="tools", quantity=1, weight=1.0),
    )
    await _make_image(image_repository, item.id, user_a.id)

    images = await image_service.get_item_images(item.id, None)
    assert len(images) == 1
