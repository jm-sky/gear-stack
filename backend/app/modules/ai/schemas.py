"""Pydantic schemas for AI module API."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Chat Schemas
# ============================================================================


class AiChatRequest(BaseModel):
    """Request for AI chat."""

    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    context: dict[str, Any] = Field(default_factory=dict, description="Optional context data")
    model: str | None = Field(None, description="Override default model")
    max_tokens: int | None = Field(None, ge=1, le=4000, description="Max tokens for response")
    temperature: float = Field(default=1.0, ge=0.0, le=2.0, description="Temperature for sampling")


class StructuredOutput(BaseModel):
    """Structured output from AI."""

    action: str | None = Field(None, description="Action to perform")
    data: dict[str, Any] = Field(default_factory=dict, description="Action data")


class AiChatResponse(BaseModel):
    """Response from AI chat."""

    message: str = Field(..., description="AI response message")
    structured_output: StructuredOutput | None = Field(None, description="Parsed structured output")
    tokens: dict[str, int] = Field(..., description="Token usage (prompt, completion, total)")
    cost: float | None = Field(None, description="Estimated cost in USD")
    model: str = Field(..., description="Model used")
    prompt: str | None = Field(None, description="Full prompt sent to AI (for debugging, admin only)")


# ============================================================================
# Models Schemas
# ============================================================================


class AiModel(BaseModel):
    """AI model information."""

    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Model display name")
    provider: str = Field(..., description="Provider name")
    description: str | None = Field(None, description="Model description")
    context_length: int = Field(..., description="Maximum context length in tokens")
    cost_per_1m_input: float = Field(..., description="Cost per 1M input tokens in USD")
    cost_per_1m_output: float = Field(..., description="Cost per 1M output tokens in USD")
    recommended: bool = Field(default=False, description="Whether model is recommended")


class AiModelsResponse(BaseModel):
    """Response with available models."""

    models: list[AiModel] = Field(..., description="List of available models")


# ============================================================================
# Settings Schemas
# ============================================================================


class AiSettings(BaseModel):
    """AI user settings."""

    id: UUID = Field(..., description="Settings ID")
    user_id: str = Field(..., description="User ID")
    use_own_token: bool = Field(..., description="Whether user uses own API token")
    has_token: bool = Field(..., description="Whether user has configured token")
    selected_model: str = Field(..., description="Selected model ID")
    context_fields: dict[str, Any] = Field(..., description="Context field configuration")
    max_tokens: int | None = Field(None, description="Max tokens override")
    temperature: float = Field(..., description="Temperature setting")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AiUpdateSettings(BaseModel):
    """Update AI settings request."""

    selected_model: str | None = Field(None, description="Model to select")
    context_fields: dict[str, Any] | None = Field(None, description="Context fields configuration")
    max_tokens: int | None = Field(None, ge=1, le=4000, description="Max tokens override")
    temperature: float | None = Field(None, ge=0.0, le=2.0, description="Temperature setting")


class AiSetTokenRequest(BaseModel):
    """Set API token request."""

    api_token: str = Field(..., min_length=10, max_length=500, description="OpenRouter API token")


class AiSetTokenResponse(BaseModel):
    """Set API token response."""

    success: bool = Field(..., description="Whether token was set successfully")
    message: str = Field(..., description="Result message")


# ============================================================================
# History Schemas
# ============================================================================


class AiHistoryItem(BaseModel):
    """AI history item (list view)."""

    id: UUID = Field(..., description="History ID")
    operation_type: str = Field(..., description="Operation type (chat, classify, etc.)")
    model: str = Field(..., description="Model used")
    total_tokens: int = Field(..., description="Total tokens used")
    cost_usd: float | None = Field(None, description="Cost in USD")
    created_at: datetime = Field(..., description="Creation timestamp")


class AiHistoryDetail(BaseModel):
    """AI history detail (single view)."""

    id: UUID = Field(..., description="History ID")
    user_id: str = Field(..., description="User ID")
    operation_type: str = Field(..., description="Operation type")
    model: str = Field(..., description="Model used")
    prompt_tokens: int = Field(..., description="Prompt tokens")
    completion_tokens: int = Field(..., description="Completion tokens")
    total_tokens: int = Field(..., description="Total tokens")
    cost_usd: float | None = Field(None, description="Cost in USD")
    input_data: dict[str, Any] = Field(..., description="Input data")
    output_data: dict[str, Any] = Field(..., description="Output data")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")


class AiHistoryListResponse(BaseModel):
    """Response with history list."""

    items: list[AiHistoryItem] = Field(..., description="List of history items")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Limit used")
    offset: int = Field(..., description="Offset used")


class AiHistoryQuery(BaseModel):
    """Query parameters for history list."""

    limit: int = Field(default=50, ge=1, le=100, description="Number of items to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
    operation_type: str | None = Field(None, description="Filter by operation type")
