<script setup lang="ts">
import { Box, MoreVertical, Package } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import CardContent from '@/components/ui/card/CardContent.vue'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useSettings } from '@/modules/settings/composables/useSettings'
import type { IGearContainer } from '../types/gear.types'
import { useGear } from '../composables/useGear'
import {
  READINESS_EXCELLENT_THRESHOLD,
  READINESS_GOOD_THRESHOLD,
} from '../utils/constants'
import { COLOR_BORDER_CLASSES, COLOR_TEXT_CLASSES } from '../utils/containerColors'
import { formatWeightFromGrams } from '../utils/formatWeight'
import ColorDot from './ColorDot.vue'

const props = defineProps<{
  container: IGearContainer
}>()
const emit = defineEmits<{
  delete: [id: string]
}>()

const router = useRouter()
const { t } = useI18n()
const { calculateTotalWeight, calculateReadinessPercentage, getContainerById, containers } = useGear()
const { customContainerTypes } = useSettings()

// Computed properties
const totalWeight = computed<number>(() => calculateTotalWeight(props.container.id))
const readinessPercentage = computed<number>(() => calculateReadinessPercentage(props.container.id))
const itemsCount = computed<number>(() => props.container.items.length)

// Format weight (totalWeight is in grams)
const formattedWeight = computed<string>(() => formatWeightFromGrams(totalWeight.value))

// Readiness color
const readinessColor = computed<string>(() => {
  if (readinessPercentage.value >= READINESS_EXCELLENT_THRESHOLD) return 'text-green-600'
  if (readinessPercentage.value >= READINESS_GOOD_THRESHOLD) return 'text-yellow-600'
  return 'text-red-600'
})

// Get container type label helper
const getContainerTypeLabel = (typeKey: string): string => {
  const customType = customContainerTypes.value.find(t => t.key === typeKey)
  if (customType) {
    return customType.label
  }
  return t(`gear.container.types.${typeKey}`)
}

// Container type label
const typeLabel = computed<string>(() => {
  return getContainerTypeLabel(props.container.type)
})

// Check if container is nested
const isNested = computed<boolean>(() => {
  return !!props.container.parentContainerId
})

// Find all containers that contain this container as an item
const parentContainers = computed<IGearContainer[]>(() => {
  const parents: IGearContainer[] = []
  const containerId = props.container.id

  // Add direct parent if exists
  if (props.container.parentContainerId) {
    const directParent = getContainerById(props.container.parentContainerId)
    if (directParent) {
      parents.push(directParent)
    }
  }

  // Find all containers that have this container as an item
  for (const container of containers.value) {
    if (container.id === containerId) continue // Skip self
    if (container.items.some(item => item.containerId === containerId)) {
      // Avoid duplicates
      if (!parents.some(p => p.id === container.id)) {
        parents.push(container)
      }
    }
  }

  return parents
})

// Get first parent container
const firstParentContainer = computed<IGearContainer | undefined>(() => {
  return parentContainers.value[0]
})

// Get count of additional parents (beyond the first one)
const additionalParentsCount = computed<number>(() => {
  return Math.max(0, parentContainers.value.length - 1)
})

// Navigate to parent container
const navigateToParent = (e: Event) => {
  e.stopPropagation()
  if (firstParentContainer.value) {
    router.push(`/gear/${firstParentContainer.value.id}`)
  }
}

// Actions
const handleShow = () => {
  router.push(`/gear/${props.container.id}`)
}

const handleEdit = () => {
  router.push(`/gear/${props.container.id}/edit`)
}

const handleDelete = () => {
  emit('delete', props.container.id)
}
</script>

<template>
  <Card
    class="hover:shadow-lg hover:bg-current/5 hover:scale-102 hover:-translate-y-1 transition-all duration-300 cursor-pointer"
    :class="[
      container.color ? COLOR_BORDER_CLASSES[container.color] : '',
      container.color ? COLOR_TEXT_CLASSES[container.color] : '',
    ]"
    @click="handleShow"
  >
    <CardHeader class="text-card-foreground">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-2">
            <ColorDot :color="container.color" />
            <Package class="size-5" />
            <CardTitle>{{ container.name }}</CardTitle>
            <Badge v-if="isNested" variant="outline" class="ml-auto text-xs">
              <Box :size="12" class="mr-1" />
              {{ t('gear.container.nested') }}
            </Badge>
          </div>
          <CardDescription v-if="container.description">
            {{ container.description }}
          </CardDescription>
          <div class="flex items-center gap-2 mt-2 flex-wrap">
            <Badge variant="outline">
              {{ typeLabel }}
            </Badge>
            <div v-if="firstParentContainer" class="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                class="h-6 text-xs text-muted-foreground"
                @click.stop="navigateToParent"
              >
                {{ t('gear.container.parentContainer') }}: {{ firstParentContainer.name }}
              </Button>
              <Badge
                v-if="additionalParentsCount > 0"
                variant="secondary"
                class="h-5 text-xs px-1.5"
              >
                +{{ additionalParentsCount }}
              </Badge>
            </div>
          </div>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button
              variant="ghost"
              size="sm"
              class="size-8 p-0"
              @click.stop
            >
              <MoreVertical class="size-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem @click.stop="handleShow">
              {{ t('gear.actions.show') }}
            </DropdownMenuItem>
            <DropdownMenuItem @click.stop="handleEdit">
              {{ t('gear.actions.edit') }}
            </DropdownMenuItem>
            <DropdownMenuItem class="text-destructive hover:text-destructive! hover:bg-destructive/4!" @click.stop="handleDelete">
              {{ t('gear.actions.delete') }}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </CardHeader>

    <CardContent class="px-6 pb-4 space-y-3 text-card-foreground">
      <!-- Stats -->
      <div class="grid grid-cols-3 gap-2 sm:gap-4 text-sm">
        <div>
          <div class="text-muted-foreground">
            {{ t('gear.container.itemsCount') }}
          </div>
          <div class="font-semibold">
            {{ itemsCount }}
          </div>
        </div>
        <div>
          <div class="text-muted-foreground">
            {{ t('gear.container.totalWeight') }}
          </div>
          <div class="font-semibold">
            {{ formattedWeight }}
          </div>
        </div>
        <div>
          <div class="text-muted-foreground">
            {{ t('gear.container.readiness') }}
          </div>
          <div :class="['font-semibold', readinessColor]">
            {{ readinessPercentage }}%
          </div>
        </div>
      </div>

      <!-- Readiness Progress Bar -->
      <div class="w-full bg-muted rounded-full h-2">
        <div
          :class="[
            'h-2 rounded-full transition-all',
            readinessPercentage >= READINESS_EXCELLENT_THRESHOLD ? 'bg-green-600' : readinessPercentage >= READINESS_GOOD_THRESHOLD ? 'bg-yellow-600' : 'bg-red-600',
          ]"
          :style="{ width: `${readinessPercentage}%` }"
        />
      </div>
    </CardContent>
  </Card>
</template>

