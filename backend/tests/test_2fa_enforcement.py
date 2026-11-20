"""Regression tests: 2FA enforcement in _verify_user_token must fail closed."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.modules.auth import dependencies as deps
from app.modules.two_factor.service import TwoFactorService


def _payload(tfa_verified: bool | None) -> dict[str, Any]:
    payload: dict[str, Any] = {"type": "access", "sub": "user-1", "tv": 0}
    if tfa_verified is not None:
        payload["tfaVerified"] = tfa_verified
    return payload


def _setup(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any], has_2fa: Any) -> tuple[MagicMock, AsyncMock, MagicMock]:
    monkeypatch.setattr(deps, "verify_token", lambda _token: payload)
    user = MagicMock(tokenVersion=0, isActive=True, isEmailVerified=True)
    user_repo = MagicMock()
    user_repo.get_user_by_id = AsyncMock(return_value=user)
    blacklist = MagicMock()
    blacklist.is_blacklisted = AsyncMock(return_value=False)
    blacklist.is_jti_blacklisted = AsyncMock(return_value=False)
    if isinstance(has_2fa, Exception):
        monkeypatch.setattr(TwoFactorService, "has_two_factor_enabled", AsyncMock(side_effect=has_2fa))
    else:
        monkeypatch.setattr(TwoFactorService, "has_two_factor_enabled", AsyncMock(return_value=has_2fa))
    return user, user_repo, blacklist  # type: ignore[return-value]


async def _call(user_repo: Any, blacklist: Any) -> Any:
    return await deps._verify_user_token("tok", user_repo, blacklist, two_factor_repository=MagicMock())


@pytest.mark.asyncio
@pytest.mark.parametrize("tfa", [False, None])
async def test_2fa_user_with_unverified_token_gets_401(monkeypatch: pytest.MonkeyPatch, tfa: bool | None) -> None:
    _, repo, bl = _setup(monkeypatch, _payload(tfa), True)
    with pytest.raises(HTTPException) as exc:
        await _call(repo, bl)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_2fa_user_with_verified_token_is_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    user, repo, bl = _setup(monkeypatch, _payload(True), True)
    assert await _call(repo, bl) is user


@pytest.mark.asyncio
async def test_2fa_lookup_failure_returns_503(monkeypatch: pytest.MonkeyPatch) -> None:
    _, repo, bl = _setup(monkeypatch, _payload(False), RuntimeError("db down"))
    with pytest.raises(HTTPException) as exc:
        await _call(repo, bl)
    assert exc.value.status_code == 503


@pytest.mark.asyncio
async def test_user_without_2fa_is_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    user, repo, bl = _setup(monkeypatch, _payload(None), False)
    assert await _call(repo, bl) is user
