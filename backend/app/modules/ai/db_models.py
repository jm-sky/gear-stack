"""SQLAlchemy database models for AI module."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AIUserSettingsDB(Base):
    """User AI settings including token and model preferences."""

    __tablename__ = "ai_user_settings"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, unique=True, index=True)

    # Token configuration
    use_own_token: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    encrypted_api_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Model selection
    selected_model: Mapped[str] = mapped_column(String(255), default="anthropic/claude-3.5-haiku", nullable=False)

    # Context preferences (stored as JSON array of field names)
    context_fields: Mapped[dict[str, Any]] = mapped_column(JSON, default=lambda: ["name", "category", "weight"], nullable=False)

    # Limits (for system token usage - future feature)
    monthly_token_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monthly_cost_limit: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    monthly_cost_used: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class AIHistoryDB(Base):
    """AI interaction history with full context and cost tracking."""

    __tablename__ = "ai_history"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Operation details
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 'chat', 'classify', 'analyze', 'generate'
    final_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    context_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    response_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Model and provider info
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)

    # Token usage and cost
    tokens_input: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_output: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_total: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_input: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    cost_output: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    cost_total: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)

    # Metadata
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    used_own_token: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False, index=True)

    __table_args__ = (
        Index("idx_ai_history_user_created", "user_id", "created_at"),
        Index("idx_ai_history_operation", "operation_type"),
    )


class AICacheDB(Base):
    """Cache for AI responses to reduce API costs."""

    __tablename__ = "ai_cache"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Cache key (hash of operation + input + model)
    cache_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # Operation details
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)

    # Cached data
    response_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Metadata
    hit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
