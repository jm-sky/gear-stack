<script setup lang="ts">
import { FileText, Info } from 'lucide-vue-next'
import { computed, nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import DialogProgressOverlay from '@/components/ui/dialog/DialogProgressOverlay.vue'
import Textarea from '@/components/ui/textarea/Textarea.vue'
import { useHandleError } from '@/shared/composables/useHandleError'
import type { IGearContainer } from '../types/gear.types'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
import { markdownImportService } from '../services/markdownImportService'
import { useGearStore } from '../store/useGearStore'
import GuidelinesDialog from './GuidelinesDialog.vue'
import MarkdownImportOptions from './import-markdown/MarkdownImportOptions.vue'
import MarkdownImportPreview from './import-markdown/MarkdownImportPreview.vue'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'import-complete': []
}>()

const { t } = useI18n()
const { createContainer, updateContainer, createItem, updateItem } = useGear()
const store = useGearStore()
const { customBrands } = useGearSettings()
const { handleError } = useHandleError()

const markdownContent = ref('')
const importing = ref(false)
const importMode = ref<'create' | 'update'>('update') // Default to update mode
const recognizeFromName = ref(false) // Option to recognize brand and color from item name
const previewResult = ref<ReturnType<typeof markdownImportService.parseMarkdown> | null>(null)
const isGuidelinesDialogOpen = ref(false)
const importProgress = ref({
  current: 0,
  total: 0,
  phase: 'containers' as 'containers' | 'items',
  currentItem: '',
})
const previewRef = ref<HTMLElement | null>(null)


// Check if any containers/items have UUIDs
const hasUuids = computed(() => {
  if (!previewResult.value) return false
  return previewResult.value.containers.some(c => c.uuid || c.items.some(i => i.uuid))
})

// Calculate import progress percentage
const importProgressPercentage = computed(() => {
  if (importProgress.value.total === 0) return 0
  return Math.round((importProgress.value.current / importProgress.value.total) * 100)
})

const handleClose = () => {
  markdownContent.value = ''
  previewResult.value = null
  importProgress.value = {
    current: 0,
    total: 0,
    phase: 'containers',
    currentItem: '',
  }
  emit('update:open', false)
}

const handlePreview = async () => {
  if (!markdownContent.value.trim()) {
    toast.error(t('gear.import.emptyContent'))
    return
  }

  const result = markdownImportService.parseMarkdown(markdownContent.value, {
    recognizeFromName: recognizeFromName.value,
    customBrands: customBrands.value,
  })
  previewResult.value = result

  if (result.containers.length === 0) {
    toast.warning(t('gear.import.noContainersFound'))
  } else {
    toast.success(t('gear.import.previewSuccess', { count: result.containers.length }))
    // Scroll to preview section after DOM update
    await nextTick()
    previewRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const handleOpenGuidelines = () => {
  isGuidelinesDialogOpen.value = true
}

const handleImport = async () => {
  if (!previewResult.value || previewResult.value.containers.length === 0) {
    toast.error(t('gear.import.noPreview'))
    return
  }

  importing.value = true

  try {
    let importedCount = 0
    let updatedCount = 0
    let itemCount = 0
    let itemUpdatedCount = 0

    // Calculate total items for progress tracking
    const totalContainers = previewResult.value.containers.length
    const totalItems = previewResult.value.containers.reduce((sum, c) => sum + c.items.length, 0)
    const totalOperations = totalContainers + totalItems

    // Initialize progress
    importProgress.value = {
      current: 0,
      total: totalOperations,
      phase: 'containers',
      currentItem: '',
    }

    // Map to store container slug/id -> container UUID for nested container resolution
    const containerIdMap = new Map<string, string>()

    // Phase 1: Create/update all containers first
    const createdContainers: Array<{ containerData: typeof previewResult.value.containers[0]; container: IGearContainer }> = []

    for (const containerData of previewResult.value.containers) {
      importProgress.value.currentItem = containerData.name
      let container

      // Check if we should update existing container (has UUID and mode is update)
      if (importMode.value === 'update' && containerData.uuid) {
        const existing = store.getContainerById(containerData.uuid)
        if (existing) {
          // Update existing container with all parsed fields
          container = await updateContainer(existing.id, {
            name: containerData.name,
            description: containerData.description,
            weight: containerData.weight,
            weightUnit: containerData.weightUnit,
            url: containerData.url,
            price: containerData.price,
            currency: containerData.currency,
            favorite: containerData.favorite,
            // Keep existing type, color, brand, and other fields that aren't in markdown
          })
          updatedCount++
        } else {
          // UUID provided but container not found - create new with same UUID
          container = await createContainer({
            id: containerData.uuid, // Use UUID from markdown export
            name: containerData.name,
            type: 'other',
            description: containerData.description || t('gear.import.importedDescription'),
            weight: containerData.weight,
            weightUnit: containerData.weightUnit,
            url: containerData.url,
            price: containerData.price,
            currency: containerData.currency,
            favorite: containerData.favorite ?? false,
          })
          importedCount++
        }
      } else {
        // Create new container
        container = await createContainer({
          name: containerData.name,
          type: 'other',
          description: containerData.description || t('gear.import.importedDescription'),
          weight: containerData.weight,
          weightUnit: containerData.weightUnit,
          url: containerData.url,
          price: containerData.price,
          currency: containerData.currency,
          favorite: containerData.favorite ?? false,
        })
        importedCount++
      }

      // Store mapping: slug/id -> container UUID
      if (containerData.id) {
        containerIdMap.set(containerData.id, container.id)
      }

      // Also map UUID if available (for update mode)
      if (containerData.uuid) {
        containerIdMap.set(containerData.uuid, container.id)
      }

      createdContainers.push({ containerData, container })
      importProgress.value.current++
    }

    // Phase 2: Create/update items with nested container resolution
    importProgress.value.phase = 'items'
    for (const { containerData, container } of createdContainers) {
      // Fetch latest container from store to ensure we have up-to-date items
      const latestContainer = store.getContainerById(container.id)
      if (!latestContainer) {
        console.warn(`Container ${container.id} not found in store`)
        continue
      }

      // Import/update items
      for (const itemData of containerData.items) {
        importProgress.value.currentItem = itemData.name || t('gear.import.importingItem', 'Importing item')
        // Extract nestedContainerId before destructuring
        const { uuid: itemUuid, nestedContainerId, ...itemDto } = itemData

        // Resolve nestedContainerId (slug) to actual container UUID
        if (nestedContainerId) {
          const nestedContainerUuid = containerIdMap.get(nestedContainerId)
          if (nestedContainerUuid) {
            itemDto.containerId = nestedContainerUuid
          } else {
            console.warn(`Nested container with id "${nestedContainerId}" not found`)
          }
        }

        if (importMode.value === 'update' && itemUuid) {
          // Try to find existing item by UUID in the latest container from store
          const existingItem = latestContainer.items.find(i => i.id === itemUuid)
          if (existingItem) {
            // Update existing item
            await updateItem(existingItem.id, itemDto)
            itemUpdatedCount++
          } else {
            // UUID provided but item not found - create new with same UUID
            await createItem(latestContainer.id, {
              ...itemDto,
              id: itemUuid, // Use UUID from markdown export
            })
            itemCount++
          }
        } else {
          // Create new item
          await createItem(latestContainer.id, itemDto)
          itemCount++
        }
        importProgress.value.current++
      }
    }

    const message = importMode.value === 'update'
      ? t('gear.import.successWithUpdates', {
          created: importedCount,
          updated: updatedCount,
          items: itemCount,
          itemsUpdated: itemUpdatedCount,
        })
      : t('gear.import.success', {
          containers: importedCount,
          items: itemCount,
        })

    toast.success(message)

    emit('import-complete')
    handleClose()
  } catch (error) {
    console.error('Import error:', error)
    handleError(error)
  } finally {
    importing.value = false
  }
}
</script>

<template>
  <Dialog :open="props.open" @update:open="handleClose">
    <DialogContent class="min-w-full md:min-w-2xl max-w-screen md:max-w-6xl min-h-[70vh] max-h-[90vh] flex flex-col">
      <DialogProgressOverlay
        :visible="importing"
        :progress-percentage="importProgressPercentage"
        :title="t('gear.import.importing', 'Importing...')"
        :progress-text="t('gear.import.progress', 'Progress')"
        :current-item-text="importProgress.currentItem"
        :current="importProgress.current"
        :total="importProgress.total"
      />
      <DialogHeader>
        <DialogTitle>{{ t('gear.import.title') }}</DialogTitle>
        <DialogDescription>
          {{ t('gear.import.description') }}
        </DialogDescription>
      </DialogHeader>

      <div class="flex flex-col flex-1 overflow-y-auto space-y-4" :class="{ 'opacity-50': importing }">
        <!-- Markdown Input -->
        <div class="flex flex-col flex-1">
          <label class="text-sm font-medium mb-2 block">
            {{ t('gear.import.markdownContent') }}
          </label>
          <Textarea
            v-model="markdownContent"
            :placeholder="t('gear.import.placeholder')"
            :disabled="importing"
            rows="12"
            class="flex flex-1 min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 font-mono"
          />
        </div>

        <!-- Recognition Options & Import Mode -->
        <MarkdownImportOptions
          v-model:recognize-from-name="recognizeFromName"
          v-model:import-mode="importMode"
          :has-uuids="hasUuids"
          :show-preview="!!previewResult"
        />

        <!-- Preview Result -->
        <div ref="previewRef">
          <MarkdownImportPreview :preview-result="previewResult" />
        </div>
      </div>

      <DialogFooter class="flex-col sm:flex-row gap-2">
        <Button variant="secondary" class="sm:mr-auto" @click="handleOpenGuidelines">
          <Info class="size-4" />
          {{ t('gear.export.guidelines', 'Guidelines') }}
        </Button>
        <div class="flex gap-2">
          <Button type="button" variant="outline" @click="handleClose">
            {{ t('gear.actions.cancel') }}
          </Button>
          <Button
            type="button"
            :variant="previewResult ? 'outline' : 'default'"
            :disabled="markdownContent.trim().length < 4"
            @click="handlePreview"
          >
            <FileText class="size-4" />
            {{ t('gear.import.preview') }}
          </Button>
          <Button
            type="button"
            :variant="previewResult ? 'default' : 'outline'"
            :disabled="!previewResult || previewResult.containers.length === 0 || importing"
            :loading="importing"
            @click="handleImport"
          >
            {{ t('gear.import.import') }}
          </Button>
        </div>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  <!-- Guidelines Dialog -->
  <GuidelinesDialog v-model:open="isGuidelinesDialogOpen" />
</template>
