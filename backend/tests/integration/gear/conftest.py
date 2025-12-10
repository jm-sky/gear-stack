"""Pytest fixtures for gear module integration tests.

PHASE 0: Test Creation (Pre-Implementation Safety Net)
These fixtures establish baseline behavior before unified model migration.
"""

from datetime import UTC, datetime
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.modules.auth.models import User
from app.modules.auth.auth_utils import get_password_hash
from app.modules.gear.db_models import GearContainerDB, GearItemDB
from app.modules.gear.repository import GearRepository
from app.modules.gear.service import GearService
from app.modules.gear.schemas import ContainerCreate, ItemCreate


@pytest_asyncio.fixture
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing."""
    # Use in-memory SQLite for tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(async_db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id="test-user-id-123",
        email="test@example.com",
        name="Test User",
        hashedPassword=get_password_hash("password123"),
        isActive=True,
        isEmailVerified=True,
        createdAt=datetime.now(UTC),
    )

    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def gear_repository(async_db_session: AsyncSession) -> GearRepository:
    """Create gear repository instance."""
    return GearRepository(async_db_session)


@pytest_asyncio.fixture
async def gear_service(gear_repository: GearRepository) -> GearService:
    """Create gear service instance."""
    return GearService(gear_repository)


@pytest.fixture
def sample_container_data() -> ContainerCreate:
    """Create sample container data for testing."""
    return ContainerCreate(
        name="Test Backpack",
        description="A test backpack for integration tests",
        type="backpack",
        color="coyote",
        weight=500.0,
        weight_unit="g",
        brand="TestBrand",
        price=99.99,
    )


@pytest.fixture
def sample_item_data() -> ItemCreate:
    """Create sample item data for testing."""
    return ItemCreate(
        name="Water Bottle",
        category="water",
        quantity=1,
        weight=300.0,
        weight_unit="g",
        priority="high",
        status="owned",
        brand="Nalgene",
        price=15.99,
        currency="USD",
    )


async def create_test_container(
    service: GearService,
    user_id: str,
    name: str = "Test Container",
    container_type: str = "backpack",
    parent_id: str | None = None,
    weight: float | None = None,
    weight_unit: str | None = "g",
) -> dict:
    """Helper function to create a test container.

    Args:
        service: Gear service instance
        user_id: User ID
        name: Container name
        container_type: Container type
        parent_id: Parent container ID for nesting
        weight: Container weight
        weight_unit: Weight unit

    Returns:
        Created container as dict
    """
    data = ContainerCreate(
        name=name,
        type=container_type,
        parent_container_id=parent_id,
        weight=weight,
        weight_unit=weight_unit,
    )
    container = await service.create_container(user_id, data)
    return container.model_dump()


async def create_test_item(
    service: GearService,
    user_id: str,
    container_id: str,
    name: str = "Test Item",
    category: str = "tools",
    quantity: int = 1,
    weight: float = 100.0,
    weight_unit: str = "g",
    status: str = "owned",
    priority: str = "medium",
) -> dict:
    """Helper function to create a test item.

    Args:
        service: Gear service instance
        user_id: User ID
        container_id: Container ID
        name: Item name
        category: Item category
        quantity: Item quantity
        weight: Item weight
        weight_unit: Weight unit
        status: Item status
        priority: Item priority

    Returns:
        Created item as dict
    """
    data = ItemCreate(
        name=name,
        category=category,
        quantity=quantity,
        weight=weight,
        weight_unit=weight_unit,
        status=status,
        priority=priority,
    )
    item = await service.create_item(user_id, container_id, data)
    return item.model_dump()


async def get_container_count(session: AsyncSession, user_id: str) -> int:
    """Get total number of containers for a user."""
    result = await session.execute(
        select(GearContainerDB).where(GearContainerDB.user_id == user_id)
    )
    containers = result.scalars().all()
    return len(containers)


async def get_item_count(session: AsyncSession, container_id: str) -> int:
    """Get total number of items in a container."""
    result = await session.execute(
        select(GearItemDB).where(GearItemDB.container_id == container_id)
    )
    items = result.scalars().all()
    return len(items)
