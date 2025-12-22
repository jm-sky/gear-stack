"""Pydantic schemas for billing and subscription endpoints."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator


# ---------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------


class CreateCheckoutSessionRequest(BaseModel):
    """Request schema for creating a Stripe Checkout session."""

    planTier: Literal["pro", "pro_plus"] = Field(
        ...,
        description="Subscription plan tier (pro or pro_plus)",
    )
    billingInterval: Literal["monthly", "annual"] = Field(
        ...,
        description="Billing interval (monthly or annual)",
    )
    successUrl: HttpUrl = Field(
        ...,
        description="URL to redirect after successful payment",
    )
    cancelUrl: HttpUrl = Field(
        ...,
        description="URL to redirect if payment is cancelled",
    )


class CreatePortalSessionRequest(BaseModel):
    """Request schema for creating a Stripe Billing Portal session."""

    returnUrl: HttpUrl = Field(
        ...,
        description="URL to redirect after portal session",
    )


class UpdateOpenRouterTokenRequest(BaseModel):
    """Request schema for updating OpenRouter API token (Free tier BYOK)."""

    openrouterApiToken: str | None = Field(
        None,
        max_length=500,
        description="OpenRouter API token for Free tier users (BYOK)",
    )


# ---------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------


class SubscriptionResponse(BaseModel):
    """Response schema for subscription details."""

    id: str = Field(alias="id")
    userId: str = Field(alias="user_id")
    stripeCustomerId: str | None = Field(None, alias="stripe_customer_id")
    stripeSubscriptionId: str | None = Field(None, alias="stripe_subscription_id")
    planTier: Literal["free", "pro", "pro_plus"] = Field(alias="plan_tier")
    billingInterval: Literal["monthly", "annual"] | None = Field(None, alias="billing_interval")
    status: Literal["active", "canceled", "past_due", "unpaid", "incomplete"] = Field(alias="status")
    currentPeriodStart: datetime | None = Field(None, alias="current_period_start")
    currentPeriodEnd: datetime | None = Field(None, alias="current_period_end")
    cancelAtPeriodEnd: bool = Field(False, alias="cancel_at_period_end")
    isGrandfathered: bool = Field(False, alias="is_grandfathered")
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")

    model_config = {"from_attributes": True, "populate_by_name": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v: Any) -> str:
        """Convert UUID to string for id field."""
        if isinstance(v, UUID):
            return str(v)
        return str(v)


class CheckoutSessionResponse(BaseModel):
    """Response schema for Checkout session creation."""

    sessionId: str = Field(..., description="Stripe Checkout session ID")
    sessionUrl: str = Field(..., description="URL to redirect user to Checkout")


class PortalSessionResponse(BaseModel):
    """Response schema for Billing Portal session creation."""

    sessionUrl: str = Field(..., description="URL to redirect user to Billing Portal")


class SubscriptionLimitsResponse(BaseModel):
    """Response schema for subscription feature limits."""

    planTier: Literal["free", "pro", "pro_plus"]
    aiMonthlyTokenLimit: int
    storageLimit: int
    canExportData: bool
    canUseAdvancedFeatures: bool
    requiresByok: bool
    itemsLimit: int = Field(..., description="Maximum number of items allowed")
    containersLimit: int = Field(..., description="Maximum number of containers allowed")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


# ---------------------------------------------------------
# Webhook Schemas
# ---------------------------------------------------------


class StripeWebhookEventResponse(BaseModel):
    """Response schema for webhook event details."""

    id: str = Field(alias="id")
    eventId: str = Field(alias="stripe_event_id")
    eventType: str = Field(alias="event_type")
    processed: bool = Field(alias="processed")
    processedAt: datetime | None = Field(None, alias="processed_at")
    error: str | None = Field(None, alias="error_message")
    createdAt: datetime = Field(alias="created_at")

    model_config = {"from_attributes": True, "populate_by_name": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v: Any) -> str:
        """Convert UUID to string for id field."""
        if isinstance(v, UUID):
            return str(v)
        return str(v)


# ---------------------------------------------------------
# Subscription History Schemas
# ---------------------------------------------------------


class SubscriptionHistoryResponse(BaseModel):
    """Response schema for subscription history entry."""

    id: str = Field(alias="id")
    subscriptionId: str = Field(alias="subscription_id")
    userId: str = Field(alias="user_id")
    eventType: str = Field(alias="event_type")
    oldStatus: str | None = Field(None, alias="old_status")
    newStatus: str = Field(alias="new_status")
    oldPlanTier: str | None = Field(None, alias="old_plan_tier")
    newPlanTier: str = Field(alias="new_plan_tier")
    createdAt: datetime = Field(alias="created_at")

    model_config = {"from_attributes": True, "populate_by_name": True}

    @field_validator("id", "subscriptionId", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v: Any) -> str:
        """Convert UUID to string for UUID fields."""
        if isinstance(v, UUID):
            return str(v)
        return str(v)


# ---------------------------------------------------------
# Admin Schemas
# ---------------------------------------------------------


class AdminSubscriptionResponse(BaseModel):
    """Response schema for admin subscription details (includes user info)."""

    id: str = Field(alias="id")
    userId: str = Field(alias="user_id")
    userName: str | None = Field(None, alias="user_name")
    userEmail: str | None = Field(None, alias="user_email")
    stripeCustomerId: str | None = Field(None, alias="stripe_customer_id")
    stripeSubscriptionId: str | None = Field(None, alias="stripe_subscription_id")
    planTier: Literal["free", "pro", "pro_plus"] = Field(alias="plan_tier")
    billingInterval: Literal["monthly", "annual"] | None = Field(None, alias="billing_interval")
    status: Literal["active", "canceled", "past_due", "unpaid", "incomplete"] = Field(alias="status")
    currentPeriodStart: datetime | None = Field(None, alias="current_period_start")
    currentPeriodEnd: datetime | None = Field(None, alias="current_period_end")
    cancelAtPeriodEnd: bool = Field(False, alias="cancel_at_period_end")
    isGrandfathered: bool = Field(False, alias="is_grandfathered")
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")

    model_config = {"from_attributes": True, "populate_by_name": True}

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v: Any) -> str:
        """Convert UUID to string for id field."""
        if isinstance(v, UUID):
            return str(v)
        return str(v)


class AdminSubscriptionStatsResponse(BaseModel):
    """Response schema for subscription statistics."""

    totalUsers: int
    totalSubscriptions: int
    activeSubscriptions: int
    canceledSubscriptions: int
    pastDueSubscriptions: int
    freeUsers: int
    proUsers: int
    proPlusUsers: int
    grandfatheredUsers: int
    monthlyRevenue: float
    annualRevenue: float


class AdminUpdateSubscriptionRequest(BaseModel):
    """Request schema for admin subscription modifications."""

    planTier: Literal["free", "pro", "pro_plus"] | None = Field(
        None,
        description="Update subscription plan tier",
    )
    status: Literal["active", "canceled", "past_due", "unpaid", "incomplete"] | None = Field(
        None,
        description="Update subscription status",
    )
    isGrandfathered: bool | None = Field(
        None,
        description="Mark subscription as grandfathered (lifetime Pro)",
    )
    cancelAtPeriodEnd: bool | None = Field(
        None,
        description="Set whether to cancel at period end",
    )
    reason: str | None = Field(
        None,
        max_length=500,
        description="Reason for manual modification (for audit log)",
    )
