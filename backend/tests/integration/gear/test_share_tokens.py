"""Integration tests for container share tokens against V2-native containers.

Covers docs/issues/2026-07-23--044--container-share-tokens-table-missing-prod.md and Phase 1
of docs/plans/2026-07-23-gear-backend-v1-v2-unification.md (migration 057): the
`container_share_tokens` table was missing on production and has been recreated with
`container_id` FK -> `gear_items_v2` instead of legacy `gear_containers`.

Scope note: `GearRepository.create_share_token` / `revoke_share_token` don't touch V1 at all, so
they already work correctly for V2-only containers once the table/FK exist (Phase 1). But
`get_share_tokens_by_container` and `get_container_by_token` still resolve container
ownership/lookup via the V1 `GearContainerDB` model (`repository.py`), so they will not see
tokens for a container that only exists in `gear_items_v2` until Phase 3 repoints them. The last
test below pins down that *current, known-incomplete* behavior deliberately -- when Phase 3
lands, it should start failing and must be updated to assert the token IS returned, not deleted.
"""

from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.auth_utils import get_password_hash
from app.modules.auth.db_models import UserDB
from app.modules.gear.repository import GearRepository
from app.modules.gear.repository_v2 import GearRepositoryV2
from app.modules.gear.schemas_v2 import GearItemCreateV2
from app.modules.gear.service_v2 import GearServiceV2


@pytest_asyncio.fixture
async def test_user(async_db_session: AsyncSession) -> UserDB:
    user = UserDB(
        id="share-token-test-user",
        email="share-token-test@example.com",
        name="Share Token Test User",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_email_verified=True,
        created_at=datetime.now(UTC),
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def v2_only_container(gear_repository_v2: GearRepositoryV2, test_user: UserDB):
    """A container that exists ONLY in gear_items_v2, with no V1 gear_containers row.

    Mirrors the real production situation: any container created through today's app is
    V2-only, and #044/#043 were both caused by code that still assumes a V1 counterpart exists.
    """
    service = GearServiceV2(gear_repository_v2)
    return await service.create_item(
        test_user.id,
        GearItemCreateV2(itemType="container", name="V2-only Share Test Container", containerType="backpack"),
    )


# --- Phase 1 (migration 057): schema/FK-level fix -- no FK violation for V2-only containers ---


@pytest.mark.asyncio
async def test_create_share_token_for_v2_only_container_succeeds(
    gear_repository: GearRepository,
    v2_only_container,
    test_user: UserDB,
) -> None:
    """Regression test for #044: before 057, container_share_tokens didn't exist at all
    (500 on any share-token call). After 057, container_id FK targets gear_items_v2, so
    creating a token for a V2-only container must succeed without a FK violation.
    """
    share_token = await gear_repository.create_share_token(
        container_id=v2_only_container.id,
        user_id=test_user.id,
        token="v2-only-share-token-abc123",
    )

    assert share_token.token == "v2-only-share-token-abc123"
    assert share_token.container_id == v2_only_container.id
    assert share_token.user_id == test_user.id


@pytest.mark.asyncio
async def test_revoke_share_token_for_v2_only_container(
    gear_repository: GearRepository,
    v2_only_container,
    test_user: UserDB,
) -> None:
    """revoke_share_token never queried V1 -- it's reachable as soon as the table exists."""
    await gear_repository.create_share_token(
        container_id=v2_only_container.id,
        user_id=test_user.id,
        token="v2-only-share-token-to-revoke",
    )

    revoked = await gear_repository.revoke_share_token("v2-only-share-token-to-revoke", test_user.id)

    assert revoked is True


# --- Phase 3b: ownership check repointed at gear_items_v2 ---


@pytest.mark.asyncio
async def test_get_share_tokens_by_container_returns_tokens_for_v2_only_container(
    gear_repository: GearRepository,
    v2_only_container,
    test_user: UserDB,
) -> None:
    """Regression test for the fix landed in Phase 3b (docs/plans/2026-07-23-gear-backend-v1-v2-unification.md):
    get_share_tokens_by_container's ownership check now queries gear_items_v2 directly instead
    of the V1-only GearRepository.get_container(), so it correctly returns tokens for a
    V2-only container (previously always []) -- see the superseded version of this test from
    Phase 1, kept in git history as documentation of the gap it closed).
    """
    await gear_repository.create_share_token(
        container_id=v2_only_container.id,
        user_id=test_user.id,
        token="v2-only-share-token-listing",
    )

    tokens = await gear_repository.get_share_tokens_by_container(v2_only_container.id, test_user.id)

    assert len(tokens) == 1
    assert tokens[0].token == "v2-only-share-token-listing"
