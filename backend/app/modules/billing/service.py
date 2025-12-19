"""Billing service layer for business logic."""

import logging
from datetime import UTC, datetime

from ...core.config import settings
from .exceptions import (
    CannotDowngradeGrandfatheredError,
    FreeTrierRequiresBYOKError,
    InvalidBillingIntervalError,
    InvalidPlanTierError,
    StripeAPIError,
    StripeCustomerNotFoundError,
    StripeSubscriptionNotFoundError,
    SubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
)
from .repository import BillingRepository
from .schemas import CheckoutSessionResponse, PortalSessionResponse, SubscriptionLimitsResponse, SubscriptionResponse
from .stripe_client import StripeClient

logger = logging.getLogger(__name__)


class BillingService:
    """Service class for billing and subscription operations."""

    def __init__(self, repository: BillingRepository, stripe_client: StripeClient):
        """
        Initialize billing service.

        Args:
            repository: Billing repository instance
            stripe_client: Stripe client instance
        """
        self.repository = repository
        self.stripe_client = stripe_client

    async def get_subscription(self, user_id: str) -> SubscriptionResponse:
        """
        Get user's subscription details.

        Args:
            user_id: User ID

        Returns:
            Subscription response

        Raises:
            SubscriptionNotFoundError: If subscription doesn't exist
        """
        subscription = await self.repository.get_subscription_by_user_id(user_id)
        if not subscription:
            raise SubscriptionNotFoundError(f"Subscription not found for user {user_id}")

        return SubscriptionResponse.model_validate(subscription)

    async def create_checkout_session(
        self,
        user_id: str,
        plan_tier: str,
        billing_interval: str,
        success_url: str,
        cancel_url: str,
    ) -> CheckoutSessionResponse:
        """
        Create a Stripe Checkout session for subscription purchase.

        Args:
            user_id: User ID
            plan_tier: Subscription plan tier (pro or business)
            billing_interval: Billing interval (monthly or annual)
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled

        Returns:
            Checkout session response with session ID and URL

        Raises:
            InvalidPlanTierError: If plan tier is invalid
            InvalidBillingIntervalError: If billing interval is invalid
            SubscriptionAlreadyExistsError: If user already has paid subscription
            StripeAPIError: If Stripe API call fails
        """
        # Validate plan tier
        if plan_tier not in ["pro", "business"]:
            raise InvalidPlanTierError(f"Invalid plan tier: {plan_tier}")

        # Validate billing interval
        if billing_interval not in ["monthly", "annual"]:
            raise InvalidBillingIntervalError(f"Invalid billing interval: {billing_interval}")

        # Check if user already has a subscription
        subscription = await self.repository.get_subscription_by_user_id(user_id)
        if subscription and subscription.plan_tier in ["pro", "business"] and subscription.status == "active":
            raise SubscriptionAlreadyExistsError("User already has an active paid subscription")

        # Get or create Stripe customer
        if subscription and subscription.stripe_customer_id:
            customer_id = subscription.stripe_customer_id
        else:
            try:
                # Create Stripe customer (email will be fetched from user record in router)
                customer = await self.stripe_client.create_customer(user_id=user_id, email="", name="")
                customer_id = customer.id

                # Update subscription with customer ID
                if subscription:
                    await self.repository.update_subscription(
                        subscription.id,
                        stripe_customer_id=customer_id,
                    )
                else:
                    # Create initial subscription record
                    subscription = await self.repository.create_subscription(
                        user_id=user_id,
                        stripe_customer_id=customer_id,
                        plan_tier="free",
                        status="active",
                    )
            except Exception as e:
                logger.error(f"Failed to create Stripe customer: {e}")
                raise StripeAPIError(f"Failed to create Stripe customer: {e}")

        # Get price ID based on plan and billing interval
        price_id = self._get_price_id(plan_tier, billing_interval)

        # Create checkout session
        try:
            session = await self.stripe_client.create_checkout_session(
                customer_id=customer_id,
                price_id=price_id,
                success_url=success_url,
                cancel_url=cancel_url,
            )

            logger.info(f"Created checkout session {session.id} for user {user_id}")
            return CheckoutSessionResponse(sessionId=session.id, sessionUrl=session.url)
        except Exception as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise StripeAPIError(f"Failed to create checkout session: {e}")

    async def create_portal_session(self, user_id: str, return_url: str) -> PortalSessionResponse:
        """
        Create a Stripe Billing Portal session for subscription management.

        Args:
            user_id: User ID
            return_url: URL to redirect after portal session

        Returns:
            Portal session response with session URL

        Raises:
            SubscriptionNotFoundError: If subscription doesn't exist
            StripeCustomerNotFoundError: If Stripe customer doesn't exist
            StripeAPIError: If Stripe API call fails
        """
        subscription = await self.repository.get_subscription_by_user_id(user_id)
        if not subscription:
            raise SubscriptionNotFoundError(f"Subscription not found for user {user_id}")

        if not subscription.stripe_customer_id:
            raise StripeCustomerNotFoundError(f"Stripe customer not found for user {user_id}")

        # Grandfathered users cannot access portal (they have lifetime access)
        if subscription.is_grandfathered:
            raise CannotDowngradeGrandfatheredError("Grandfathered users have lifetime access and cannot modify their subscription")

        try:
            session = await self.stripe_client.create_portal_session(
                customer_id=subscription.stripe_customer_id,
                return_url=return_url,
            )

            logger.info(f"Created portal session for user {user_id}")
            return PortalSessionResponse(sessionUrl=session.url)
        except Exception as e:
            logger.error(f"Failed to create portal session: {e}")
            raise StripeAPIError(f"Failed to create portal session: {e}")

    async def cancel_subscription(self, user_id: str) -> SubscriptionResponse:
        """
        Cancel user's subscription (at period end).

        Args:
            user_id: User ID

        Returns:
            Updated subscription response

        Raises:
            SubscriptionNotFoundError: If subscription doesn't exist
            StripeSubscriptionNotFoundError: If Stripe subscription doesn't exist
            CannotDowngradeGrandfatheredError: If user is grandfathered
            StripeAPIError: If Stripe API call fails
        """
        subscription = await self.repository.get_subscription_by_user_id(user_id)
        if not subscription:
            raise SubscriptionNotFoundError(f"Subscription not found for user {user_id}")

        if subscription.is_grandfathered:
            raise CannotDowngradeGrandfatheredError("Grandfathered users have lifetime access and cannot cancel")

        if not subscription.stripe_subscription_id:
            raise StripeSubscriptionNotFoundError(f"Stripe subscription not found for user {user_id}")

        try:
            # Cancel subscription at period end
            stripe_sub = await self.stripe_client.cancel_subscription(subscription.stripe_subscription_id)

            # Update database
            updated_subscription = await self.repository.update_subscription(
                subscription.id,
                cancel_at_period_end=True,
                updated_at=datetime.now(UTC),
            )

            # Log history
            await self.repository.create_subscription_history(
                subscription_id=subscription.id,
                change_type="cancellation_scheduled",
                old_value=None,
                new_value=f"cancel_at_period_end={stripe_sub.cancel_at_period_end}",
                reason="User requested cancellation",
            )

            logger.info(f"Cancelled subscription for user {user_id}")
            return SubscriptionResponse.model_validate(updated_subscription)
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise StripeAPIError(f"Failed to cancel subscription: {e}")

    async def update_openrouter_token(self, user_id: str, token: str | None) -> SubscriptionResponse:
        """
        Update user's OpenRouter API token (for Free tier BYOK).

        Args:
            user_id: User ID
            token: OpenRouter API token (None to clear)

        Returns:
            Updated subscription response

        Raises:
            SubscriptionNotFoundError: If subscription doesn't exist
        """
        subscription = await self.repository.get_subscription_by_user_id(user_id)
        if not subscription:
            raise SubscriptionNotFoundError(f"Subscription not found for user {user_id}")

        # Update user's OpenRouter token (stored in users table)
        # This is handled in the router by updating the User model
        # Here we just return the subscription

        logger.info(f"Updated OpenRouter token for user {user_id}")
        return SubscriptionResponse.model_validate(subscription)

    async def get_subscription_limits(self, user_id: str) -> SubscriptionLimitsResponse:
        """
        Get feature limits for user's subscription plan.

        Args:
            user_id: User ID

        Returns:
            Subscription limits response

        Raises:
            SubscriptionNotFoundError: If subscription doesn't exist
        """
        subscription = await self.repository.get_subscription_by_user_id(user_id)
        if not subscription:
            raise SubscriptionNotFoundError(f"Subscription not found for user {user_id}")

        plan_tier = subscription.plan_tier

        # Define limits based on plan tier
        limits: dict[str, dict[str, int | bool]] = {
            "free": {
                "aiMonthlyTokenLimit": 0,  # 0 = BYOK required
                "storageLimit": 100 * 1024 * 1024,  # 100 MB
                "canExportData": True,
                "canUseAdvancedFeatures": False,
                "requiresByok": True,
            },
            "pro": {
                "aiMonthlyTokenLimit": 1_000_000,  # ~$1 worth
                "storageLimit": 5 * 1024 * 1024 * 1024,  # 5 GB
                "canExportData": True,
                "canUseAdvancedFeatures": True,
                "requiresByok": False,
            },
            "business": {
                "aiMonthlyTokenLimit": 10_000_000,  # ~$10 worth
                "storageLimit": 50 * 1024 * 1024 * 1024,  # 50 GB
                "canExportData": True,
                "canUseAdvancedFeatures": True,
                "requiresByok": False,
            },
        }

        plan_limits = limits.get(plan_tier, limits["free"])

        # Type cast plan_tier to Literal and dict bool values to proper types
        from typing import cast, Literal

        plan_tier_typed = cast(Literal["free", "pro", "business"], plan_tier)

        return SubscriptionLimitsResponse(
            planTier=plan_tier_typed,
            aiMonthlyTokenLimit=plan_limits["aiMonthlyTokenLimit"],
            storageLimit=plan_limits["storageLimit"],
            canExportData=cast(bool, plan_limits["canExportData"]),
            canUseAdvancedFeatures=cast(bool, plan_limits["canUseAdvancedFeatures"]),
            requiresByok=cast(bool, plan_limits["requiresByok"]),
        )

    async def check_ai_access(self, user_id: str, openrouter_token: str | None = None) -> bool:
        """
        Check if user has access to AI features.

        Args:
            user_id: User ID
            openrouter_token: User's OpenRouter token (if Free tier)

        Returns:
            True if user has AI access, False otherwise

        Raises:
            FreeTrierRequiresBYOKError: If Free tier user has no token
        """
        subscription = await self.repository.get_subscription_by_user_id(user_id)
        if not subscription:
            return False

        # Paid tiers have AI access
        if subscription.plan_tier in ["pro", "business"]:
            return True

        # Free tier requires BYOK
        if subscription.plan_tier == "free":
            if not openrouter_token:
                raise FreeTrierRequiresBYOKError("Free tier users must provide OpenRouter API token")
            return True

        return False

    def _get_price_id(self, plan_tier: str, billing_interval: str) -> str:
        """
        Get Stripe price ID for plan tier and billing interval.

        Args:
            plan_tier: Plan tier (pro or business)
            billing_interval: Billing interval (monthly or annual)

        Returns:
            Stripe price ID

        Raises:
            InvalidPlanTierError: If plan tier is invalid
            InvalidBillingIntervalError: If billing interval is invalid
        """
        price_map = {
            "pro": {
                "monthly": settings.stripe.pro_monthly_price_id,
                "annual": settings.stripe.pro_annual_price_id,
            },
            "business": {
                "monthly": settings.stripe.business_monthly_price_id,
                "annual": settings.stripe.business_annual_price_id,
            },
        }

        if plan_tier not in price_map:
            raise InvalidPlanTierError(f"Invalid plan tier: {plan_tier}")

        if billing_interval not in price_map[plan_tier]:
            raise InvalidBillingIntervalError(f"Invalid billing interval: {billing_interval}")

        price_id = price_map[plan_tier][billing_interval]
        if not price_id:
            raise InvalidPlanTierError(f"Price ID not configured for {plan_tier}/{billing_interval}")

        return price_id
