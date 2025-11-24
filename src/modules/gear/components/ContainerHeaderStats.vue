<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { IGearContainer } from '../types/gear.types'
import { useGearSettings } from '../composables/useGearSettings'
import { useGearStore } from '../store/useGearStore'
import {
  READINESS_EXCELLENT_THRESHOLD,
  READINESS_GOOD_THRESHOLD,
} from '../utils/constants'
import {
  calculateReadinessPercentageSync,
  calculateTotalPriceSync,
  calculateTotalWeightSync,
  calculateWeightLimitPercentageSync,
} from '../utils/containerCalculations'
import { formatCurrency } from '../utils/currencyFormatter'
import { convertToGrams, formatWeightToPreferredUnit } from '../utils/formatWeight'

const props = defineProps<{
  container: IGearContainer
  showTotalPrice?: boolean
}>()

const { t } = useI18n()
const store = useGearStore()
const { settings: gearSettings, defaultCurrency } = useGearSettings()
const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

const totalWeight = computed<number>(() => calculateTotalWeightSync(props.container, store.getAllContainers))
const readinessPercentage = computed<number>(() => calculateReadinessPercentageSync(props.container))
const itemsCount = computed<number>(() => props.container.items.length)
const totalPriceByCurrency = computed<Record<string, number>>(() => calculateTotalPriceSync(props.container, store.getAllContainers, defaultCurrency.value))

// Format weight (totalWeight is in grams)
const formattedWeight = computed<string>(() => formatWeightToPreferredUnit(totalWeight.value, settings.value.preferredWeightUnit))

// Readiness color
const readinessColor = computed<string>(() => {
  if (readinessPercentage.value >= READINESS_EXCELLENT_THRESHOLD) return 'text-green-600'
  if (readinessPercentage.value >= READINESS_GOOD_THRESHOLD) return 'text-yellow-600'
  return 'text-red-600'
})

// Weight limit
const weightLimitPercentage = computed<number | null>(() => {
  return calculateWeightLimitPercentageSync(props.container, store.getAllContainers)
})

const hasWeightLimit = computed<boolean>(() => weightLimitPercentage.value !== null)
const weightLimitColor = computed<string>(() => {
  if (!weightLimitPercentage.value) return ''
  if (weightLimitPercentage.value >= 100) return 'text-red-600'
  if (weightLimitPercentage.value >= 90) return 'text-orange-600'
  if (weightLimitPercentage.value >= 70) return 'text-yellow-600'
  return 'text-green-600'
})

const formattedMaxWeight = computed<string>(() => {
  if (!props.container.maxWeight || !props.container.maxWeightUnit) return ''
  return formatWeightToPreferredUnit(
    convertToGrams(props.container.maxWeight, props.container.maxWeightUnit),
    settings.value.preferredWeightUnit
  )
})
</script>

<template>
  <div class="grid grid-cols-1 gap-4" :class="showTotalPrice ? 'md:grid-cols-4' : 'md:grid-cols-3'">
    <!-- Items Count -->
    <div class="bg-card rounded-lg border p-4">
      <div class="text-sm text-muted-foreground mb-1">
        {{ t('gear.container.itemsCountLabel') }}
      </div>
      <div class="text-2xl font-bold">
        {{ itemsCount }}
      </div>
    </div>

    <!-- Total Weight -->
    <div class="bg-card rounded-lg border p-4">
      <div class="text-sm text-muted-foreground mb-1">
        {{ t('gear.container.totalWeight') }}
      </div>
      <div :class="['text-2xl font-bold', hasWeightLimit ? weightLimitColor : '']">
        {{ formattedWeight }}
        <span v-if="hasWeightLimit" class="text-sm text-muted-foreground">
          / {{ formattedMaxWeight }}
        </span>
      </div>
      <div v-if="hasWeightLimit && weightLimitPercentage !== null" class="w-full bg-muted rounded-full h-2 mt-2">
        <div
          :class="[
            'h-2 rounded-full transition-all',
            weightLimitPercentage >= 100 ? 'bg-red-600' : weightLimitPercentage >= 90 ? 'bg-orange-600' : weightLimitPercentage >= 70 ? 'bg-yellow-600' : 'bg-green-600',
          ]"
          :style="{ width: `${Math.min(weightLimitPercentage, 100)}%` }"
        />
      </div>
    </div>

    <!-- Readiness -->
    <div class="bg-card rounded-lg border p-4">
      <div class="text-sm text-muted-foreground mb-1">
        {{ t('gear.container.readiness') }}
      </div>
      <div :class="['text-2xl font-bold', readinessColor]">
        {{ readinessPercentage }}%
      </div>
      <div class="w-full bg-muted rounded-full h-2 mt-2">
        <div
          :class="[
            'h-2 rounded-full transition-all',
            readinessPercentage >= READINESS_EXCELLENT_THRESHOLD ? 'bg-green-600' : readinessPercentage >= READINESS_GOOD_THRESHOLD ? 'bg-yellow-600' : 'bg-red-600',
          ]"
          :style="{ width: `${readinessPercentage}%` }"
        />
      </div>
    </div>

    <!-- Total Price (if any items have prices) -->
    <div v-if="showTotalPrice && Object.keys(totalPriceByCurrency).length > 0" class="bg-card rounded-lg border p-4">
      <div class="text-sm text-muted-foreground mb-2">
        {{ t('gear.item.totalPrice') }}
      </div>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="(amount, currency) in totalPriceByCurrency"
          :key="currency"
          class="text-lg font-bold text-nowrap border rounded-md px-3 py-1"
        >
          {{ formatCurrency(amount, currency) }}
        </div>
      </div>
    </div>
  </div>
</template>

