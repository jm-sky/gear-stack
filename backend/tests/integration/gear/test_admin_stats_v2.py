"""Integration tests for admin/stats modules against V2-native gear data.

Covers Phase 3c/3d of docs/plans/2026-07-23-gear-backend-v1-v2-unification.md:
app/modules/stats/router.py and app/modules/admin/repository.py+service.py both queried legacy
GearContainerDB/GearItemDB (V1) directly -- not discovered by the original issue #043 scope, but
found while auditing which code reads the V1 tables directly and would 500 once those tables are
dropped in Phase 5. Both now query gear_items_v2.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admin.repository import AdminRepository
from app.modules.admin.service import AdminService
from app.modules.auth.db_models import UserDB
from app.modules.auth.repositories import UserRepository as AuthUserRepository
from app.modules.gear.repository_v2 import GearRepositoryV2
from app.modules.gear.service_v2 import GearServiceV2
from app.modules.stats.router import get_container_stats, get_item_stats
from app.modules.users.repositories import UserRepository

from .conftest import create_test_container_v2, create_test_item_v2


@pytest_asyncio.fixture
async def admin_service(async_db_session: AsyncSession) -> AdminService:
    auth_user_repo = AuthUserRepository(async_db_session)
    return AdminService(
        repository=AdminRepository(async_db_session),
        user_repository=UserRepository(auth_user_repo),
        auth_user_repository=auth_user_repo,
    )


@pytest.mark.asyncio
async def test_admin_get_all_containers_and_items_v2_only(
    admin_service: AdminService,
    gear_repository_v2: GearRepositoryV2,
    test_user: UserDB,
) -> None:
    gear_service_v2 = GearServiceV2(gear_repository_v2)
    container = await create_test_container_v2(gear_service_v2, test_user.id, name="Admin V2 Container")
    item = await create_test_item_v2(gear_service_v2, test_user.id, container.id, name="Admin V2 Item")

    containers = await admin_service.get_all_containers()
    matching = [c for c in containers if c.id == container.id]
    assert len(matching) == 1
    assert matching[0].itemCount == 1
    assert matching[0].authorId == test_user.id

    single_container = await admin_service.get_container_by_id(container.id)
    assert single_container is not None
    assert single_container.itemCount == 1

    items = await admin_service.get_all_items()
    matching_items = [i for i in items if i.id == item.id]
    assert len(matching_items) == 1
    assert matching_items[0].containerId == container.id
    assert matching_items[0].containerName == "Admin V2 Container"
    assert matching_items[0].authorId == test_user.id

    single_item = await admin_service.get_item_by_id(item.id)
    assert single_item is not None
    assert single_item.containerName == "Admin V2 Container"


@pytest.mark.asyncio
async def test_admin_update_and_delete_container_v2_only(
    admin_service: AdminService,
    gear_repository_v2: GearRepositoryV2,
    test_user: UserDB,
) -> None:
    gear_service_v2 = GearServiceV2(gear_repository_v2)
    container = await create_test_container_v2(gear_service_v2, test_user.id, name="Before Rename")

    updated = await admin_service.update_container(container.id, {"name": "After Rename"})
    assert updated is not None
    assert updated.name == "After Rename"

    deleted = await admin_service.delete_container(container.id)
    assert deleted is True
    assert await admin_service.get_container_by_id(container.id) is None


@pytest.mark.asyncio
async def test_stats_counts_v2_only_containers_and_items(
    async_db_session: AsyncSession,
    gear_repository_v2: GearRepositoryV2,
    test_user: UserDB,
) -> None:
    """Regression test for stats/router.py Phase 3c fix: counts must come from gear_items_v2,
    not the (now-empty-in-practice, for real V2-only data) legacy gear_containers/gear_items.
    """
    gear_service_v2 = GearServiceV2(gear_repository_v2)
    container = await create_test_container_v2(gear_service_v2, test_user.id, name="Stats Container")
    await create_test_item_v2(gear_service_v2, test_user.id, container.id, name="Stats Item")

    container_stats = await get_container_stats(db=async_db_session)
    item_stats = await get_item_stats(db=async_db_session)

    assert container_stats.total == 1
    assert item_stats.total == 1
