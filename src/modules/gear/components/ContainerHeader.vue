<script setup lang="ts">
import { ArrowLeft, BoxIcon, Download, Edit, MessageSquare, MoreVertical, Plus, SparklesIcon, Upload } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import DropdownMenuSeparator from '@/components/ui/dropdown-menu/DropdownMenuSeparator.vue'
import { useCoreSettings } from '@/modules/settings/composables/useCoreSettings'
import type { IGearContainer } from '../types/gear.types'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
import {
  READINESS_EXCELLENT_THRESHOLD,
  READINESS_GOOD_THRESHOLD,
} from '../utils/constants'
import { formatWeight, formatWeightToPreferredUnit } from '../utils/formatWeight'

const props = defineProps<{
  container: IGearContainer
}>()

const emit = defineEmits<{
  export: []
  import: []
  addContainer: []
  exportToPrompt: []
  recognizeParametersAll: []
}>()

const router = useRouter()
const { t } = useI18n()
const { calculateTotalWeight, calculateReadinessPercentage } = useGear()
const { customContainerTypes } = useGearSettings()
const { settings: coreSettings } = useCoreSettings()
const settings = computed(() => ({ preferredWeightUnit: coreSettings.value.preferredWeightUnit }))

// Computed properties
const totalWeight = computed<number>(() => calculateTotalWeight(props.container.id))
const readinessPercentage = computed<number>(() => calculateReadinessPercentage(props.container.id))
const itemsCount = computed<number>(() => props.container.items.length)

// Format weight (totalWeight is in grams)
const formattedWeight = computed<string>(() => formatWeightToPreferredUnit(totalWeight.value, settings.value.preferredWeightUnit))

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
const handleEdit = () => {
  router.push(`/gear/${props.container.id}/edit`)
}

const handleAddItem = () => {
  router.push(`/gear/${props.container.id}/items/new`)
}

const handleAddContainer = () => {
  emit('addContainer')
}

const handleExport = () => {
  emit('export')
}

const handleImport = () => {
  emit('import')
}

const handleExportToPrompt = () => {
  emit('exportToPrompt')
}

const handleBack = () => {
  router.push('/gear')
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4">
      <div class="flex items-center justify-between gap-3">
        <Button variant="ghost" size="sm" @click="handleBack">
          <ArrowLeft class="size-4" />
          {{ t('common.back') }}
        </Button>
        <Button
          v-tooltip.bottom="t('gear.actions.exportToPrompt')"
          variant="ghost"
          size="sm"
          @click="handleExportToPrompt"
        >
          <SparklesIcon class="size-4" />
        </Button>
      </div>

      <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
        <div class="flex-1">
          <h1 class="text-3xl font-bold mb-2">
            {{ container.name }}
          </h1>
          <p v-if="container.description" class="text-muted-foreground mb-3">
            {{ container.description }}
          </p>
          <div class="flex items-center gap-2 flex-wrap">
            <Badge variant="outline">
              {{ typeLabel }}
            </Badge>
            <Badge v-if="container.brand" variant="secondary">
              {{ container.brand }}
            </Badge>
            <Badge v-if="container.weight !== undefined && container.weightUnit" variant="secondary">
              {{ formatWeight(container.weight, container.weightUnit) }}
            </Badge>
            <a
              v-if="container.url"
              :href="container.url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-primary hover:underline text-sm"
              @click.stop
            >
              {{ t('gear.container.url') }}
            </a>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            class="shrink-0"
            @click="handleEdit"
          >
            <Edit class="size-4" />
            <span class="hidden sm:inline">{{ t('gear.actions.edit') }}</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            class="shrink-0"
            @click="handleAddContainer"
          >
            <BoxIcon class="size-4" />
            <span class="hidden sm:inline">{{ t('gear.container.addNested') }}</span>
          </Button>
          <Button size="sm" class="shrink-0" @click="handleAddItem">
            <Plus class="size-4" />
            {{ t('gear.item.create') }}
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="outline" size="sm" class="shrink-0">
                <MoreVertical class="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem @click="handleExport">
                <Download class="size-4" />
                {{ t('gear.actions.export') }}
              </DropdownMenuItem>
              <DropdownMenuItem @click="handleImport">
                <Upload class="size-4" />
                {{ t('gear.actions.import') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="handleExportToPrompt">
                <MessageSquare class="size-4" />
                {{ t('gear.actions.exportToPrompt') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="$emit('recognizeParametersAll')">
                <SparklesIcon class="size-4" />
                {{ t('gear.actions.recognizeParametersAll') }}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-card rounded-lg border p-4">
        <div class="text-sm text-muted-foreground mb-1">
          {{ t('gear.container.itemsCount') }}
        </div>
        <div class="text-2xl font-bold">
          {{ itemsCount }}
        </div>
      </div>
      <div class="bg-card rounded-lg border p-4">
        <div class="text-sm text-muted-foreground mb-1">
          {{ t('gear.container.totalWeight') }}
        </div>
        <div class="text-2xl font-bold">
          {{ formattedWeight }}
        </div>
      </div>
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
    </div>
  </div>
</template>

