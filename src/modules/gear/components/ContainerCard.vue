<script setup lang="ts">
import { MoreVertical, Package } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
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
import { formatWeightFromGrams } from '../utils/formatWeight'

const props = defineProps<{
  container: IGearContainer
}>()
const emit = defineEmits<{
  delete: [id: string]
}>()

const router = useRouter()
const { t } = useI18n()
const { calculateTotalWeight, calculateReadinessPercentage } = useGear()
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
  <Card class="hover:shadow-md transition-shadow cursor-pointer" @click="handleShow">
    <CardHeader>
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-2">
            <Package class="h-5 w-5 text-muted-foreground" />
            <CardTitle>{{ container.name }}</CardTitle>
          </div>
          <CardDescription v-if="container.description">
            {{ container.description }}
          </CardDescription>
          <Badge variant="outline" class="mt-2">
            {{ typeLabel }}
          </Badge>
        </div>
        <DropdownMenu @click.stop>
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" size="sm" class="size-8 p-0">
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
            <DropdownMenuItem class="text-destructive" @click.stop="handleDelete">
              {{ t('gear.actions.delete') }}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </CardHeader>

    <div class="px-6 pb-6 space-y-3">
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
    </div>
  </Card>
</template>

