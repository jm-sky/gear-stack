"""Migration integrity tests for V1 to V2 unified model.

PHASE 4: Migration Testing
These tests verify that the V2 unified model works correctly with nested data.
Tests create data using V2 API and verify correct behavior.

Test Coverage:
- Container nesting works in V2
- Item-container relationships work in V2
- Field mappings correct
- Type-specific fields properly isolated
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.db_models import UserDB
from app.modules.gear.schemas_v2 import GearItemCreateV2
from app.modules.gear.service_v2 import GearServiceV2


class TestMigrationIntegrity:
    """Tests to verify V2 unified model behavior."""

    @pytest.mark.asyncio
    async def test_container_nesting_preserved(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify container nesting works in V2: parentItemId."""
        # Arrange: Create nested containers using V2 API
        parent_data = GearItemCreateV2(
            itemType="container",
            name="Parent Container",
            containerType="backpack",
        )
        parent_v2 = await gear_service_v2.create_item(test_user.id, parent_data)

        child_data = GearItemCreateV2(
            itemType="container",
            name="Child Container",
            containerType="pouch",
            parentItemId=parent_v2.id,
        )
        child_v2 = await gear_service_v2.create_item(test_user.id, child_data)

        # Act: Refresh from DB
        await async_db_session.refresh(parent_v2)
        await async_db_session.refresh(child_v2)

        # Assert
        assert parent_v2.parent_item_id is None  # Root container
        assert child_v2.parent_item_id == parent_v2.id  # Nested under parent
        assert parent_v2.item_type == "container"
        assert child_v2.item_type == "container"

    @pytest.mark.asyncio
    async def test_item_container_relationship_preserved(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify item-container relationship works in V2: parentItemId."""
        # Arrange: Create container and item using V2 API
        container_data = GearItemCreateV2(
            itemType="container",
            name="Container",
            containerType="backpack",
        )
        container_v2 = await gear_service_v2.create_item(test_user.id, container_data)

        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            quantity=1,
            weight=200,
            weightUnit="g",
            priority="medium",
            status="owned",
            parentItemId=container_v2.id,
        )
        item_v2 = await gear_service_v2.create_item(test_user.id, item_data)

        # Act: Refresh from DB
        await async_db_session.refresh(container_v2)
        await async_db_session.refresh(item_v2)

        # Assert
        assert item_v2.parent_item_id == container_v2.id  # Item nested under container
        assert container_v2.item_type == "container"
        assert item_v2.item_type == "item"

    @pytest.mark.asyncio
    async def test_container_fields_mapped_correctly(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify container fields are stored correctly in V2."""
        # Arrange: Create container with all fields using V2 API
        container_data = GearItemCreateV2(
            itemType="container",
            name="Test Container",
            description="Test Description",
            containerType="backpack",
            color="coyote",
            brand="Mystery Ranch",
            price=450.00,
            weight=1500,
            weightUnit="g",
            maxWeight=20,
            maxWeightUnit="kg",
            isPublic=True,
            favorite=True,
            showItemImages=True,
        )
        container_v2 = await gear_service_v2.create_item(test_user.id, container_data)

        # Act: Refresh from DB
        await async_db_session.refresh(container_v2)

        # Assert field mappings
        assert container_v2.name == "Test Container"
        assert container_v2.description == "Test Description"
        assert container_v2.container_type == "backpack"
        assert container_v2.color == "coyote"
        assert container_v2.brand == "Mystery Ranch"
        assert container_v2.price == 450.00
        assert container_v2.weight == 1500
        assert container_v2.weight_unit == "g"
        assert container_v2.max_weight == 20
        assert container_v2.max_weight_unit == "kg"
        assert container_v2.is_public is True
        assert container_v2.favorite is True
        assert container_v2.show_item_images is True

    @pytest.mark.asyncio
    async def test_item_fields_mapped_correctly(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify item fields are stored correctly in V2."""
        # Arrange: Create container first
        container_data = GearItemCreateV2(
            itemType="container",
            name="Test Container",
            containerType="backpack",
        )
        container_v2 = await gear_service_v2.create_item(test_user.id, container_data)

        # Create item with all fields using V2 API
        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            quantity=2,
            weight=250,
            weightUnit="g",
            priority="high",
            status="owned",
            quality="high",
            brand="Nalgene",
            price=20.00,
            currency="USD",
            wearable=False,
            consumable=False,
            parentItemId=container_v2.id,
        )
        item_v2 = await gear_service_v2.create_item(test_user.id, item_data)

        # Act: Refresh from DB
        await async_db_session.refresh(item_v2)

        # Assert field mappings
        assert item_v2.name == "Water Bottle"
        assert item_v2.category == "water"
        assert item_v2.quantity == 2
        assert item_v2.weight == 250
        assert item_v2.weight_unit == "g"
        assert item_v2.priority == "high"
        assert item_v2.status == "owned"
        assert item_v2.quality == "high"
        assert item_v2.brand == "Nalgene"
        assert item_v2.price == 20.00
        assert item_v2.currency == "USD"
        assert item_v2.wearable is False
        assert item_v2.consumable is False
        assert item_v2.parent_item_id == container_v2.id

    @pytest.mark.asyncio
    async def test_container_has_no_item_fields(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify containers don't have item-specific fields populated."""
        # Arrange: Create container using V2 API
        container_data = GearItemCreateV2(
            itemType="container",
            name="Test Container",
            containerType="backpack",
        )
        container_v2 = await gear_service_v2.create_item(test_user.id, container_data)

        # Act: Refresh from DB
        await async_db_session.refresh(container_v2)

        # Assert item-specific fields are NULL/default for containers
        # Note: Some fields have DB defaults (quantity=1, status='owned', priority='medium')
        # This is acceptable as long as containers don't expose these in API
        assert container_v2.category is None  # Category is the key discriminator
        assert container_v2.quantity is None or container_v2.quantity == 1  # Default
        assert container_v2.status is None or container_v2.status == "owned"  # Default
        assert container_v2.priority is None or container_v2.priority == "medium"  # Default
        assert container_v2.expiration_date is None
        assert container_v2.quality is None
        assert container_v2.wearable is None or container_v2.wearable is False  # Default
        assert container_v2.consumable is None or container_v2.consumable is False  # Default

    @pytest.mark.asyncio
    async def test_item_has_no_container_fields(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service_v2: GearServiceV2,
    ) -> None:
        """Verify items don't have container-specific fields populated."""
        # Arrange: Create container first
        container_data = GearItemCreateV2(
            itemType="container",
            name="Test Container",
            containerType="backpack",
        )
        container_v2 = await gear_service_v2.create_item(test_user.id, container_data)

        # Create item using V2 API
        item_data = GearItemCreateV2(
            itemType="item",
            name="Water Bottle",
            category="water",
            quantity=1,
            parentItemId=container_v2.id,
        )
        item_v2 = await gear_service_v2.create_item(test_user.id, item_data)

        # Act: Refresh from DB
        await async_db_session.refresh(item_v2)

        # Assert container-specific fields are NULL/default for items
        assert item_v2.container_type is None
        assert item_v2.max_weight is None
        assert item_v2.max_weight_unit is None
        assert item_v2.hide_when_nested is None or item_v2.hide_when_nested is False  # Default
        assert item_v2.is_public is None or item_v2.is_public is False  # Default
        assert item_v2.favorite is None or item_v2.favorite is False  # Default
        assert item_v2.show_item_images is None or item_v2.show_item_images is False  # Default

    @pytest.mark.asyncio
    async def test_container_share_tokens_fk_only_gear_items_v2(
        self,
        async_db_session: AsyncSession,
    ) -> None:
        """Guard against a repeat of the migration-052 bug (docs/issues/2026-07-23--043...).

        052 tried to drop item_images/container_ratings' old V1 FK by a guessed constraint
        name, which silently no-op'd on production, leaving a stale FK to gear_items/
        gear_containers coexisting alongside the correct one to gear_items_v2. Migration 058
        (docs/plans/2026-07-23-gear-backend-v1-v2-unification.md, Phase 2) fixed this on the
        real database by looking up actual constraint names instead of guessing -- verified
        manually against a restored production copy (see the plan doc's Phase 2 section).

        This test only covers `container_share_tokens`, the one ancillary table whose ORM model
        (`ContainerShareTokenDB` in db_models.py) already declares the gear_items_v2 FK, because
        `backend_test` (this test's database) is built from `Base.metadata.create_all()` --
        i.e. from the ORM model declarations, not from the raw-SQL migrations. `item_images`,
        `container_ratings`, `item_promotions`, and `content_reports` still declare V1-pointing
        `ForeignKey(...)`/`relationship(...)` in their ORM models on purpose: those relationships
        (e.g. `GearContainerDB.items`, used throughout the still-live V1 repository methods) are
        only safe to repoint once Phase 3 has moved the query code off them. Extend this test to
        cover the other four once Phase 3e updates their ORM declarations to match.
        """
        result = await async_db_session.execute(text("""
                SELECT ccu.table_name AS referenced_table
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name
                    AND tc.table_schema = ccu.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public'
                    AND tc.table_name = 'container_share_tokens'
                    AND kcu.column_name = 'container_id';
            """))
        referenced_tables = [row.referenced_table for row in result.fetchall()]

        assert referenced_tables == ["gear_items_v2"], f"container_share_tokens.container_id should have exactly one FK, to gear_items_v2, " f"but found: {referenced_tables}"
