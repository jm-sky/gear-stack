<script setup lang="ts">
import { computed } from 'vue'
import { formatWeightToPreferredUnit, formatWeightWithPreferredUnit } from '@/modules/gear/utils/formatWeight'
import type { IGearItem, TGearWeightUnit } from '@/modules/gear/types/gear.types'

const { item, isNestedContainer, totalWeight, preferredWeightUnit } = defineProps<{
  item: IGearItem
  isNestedContainer: boolean
  totalWeight?: number
  preferredWeightUnit: TGearWeightUnit
}>()

const formattedWeight = computed<string>(() => {
  if (isNestedContainer && totalWeight !== undefined) {
    return formatWeightToPreferredUnit(totalWeight * item.quantity, preferredWeightUnit)
  }
  return formatWeightWithPreferredUnit(
    item.weight * item.quantity,
    item.weightUnit ?? 'g',
    preferredWeightUnit,
  )
})
</script>

<template>
  <div class="text-end px-4">
    {{ formattedWeight }}
  </div>
</template>
