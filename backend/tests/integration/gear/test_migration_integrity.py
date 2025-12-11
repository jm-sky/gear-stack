"""Migration integrity tests for V1 to V2 unified model.

PHASE 4: Migration Testing
These tests verify that data migration from V1 (dual-model) to V2 (unified model)
preserves all data correctly.

Test Coverage:
- All containers migrated
- All items migrated
- Parent-child relationships preserved
- Field mappings correct
- No data loss
"""

import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.db_models import UserDB
from app.modules.gear.db_models import GearContainerDB, GearItemDB
from app.modules.gear.db_models_v2 import GearItemDBV2
from app.modules.gear.service import GearService
from app.modules.gear.schemas import ContainerCreate, ItemCreate


class TestMigrationIntegrity:
    """Tests to verify migration from V1 to V2 preserves all data."""

    @pytest.mark.asyncio
    async def test_all_containers_migrated(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
    ) -> None:
        """Verify all V1 containers exist in V2 with itemType='container'."""
        # Get counts
        v1_stmt = select(func.count()).select_from(GearContainerDB).where(GearContainerDB.user_id == test_user.id)
        v1_result = await async_db_session.execute(v1_stmt)
        v1_count = v1_result.scalar()

        v2_stmt = (
            select(func.count())
            .select_from(GearItemDBV2)
            .where(
                GearItemDBV2.user_id == test_user.id,
                GearItemDBV2.item_type == "container",
            )
        )
        v2_result = await async_db_session.execute(v2_stmt)
        v2_count = v2_result.scalar()

        # Assert
        assert v2_count == v1_count, f"Container count mismatch: V1 has {v1_count}, V2 has {v2_count}"

    @pytest.mark.asyncio
    async def test_all_items_migrated(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
    ) -> None:
        """Verify all V1 items exist in V2 with itemType='item'."""
        # Get counts
        v1_stmt = select(func.count()).select_from(GearItemDB).join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id).where(GearContainerDB.user_id == test_user.id)
        v1_result = await async_db_session.execute(v1_stmt)
        v1_count = v1_result.scalar()

        v2_stmt = (
            select(func.count())
            .select_from(GearItemDBV2)
            .where(
                GearItemDBV2.user_id == test_user.id,
                GearItemDBV2.item_type == "item",
            )
        )
        v2_result = await async_db_session.execute(v2_stmt)
        v2_count = v2_result.scalar()

        # Assert
        assert v2_count == v1_count, f"Item count mismatch: V1 has {v1_count}, V2 has {v2_count}"

    @pytest.mark.asyncio
    async def test_total_count_preserved(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
    ) -> None:
        """Verify total row count: V2 = V1_containers + V1_items."""
        # Get V1 counts
        v1_containers_stmt = select(func.count()).select_from(GearContainerDB).where(GearContainerDB.user_id == test_user.id)
        v1_containers_result = await async_db_session.execute(v1_containers_stmt)
        v1_containers_count = v1_containers_result.scalar()

        v1_items_stmt = select(func.count()).select_from(GearItemDB).join(GearContainerDB, GearItemDB.container_id == GearContainerDB.id).where(GearContainerDB.user_id == test_user.id)
        v1_items_result = await async_db_session.execute(v1_items_stmt)
        v1_items_count = v1_items_result.scalar()

        # Get V2 count
        v2_stmt = select(func.count()).select_from(GearItemDBV2).where(GearItemDBV2.user_id == test_user.id)
        v2_result = await async_db_session.execute(v2_stmt)
        v2_count = v2_result.scalar()

        expected_count = v1_containers_count + v1_items_count

        # Assert
        assert v2_count == expected_count, f"Total count mismatch: expected {expected_count} " f"({v1_containers_count} containers + {v1_items_count} items), " f"got {v2_count}"

    @pytest.mark.asyncio
    async def test_container_nesting_preserved(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service: GearService,
    ) -> None:
        """Verify container nesting: parent_container_id → parent_item_id."""
        # Arrange: Create nested containers in V1
        parent_data = ContainerCreate(
            name="Parent Container",
            type="backpack",
        )
        parent_v1 = await gear_service.create_container(test_user.id, parent_data)

        child_data = ContainerCreate(
            name="Child Container",
            type="pouch",
            parentContainerId=parent_v1.id,
        )
        child_v1 = await gear_service.create_container(test_user.id, child_data)

        # Act: Get V2 versions
        parent_v2_stmt = select(GearItemDBV2).where(
            GearItemDBV2.id == parent_v1.id,
            GearItemDBV2.item_type == "container",
        )
        parent_v2_result = await async_db_session.execute(parent_v2_stmt)
        parent_v2 = parent_v2_result.scalar_one()

        child_v2_stmt = select(GearItemDBV2).where(
            GearItemDBV2.id == child_v1.id,
            GearItemDBV2.item_type == "container",
        )
        child_v2_result = await async_db_session.execute(child_v2_stmt)
        child_v2 = child_v2_result.scalar_one()

        # Assert
        assert parent_v2.parent_item_id is None  # Root container
        assert child_v2.parent_item_id == parent_v2.id  # Nested under parent

    @pytest.mark.asyncio
    async def test_item_container_relationship_preserved(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service: GearService,
    ) -> None:
        """Verify item-container relationship: container_id → parent_item_id."""
        # Arrange: Create container and item in V1
        container_data = ContainerCreate(
            name="Container",
            type="backpack",
        )
        container_v1 = await gear_service.create_container(test_user.id, container_data)

        item_data = ItemCreate(
            name="Water Bottle",
            category="water",
            quantity=1,
            weight=200,
            weightUnit="g",
            priority="medium",
            status="owned",
        )
        item_v1 = await gear_service.create_item(container_v1.id, test_user.id, item_data)

        # Act: Get V2 versions
        container_v2_stmt = select(GearItemDBV2).where(
            GearItemDBV2.id == container_v1.id,
            GearItemDBV2.item_type == "container",
        )
        container_v2_result = await async_db_session.execute(container_v2_stmt)
        container_v2 = container_v2_result.scalar_one()

        item_v2_stmt = select(GearItemDBV2).where(
            GearItemDBV2.id == item_v1.id,
            GearItemDBV2.item_type == "item",
        )
        item_v2_result = await async_db_session.execute(item_v2_stmt)
        item_v2 = item_v2_result.scalar_one()

        # Assert
        assert item_v2.parent_item_id == container_v2.id

    @pytest.mark.asyncio
    async def test_container_fields_mapped_correctly(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service: GearService,
    ) -> None:
        """Verify container field mapping to V2."""
        # Arrange: Create container with all fields
        container_data = ContainerCreate(
            name="Test Container",
            description="Test Description",
            type="backpack",
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
        container_v1 = await gear_service.create_container(test_user.id, container_data)

        # Act: Get V2 version
        v2_stmt = select(GearItemDBV2).where(
            GearItemDBV2.id == container_v1.id,
            GearItemDBV2.item_type == "container",
        )
        v2_result = await async_db_session.execute(v2_stmt)
        container_v2 = v2_result.scalar_one()

        # Assert field mappings
        assert container_v2.name == container_v1.name
        assert container_v2.description == container_v1.description
        assert container_v2.container_type == container_v1.type  # type → container_type
        assert container_v2.color == container_v1.color
        assert container_v2.brand == container_v1.brand
        assert container_v2.price == container_v1.price
        assert container_v2.weight == container_v1.weight
        assert container_v2.weight_unit == container_v1.weightUnit
        assert container_v2.max_weight == container_v1.maxWeight
        assert container_v2.max_weight_unit == container_v1.maxWeightUnit
        assert container_v2.is_public == container_v1.isPublic
        assert container_v2.favorite == container_v1.favorite
        assert container_v2.show_item_images == container_v1.showItemImages

    @pytest.mark.asyncio
    async def test_item_fields_mapped_correctly(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service: GearService,
    ) -> None:
        """Verify item field mapping to V2."""
        # Arrange: Create container and item with all fields
        container_data = ContainerCreate(
            name="Container",
            type="backpack",
        )
        container_v1 = await gear_service.create_container(test_user.id, container_data)

        item_data = ItemCreate(
            name="Water Bottle",
            category="water",
            quantity=2,
            weight=200,
            weightUnit="g",
            priority="high",
            status="owned",
            brand="Nalgene",
            price=12.99,
            currency="USD",
            quality="high",
            wearable=False,
            consumable=False,
            order=5,
        )
        item_v1 = await gear_service.create_item(container_v1.id, test_user.id, item_data)

        # Act: Get V2 version
        v2_stmt = select(GearItemDBV2).where(
            GearItemDBV2.id == item_v1.id,
            GearItemDBV2.item_type == "item",
        )
        v2_result = await async_db_session.execute(v2_stmt)
        item_v2 = v2_result.scalar_one()

        # Assert field mappings
        assert item_v2.name == item_v1.name
        assert item_v2.category == item_v1.category
        assert item_v2.quantity == item_v1.quantity
        assert item_v2.weight == item_v1.weight
        assert item_v2.weight_unit == item_v1.weightUnit
        assert item_v2.priority == item_v1.priority
        assert item_v2.status == item_v1.status
        assert item_v2.brand == item_v1.brand
        assert item_v2.price == item_v1.price
        assert item_v2.currency == item_v1.currency
        assert item_v2.quality == item_v1.quality
        assert item_v2.wearable == item_v1.wearable
        assert item_v2.consumable == item_v1.consumable
        assert item_v2.order_index == item_v1.order  # order → order_index

    @pytest.mark.asyncio
    async def test_container_has_no_item_fields(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service: GearService,
    ) -> None:
        """Verify containers have NULL item-specific fields."""
        # Arrange: Create container
        container_data = ContainerCreate(
            name="Container",
            type="backpack",
        )
        container_v1 = await gear_service.create_container(test_user.id, container_data)

        # Act: Get V2 version
        v2_stmt = select(GearItemDBV2).where(
            GearItemDBV2.id == container_v1.id,
            GearItemDBV2.item_type == "container",
        )
        v2_result = await async_db_session.execute(v2_stmt)
        container_v2 = v2_result.scalar_one()

        # Assert key item-specific field is NULL (category is required for items)
        assert container_v2.category is None

    @pytest.mark.asyncio
    async def test_item_has_no_container_fields(
        self,
        async_db_session: AsyncSession,
        test_user: UserDB,
        gear_service: GearService,
    ) -> None:
        """Verify items have NULL container-specific fields."""
        # Arrange: Create container and item
        container_data = ContainerCreate(
            name="Container",
            type="backpack",
        )
        container_v1 = await gear_service.create_container(test_user.id, container_data)

        item_data = ItemCreate(
            name="Water Bottle",
            category="water",
            quantity=1,
            weight=200,
            weightUnit="g",
            priority="medium",
            status="owned",
        )
        item_v1 = await gear_service.create_item(container_v1.id, test_user.id, item_data)

        # Act: Get V2 version
        v2_stmt = select(GearItemDBV2).where(
            GearItemDBV2.id == item_v1.id,
            GearItemDBV2.item_type == "item",
        )
        v2_result = await async_db_session.execute(v2_stmt)
        item_v2 = v2_result.scalar_one()

        # Assert key container-specific field is NULL (container_type is required for containers)
        assert item_v2.container_type is None
