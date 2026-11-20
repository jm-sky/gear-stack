"""Regression tests: /api/logs/* must require admin/owner authentication."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.modules.auth.dependencies import get_current_user
from app.modules.logs.repositories import get_log_repository
from main import app

_LOG_ENDPOINTS: list[tuple[str, str]] = [
    ("GET", "/api/logs/"),
    ("GET", "/api/logs/errors"),
    ("GET", "/api/logs/some-id"),
    ("DELETE", "/api/logs/cleanup"),
    ("POST", "/api/logs/"),
]


def _user(*, admin: bool = False, owner: bool = False) -> MagicMock:
    return MagicMock(isAdmin=admin, isOwner=owner)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    repo = MagicMock()
    repo.get_logs = AsyncMock(return_value=[])
    repo.get_error_logs = AsyncMock(return_value=[])
    repo.count_logs = AsyncMock(return_value=0)
    repo.cleanup_old_logs = AsyncMock(return_value=0)
    repo.delete_old_logs = AsyncMock(return_value=0)
    app.dependency_overrides[get_log_repository] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.parametrize(("method", "path"), _LOG_ENDPOINTS)
def test_anonymous_is_rejected(client: TestClient, method: str, path: str) -> None:
    response = client.request(method, path, json={} if method == "POST" else None)
    assert response.status_code in (401, 403)


@pytest.mark.parametrize(("method", "path"), _LOG_ENDPOINTS)
def test_regular_user_is_forbidden(client: TestClient, method: str, path: str) -> None:
    app.dependency_overrides[get_current_user] = lambda: _user()
    response = client.request(method, path, json={} if method == "POST" else None)
    assert response.status_code in (401, 403)


def test_admin_can_list_logs(client: TestClient) -> None:
    app.dependency_overrides[get_current_user] = lambda: _user(admin=True)
    assert client.get("/api/logs/").status_code == 200


def test_owner_can_list_error_logs(client: TestClient) -> None:
    app.dependency_overrides[get_current_user] = lambda: _user(owner=True)
    assert client.get("/api/logs/errors").status_code == 200
