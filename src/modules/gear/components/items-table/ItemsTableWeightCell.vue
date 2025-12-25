<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatWeightToPreferredUnit, formatWeightWithPreferredUnit } from '@/modules/gear/utils/formatWeight'
import type { IGearItemV2, TGearWeightUnit } from '@/modules/gear/types/gear.types.v2'

const { item, isNestedContainer, totalWeight, preferredWeightUnit } = defineProps<{
  item: IGearItemV2
  isNestedContainer: boolean
  totalWeight?: number
  preferredWeightUnit: TGearWeightUnit
}>()

const { locale } = useI18n()

const formattedWeight = computed<string>(() => {
  if (isNestedContainer && totalWeight !== undefined) {
    return formatWeightToPreferredUnit(totalWeight * (item.quantity ?? 1), preferredWeightUnit, locale.value)
  }
  return formatWeightWithPreferredUnit(
    (item.weight ?? 0) * (item.quantity ?? 1),
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
