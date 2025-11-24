<script setup lang="ts">
import { Box, Package, Star } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import CardContent from '@/components/ui/card/CardContent.vue'
import type { IGearContainer } from '../types/gear.types'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
import { useGearStore } from '../store/useGearStore'
import {
  READINESS_EXCELLENT_THRESHOLD,
  READINESS_GOOD_THRESHOLD,
} from '../utils/constants'
import {
  calculateReadinessPercentageSync,
  calculateTotalWeightSync,
} from '../utils/containerCalculations'
import { COLOR_BORDER_CLASSES, COLOR_TEXT_CLASSES } from '../utils/containerColors'
import { formatWeightToPreferredUnit } from '../utils/formatWeight'
import ColorDot from './ColorDot.vue'
import ContainerCardActions from './ContainerCardActions.vue'
import ContainerCardBadges from './ContainerCardBadges.vue'
import ContainerCardCreatedDate from './ContainerCardCreatedDate.vue'
import ContainerCardStats from './ContainerCardStats.vue'
import ContainerReadinessProgressBar from './ContainerReadinessProgressBar.vue'

const props = defineProps<{
  container: IGearContainer
}>()
const emit = defineEmits<{
  delete: [id: string]
}>()

const router = useRouter()
const { t } = useI18n()
const store = useGearStore()
const { updateContainer } = useGear()
const { settings: gearSettings } = useGearSettings()
const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

// Computed properties - use sync helpers for computed
const totalWeight = computed<number>(() => {
  return calculateTotalWeightSync(props.container, store.getAllContainers)
})
const readinessPercentage = computed<number>(() => {
  return calculateReadinessPercentageSync(props.container)
})
const itemsCount = computed<number>(() => props.container.items.length)

// Format weight (totalWeight is in grams)
const formattedWeight = computed<string>(() => formatWeightToPreferredUnit(totalWeight.value, settings.value.preferredWeightUnit))

// Readiness color
const readinessColor = computed<string>(() => {
  if (readinessPercentage.value >= READINESS_EXCELLENT_THRESHOLD) return 'text-green-600'
  if (readinessPercentage.value >= READINESS_GOOD_THRESHOLD) return 'text-yellow-600'
  return 'text-red-600'
})

// Check if container is nested
const isNested = computed<boolean>(() => {
  return !!props.container.parentContainerId
})

// Navigate to container detail
const handleShow = () => {
  router.push(`/gear/${props.container.id}`)
}

// Toggle favorite status
const handleToggleFavorite = async (e: Event) => {
  e.stopPropagation()
  try {
    const newFavoriteStatus = !props.container.favorite
    await updateContainer(props.container.id, {
      favorite: newFavoriteStatus,
    })
    toast.success(
      newFavoriteStatus
        ? t('gear.container.favoriteAdded')
        : t('gear.container.favoriteRemoved'),
    )
  } catch (error) {
    console.error('Failed to update favorite status:', error)
    toast.error(t('common.error'))
  }
}
</script>

<template>
  <Card
    class="gap-2 hover:shadow-lg hover:bg-current/5 hover:scale-102 hover:-translate-y-1 transition-all duration-300 cursor-pointer"
    :class="[
      container.color ? COLOR_BORDER_CLASSES[container.color] : '',
      container.color ? COLOR_TEXT_CLASSES[container.color] : '',
    ]"
    @click="handleShow"
  >
    <CardHeader class="h-8 text-card-foreground flex items-center justify-between">
      <div class="flex items-center gap-2">
        <ColorDot :color="container.color ?? undefined" />
        <Package class="size-5" />
        <CardTitle>{{ container.name }}</CardTitle>
        <Badge v-if="isNested" variant="outline" class="ml-auto text-xs">
          <Box :size="12" class="mr-1" />
          {{ t('gear.container.nested') }}
        </Badge>
      </div>
      <div class="flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          class="size-8 p-0"
          :aria-label="container.favorite ? t('gear.container.removeFavorite') : t('gear.container.addFavorite')"
          @click.stop="handleToggleFavorite"
        >
          <Star
            :class="[
              'size-4',
              container.favorite ? 'fill-yellow-500 text-yellow-500' : 'text-muted-foreground',
            ]"
          />
        </Button>
        <ContainerCardActions :container @delete="emit('delete', $event)" />
      </div>
    </CardHeader>

    <CardContent class="flex flex-col flex-1 gap-3 px-6 pb-4 text-card-foreground">
      <ContainerCardBadges :container />

      <CardDescription class="flex-1">
        {{ container.description ?? '' }}
      </CardDescription>

      <ContainerCardStats
        :items-count
        :formatted-weight
        :readiness-percentage
        :readiness-color
      />

      <ContainerReadinessProgressBar :readiness-percentage />

      <div class="-mb-6 mt-2 flex items-center justify-end">
        <ContainerCardCreatedDate :created-at="container.createdAt" />
      </div>
    </CardContent>
  </Card>
</template>

