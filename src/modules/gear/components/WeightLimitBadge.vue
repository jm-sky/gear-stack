<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import type { IGearContainer } from '../types/gear.types'
import { useGearStore } from '../store/useGearStore'
import { calculateWeightLimitPercentageSync } from '../utils/containerCalculations'

const props = defineProps<{
  container: IGearContainer
}>()

const { t } = useI18n()
const store = useGearStore()

const weightLimitPercentage = computed<number | null>(() =>
  calculateWeightLimitPercentageSync(props.container, store.getAllContainers)
)

const hasWeightLimit = computed<boolean>(() => weightLimitPercentage.value !== null)

const shouldShow = computed<boolean>(() =>
  hasWeightLimit.value && weightLimitPercentage.value !== null && weightLimitPercentage.value >= 90
)

const badgeClasses = computed<string>(() => {
  if (weightLimitPercentage.value === null) return ''
  return weightLimitPercentage.value >= 100
    ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    : 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
})

const badgeText = computed<string>(() => {
  if (weightLimitPercentage.value === null) return ''
  const message = weightLimitPercentage.value >= 100
    ? t('gear.container.weightLimitExceeded')
    : t('gear.container.weightLimitWarning')
  return `${message} (${weightLimitPercentage.value}%)`
})
</script>

<template>
  <Badge
    v-if="shouldShow"
    :class="badgeClasses"
  >
    {{ badgeText }}
  </Badge>
</template>





