<script setup lang="ts">
import { ref } from 'vue'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { BillingInterval } from '../types'
import PlanCard from '../components/PlanCard.vue'
import SubscriptionCard from '../components/SubscriptionCard.vue'
import { useSubscription } from '../composables/useSubscription'
import { PLAN_FEATURES } from '../types'

const { currentPlan, upgradeToPlan, isUpgrading } = useSubscription()

const billingInterval = ref<BillingInterval>('monthly')

const handleSelectPlan = async (planTier: 'pro' | 'business') => {
  await upgradeToPlan(planTier, billingInterval.value)
}
</script>

<template>
  <div class="container mx-auto space-y-8 py-8">
    <div>
      <h1 class="text-3xl font-bold">
        Billing & Subscription
      </h1>
      <p class="mt-2 text-muted-foreground">
        Manage your subscription and billing information
      </p>
    </div>

    <div class="grid gap-8 lg:grid-cols-3">
      <div class="lg:col-span-1">
        <SubscriptionCard />
      </div>

      <div class="lg:col-span-2">
        <div class="space-y-6">
          <div>
            <h2 class="text-2xl font-bold">
              Upgrade Your Plan
            </h2>
            <p class="mt-2 text-muted-foreground">
              Choose the plan that's right for you
            </p>
          </div>

          <Tabs :model-value="billingInterval" @update:model-value="(v) => billingInterval = v as BillingInterval">
            <TabsList class="grid w-full grid-cols-2">
              <TabsTrigger value="monthly">
                Monthly
              </TabsTrigger>
              <TabsTrigger value="annual">
                Annual (Save 17%)
              </TabsTrigger>
            </TabsList>

            <TabsContent value="monthly" class="mt-6">
              <div class="grid gap-6 md:grid-cols-2">
                <PlanCard
                  :plan="PLAN_FEATURES.pro"
                  billing-interval="monthly"
                  :is-current-plan="currentPlan === 'pro'"
                  :is-loading="isUpgrading"
                  :on-select-plan="() => handleSelectPlan('pro')"
                />
                <PlanCard
                  :plan="PLAN_FEATURES.business"
                  billing-interval="monthly"
                  :is-current-plan="currentPlan === 'business'"
                  :is-loading="isUpgrading"
                  :on-select-plan="() => handleSelectPlan('business')"
                />
              </div>
            </TabsContent>

            <TabsContent value="annual" class="mt-6">
              <div class="grid gap-6 md:grid-cols-2">
                <PlanCard
                  :plan="PLAN_FEATURES.pro"
                  billing-interval="annual"
                  :is-current-plan="currentPlan === 'pro'"
                  :is-loading="isUpgrading"
                  :on-select-plan="() => handleSelectPlan('pro')"
                />
                <PlanCard
                  :plan="PLAN_FEATURES.business"
                  billing-interval="annual"
                  :is-current-plan="currentPlan === 'business'"
                  :is-loading="isUpgrading"
                  :on-select-plan="() => handleSelectPlan('business')"
                />
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  </div>
</template>
