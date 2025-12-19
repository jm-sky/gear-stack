<script setup lang="ts">
import { Check } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import type { BillingInterval, PlanFeatures } from '../types'

const { plan, billingInterval, isCurrentPlan, onSelectPlan, isLoading } = defineProps<{
  plan: PlanFeatures
  billingInterval: BillingInterval
  isCurrentPlan?: boolean
  onSelectPlan?: () => void
  isLoading?: boolean
}>()

const price = billingInterval === 'annual' ? plan.price.annualMonthly : plan.price.monthly
const originalPrice = billingInterval === 'annual' ? plan.price.monthly : null
</script>

<template>
  <Card :class="{ 'border-primary': plan.popular }">
    <CardHeader>
      <div class="flex items-center justify-between">
        <CardTitle>{{ plan.name }}</CardTitle>
        <Badge v-if="plan.popular" variant="default">
          Popular
        </Badge>
      </div>
      <CardDescription>
        <div class="mt-4 flex items-baseline gap-2">
          <span class="text-3xl font-bold">${{ price }}</span>
          <span class="text-muted-foreground">/month</span>
        </div>
        <div v-if="originalPrice" class="text-sm text-muted-foreground">
          <span class="line-through">${{ originalPrice }}/month</span>
          <span class="ml-2 text-green-600">Save 17%</span>
        </div>
      </CardDescription>
    </CardHeader>

    <CardContent>
      <ul class="space-y-2">
        <li v-for="feature in plan.features" :key="feature" class="flex items-start gap-2">
          <Check class="mt-0.5 size-4 shrink-0 text-green-600" />
          <span class="text-sm">{{ feature }}</span>
        </li>
      </ul>
    </CardContent>

    <CardFooter>
      <Button
        v-if="isCurrentPlan"
        variant="outline"
        class="w-full"
        disabled
      >
        Current Plan
      </Button>
      <Button
        v-else-if="onSelectPlan"
        class="w-full"
        :disabled="isLoading"
        @click="onSelectPlan"
      >
        Select {{ plan.name }}
      </Button>
    </CardFooter>
  </Card>
</template>
