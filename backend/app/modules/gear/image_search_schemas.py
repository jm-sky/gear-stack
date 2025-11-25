"""Pydantic schemas for image search API."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ImageSearchEngineResponse(BaseModel):
    """Response schema for image search engine."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    name: str
    type: str = Field(description="Engine type: 'html_scraper' or 'api'")
    base_url: str = Field(alias="baseUrl")
    search_template: str | None = Field(None, alias="searchTemplate")
    image_selectors: dict[str, Any] | None = Field(None, alias="imageSelectors")
    api_endpoint: str | None = Field(None, alias="apiEndpoint")
    api_key: str | None = Field(None, alias="apiKey", exclude=True)  # Never expose API keys
    request_headers: dict[str, str] | None = Field(None, alias="requestHeaders")
    response_mapping: dict[str, str] | None = Field(None, alias="responseMapping")
    is_active: bool = Field(alias="isActive")
    priority: int


class ImageSearchRequest(BaseModel):
    """Request schema for image search."""

    model_config = ConfigDict(populate_by_name=True)

    item_id: str = Field(..., alias="itemId", description="Item ID to search images for")
    search_query: str | None = Field(None, alias="searchQuery", description="Custom search query (optional, will be built from item if not provided)")
    engine_ids: list[str] | None = Field(None, alias="engineIds", description="Specific engine IDs to use (optional, uses all active if not provided)")


class ImageSearchResult(BaseModel):
    """Schema for a single image search result."""

    model_config = ConfigDict(populate_by_name=True)

    image_url: str = Field(alias="imageUrl")
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    source_url: str | None = Field(None, alias="sourceUrl")
    source_name: str | None = Field(None, alias="sourceName")
    search_engine_id: str = Field(alias="searchEngineId")
    search_engine_name: str = Field(alias="searchEngineName")


class ImageSearchResponse(BaseModel):
    """Response schema for image search."""

    model_config = ConfigDict(populate_by_name=True)

    results: list[ImageSearchResult]
    total: int


class DownloadAndAddImageRequest(BaseModel):
    """Request schema for downloading and adding an image from search result."""

    model_config = ConfigDict(populate_by_name=True)

    item_id: str = Field(alias="itemId")
    image_url: str = Field(alias="imageUrl")
    source_url: str | None = Field(None, alias="sourceUrl")
    source_name: str | None = Field(None, alias="sourceName")
    search_engine_id: str = Field(alias="searchEngineId")
    is_primary: bool = Field(False, alias="isPrimary")
