<script setup lang="ts">
import { CalendarPlus, CalendarSync, ExternalLink, Link2, RefreshCcw } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import DropdownMenuSeparator from '@/components/ui/dropdown-menu/DropdownMenuSeparator.vue'
import { useAi } from '@/modules/ai/composables/useAi'
import { useBackend } from '@/shared/composables/useBackend'
import { smallDateTime } from '@/shared/utils/smallDateTime'
import type { IGearContainer } from '../types/gear.types'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { GearRoutePath } from '../routes'
import { getActionIcon } from '../utils/actionIcons'
import { formatWeight } from '../utils/formatWeight'
import { isSet } from '../utils/helpers'
import CloneContainerDialog from './CloneContainerDialog.vue'
import ContainerHeaderName from './ContainerHeaderName.vue'
import ContainerHeaderStats from './ContainerHeaderStats.vue'
import ContainerRatingBadge from './ContainerRatingBadge.vue'
import FavoriteContainerButton from './FavoriteContainerButton.vue'
import ItemsTableEditModeToggle from './ItemsTableEditModeToggle.vue'
import MarkdownRenderer from './MarkdownRenderer.vue'
import WeightLimitBadge from './WeightLimitBadge.vue'

// Action icons
const BackIcon = getActionIcon('back')
const ExportToPromptIcon = getActionIcon('exportToPrompt')
const EditIcon = getActionIcon('edit')
const CloneIcon = getActionIcon('clone')
const AddContainerIcon = getActionIcon('addContainer')
const AddItemIcon = getActionIcon('addItem')
const MoreActionsIcon = getActionIcon('moreActions')
const ExportIcon = getActionIcon('export')
const ExportToCSVIcon = getActionIcon('exportToCSV')
const ImportIcon = getActionIcon('import')
const RecognizeParametersAllIcon = getActionIcon('recognizeParametersAll')
const AiIcon = getActionIcon('ai')

const props = defineProps<{
  container: IGearContainer
}>()

const emit = defineEmits<{
  export: []
  import: []
  addContainer: []
  exportToPrompt: []
  exportToCsv: []
  recognizeParametersAll: []
  aiChat: []
  manageShareTokens: []
  refresh: []
}>()

const router = useRouter()
const { t } = useI18n()
const { typeLabel } = useContainerTypeLabel(computed(() => props.container.type))
const { canUseAi } = useAi()
const { shouldUseAPI } = useBackend()

const isCloneDialogOpen = ref(false)

const handleEdit = () => {
  router.push(GearRoutePath.ContainerEditById(props.container.id))
}

const handleClone = () => {
  isCloneDialogOpen.value = true
}

const handleAddItem = () => {
  router.push(GearRoutePath.ItemNew.replace(':containerId', props.container.id))
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

const handleExportToCSV = () => {
  emit('exportToCsv')
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4">
      <div class="flex items-center justify-between gap-3">
        <Button
          variant="ghost"
          size="sm"
          @click="router.back()"
        >
          <BackIcon class="size-4" />
          {{ t('common.back') }}
        </Button>
        <div class="flex items-center gap-2">
          <Button
            v-if="shouldUseAPI"
            v-tooltip.bottom="t('gear.containers.refresh')"
            variant="ghost"
            size="sm"
            :aria-label="t('gear.containers.refresh')"
            @click="$emit('refresh')"
          >
            <RefreshCcw class="size-4" />
          </Button>
          <Button
            v-if="canUseAi"
            v-tooltip.bottom="t('gear.actions.aiAssistant')"
            variant="ghost"
            size="sm"
            :aria-label="t('gear.actions.aiAssistant')"
            @click="$emit('aiChat')"
          >
            <AiIcon class="size-4" />
          </Button>
          <Button
            v-tooltip.bottom="t('gear.actions.exportToPrompt')"
            variant="ghost"
            size="sm"
            :aria-label="t('gear.actions.exportToPrompt')"
            @click="handleExportToPrompt"
          >
            <ExportToPromptIcon class="size-4" />
          </Button>
          <FavoriteContainerButton :container />
        </div>
      </div>

      <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
        <div class="flex-1">
          <ContainerHeaderName :container />
          <div v-if="container.description" class="text-muted-foreground mb-3">
            <MarkdownRenderer
              :content="container.description"
              class="text-sm"
            />
          </div>
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
            <WeightLimitBadge :container />
            <ContainerRatingBadge :container />
            <ExternalLink
              v-if="container.url"
              :href="container.url"
              @click.stop
            >
              {{ t('gear.container.url') }}
            </ExternalLink>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <ItemsTableEditModeToggle />
          <Button
            variant="outline"
            size="sm"
            class="shrink-0"
            @click="handleEdit"
          >
            <EditIcon class="size-4" />
            <span class="hidden sm:inline">{{ t('gear.actions.edit') }}</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            class="shrink-0"
            @click="handleAddContainer"
          >
            <AddContainerIcon class="size-4" />
            <span class="hidden sm:inline">{{ t('gear.container.addNested') }}</span>
          </Button>
          <Button size="sm" class="shrink-0 flex-1 sm:flex-none" @click="handleAddItem">
            <AddItemIcon class="size-4" />
            {{ t('gear.item.create') }}
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button
                v-tooltip.bottom="t('gear.actions.moreActions')"
                variant="outline"
                size="sm"
                class="shrink-0"
                :aria-label="t('gear.actions.moreActions')"
              >
                <MoreActionsIcon class="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem @click="handleClone">
                <CloneIcon class="size-4" />
                {{ t('gear.container.clone') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="handleImport">
                <ImportIcon class="size-4" />
                {{ t('gear.actions.import') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="handleExport">
                <ExportIcon class="size-4" />
                {{ t('gear.actions.exportToJSON') }}
              </DropdownMenuItem>
              <DropdownMenuItem @click="handleExportToCSV">
                <ExportToCSVIcon class="size-4" />
                {{ t('gear.actions.exportToCSV') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="handleExportToPrompt">
                <ExportToPromptIcon class="size-4" />
                {{ t('gear.actions.exportToPrompt') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="$emit('recognizeParametersAll')">
                <RecognizeParametersAllIcon class="size-4" />
                {{ t('gear.actions.recognizeParametersAll') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="$emit('manageShareTokens')">
                <Link2 class="size-4" />
                {{ t('gear.actions.manageShareTokens') }}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>

    <ContainerHeaderStats :container />

    <!-- Clone Dialog -->
    <CloneContainerDialog
      v-model:open="isCloneDialogOpen"
      :container="container"
    />
  </div>
</template>
