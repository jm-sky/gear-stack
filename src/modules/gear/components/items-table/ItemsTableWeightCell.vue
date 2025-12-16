<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatWeightToPreferredUnit, formatWeightWithPreferredUnit } from '@/modules/gear/utils/formatWeight'
import type { IGearItem, TGearWeightUnit } from '@/modules/gear/types/gear.types'

const { item, isNestedContainer, totalWeight, preferredWeightUnit } = defineProps<{
  item: IGearItem
  isNestedContainer: boolean
  totalWeight?: number
  preferredWeightUnit: TGearWeightUnit
}>()

const { locale } = useI18n()

const formattedWeight = computed<string>(() => {
  if (isNestedContainer && totalWeight !== undefined) {
    return formatWeightToPreferredUnit(totalWeight * item.quantity, preferredWeightUnit, locale.value)
  }
  return formatWeightWithPreferredUnit(
    item.weight * item.quantity,
    item.weightUnit ?? 'g',
    preferredWeightUnit,
    locale.value,
  )
})
</script>

<template>
  <div class="text-end px-4">
    {{ formattedWeight }}
  </div>
</template>
