/**
 * TypeScript types for Stripe billing module
 */

export type PlanTier = 'free' | 'pro' | 'business'

export type BillingInterval = 'monthly' | 'annual'

export type SubscriptionStatus = 'active' | 'canceled' | 'past_due' | 'unpaid' | 'incomplete'

export interface Subscription {
  id: string
  userId: string
  stripeCustomerId: string | null
  stripeSubscriptionId: string | null
  planTier: PlanTier
  billingInterval: BillingInterval | null
  status: SubscriptionStatus
  currentPeriodStart: string | null
  currentPeriodEnd: string | null
  cancelAtPeriodEnd: boolean
  isGrandfathered: boolean
  createdAt: string
  updatedAt: string
}

export interface SubscriptionLimits {
  planTier: PlanTier
  aiMonthlyTokenLimit: number
  storageLimit: number
  canExportData: boolean
  canUseAdvancedFeatures: boolean
  requiresByok: boolean
}

export interface CreateCheckoutSessionRequest {
  planTier: Exclude<PlanTier, 'free'>
  billingInterval: BillingInterval
  successUrl: string
  cancelUrl: string
}

export interface CheckoutSessionResponse {
  sessionId: string
  sessionUrl: string
}

export interface CreatePortalSessionRequest {
  returnUrl: string
}

export interface PortalSessionResponse {
  sessionUrl: string
}

export interface UpdateOpenRouterTokenRequest {
  openrouterApiToken: string | null
}

export interface PlanFeatures {
  tier: PlanTier
  name: string
  price: {
    monthly: number
    annual: number
    annualMonthly: number // Annual price divided by 12
  }
  features: string[]
  limits: {
    aiTokens: number
    storage: number
  }
  popular?: boolean
}

export const PLAN_FEATURES: Record<PlanTier, PlanFeatures> = {
  free: {
    tier: 'free',
    name: 'Free',
    price: {
      monthly: 0,
      annual: 0,
      annualMonthly: 0,
    },
    features: [
      'Basic gear management',
      'Data export (JSON/Markdown)',
      'BYOK: Bring Your Own API Key (OpenRouter)',
      '100 MB storage',
    ],
    limits: {
      aiTokens: 0, // BYOK required
      storage: 100 * 1024 * 1024, // 100 MB
    },
  },
  pro: {
    tier: 'pro',
    name: 'Pro',
    price: {
      monthly: 4.99,
      annual: 49,
      annualMonthly: 4.08,
    },
    features: [
      'Everything in Free',
      'AI-powered gear recommendations',
      '~$1 worth of AI tokens/month',
      'Advanced features',
      '5 GB storage',
    ],
    limits: {
      aiTokens: 1_000_000,
      storage: 5 * 1024 * 1024 * 1024, // 5 GB
    },
    popular: true,
  },
  business: {
    tier: 'business',
    name: 'Business',
    price: {
      monthly: 14.99,
      annual: 149,
      annualMonthly: 12.42,
    },
    features: [
      'Everything in Pro',
      'Priority AI processing',
      '~$10 worth of AI tokens/month',
      'Premium support',
      '50 GB storage',
    ],
    limits: {
      aiTokens: 10_000_000,
      storage: 50 * 1024 * 1024 * 1024, // 50 GB
    },
  },
}

export const ANNUAL_DISCOUNT_PERCENT = 17
