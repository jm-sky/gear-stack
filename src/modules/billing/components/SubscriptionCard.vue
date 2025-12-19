<script setup lang="ts">
import { AlertCircle, Check, Crown } from 'lucide-vue-next'
import { computed } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { useSubscription } from '../composables/useSubscription'
import { PLAN_FEATURES } from '../types'

const {
  subscription,
  currentPlan,
  currentPlanFeatures,
  isGrandfathered,
  isCanceled,
  isPastDue,
  cancelAtPeriodEnd,
  isPaidTier,
  openBillingPortal,
  isOpeningPortal,
} = useSubscription()

const statusBadgeVariant = computed(() => {
  if (isPastDue.value) return 'destructive'
  if (isCanceled.value || cancelAtPeriodEnd.value) return 'secondary'
  return 'default'
})

const statusText = computed(() => {
  if (isPastDue.value) return 'Past Due'
  if (isCanceled.value) return 'Canceled'
  if (cancelAtPeriodEnd.value) return 'Canceling'
  if (isGrandfathered.value) return 'Grandfathered'
  return 'Active'
})

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const planFeatures = computed(() => PLAN_FEATURES[currentPlan.value]?.features || [])
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <CardTitle class="text-2xl">
            {{ currentPlanFeatures?.name }} Plan
          </CardTitle>
          <Crown v-if="isGrandfathered" class="size-5 text-yellow-500" />
        </div>
        <Badge :variant="statusBadgeVariant">
          {{ statusText }}
        </Badge>
      </div>
      <CardDescription v-if="currentPlanFeatures">
        <span v-if="subscription?.billingInterval === 'monthly'">
          ${{ currentPlanFeatures.price.monthly }}/month
        </span>
        <span v-else-if="subscription?.billingInterval === 'annual'">
          ${{ currentPlanFeatures.price.annualMonthly }}/month (billed annually)
        </span>
        <span v-else>Free Plan</span>
      </CardDescription>
    </CardHeader>

    <CardContent class="space-y-4">
      <div class="space-y-2">
        <h3 class="text-sm font-medium">
          Features
        </h3>
        <ul class="space-y-1">
          <li v-for="feature in planFeatures" :key="feature" class="flex items-center gap-2 text-sm">
            <Check class="size-4 text-green-600" />
            <span>{{ feature }}</span>
          </li>
        </ul>
      </div>

      <div v-if="isPaidTier && subscription" class="space-y-2">
        <h3 class="text-sm font-medium">
          Billing Information
        </h3>
        <div class="space-y-1 text-sm text-muted-foreground">
          <div class="flex justify-between">
            <span>Current Period:</span>
            <span>{{ formatDate(subscription.currentPeriodStart) }} - {{ formatDate(subscription.currentPeriodEnd) }}</span>
          </div>
          <div v-if="cancelAtPeriodEnd" class="flex items-center gap-2 text-amber-600">
            <AlertCircle class="size-4" />
            <span>Subscription will cancel on {{ formatDate(subscription.currentPeriodEnd) }}</span>
          </div>
        </div>
      </div>

      <div v-if="isGrandfathered" class="rounded-lg bg-yellow-50 p-3 text-sm">
        <div class="flex items-center gap-2 font-medium text-yellow-800">
          <Crown class="size-4" />
          <span>Lifetime Pro Access</span>
        </div>
        <p class="mt-1 text-yellow-700">
          You have grandfathered lifetime access to Pro features.
        </p>
      </div>
    </CardContent>

    <CardFooter v-if="isPaidTier && !isGrandfathered">
      <Button
        variant="outline"
        class="w-full"
        :disabled="isOpeningPortal"
        @click="openBillingPortal"
      >
        Manage Subscription
      </Button>
    </CardFooter>
  </Card>
</template>
