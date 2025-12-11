"""Integration tests for gear item CRUD operations.

PHASE 0: Test Creation (Pre-Implementation Safety Net)
Verify current item behavior before unified model migration.

These tests document the current system where items are stored separately from containers,
with items referencing containers via container_id.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.db_models import UserDB
from app.modules.gear.schemas import ItemCreate, ItemUpdate
from app.modules.gear.service import GearService

from .conftest import create_test_container, create_test_item, get_item_count


class TestItemCreate:
    """Tests for creating gear items."""

    @pytest.mark.asyncio
    async def test_create_item_minimal_data(
        self,
        gear_service: GearService,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test creating an item with minimal required fields."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        data = ItemCreate(
            name="Water Bottle",
            category="water",
            weight=300.0,
        )

        # Act
        item = await gear_service.create_item(container["id"], test_user.id, data)

        # Assert
        assert item is not None
        assert item.id is not None
        assert item.name == "Water Bottle"
        assert item.category == "water"
        assert item.weight == 300.0
        assert item.weightUnit == "g"  # Default value
        assert item.quantity == 1  # Default value
        assert item.priority == "medium"  # Default value
        assert item.status == "owned"  # Default value
        assert item.container is not None
        assert item.container.id == container["id"]
        assert await get_item_count(async_db_session, container["id"]) == 1

    @pytest.mark.asyncio
    async def test_create_item_full_data(
        self,
        gear_service: GearService,
        test_user: UserDB,
        sample_item_data: ItemCreate,
    ) -> None:
        """Test creating an item with all fields populated."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")

        # Act
        item = await gear_service.create_item(
            container["id"], test_user.id, sample_item_data
        )

        # Assert
        assert item is not None
        assert item.id is not None
        assert item.name == sample_item_data.name
        assert item.category == sample_item_data.category
        assert item.quantity == sample_item_data.quantity
        assert item.weight == sample_item_data.weight
        assert item.weightUnit == sample_item_data.weightUnit
        assert item.priority == sample_item_data.priority
        assert item.status == sample_item_data.status
        assert item.brand == sample_item_data.brand
        assert item.price == sample_item_data.price
        assert item.currency == sample_item_data.currency

    @pytest.mark.asyncio
    async def test_create_multiple_items_in_container(
        self,
        gear_service: GearService,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test creating multiple items in the same container."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")

        # Act
        item1 = await create_test_item(
            gear_service, test_user.id, container["id"], "Item 1", category="water"
        )
        item2 = await create_test_item(
            gear_service, test_user.id, container["id"], "Item 2", category="food"
        )
        item3 = await create_test_item(
            gear_service, test_user.id, container["id"], "Item 3", category="tools"
        )

        # Assert
        assert item1["id"] != item2["id"] != item3["id"]
        assert await get_item_count(async_db_session, container["id"]) == 3

    @pytest.mark.asyncio
    async def test_create_items_in_different_containers(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test creating items in different containers."""
        # Arrange
        container1 = await create_test_container(
            gear_service, test_user.id, "Backpack 1"
        )
        container2 = await create_test_container(
            gear_service, test_user.id, "Backpack 2"
        )

        # Act
        item1 = await create_test_item(
            gear_service, test_user.id, container1["id"], "Item in Container 1"
        )
        item2 = await create_test_item(
            gear_service, test_user.id, container2["id"], "Item in Container 2"
        )

        # Assert
        assert item1["container"]["id"] == container1["id"]
        assert item2["container"]["id"] == container2["id"]
        assert item1["id"] != item2["id"]

    @pytest.mark.asyncio
    async def test_create_item_with_quantity(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test creating an item with quantity > 1."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        data = ItemCreate(
            name="Energy Bar",
            category="food",
            weight=50.0,
            quantity=5,
        )

        # Act
        item = await gear_service.create_item(container["id"], test_user.id, data)

        # Assert
        assert item.quantity == 5
        assert item.weight == 50.0  # Weight per item, not total


class TestItemRead:
    """Tests for reading/retrieving gear items."""

    @pytest.mark.asyncio
    async def test_get_item_by_id(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test retrieving an item by its ID."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        created = await create_test_item(
            gear_service, test_user.id, container["id"], "Test Item"
        )

        # Act
        item = await gear_service.get_item(created["id"], test_user.id)

        # Assert
        assert item is not None
        assert item.id == created["id"]
        assert item.name == "Test Item"
        assert item.container is not None
        assert item.container.id == container["id"]

    @pytest.mark.asyncio
    async def test_get_items_in_container(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test retrieving all items in a specific container."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        await create_test_item(
            gear_service, test_user.id, container["id"], "Item 1", category="water"
        )
        await create_test_item(
            gear_service, test_user.id, container["id"], "Item 2", category="food"
        )
        await create_test_item(
            gear_service, test_user.id, container["id"], "Item 3", category="tools"
        )

        # Act
        items = await gear_service.get_items(container["id"], test_user.id)

        # Assert
        assert len(items) == 3
        names = {item.name for item in items}
        assert names == {"Item 1", "Item 2", "Item 3"}
        # All items should belong to the same container
        for item in items:
            assert item.container is not None
            assert item.container.id == container["id"]

    @pytest.mark.asyncio
    async def test_get_all_items_for_user(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test retrieving all items across all containers for a user."""
        # Arrange
        container1 = await create_test_container(
            gear_service, test_user.id, "Backpack 1"
        )
        container2 = await create_test_container(
            gear_service, test_user.id, "Backpack 2"
        )
        await create_test_item(gear_service, test_user.id, container1["id"], "Item 1")
        await create_test_item(gear_service, test_user.id, container1["id"], "Item 2")
        await create_test_item(gear_service, test_user.id, container2["id"], "Item 3")

        # Act
        items = await gear_service.get_all_items(test_user.id)

        # Assert
        assert len(items) == 3
        names = {item.name for item in items}
        assert names == {"Item 1", "Item 2", "Item 3"}

    @pytest.mark.asyncio
    async def test_get_item_not_found(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test retrieving a non-existent item returns None."""
        # Act
        item = await gear_service.get_item("non-existent-id", test_user.id)

        # Assert
        assert item is None

    @pytest.mark.asyncio
    async def test_get_item_wrong_user(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that user cannot access another user's item."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        created = await create_test_item(
            gear_service, test_user.id, container["id"], "User Item"
        )

        # Act - Try to access with different user ID
        item = await gear_service.get_item(created["id"], "different-user-id")

        # Assert
        assert item is None


class TestItemUpdate:
    """Tests for updating gear items."""

    @pytest.mark.asyncio
    async def test_update_item_name(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test updating an item's name."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        created = await create_test_item(
            gear_service, test_user.id, container["id"], "Original Name"
        )
        update_data = ItemUpdate(name="Updated Name")

        # Act
        updated = await gear_service.update_item(
            created["id"], test_user.id, update_data
        )

        # Assert
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.id == created["id"]

    @pytest.mark.asyncio
    async def test_update_item_multiple_fields(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test updating multiple fields of an item."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        created = await create_test_item(
            gear_service, test_user.id, container["id"], "Test Item"
        )
        update_data = ItemUpdate(
            name="Updated Item",
            category="shelter",
            quantity=3,
            weight=500.0,
            priority="high",
            status="missing",
        )

        # Act
        updated = await gear_service.update_item(
            created["id"], test_user.id, update_data
        )

        # Assert
        assert updated is not None
        assert updated.name == "Updated Item"
        assert updated.category == "shelter"
        assert updated.quantity == 3
        assert updated.weight == 500.0
        assert updated.priority == "high"
        assert updated.status == "missing"

    @pytest.mark.asyncio
    async def test_update_item_partial(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test partial update (only some fields) preserves other fields."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        data = ItemCreate(
            name="Original",
            category="water",
            weight=300.0,
            quantity=2,
            priority="high",
            status="owned",
        )
        created = await gear_service.create_item(container["id"], test_user.id, data)
        update_data = ItemUpdate(name="Updated")

        # Act
        updated = await gear_service.update_item(created.id, test_user.id, update_data)

        # Assert
        assert updated is not None
        assert updated.name == "Updated"
        # Other fields should be preserved
        assert updated.category == "water"
        assert updated.weight == 300.0
        assert updated.quantity == 2
        assert updated.priority == "high"
        assert updated.status == "owned"

    @pytest.mark.asyncio
    async def test_move_item_via_update_not_supported(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that moving item between containers via ItemUpdate.containerId is not supported.

        Note: Current implementation doesn't support changing containerId via update.
        Items remain in their original container even if containerId is passed in update.
        """
        # Arrange
        container1 = await create_test_container(
            gear_service, test_user.id, "Backpack 1"
        )
        container2 = await create_test_container(
            gear_service, test_user.id, "Backpack 2"
        )
        created = await create_test_item(
            gear_service, test_user.id, container1["id"], "Immovable Item"
        )
        update_data = ItemUpdate(containerId=container2["id"])

        # Act
        updated = await gear_service.update_item(
            created["id"], test_user.id, update_data
        )

        # Refetch to verify actual container
        refetched = await gear_service.get_item(created["id"], test_user.id)

        # Assert
        assert updated is not None
        assert updated.name == "Immovable Item"
        # Item should still be in container1 (moving not supported)
        assert refetched is not None
        assert refetched.container is not None
        assert refetched.container.id == container1["id"]


class TestItemDelete:
    """Tests for deleting gear items."""

    @pytest.mark.asyncio
    async def test_delete_item(
        self,
        gear_service: GearService,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test deleting an item."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        created = await create_test_item(
            gear_service, test_user.id, container["id"], "To Delete"
        )
        initial_count = await get_item_count(async_db_session, container["id"])

        # Act
        result = await gear_service.delete_item(created["id"], test_user.id)

        # Assert
        assert result is True
        final_count = await get_item_count(async_db_session, container["id"])
        assert final_count == initial_count - 1
        # Verify item no longer accessible
        deleted = await gear_service.get_item(created["id"], test_user.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_multiple_items(
        self,
        gear_service: GearService,
        test_user: UserDB,
        async_db_session: AsyncSession,
    ) -> None:
        """Test deleting multiple items from a container."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        item1 = await create_test_item(
            gear_service, test_user.id, container["id"], "Item 1"
        )
        item2 = await create_test_item(
            gear_service, test_user.id, container["id"], "Item 2"
        )
        item3 = await create_test_item(
            gear_service, test_user.id, container["id"], "Item 3"
        )
        assert await get_item_count(async_db_session, container["id"]) == 3

        # Act
        await gear_service.delete_item(item1["id"], test_user.id)
        await gear_service.delete_item(item2["id"], test_user.id)

        # Assert
        assert await get_item_count(async_db_session, container["id"]) == 1
        # Only item3 should remain
        remaining = await gear_service.get_item(item3["id"], test_user.id)
        assert remaining is not None
        assert remaining.name == "Item 3"

    @pytest.mark.asyncio
    async def test_delete_item_not_found(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test deleting a non-existent item returns False."""
        # Act
        result = await gear_service.delete_item("non-existent-id", test_user.id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_item_wrong_user(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that user cannot delete another user's item."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        created = await create_test_item(
            gear_service, test_user.id, container["id"], "User Item"
        )

        # Act - Try to delete with different user ID
        result = await gear_service.delete_item(created["id"], "different-user-id")

        # Assert
        assert result is False
        # Item should still exist
        item = await gear_service.get_item(created["id"], test_user.id)
        assert item is not None
        assert item.name == "User Item"

    @pytest.mark.asyncio
    async def test_delete_container_deletes_items(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that deleting a container also deletes its items (cascade)."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")
        item1 = await create_test_item(
            gear_service, test_user.id, container["id"], "Item 1"
        )
        item2 = await create_test_item(
            gear_service, test_user.id, container["id"], "Item 2"
        )

        # Act
        await gear_service.delete_container(container["id"], test_user.id)

        # Assert
        # Items should be deleted (cascade)
        deleted_item1 = await gear_service.get_item(item1["id"], test_user.id)
        deleted_item2 = await gear_service.get_item(item2["id"], test_user.id)
        assert deleted_item1 is None
        assert deleted_item2 is None


class TestItemValidation:
    """Tests for item data validation."""

    @pytest.mark.asyncio
    async def test_create_item_missing_name(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that item requires a name."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")

        # Note: Pydantic validation should prevent empty name
        with pytest.raises((ValueError, Exception)):
            data = ItemCreate(
                name="",  # Empty name should fail
                category="water",
                weight=100.0,
            )
            await gear_service.create_item(container["id"], test_user.id, data)

    @pytest.mark.asyncio
    async def test_create_item_negative_weight(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that item weight must be >= 0."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")

        # Pydantic validation should prevent negative weight
        with pytest.raises((ValueError, Exception)):
            data = ItemCreate(
                name="Invalid Item",
                category="water",
                weight=-100.0,  # Negative weight should fail
            )
            await gear_service.create_item(container["id"], test_user.id, data)

    @pytest.mark.asyncio
    async def test_create_item_zero_quantity(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test that item quantity must be >= 1."""
        # Arrange
        container = await create_test_container(gear_service, test_user.id, "Backpack")

        # Pydantic validation should prevent quantity < 1
        with pytest.raises((ValueError, Exception)):
            data = ItemCreate(
                name="Invalid Item",
                category="water",
                weight=100.0,
                quantity=0,  # Zero quantity should fail
            )
            await gear_service.create_item(container["id"], test_user.id, data)

    @pytest.mark.asyncio
    async def test_create_item_in_nonexistent_container(
        self,
        gear_service: GearService,
        test_user: UserDB,
    ) -> None:
        """Test creating item in non-existent container returns None."""
        # Arrange
        data = ItemCreate(
            name="Orphan Item",
            category="water",
            weight=100.0,
        )

        # Act
        item = await gear_service.create_item(
            "non-existent-container", test_user.id, data
        )

        # Assert
        assert item is None  # Service should return None for invalid container
