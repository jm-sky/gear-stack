"""Integration smoke tests for the 2FA API router.

Regression guard for meta #001 / gear-stack #016: the two_factor module must
be registered under /api/two-factor/* exactly once. A duplicated prefix yields
404 for frontend calls to /api/two-factor/totp/initiate etc.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.modules.two_factor.router import router as two_factor_router
from main import app

TWO_FACTOR_PATHS_GET = [
    "/api/two-factor/status",
    "/api/two-factor/totp/status",
    "/api/two-factor/webauthn/status",
    "/api/two-factor/webauthn/passkeys",
]

TWO_FACTOR_PATHS_POST = [
    "/api/two-factor/totp/initiate",
    "/api/two-factor/webauthn/register/initiate",
]


@pytest.fixture(name="client")
def client_fixture() -> TestClient:
    return TestClient(app)


def test_two_factor_module_router_has_no_prefix() -> None:
    """Prefix belongs only on include_router in api/router.py."""
    assert two_factor_router.prefix == ""


def test_openapi_two_factor_paths_have_single_prefix() -> None:
    """OpenAPI schema must list /api/two-factor/* without a duplicated segment."""
    paths = [path for path in app.openapi()["paths"] if "/two-factor" in path]
    assert paths, "expected at least one /api/two-factor path in OpenAPI"

    double_prefix = [path for path in paths if "/two-factor/two-factor/" in path]
    assert double_prefix == [], f"double prefix detected: {double_prefix}"


@pytest.mark.parametrize("path", TWO_FACTOR_PATHS_GET)
def test_two_factor_get_routes_are_registered(client: TestClient, path: str) -> None:
    """Unauthenticated GET must not return 404 (router missing)."""
    response = client.get(path)
    assert response.status_code != status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("path", TWO_FACTOR_PATHS_POST)
def test_two_factor_post_routes_are_registered(client: TestClient, path: str) -> None:
    """Unauthenticated POST must not return 404 (router missing)."""
    response = client.post(path, json={})
    assert response.status_code != status.HTTP_404_NOT_FOUND
