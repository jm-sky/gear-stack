"""Unit tests for LocalStorageAdapter path traversal protection."""

from pathlib import Path

import pytest

from app.core.storage.local_adapter import LocalStorageAdapter


@pytest.fixture
def adapter(tmp_path: Path) -> LocalStorageAdapter:
    return LocalStorageAdapter(base_path=str(tmp_path / "uploads"))


@pytest.mark.asyncio
async def test_upload_download_roundtrip(adapter: LocalStorageAdapter) -> None:
    path = await adapter.upload(b"hello", "items/a.txt", "text/plain")
    assert path == "items/a.txt"
    assert await adapter.exists("items/a.txt")
    assert await adapter.download("items/a.txt") == b"hello"


@pytest.mark.asyncio
async def test_rejects_parent_directory_segments(adapter: LocalStorageAdapter) -> None:
    with pytest.raises(ValueError, match="parent directory"):
        await adapter.upload(b"x", "../etc/passwd", "text/plain")

    with pytest.raises(ValueError, match="parent directory"):
        await adapter.download("items/../../etc/passwd")

    with pytest.raises(ValueError, match="parent directory"):
        await adapter.delete("../secret")


@pytest.mark.asyncio
async def test_rejects_absolute_path(adapter: LocalStorageAdapter, tmp_path: Path) -> None:
    absolute = str(tmp_path / "outside.txt")
    with pytest.raises(ValueError, match="relative"):
        await adapter.upload(b"x", absolute, "text/plain")


@pytest.mark.asyncio
async def test_rejects_empty_path(adapter: LocalStorageAdapter) -> None:
    with pytest.raises(ValueError, match="empty"):
        await adapter.upload(b"x", "  ", "text/plain")


@pytest.mark.asyncio
async def test_exists_returns_false_for_unsafe_path(adapter: LocalStorageAdapter) -> None:
    assert await adapter.exists("../etc/passwd") is False


@pytest.mark.asyncio
async def test_get_url_validates_path(adapter: LocalStorageAdapter) -> None:
    url = await adapter.get_url("items/photo.jpg")
    assert url == "/uploads/items/photo.jpg"

    with pytest.raises(ValueError, match="parent directory"):
        await adapter.get_url("../photo.jpg")


@pytest.mark.asyncio
async def test_delete_missing_safe_path(adapter: LocalStorageAdapter) -> None:
    assert await adapter.delete("missing/file.txt") is False
