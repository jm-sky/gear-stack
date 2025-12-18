# Stripe Subscription Implementation Plan

**Status:** ✅ Patterns Verified - Ready for Implementation
**Created:** 2025-12-18
**Last Updated:** 2025-12-18

## Executive Summary

This document outlines the complete implementation plan for integrating Stripe subscription billing into Gear Stack. The system will transform the current boolean `is_premium` flag into a comprehensive three-tier subscription system (Free, Pro, Business) with monthly and annual billing options.

**⚠️ IMPORTANT:** This plan has been verified against actual codebase patterns. See **[Pattern Verification Document](./stripe-pattern-verification.md)** for detailed pattern analysis.

## Related Documents

- **[Requirements](./stripe-subscription-requirements.md)** - Business requirements and feature specifications
- **[Pattern Verification](./stripe-pattern-verification.md)** - Verified codebase patterns and conventions

## User Requirements

### Subscription Structure
- **Free Tier:** Basic features with BYOK AI ($1) and storage (100MB)
- **Pro Tier:** Enhanced features with $10 AI limit and 5GB storage
- **Business Tier:** Advanced features with $50 AI limit and 50GB storage

### Billing Model
- Monthly subscriptions for Pro and Business
- Annual subscriptions with 17% discount (2 months free)
- No trial period
- **Final Pricing:**
  - **Pro:** $4.99/month or $49/year
  - **Business:** $14.99/month or $149/year

### Technical Approach
- **Stripe Checkout (hosted):** Simplest implementation, PCI compliant
- **Stripe Billing Portal:** Customer self-service for subscription management
- User has Stripe account but needs setup assistance

## Current State Analysis

### Existing Infrastructure ✅

1. **Premium User System**
   - Location: `backend/app/modules/auth/db_models.py:52`
   - Field: `is_premium: Mapped[bool]`
   - Currently toggled manually via admin panel

2. **Feature Limits Module**
   - Location: `backend/app/modules/feature_limits/`
   - Roles: `user`, `premium`, `admin`, `owner`
   - Fields: `ai_limit` (USD), `storage_limit_bytes`
   - API: GET/POST/PATCH/DELETE `/feature-limits/{role}`

3. **Permission System**
   - Composable: `src/shared/composables/usePermissions.ts`
   - Check: `canUsePremiumFeatures()` returns true for premium/admin/owner
   - Used throughout app to gate features

4. **Premium UI Components**
   - `PremiumFeatureBadge.vue` - Shows "Premium Feature" badge
   - `StorageUsageCard.vue` - Displays storage usage with limits
   - Role-based feature restrictions

### Missing Components ❌

- ❌ Stripe SDK integration (backend + frontend)
- ❌ Payment/billing module
- ❌ Database tables: `subscriptions`, `stripe_webhook_events`, `subscription_history`
- ❌ Checkout flow and billing portal
- ❌ Webhook handler for Stripe events
- ❌ Pricing page with plan comparison
- ❌ Subscription management UI

## Architecture Design

### Backend Module Structure

Create new module: `backend/app/modules/billing/`

```
billing/
├── __init__.py
├── router.py              # API endpoints
├── service.py             # Business logic
├── repository.py          # Database operations
├── db_models.py           # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── stripe_client.py       # Stripe SDK wrapper
├── webhook_handler.py     # Webhook event processor
└── exceptions.py          # Custom exceptions
```

### Database Schema

#### 1. `subscriptions` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | String(36) | FK to users.id (unique) |
| `stripe_customer_id` | String(255) | Stripe customer ID |
| `stripe_subscription_id` | String(255) | Stripe subscription ID (unique) |
| `stripe_price_id` | String(255) | Stripe price ID |
| `plan_tier` | Enum | 'free', 'pro', 'business' |
| `billing_interval` | Enum | 'month', 'year' |
| `status` | Enum | 'active', 'canceled', 'past_due', etc. |
| `current_period_start` | DateTime | Billing period start |
| `current_period_end` | DateTime | Billing period end |
| `cancel_at_period_end` | Boolean | Scheduled cancellation flag |
| `canceled_at` | DateTime | Cancellation timestamp |
| `is_grandfathered` | Boolean | Lifetime Pro access (migrated users) |
| `created_at` | DateTime | Record creation |
| `updated_at` | DateTime | Last update |

**Indexes:**
- `user_id` (unique)
- `stripe_customer_id`
- `stripe_subscription_id` (unique)
- `plan_tier`
- `status`

#### 2. `stripe_webhook_events` Table

Audit log for all webhook events received from Stripe.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `stripe_event_id` | String(255) | Stripe event ID (unique) |
| `event_type` | String(100) | Event type (e.g., 'customer.subscription.updated') |
| `payload` | JSONB | Full event payload |
| `processed` | Boolean | Processing status |
| `processed_at` | DateTime | Processing timestamp |
| `error_message` | Text | Error details if processing failed |
| `created_at` | DateTime | Event received timestamp |

**Indexes:**
- `stripe_event_id` (unique)
- `processed`

#### 3. `subscription_history` Table

Audit trail for subscription changes.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `subscription_id` | UUID | FK to subscriptions |
| `user_id` | String(36) | FK to users |
| `event_type` | Enum | 'created', 'updated', 'canceled', 'renewed', 'payment_failed' |
| `old_status` | String | Previous status |
| `new_status` | String | New status |
| `old_plan_tier` | String | Previous plan |
| `new_plan_tier` | String | New plan |
| `metadata` | JSONB | Additional context |
| `created_at` | DateTime | Event timestamp |

**Indexes:**
- `subscription_id`
- `user_id`

### Integration Points

#### With `feature_limits` Module

Map subscription tiers to feature limit roles:

- `free` → `user` role limits
- `pro` → `premium` role limits
- `business` → new `business` role limits
- `admin`/`owner` → unlimited (unchanged)

#### With `auth` Module

- Maintain `UserDB.is_premium` for backward compatibility
- Auto-sync based on subscription status:
  - `is_premium = true` if `plan_tier IN ('pro', 'business')` AND `status = 'active'`
  - `is_premium = false` otherwise

#### With `users` Module

- Extend `GET /users/me` to include subscription details
- Add `subscription_tier` to `UserResponse.features`

### Frontend Module Structure

Create new module: `src/modules/billing/`

```
billing/
├── components/
│   ├── PricingCard.vue
│   ├── PricingTable.vue
│   ├── SubscriptionStatusCard.vue
│   ├── BillingIntervalToggle.vue
│   └── UpgradePromptBanner.vue
├── composables/
│   ├── useSubscription.ts
│   └── useCheckout.ts
├── pages/
│   ├── PricingPage.vue
│   └── BillingPage.vue
├── services/
│   └── billingApiService.ts
├── store/
│   └── useBillingStore.ts         # Optional client-side cache
├── types/
│   └── billing.type.ts
├── validation/
│   └── subscription.schema.ts     # Zod schemas
├── utils/
│   └── queryUtils.ts              # Query keys & retry logic
├── routes.ts
└── i18n/
    ├── index.ts
    └── locales/
        ├── en.ts                  # ⚠️ Use .ts, NOT .json
        └── pl.ts
```

## Implementation Details

### Backend API Endpoints

#### 1. `POST /billing/checkout`

Create Stripe Checkout session for plan upgrade.

**Request:**
```json
{
  "priceId": "price_...",
  "planTier": "pro",
  "billingInterval": "month"
}
```

**Response:**
```json
{
  "sessionId": "cs_...",
  "url": "https://checkout.stripe.com/..."
}
```

**Logic:**
1. Validate price ID matches plan tier
2. Get or create Stripe customer
3. Create Stripe Checkout session with success/cancel URLs
4. Return checkout URL for redirect

#### 2. `POST /billing/portal`

Create Stripe Billing Portal session for subscription management.

**Request:**
```json
{
  "returnUrl": "https://app.example.com/settings/billing"
}
```

**Response:**
```json
{
  "url": "https://billing.stripe.com/..."
}
```

**Logic:**
1. Get user's subscription
2. Require active Stripe customer
3. Create Billing Portal session
4. Return portal URL for redirect

#### 3. `GET /billing/subscription`

Get current user's subscription details with feature limits.

**Response:**
```json
{
  "subscription": {
    "id": "uuid",
    "userId": "ulid",
    "planTier": "pro",
    "billingInterval": "month",
    "status": "active",
    "currentPeriodEnd": "2025-01-18T00:00:00Z",
    "cancelAtPeriodEnd": false
  },
  "limits": {
    "aiLimit": 10.0,
    "storageLimit": 5368709120
  }
}
```

#### 4. `POST /billing/subscription/cancel`

Cancel subscription (end of period or immediately).

**Request:**
```json
{
  "cancelAtPeriodEnd": true
}
```

**Response:**
```json
{
  "subscription": { ... },
  "message": "Subscription will be canceled at end of period"
}
```

#### 5. `POST /billing/webhooks/stripe` ⚠️ No Auth

Handle Stripe webhook events (signature verification only).

**Critical Events:**
- `customer.subscription.created` - New subscription activated
- `customer.subscription.updated` - Status/plan changed
- `customer.subscription.deleted` - Subscription canceled
- `invoice.payment_succeeded` - Payment successful
- `invoice.payment_failed` - Payment failed

**Logic:**
1. Verify webhook signature using `STRIPE_WEBHOOK_SECRET`
2. Parse event type and data
3. Dispatch to appropriate handler
4. Log event to `stripe_webhook_events` table
5. Return 200 OK (Stripe requires quick response)

### Stripe Webhook Handlers

#### `handle_subscription_created(subscription)`

```python
async def handle_subscription_created(self, subscription: stripe.Subscription):
    # Extract data
    customer_id = subscription.customer
    price_id = subscription.items.data[0].price.id
    status = subscription.status

    # Find user by stripe_customer_id
    user = await self.repo.get_user_by_stripe_customer_id(customer_id)

    # Create/update subscription in database
    await self.repo.upsert_subscription(
        user_id=user.id,
        stripe_subscription_id=subscription.id,
        stripe_price_id=price_id,
        plan_tier=self._get_plan_tier_from_price(price_id),
        status=status,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
    )

    # Update user.is_premium
    await self.repo.update_user_premium_status(user.id, is_premium=True)

    # Log to subscription_history
    await self.repo.create_subscription_history_entry(...)
```

#### `handle_subscription_updated(subscription)`

Handles status changes, upgrades, downgrades, renewals.

**Key scenarios:**
- Status change: `active` → `past_due` (payment failed)
- Plan change: Pro monthly → Pro annual
- Cancellation scheduled: `cancel_at_period_end = true`

#### `handle_subscription_deleted(subscription)`

Subscription canceled or expired.

**Actions:**
1. Update subscription status to 'canceled'
2. Set `user.is_premium = false` if not admin/owner
3. Log to history

#### `handle_payment_succeeded(invoice)`

Successful payment for subscription renewal.

**Actions:**
1. Ensure subscription status is 'active'
2. Log to history

#### `handle_payment_failed(invoice)`

Payment failed (card declined, insufficient funds, etc.).

**Actions:**
1. Update subscription status to 'past_due'
2. Optionally send notification email
3. Log to history
4. Allow grace period before access revocation

### Frontend Implementation

#### TypeScript Types

```typescript
export type PlanTier = 'free' | 'pro' | 'business'
export type BillingInterval = 'month' | 'year'
export type SubscriptionStatus =
  | 'active'
  | 'canceled'
  | 'past_due'
  | 'unpaid'
  | 'incomplete'
  | 'trialing'

export interface Subscription {
  id: string
  userId: string
  planTier: PlanTier
  billingInterval?: BillingInterval
  status: SubscriptionStatus
  currentPeriodStart?: string
  currentPeriodEnd?: string
  cancelAtPeriodEnd: boolean
  canceledAt?: string
  createdAt: string
  updatedAt: string
}

export interface PlanDetails {
  tier: PlanTier
  name: string
  price: number
  interval: BillingInterval
  features: string[]
  aiLimit: number | null  // null = unlimited
  storageLimit: number    // bytes
  highlighted?: boolean
}

export interface SubscriptionWithLimits {
  subscription: Subscription
  limits: {
    aiLimit: number | null
    storageLimit: number
  }
}
```

#### `useSubscription()` Composable

```typescript
export function useSubscription() {
  const queryClient = useQueryClient()
  const { user } = usePermissions()

  // Fetch subscription with TanStack Query
  const { data: subscriptionData, isLoading } = useQuery({
    queryKey: ['subscription', user.value?.id],
    queryFn: () => billingService.getSubscription(),
    enabled: computed(() => !!user.value),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const subscription = computed(() => subscriptionData.value?.subscription)
  const limits = computed(() => subscriptionData.value?.limits)

  // Computed properties
  const isFreeTier = computed(() => subscription.value?.planTier === 'free')
  const isProTier = computed(() => subscription.value?.planTier === 'pro')
  const isBusinessTier = computed(() => subscription.value?.planTier === 'business')
  const canUpgrade = computed(() => subscription.value?.planTier !== 'business')

  // Cancel subscription mutation
  const { mutateAsync: cancelSubscription, isPending: isCanceling } = useMutation({
    mutationFn: (cancelAtPeriodEnd: boolean) =>
      billingService.cancelSubscription(cancelAtPeriodEnd),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] })
    },
  })

  return {
    subscription,
    limits,
    isLoading,
    isFreeTier,
    isProTier,
    isBusinessTier,
    canUpgrade,
    cancelSubscription,
    isCanceling,
  }
}
```

#### Pricing Page Flow

**User Journey:**

1. **Unauthenticated User:**
   - Views pricing page at `/pricing`
   - Selects plan (Free/Pro/Business)
   - Redirected to `/auth/login` or `/auth/register`

2. **Authenticated User (Free Tier):**
   - Views pricing page
   - Clicks "Upgrade to Pro" or "Upgrade to Business"
   - Frontend calls `POST /billing/checkout` with price ID
   - Backend returns Stripe Checkout URL
   - User redirected to Stripe Checkout (hosted page)
   - Completes payment on Stripe
   - Redirected back to app (success URL: `/settings/billing?success=true`)

3. **Authenticated User (Pro/Business Tier):**
   - Views current plan in settings
   - Clicks "Manage Billing"
   - Frontend calls `POST /billing/portal`
   - Backend returns Stripe Billing Portal URL
   - User redirected to portal
   - Can update payment method, view invoices, cancel subscription

#### Component: `PricingCard.vue`

```vue
<script setup lang="ts">
interface Props {
  plan: PlanDetails
  currentTier?: PlanTier
}

const props = defineProps<Props>()
const emit = defineEmits<{
  select: [plan: PlanDetails]
}>()

const isCurrentPlan = computed(() => props.currentTier === props.plan.tier)
const buttonLabel = computed(() => {
  if (isCurrentPlan.value) return 'Current Plan'
  if (props.plan.tier === 'free') return 'Get Started'
  return `Upgrade to ${props.plan.name}`
})
</script>

<template>
  <Card :class="{ 'border-primary': plan.highlighted }">
    <CardHeader>
      <CardTitle>{{ plan.name }}</CardTitle>
      <CardDescription>
        <span class="text-3xl font-bold">${{ plan.price }}</span>
        <span class="text-muted-foreground">
          /{{ plan.interval === 'month' ? 'mo' : 'yr' }}
        </span>
      </CardDescription>
    </CardHeader>
    <CardContent>
      <ul class="space-y-2">
        <li v-for="feature in plan.features" :key="feature">
          <Check class="inline size-4 text-primary" />
          {{ feature }}
        </li>
      </ul>
    </CardContent>
    <CardFooter>
      <Button
        :variant="plan.highlighted ? 'default' : 'outline'"
        :disabled="isCurrentPlan"
        class="w-full"
        @click="emit('select', plan)"
      >
        {{ buttonLabel }}
      </Button>
    </CardFooter>
  </Card>
</template>
```

#### Component: `SubscriptionStatusCard.vue`

Displays current subscription status in Settings page.

**Features:**
- Plan badge (Free/Pro/Business)
- Current limits (AI, Storage)
- Next billing date
- "Manage Billing" button → Stripe Billing Portal
- Cancellation warning if `cancel_at_period_end = true`

## Configuration

### Environment Variables

#### Backend `.env`

```bash
# -----------------------------------------------------------------------------
# Stripe Billing Configuration
# -----------------------------------------------------------------------------
STRIPE_ENABLED=true

# API Keys (get from: https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Webhook Secret (get from: https://dashboard.stripe.com/webhooks)
STRIPE_WEBHOOK_SECRET=whsec_...

# Price IDs (created in Stripe Dashboard)
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_ANNUAL_PRICE_ID=price_...
STRIPE_BUSINESS_MONTHLY_PRICE_ID=price_...
STRIPE_BUSINESS_ANNUAL_PRICE_ID=price_...
```

#### Frontend `.env`

```bash
# ============================================
# Stripe Configuration (Frontend)
# ============================================
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_STRIPE_PRO_MONTHLY_PRICE_ID=price_...
VITE_STRIPE_PRO_ANNUAL_PRICE_ID=price_...
VITE_STRIPE_BUSINESS_MONTHLY_PRICE_ID=price_...
VITE_STRIPE_BUSINESS_ANNUAL_PRICE_ID=price_...
```

### Stripe Dashboard Setup

#### 1. Create Products

**Product 1: Pro Plan**
- Name: "Pro Plan"
- Description: "Enhanced features with higher limits"
- Statement descriptor: "GEARSTACK PRO"

**Product 2: Business Plan**
- Name: "Business Plan"
- Description: "Advanced features with highest limits"
- Statement descriptor: "GEARSTACK BIZ"

#### 2. Create Prices

For each product, create two prices:

**Pro Monthly:**
- Amount: $4.99 USD
- Billing period: Monthly
- ID: `price_promonthly...` (copy to env)

**Pro Annual:**
- Amount: $49.00 USD (17% discount)
- Billing period: Yearly
- ID: `price_proannual...` (copy to env)

**Business Monthly:**
- Amount: $14.99 USD
- Billing period: Monthly
- ID: `price_businessmonthly...`

**Business Annual:**
- Amount: $149.00 USD (17% discount)
- Billing period: Yearly
- ID: `price_businessannual...`

#### 3. Configure Webhook

1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://yourdomain.com/api/billing/webhooks/stripe`
4. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET`

#### 4. Configure Billing Portal

1. Go to: https://dashboard.stripe.com/settings/billing/portal
2. Enable customer portal
3. Configure:
   - ✅ Update payment method
   - ✅ View invoice history
   - ✅ Cancel subscription
   - ✅ Update subscription (upgrade/downgrade)
4. Set business information (logo, support email)

## Migration Strategy

### Database Migration: `047_add_billing_tables.py`

**Key Steps:**

1. Create `subscriptions` table (with `is_grandfathered` field)
2. Create `stripe_webhook_events` table
3. Create `subscription_history` table
4. Create indexes
5. **Migrate existing premium users to grandfathered Pro:**
   ```sql
   INSERT INTO subscriptions (user_id, plan_tier, status, is_grandfathered, created_at, updated_at)
   SELECT
       id,
       'pro',
       'active',
       TRUE,  -- is_grandfathered for lifetime access
       created_at,
       NOW()
   FROM users
   WHERE is_premium = TRUE
   ON CONFLICT (user_id) DO NOTHING
   ```
6. Update `feature_limits` constraint to include 'business' role
7. Insert default limits for 'business' tier:
   - AI limit: $50
   - Storage limit: 50GB (53,687,091,200 bytes)
8. Update 'premium' role limits (Pro tier):
   - AI limit: $10
   - Storage limit: 5GB (5,368,709,120 bytes)
9. Add `openrouter_api_token` field to `users` table (for Free tier BYOK)

### Rollback Plan

If migration fails or needs rollback:

```sql
-- Drop tables in reverse order
DROP TABLE IF EXISTS subscription_history CASCADE;
DROP TABLE IF EXISTS stripe_webhook_events CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;

-- Revert feature_limits constraint
ALTER TABLE feature_limits
DROP CONSTRAINT IF EXISTS valid_role;
ALTER TABLE feature_limits
ADD CONSTRAINT valid_role
CHECK (role IN ('user', 'premium', 'admin', 'owner'));

-- Delete business role limits
DELETE FROM feature_limits WHERE role = 'business';
```

### Backward Compatibility

**Maintain `is_premium` flag:**

The `UserDB.is_premium` field will be automatically synced by webhook handlers:

```python
# In webhook_handler.py
async def sync_user_premium_status(user_id: str):
    subscription = await get_subscription(user_id)

    is_premium = (
        subscription.status == 'active'
        and subscription.plan_tier in ['pro', 'business']
    )

    await update_user(user_id, is_premium=is_premium)
```

**Existing code continues to work:**
- `usePermissions().canUsePremiumFeatures` → checks `is_premium`
- Admin panel toggles → create/update subscription record
- All existing premium checks → unchanged

**New code can use granular checks:**
```typescript
const { subscription } = useSubscription()
const canUseAdvancedAI = subscription.value?.planTier === 'business'
```

## Testing Strategy

### Test Mode

**Always start with Stripe Test Mode:**
- Use test API keys: `sk_test_...`, `pk_test_...`
- Test webhook secret: `whsec_test_...`
- Test cards:
  - Success: `4242 4242 4242 4242`
  - Decline: `4000 0000 0000 0002`
  - Auth required: `4000 0025 0000 3155`

### Local Webhook Testing

**Use Stripe CLI:**

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/api/billing/webhooks/stripe

# Trigger test events
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
```

### Test Scenarios

#### 1. Checkout Flow
- ✅ Unauthenticated user views pricing → redirected to login
- ✅ Authenticated user clicks "Upgrade to Pro" → checkout session created
- ✅ User redirected to Stripe Checkout
- ✅ User completes payment with test card
- ✅ User redirected back to app with success message
- ✅ Subscription created in database
- ✅ User sees "Pro" badge in settings
- ✅ Feature limits updated

#### 2. Webhook Processing
- ✅ `subscription.created` → subscription record created
- ✅ `subscription.updated` → status/plan updated
- ✅ `subscription.deleted` → user downgraded to free
- ✅ `payment_succeeded` → subscription remains active
- ✅ `payment_failed` → subscription marked as past_due
- ✅ Webhook signature verification rejects invalid signatures
- ✅ Duplicate webhook events (same `stripe_event_id`) ignored

#### 3. Billing Portal
- ✅ User clicks "Manage Billing" → portal session created
- ✅ User redirected to Stripe Billing Portal
- ✅ User can view invoices
- ✅ User can update payment method
- ✅ User can cancel subscription
- ✅ Cancellation with `cancel_at_period_end=true` allows access until end
- ✅ Immediate cancellation revokes access immediately

#### 4. Plan Changes
- ✅ Upgrade: Free → Pro (payment required)
- ✅ Upgrade: Pro → Business (prorated charge)
- ✅ Downgrade: Business → Pro (credit applied to next invoice)
- ✅ Downgrade at period end: Access maintained until current period ends

#### 5. Payment Failures
- ✅ Payment fails → subscription status = 'past_due'
- ✅ Grace period: User retains access for X days
- ✅ Multiple failures → subscription status = 'unpaid'
- ✅ Access revoked after grace period
- ✅ User notified via email (if email notifications implemented)

#### 6. Edge Cases
- ✅ User with active subscription tries to checkout again → prevented
- ✅ Admin manually sets `is_premium=true` → subscription record created
- ✅ User deletes account → subscription canceled via Stripe
- ✅ Webhook arrives before checkout redirect → handled gracefully
- ✅ Network error during webhook processing → retried by Stripe

### Backend Unit Tests

```python
# backend/tests/billing/test_billing_service.py

async def test_create_checkout_session():
    """Test checkout session creation"""
    service = BillingService(repo, stripe_client)
    user = create_test_user(is_premium=False)

    session_url = await service.create_checkout_session(
        user=user,
        price_id="price_test_pro_monthly",
        plan_tier=PlanTier.PRO,
        billing_interval=BillingInterval.MONTH
    )

    assert session_url.startswith("https://checkout.stripe.com")

async def test_webhook_subscription_created():
    """Test subscription created webhook handler"""
    handler = StripeWebhookHandler(repo)
    subscription = create_mock_stripe_subscription(
        customer="cus_test123",
        status="active",
        price_id="price_test_pro_monthly"
    )

    await handler.handle_subscription_created(subscription)

    # Verify subscription created in database
    db_subscription = await repo.get_subscription_by_stripe_id(subscription.id)
    assert db_subscription.plan_tier == PlanTier.PRO
    assert db_subscription.status == SubscriptionStatus.ACTIVE

    # Verify user.is_premium updated
    user = await repo.get_user(db_subscription.user_id)
    assert user.is_premium is True

async def test_sync_user_premium_status():
    """Test user premium status sync"""
    service = BillingService(repo, stripe_client)
    user = create_test_user()
    subscription = create_test_subscription(
        user_id=user.id,
        plan_tier=PlanTier.PRO,
        status=SubscriptionStatus.ACTIVE
    )

    await service.sync_user_premium_status(user.id)

    updated_user = await repo.get_user(user.id)
    assert updated_user.is_premium is True
```

### Frontend Integration Tests

```typescript
// src/modules/billing/__tests__/useSubscription.test.ts

describe('useSubscription', () => {
  it('should load subscription data', async () => {
    const { subscription, isLoading } = useSubscription()

    await waitFor(() => expect(isLoading.value).toBe(false))

    expect(subscription.value).toMatchObject({
      planTier: 'pro',
      status: 'active',
    })
  })

  it('should handle checkout flow', async () => {
    const { result } = renderComposable(() => useCheckout())

    await result.createCheckout('pro', 'month')

    expect(window.location.href).toContain('checkout.stripe.com')
  })

  it('should cancel subscription', async () => {
    const { subscription, cancelSubscription } = useSubscription()

    await cancelSubscription(true)

    expect(subscription.value?.cancelAtPeriodEnd).toBe(true)
  })
})
```

## Implementation Phases

### Phase 1: Backend Foundation (Week 1)

**Goal:** Database schema and core models

**Tasks:**
1. ✅ Add `stripe>=8.0.0` to `requirements.txt`
2. ✅ Create `backend/app/modules/billing/` directory structure
3. ✅ Create migration `047_add_billing_tables.py`
4. ✅ Implement `db_models.py` (SubscriptionDB, StripeWebhookEventDB, SubscriptionHistoryDB)
5. ✅ Implement `repository.py` (database operations)
6. ✅ Implement `stripe_client.py` (Stripe SDK wrapper)
7. ✅ Update `config.py` with StripeSettings
8. ✅ Update `.env.example` with Stripe variables

**Deliverables:**
- Database tables created and tested
- Stripe client configured
- Repository layer functional

**Critical Files:**
- `backend/requirements.txt`
- `backend/migrations/047_add_billing_tables.py`
- `backend/app/modules/billing/db_models.py`
- `backend/app/modules/billing/repository.py`
- `backend/app/modules/billing/stripe_client.py`
- `backend/app/core/config.py`

### Phase 2: Backend API & Webhooks (Week 2)

**Goal:** API endpoints and webhook processing

**Tasks:**
1. ✅ Implement `service.py` (business logic)
2. ✅ Implement `schemas.py` (Pydantic request/response models)
3. ✅ Implement `router.py` (API endpoints)
4. ✅ Implement `webhook_handler.py` (event processors)
5. ✅ Implement `exceptions.py` (custom errors)
6. ✅ Register billing router in `app_factory.py`
7. ✅ Test checkout endpoint with Postman
8. ✅ Test webhook handling with Stripe CLI
9. ✅ Implement user premium status sync
10. ✅ Write unit tests

**Deliverables:**
- All API endpoints functional
- Webhook processing working
- Automated tests passing

**Critical Files:**
- `backend/app/modules/billing/service.py`
- `backend/app/modules/billing/router.py`
- `backend/app/modules/billing/webhook_handler.py`
- `backend/app/core/app_factory.py`
- `backend/tests/billing/test_*.py`

### Phase 3: Frontend Foundation (Week 3)

**Goal:** Frontend module structure and state management

**Tasks:**
1. ✅ Create `src/modules/billing/` directory structure
2. ✅ Define TypeScript types (`subscription.type.ts`)
3. ✅ Implement `billingService.ts` (API client)
4. ✅ Implement `useSubscription.ts` composable
5. ✅ Implement `useCheckout.ts` composable
6. ✅ Update `.env.example` with frontend Stripe variables
7. ✅ Create `routes.ts` for billing module
8. ✅ Test composables with mock data

**Deliverables:**
- Billing module structure complete
- TanStack Query integration working
- Type-safe API client

**Critical Files:**
- `src/modules/billing/types/subscription.type.ts`
- `src/modules/billing/services/billingService.ts`
- `src/modules/billing/composables/useSubscription.ts`
- `src/modules/billing/composables/useCheckout.ts`
- `src/modules/billing/routes.ts`

### Phase 4: Frontend UI (Week 4)

**Goal:** User-facing pricing and billing pages

**Tasks:**
1. ✅ Create `PricingCard.vue`
2. ✅ Create `PricingTable.vue`
3. ✅ Create `BillingIntervalToggle.vue`
4. ✅ Create `SubscriptionStatusCard.vue`
5. ✅ Create `UpgradePromptBanner.vue`
6. ✅ Create `PricingPage.vue`
7. ✅ Create `BillingPage.vue`
8. ✅ Add i18n translations (en.json, pl.json)
9. ✅ Merge billing routes into main router
10. ✅ Add "Pricing" link to navigation
11. ✅ Add `SubscriptionStatusCard` to `SettingsPage.vue`
12. ✅ Test full checkout flow end-to-end

**Deliverables:**
- Pricing page live at `/pricing`
- Billing page live at `/settings/billing`
- Full checkout flow functional
- Responsive design

**Critical Files:**
- `src/modules/billing/pages/PricingPage.vue`
- `src/modules/billing/pages/BillingPage.vue`
- `src/modules/billing/components/*.vue`
- `src/modules/settings/pages/SettingsPage.vue`
- `src/router/routes.ts`

### Phase 5: Integration & Polish (Week 5)

**Goal:** Admin integration and UX refinements

**Tasks:**
1. ✅ Update Admin Panel to display subscription data
2. ✅ Add subscription column to Admin Users table
3. ✅ Add "Grant Pro/Business" action in admin panel
4. ✅ Implement upgrade prompts for free users
5. ✅ Add subscription status badge to user profile
6. ✅ Test all webhook event types
7. ✅ Test migration with production-like data
8. ✅ Add error handling and user feedback (toasts)
9. ✅ Add loading states and animations
10. ✅ Conduct user acceptance testing

**Deliverables:**
- Admin features complete
- Upgrade prompts working
- All edge cases handled
- Polished UX

**Critical Files:**
- `src/modules/admin/components/UsersTable.vue`
- `src/modules/user/pages/ProfilePage.vue`
- Various components (loading states, error handling)

### Phase 6: Production Setup (Week 6)

**Goal:** Production Stripe configuration and deployment

**Tasks:**
1. ✅ Create Stripe Products in Dashboard (Pro, Business)
2. ✅ Create Stripe Prices (4 total: Pro monthly/annual, Business monthly/annual)
3. ✅ Copy Price IDs to environment variables
4. ✅ Create webhook endpoint in Stripe Dashboard
5. ✅ Copy webhook secret to environment
6. ✅ Configure Stripe Billing Portal settings
7. ✅ Set business information (logo, support email)
8. ✅ Switch to production API keys
9. ✅ Run migration in production
10. ✅ Deploy backend
11. ✅ Deploy frontend
12. ✅ Verify webhook connectivity
13. ✅ Test checkout in production (test mode first!)
14. ✅ Monitor webhook logs
15. ✅ Create documentation for team

**Deliverables:**
- Production Stripe account fully configured
- Application deployed and operational
- Webhooks processing correctly
- Documentation complete

## Security Considerations

### 1. Webhook Signature Verification

**Critical:** Always verify webhook signatures to prevent spoofing.

```python
try:
    event = stripe.Webhook.construct_event(
        payload=request_body,
        sig_header=signature_header,
        secret=webhook_secret
    )
except stripe.error.SignatureVerificationError:
    raise HTTPException(status_code=400, detail="Invalid signature")
```

### 2. Price ID Validation

Prevent users from submitting arbitrary price IDs:

```python
VALID_PRICE_IDS = {
    'pro_month': settings.stripe.pro_monthly_price_id,
    'pro_year': settings.stripe.pro_annual_price_id,
    'business_month': settings.stripe.business_monthly_price_id,
    'business_year': settings.stripe.business_annual_price_id,
}

if price_id not in VALID_PRICE_IDS.values():
    raise HTTPException(status_code=400, detail="Invalid price ID")
```

### 3. Customer ID Verification

Ensure users can only access their own subscriptions:

```python
subscription = await repo.get_subscription_by_user_id(current_user.id)
if not subscription or subscription.stripe_customer_id != customer_id:
    raise HTTPException(status_code=403, detail="Access denied")
```

### 4. API Key Management

- **Never commit API keys to git**
- Use `.env` files (ignored by git)
- Rotate keys periodically
- Use separate keys for test/production

### 5. HTTPS Required

- Stripe webhooks require HTTPS
- Use TLS certificates (Let's Encrypt)
- Enforce HTTPS in production

## Error Handling

### Stripe API Errors

```python
try:
    session = stripe.checkout.Session.create(...)
except stripe.error.CardError as e:
    # Card declined
    raise HTTPException(status_code=400, detail=str(e))
except stripe.error.RateLimitError as e:
    # Rate limit exceeded
    raise HTTPException(status_code=429, detail="Rate limit exceeded")
except stripe.error.InvalidRequestError as e:
    # Invalid parameters
    raise HTTPException(status_code=400, detail=str(e))
except stripe.error.AuthenticationError as e:
    # Invalid API key
    logger.error(f"Stripe authentication error: {e}")
    raise HTTPException(status_code=500, detail="Payment system error")
except stripe.error.StripeError as e:
    # Generic Stripe error
    logger.error(f"Stripe error: {e}")
    raise HTTPException(status_code=500, detail="Payment system error")
```

### User-Facing Error Messages

- ❌ "Stripe error: Invalid API key" (exposes internals)
- ✅ "Unable to process payment. Please try again later." (user-friendly)

### Webhook Processing Errors

```python
try:
    await handler.handle_event(event)
except Exception as e:
    # Log error but return 200 to prevent Stripe retries
    logger.error(f"Webhook processing error: {e}")
    await repo.log_webhook_error(event.id, str(e))
    # Return 200 to acknowledge receipt
    return {"status": "error_logged"}
```

## Monitoring & Logging

### 1. Webhook Event Logging

All webhook events stored in `stripe_webhook_events` table:
- Event ID (for deduplication)
- Event type
- Full payload (JSONB)
- Processing status
- Error messages

### 2. Subscription Metrics

Track key metrics:
- Active subscriptions by tier (Free/Pro/Business)
- Monthly recurring revenue (MRR)
- Churn rate
- Upgrade/downgrade flows
- Payment failure rate

### 3. Error Tracking

Use existing Sentry integration:
- Tag errors with `module:billing`
- Track payment failure patterns
- Monitor webhook processing failures
- Alert on critical errors

### 4. Alerts

Set up alerts for:
- Webhook endpoint downtime
- High payment failure rate (>5%)
- Unusual cancellation spike
- API key expiration

## Future Enhancements

### 1. Promo Codes ✨

Stripe supports promotional codes natively:
- Already enabled: `allow_promotion_codes=True` in checkout
- Create codes in Stripe Dashboard
- Track redemption in subscription metadata

### 2. Usage-Based Billing 📊

Meter actual AI usage and charge accordingly:
- Report usage to Stripe: `stripe.billing.Meter.create_event()`
- Define usage tiers in Stripe
- Invoice based on consumption
- Implement overage charges

### 3. Team/Organization Plans 👥

Multi-user subscriptions:
- Seat-based pricing (e.g., $10/user/month)
- Team management UI
- Invite system
- Shared workspaces

### 4. Lifetime Access 🎉

One-time payment option:
- Use Stripe Payment Links (not subscriptions)
- Manual grant of lifetime access
- Special role: `lifetime_premium`

### 5. Annual Discount Display 💰

Show savings prominently:
```vue
<Badge variant="success">
  Save {{ annualSavingsPercentage }}% with annual billing
</Badge>
```

Calculate: `(monthly × 12 - annual) / (monthly × 12) × 100`

### 6. Grace Period for Failed Payments ⏰

Allow access for X days after payment failure:
```python
grace_period_days = 3
is_in_grace = (
    subscription.status == 'past_due'
    and (now - subscription.current_period_end).days <= grace_period_days
)
can_access = subscription.status == 'active' or is_in_grace
```

## Critical Files Summary

### Backend (New Files)

| Priority | File | Purpose |
|----------|------|---------|
| 🔴 Critical | `backend/migrations/047_add_billing_tables.py` | Database schema migration |
| 🔴 Critical | `backend/app/modules/billing/webhook_handler.py` | Process Stripe webhook events |
| 🔴 Critical | `backend/app/modules/billing/service.py` | Core business logic |
| 🟡 High | `backend/app/modules/billing/router.py` | API endpoints |
| 🟡 High | `backend/app/modules/billing/db_models.py` | SQLAlchemy models |
| 🟡 High | `backend/app/modules/billing/repository.py` | Database operations |
| 🟢 Medium | `backend/app/modules/billing/stripe_client.py` | Stripe SDK wrapper |
| 🟢 Medium | `backend/app/modules/billing/schemas.py` | Pydantic schemas |

### Backend (Modified Files)

| Priority | File | Changes |
|----------|------|---------|
| 🟡 High | `backend/app/core/config.py` | Add StripeSettings |
| 🟡 High | `backend/app/core/app_factory.py` | Register billing router |
| 🟡 High | `backend/requirements.txt` | Add `stripe>=8.0.0` |
| 🟢 Medium | `backend/app/modules/users/router.py` | Include subscription in `/users/me` |

### Frontend (New Files)

| Priority | File | Purpose |
|----------|------|---------|
| 🔴 Critical | `src/modules/billing/composables/useSubscription.ts` | Subscription state management |
| 🔴 Critical | `src/modules/billing/pages/PricingPage.vue` | Public pricing page |
| 🟡 High | `src/modules/billing/services/billingService.ts` | API client |
| 🟡 High | `src/modules/billing/components/SubscriptionStatusCard.vue` | Settings integration |
| 🟡 High | `src/modules/billing/types/subscription.type.ts` | TypeScript types |
| 🟢 Medium | `src/modules/billing/pages/BillingPage.vue` | Billing management |
| 🟢 Medium | `src/modules/billing/components/PricingCard.vue` | Plan display |
| 🟢 Medium | `src/modules/billing/components/PricingTable.vue` | Plan comparison |

### Frontend (Modified Files)

| Priority | File | Changes |
|----------|------|---------|
| 🟡 High | `src/modules/settings/pages/SettingsPage.vue` | Add SubscriptionStatusCard |
| 🟡 High | `src/router/routes.ts` | Merge billing routes |
| 🟢 Medium | `src/shared/composables/usePermissions.ts` | Optional: granular tier checks |

## Rollout Checklist

### Pre-Deployment

- [ ] All backend tests passing
- [ ] All frontend tests passing
- [ ] Code reviewed and approved
- [ ] Documentation complete
- [ ] Stripe test mode fully tested
- [ ] Environment variables documented

### Stripe Setup

- [ ] Stripe account created/verified
- [ ] Products created (Pro, Business)
- [ ] Prices created (4 total)
- [ ] Price IDs copied to env
- [ ] Webhook endpoint created
- [ ] Webhook secret copied to env
- [ ] Billing Portal configured
- [ ] Business info set (logo, support email)

### Deployment

- [ ] Database backup taken
- [ ] Migration script reviewed
- [ ] Migration executed successfully
- [ ] Backend deployed
- [ ] Frontend deployed
- [ ] Webhook endpoint accessible (test with Stripe)
- [ ] Environment variables set correctly

### Post-Deployment

- [ ] Test checkout flow in production test mode
- [ ] Verify webhooks processing correctly
- [ ] Check subscription creation
- [ ] Check user premium status sync
- [ ] Monitor error logs
- [ ] Test cancellation flow
- [ ] Test billing portal access

### Production Go-Live

- [ ] Switch to production API keys
- [ ] Final smoke test with real (refundable) transaction
- [ ] Monitor first real subscriptions
- [ ] Verify invoices generated correctly
- [ ] Customer support briefed
- [ ] Marketing assets ready (if applicable)

## Support & Troubleshooting

### Common Issues

**Issue:** Webhook not receiving events
- **Check:** Is endpoint publicly accessible?
- **Check:** Is HTTPS configured correctly?
- **Check:** Is webhook secret correct?
- **Solution:** Test with Stripe CLI: `stripe trigger customer.subscription.created`

**Issue:** Checkout session creation fails
- **Check:** Are price IDs correct?
- **Check:** Is Stripe API key valid?
- **Check:** Are environment variables loaded?
- **Solution:** Check backend logs for Stripe error messages

**Issue:** User premium status not updating
- **Check:** Are webhooks being processed?
- **Check:** Is `sync_user_premium_status()` being called?
- **Check:** Database logs in `subscription_history` table
- **Solution:** Manually trigger webhook event via Stripe Dashboard

**Issue:** Subscription shows wrong plan tier
- **Check:** Price ID mapping in code
- **Check:** Recent webhook events in database
- **Solution:** Manually sync from Stripe: `subscription = stripe.Subscription.retrieve(sub_id)`

### Debug Mode

Enable verbose logging:

```python
# backend/app/modules/billing/service.py
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
```

### Stripe Dashboard Links

- API Keys: https://dashboard.stripe.com/apikeys
- Webhooks: https://dashboard.stripe.com/webhooks
- Products: https://dashboard.stripe.com/products
- Customers: https://dashboard.stripe.com/customers
- Subscriptions: https://dashboard.stripe.com/subscriptions
- Events: https://dashboard.stripe.com/events
- Logs: https://dashboard.stripe.com/logs

## Conclusion

This implementation plan provides a complete blueprint for integrating Stripe subscriptions into Gear Stack. The architecture leverages existing patterns, maintains backward compatibility, and follows industry best practices for payment processing.

**Key Success Factors:**
- Stripe Checkout (hosted) minimizes PCI compliance burden
- Webhook-driven sync ensures data consistency
- Backward-compatible `is_premium` flag eases migration
- Clear separation of concerns (module-based architecture)
- Comprehensive testing strategy
- Phased implementation reduces risk

**Estimated Timeline:** 6 weeks (1 week per phase)

**Next Steps:**
1. Review and approve this plan
2. Set up Stripe account and products
3. Begin Phase 1: Backend Foundation

---

**Document Version:** 2.0
**Last Updated:** 2025-12-18
**Author:** Claude Code Assistant
**Status:** ✅ Patterns Verified & Aligned with Codebase - Ready for Implementation

---

## Critical Pattern Notes

**⚠️ Before Implementation, Review:**
- **[Pattern Verification Document](./stripe-pattern-verification.md)** - Detailed analysis of verified codebase patterns
- **Key Changes from Initial Plan:**
  - i18n uses `.ts` files (NOT `.json`)
  - Database models use `DateTime(timezone=True)` and `datetime.now(UTC)`
  - Added `is_grandfathered` field for lifetime Pro access
  - Final pricing: Pro $4.99/mo, Business $14.99/mo
  - Free tier requires BYOK (own OpenRouter token)

---

## Related Documents

- **[Requirements](./stripe-subscription-requirements.md)** - Business requirements
- **[Pattern Verification](./stripe-pattern-verification.md)** - Verified codebase patterns
