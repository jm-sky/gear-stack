"""Pydantic schemas for billing and subscription endpoints."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


# ---------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------


class CreateCheckoutSessionRequest(BaseModel):
    """Request schema for creating a Stripe Checkout session."""

    planTier: Literal["pro", "business"] = Field(
        ...,
        description="Subscription plan tier (pro or business)",
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

    id: str
    userId: str
    stripeCustomerId: str | None = None
    stripeSubscriptionId: str | None = None
    planTier: Literal["free", "pro", "business"]
    billingInterval: Literal["monthly", "annual"] | None = None
    status: Literal["active", "canceled", "past_due", "unpaid", "incomplete"]
    currentPeriodStart: datetime | None = None
    currentPeriodEnd: datetime | None = None
    cancelAtPeriodEnd: bool = False
    isGrandfathered: bool = False
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class CheckoutSessionResponse(BaseModel):
    """Response schema for Checkout session creation."""

    sessionId: str = Field(..., description="Stripe Checkout session ID")
    sessionUrl: str = Field(..., description="URL to redirect user to Checkout")


class PortalSessionResponse(BaseModel):
    """Response schema for Billing Portal session creation."""

    sessionUrl: str = Field(..., description="URL to redirect user to Billing Portal")


class SubscriptionLimitsResponse(BaseModel):
    """Response schema for subscription feature limits."""

    planTier: Literal["free", "pro", "business"]
    aiMonthlyTokenLimit: int
    storageLimit: int
    canExportData: bool
    canUseAdvancedFeatures: bool
    requiresByok: bool


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


# ---------------------------------------------------------
# Webhook Schemas
# ---------------------------------------------------------


class StripeWebhookEventResponse(BaseModel):
    """Response schema for webhook event details."""

    id: str
    eventId: str
    eventType: str
    processed: bool
    processedAt: datetime | None = None
    error: str | None = None
    createdAt: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


# ---------------------------------------------------------
# Subscription History Schemas
# ---------------------------------------------------------


class SubscriptionHistoryResponse(BaseModel):
    """Response schema for subscription history entry."""

    id: str
    subscriptionId: str
    changeType: str
    oldValue: str | None = None
    newValue: str | None = None
    reason: str | None = None
    createdAt: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
