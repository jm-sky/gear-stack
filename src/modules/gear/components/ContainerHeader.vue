<script setup lang="ts">
import { ArrowLeft, BoxIcon, CalendarPlus, CalendarSync, Download, Edit, MessageSquare, MoreVertical, Plus, SparklesIcon, Star, Upload } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import DropdownMenuSeparator from '@/components/ui/dropdown-menu/DropdownMenuSeparator.vue'
import { smallDateTime } from '@/shared/utils/smallDateTime'
import type { IGearContainer } from '../types/gear.types'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { useGear } from '../composables/useGear'
import { useGearStore } from '../store/useGearStore'
import { calculateWeightLimitPercentageSync } from '../utils/containerCalculations'
import { formatWeight } from '../utils/formatWeight'
import { isSet } from '../utils/helpers'
import ContainerHeaderStats from './ContainerHeaderStats.vue'

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
const store = useGearStore()
const { updateContainer } = useGear()
const { typeLabel } = useContainerTypeLabel(computed(() => props.container.type))

const weightLimitPercentage = computed<number | null>(() => calculateWeightLimitPercentageSync(props.container, store.getAllContainers))
const hasWeightLimit = computed<boolean>(() => weightLimitPercentage.value !== null)

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

const handleToggleFavorite = async () => {
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
          :aria-label="$t('gear.actions.exportToPrompt')"
          @click="handleExportToPrompt"
        >
          <SparklesIcon class="size-4" />
        </Button>
        <Button
          v-tooltip.bottom="container.favorite ? t('gear.container.removeFavorite') : t('gear.container.addFavorite')"
          variant="ghost"
          size="sm"
          :aria-label="container.favorite ? t('gear.container.removeFavorite') : t('gear.container.addFavorite')"
          @click="handleToggleFavorite"
        >
          <Star
            :class="[
              'size-4',
              container.favorite ? 'fill-yellow-500 text-yellow-500' : 'text-muted-foreground',
            ]"
          />
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
            <Badge
              v-tooltip.bottom="t('common.created')"
              variant="secondary"
              class="text-xs"
            >
              <CalendarPlus class="size-4" />
              {{ smallDateTime(container.createdAt) }}
            </Badge>
            <Badge
              v-if="container.updatedAt !== container.createdAt"
              v-tooltip.bottom="t('common.updated')"
              variant="secondary"
              class="text-xs"
            >
              <CalendarSync class="size-4" /> {{ smallDateTime(container.updatedAt) }}
            </Badge>
            <Badge v-if="container.brand" variant="secondary" class="normal-case">
              {{ container.brand }}
            </Badge>
            <Badge v-if="isSet(container.weight) && isSet(container.weightUnit)" variant="secondary">
              {{ formatWeight(container.weight, container.weightUnit) }}
            </Badge>
            <Badge
              v-if="hasWeightLimit && weightLimitPercentage !== null && weightLimitPercentage >= 90"
              :class="weightLimitPercentage >= 100 ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'"
            >
              {{ weightLimitPercentage >= 100 ? t('gear.container.weightLimitExceeded') : t('gear.container.weightLimitWarning') }}
              ({{ weightLimitPercentage }}%)
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
          <Button size="sm" class="shrink-0 flex-1 sm:flex-none" @click="handleAddItem">
            <Plus class="size-4" />
            {{ t('gear.item.create') }}
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button
                variant="outline"
                size="sm"
                class="shrink-0"
                :aria-label="$t('gear.actions.moreActions')"
              >
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

    <ContainerHeaderStats :container />
  </div>
</template>

