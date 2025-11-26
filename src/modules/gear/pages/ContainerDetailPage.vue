<script setup lang="ts">
// File operations handled via native input element
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import AiChatDialog from '@/modules/ai/components/AiChatDialog.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { useBackend } from '@/shared/composables/useBackend'
import type { IGearItem } from '../types/gear.types'
import AddNestedContainerDialog from '../components/AddNestedContainerDialog.vue'
import CategoryPieChart from '../components/CategoryPieChart.vue'
import ContainerHeader from '../components/ContainerHeader.vue'
import ContainerItemImagesGallery from '../components/ContainerItemImagesGallery.vue'
import ExportToCSVDialog from '../components/ExportToCSVDialog.vue'
import ExportToPromptDialog from '../components/ExportToPromptDialog.vue'
import ItemsTable from '../components/ItemsTable.vue'
import SortConfirmationAlert from '../components/SortConfirmationAlert.vue'
import { useContainer } from '../composables/useContainer'
import { useGear } from '../composables/useGear'
import { GearRoutePath } from '../routes'
import { gearItemService } from '../services/gearItemService'
import { useGearStore } from '../store/useGearStore'
import { recognizeParameters, recognizeParametersForItems } from '../utils/parameterRecognition'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const store = useGearStore()
const { shouldUseAPI } = useBackend()
const { container } = useContainer()
const { deleteItem, updateItem, updateContainer, exportData, importData, createItem, getContainerById } = useGear()
const { user, isAuthenticated } = useAuth()

const containerId = route.params.id as string

// Check if user can edit container (admin AND owner)
const canEditContainer = computed(() => {
  if (!isAuthenticated.value || !user.value || !container.value) {
    return false
  }
  // Check if user is admin
  const isAdmin = user.value?.isAdmin ?? false
  if (!isAdmin) return false

  // For public containers, check authorId
  if (container.value.authorId) {
    return container.value.authorId === user.value.id
  }
  // For private containers (no authorId), if we can access the container,
  // it means we own it (backend handles authorization)
  // For localStorage, all containers are considered owned by current user
  return true
})

// Dialog state
const isAddContainerDialogOpen = ref(false)
const isExportToPromptDialogOpen = ref(false)
const isExportToCSVDialogOpen = ref(false)
const isAiDialogOpen = ref(false)

// File operations handled in handleImport

// Items
const items = computed<IGearItem[]>(() => container.value?.items ?? [])

// Display items with pending sorting changes applied
// This ensures that when user reorders items, the table shows the new order immediately
// even before saving, allowing for multiple reorders in sequence
const displayItems = computed<IGearItem[]>(() => {
  if (pendingSortingChanges.value.length === 0) {
    return items.value
  }

  // Create a map of pending changes by item ID
  const pendingMap = new Map(pendingSortingChanges.value.map(item => [item.id, item]))

  // Merge pending changes with current items
  // Items with pending changes use pending order, others keep their current order
  const mergedItems = items.value.map(item => {
    const pending = pendingMap.get(item.id)
    if (pending) {
      return { ...item, order: pending.order }
    }
    return item
  })

  // If pending changes contain all items (complete reorder), sort by order
  // Otherwise, items are already in correct order from items.value
  if (pendingSortingChanges.value.length === items.value.length) {
    return [...mergedItems].sort((a, b) => {
      const orderA = a.order ?? Number.MAX_SAFE_INTEGER
      const orderB = b.order ?? Number.MAX_SAFE_INTEGER
      return orderA - orderB
    })
  }

  return mergedItems
})

// Pending sorting changes (for batch save when backend enabled)
const pendingSortingChanges = ref<IGearItem[]>([])
const isSavingSorting = ref(false)

// Actions
const handleEditItem = (item: IGearItem) => {
  router.push({
    path: GearRoutePath.ItemEditById(containerId, item.id),
    query: { returnTo: 'container' },
  })
}

const handleDeleteItem = async (item: IGearItem) => {
  if (!confirm(t('gear.item.deleteConfirm'))) return
  try {
    await deleteItem(item.id)
    toast.success(t('common.success'))
  } catch {
    toast.error(t('common.error'))
  }
}

const handleStatusChange = async (item: IGearItem, status: IGearItem['status']) => {
  try {
    await updateItem(item.id, { status })
    toast.success(t('common.success'))
  } catch {
    toast.error(t('common.error'))
  }
}

const handleHideItemImages = async () => {
  if (!container.value) return
  try {
    await updateContainer(container.value.id, { showItemImages: false })
    toast.success(t('gear.container.itemImages.hidden', 'Item images hidden'))
  } catch {
    toast.error(t('common.error'))
  }
}

const handleReorder = (reorderedItems: IGearItem[]) => {
  // Store pending changes - don't save yet, wait for user confirmation
  // Alert will show for both backend and localStorage
  // This works the same way as handleSortingChange - batch mode with confirmation
  pendingSortingChanges.value = reorderedItems
}

const handleSortingChange = (sortedItems: IGearItem[]) => {
  // If sorting was cleared (empty array), clear pending changes
  if (sortedItems.length === 0) {
    pendingSortingChanges.value = []
    return
  }

  // Store pending changes - don't save yet, wait for user confirmation
  // Alert will show for both backend and localStorage
  pendingSortingChanges.value = sortedItems
}

const handleSaveSorting = async () => {
  if (pendingSortingChanges.value.length === 0) return

  try {
    isSavingSorting.value = true
    const service = gearItemService()

    // Use batchUpdateOrder for both backend and localStorage
    if ('batchUpdateOrder' in service && typeof service.batchUpdateOrder === 'function') {
      await service.batchUpdateOrder(pendingSortingChanges.value)
      toast.success(t('gear.item.reorderSuccess', 'Kolejność przedmiotów została zaktualizowana'))
      pendingSortingChanges.value = []
    } else {
      // Fallback: Update all items with new order values
      await Promise.all(
        pendingSortingChanges.value.map(item =>
          updateItem(item.id, { order: item.order }),
        ),
      )
      toast.success(t('gear.item.reorderSuccess', 'Kolejność przedmiotów została zaktualizowana'))
      pendingSortingChanges.value = []
    }
  } catch {
    toast.error(t('common.error'))
  } finally {
    isSavingSorting.value = false
  }
}

const handleCancelSorting = async () => {
  // Clear pending changes
  pendingSortingChanges.value = []

  // Reload container to restore original order
  // For localStorage: store is reactive, so clearing pending changes is enough
  // For backend: we need to reload from API to get original order
  if (shouldUseAPI.value && container.value) {
    try {
      // Reload container from API to restore original order
      await getContainerById(container.value.id)
      // Container will automatically update via reactive computed property
    } catch {
      // If refresh fails, just clear pending changes
      // User can manually reset sorting
    }
  }
}

const handleExport = async () => {
  try {
    const json = await exportData()
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `gear-stack-export-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    toast.success(t('common.success'))
  } catch {
    toast.error(t('common.error'))
  }
}

const handleImport = () => {
  // Use native input element for file selection
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'application/json'
  input.onchange = (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = async (event) => {
      try {
        const json = event.target?.result as string
        await importData(json)
        toast.success(t('common.success'))
        // Reload page to show imported data
        window.location.reload()
      } catch (error) {
        toast.error(t('common.error'))
        console.error('Import error:', error)
      }
    }
    reader.readAsText(file)
  }
  input.click()
}

const handleAddContainer = () => {
  isAddContainerDialogOpen.value = true
}

const handleAddNestedContainer = async (nestedContainerId: string) => {
  try {
    const nestedContainer = store.getContainerById(nestedContainerId)
    if (!nestedContainer) {
      toast.error(t('common.error'))
      return
    }

    // Create an item that references the nested container
    // Use container name as item name
    await createItem(containerId, {
      name: nestedContainer.name,
      category: 'other',
      quantity: 1,
      weight: 0,
      weightUnit: 'g',
      priority: 'medium',
      status: 'owned',
      containerId: nestedContainerId,
    })
    toast.success(t('common.success'))
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error adding nested container:', error)
  }
}

const handleExportToPrompt = () => {
  if (!container.value) return
  isExportToPromptDialogOpen.value = true
}

const handleExportToCSV = () => {
  if (!container.value) return
  isExportToCSVDialogOpen.value = true
}

const handleRecognizeParameters = async (item: IGearItem) => {
  try {
    const params = recognizeParameters(item.name)

    if (!params.brand && !params.color) {
      toast.info(t('gear.actions.noParametersFound'))
      return
    }

    const updateData: Partial<IGearItem> = {}
    if (params.brand && !item.brand) {
      updateData.brand = params.brand
    }
    if (params.color && !item.color) {
      updateData.color = params.color
    }

    if (Object.keys(updateData).length > 0) {
      await updateItem(item.id, updateData)
      toast.success(t('gear.actions.parametersRecognized'))
    } else {
      toast.info(t('gear.actions.noParametersFound'))
    }
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error recognizing parameters:', error)
  }
}

const handleRecognizeParametersAll = async () => {
  if (!container.value || !items.value || items.value.length === 0) return

  try {
    toast.loading(t('gear.actions.recognizing'))

    const paramsMap = recognizeParametersForItems(items.value)
    let updatedCount = 0

    for (const item of items.value) {
      const params = paramsMap.get(item.id)
      if (!params) continue

      const updateData: Partial<IGearItem> = {}
      if (params.brand && !item.brand) {
        updateData.brand = params.brand
      }
      if (params.color && !item.color) {
        updateData.color = params.color
      }

      if (Object.keys(updateData).length > 0) {
        await updateItem(item.id, updateData)
        updatedCount++
      }
    }

    toast.dismiss()
    if (updatedCount > 0) {
      toast.success(t('gear.actions.parametersRecognized', { count: updatedCount }))
    } else {
      toast.info(t('gear.actions.noParametersFound'))
    }
  } catch (error) {
    toast.dismiss()
    toast.error(t('common.error'))
    console.error('Error recognizing parameters:', error)
  }
}

// Redirect if container not found
if (!container.value) {
  router.push(GearRoutePath.Containers)
}
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="container" class="space-y-6 w-full max-w-full">
      <ContainerHeader
        :container="container"
        @export="handleExport"
        @import="handleImport"
        @add-container="handleAddContainer"
        @export-to-prompt="handleExportToPrompt"
        @export-to-csv="handleExportToCSV"
        @recognize-parameters-all="handleRecognizeParametersAll"
        @ai-chat="isAiDialogOpen = true"
      />

      <!-- Sort Confirmation Alert (always show when there are pending changes) -->
      <SortConfirmationAlert
        v-if="pendingSortingChanges.length > 0"
        :pending-items="pendingSortingChanges"
        :loading="isSavingSorting"
        @save="handleSaveSorting"
        @cancel="handleCancelSorting"
      />

      <!-- Items Table -->
      <ItemsTable
        :items="displayItems"
        :container-id="containerId"
        @edit="handleEditItem"
        @delete="handleDeleteItem"
        @status-change="handleStatusChange"
        @recognize-parameters="handleRecognizeParameters"
        @reorder="handleReorder"
        @sorting-change="handleSortingChange"
      />

      <!-- Container Item Images Gallery -->
      <ContainerItemImagesGallery
        :items="items"
        :container-id="containerId"
        :editable="canEditContainer"
        :show-item-images="container.showItemImages"
        @hide="handleHideItemImages"
      />

      <!-- Category Pie Chart -->
      <CategoryPieChart :container="container" />

      <!-- Add Nested Container Dialog -->
      <AddNestedContainerDialog
        v-model:open="isAddContainerDialogOpen"
        :current-container-id="containerId"
        @confirm="handleAddNestedContainer"
      />

      <!-- Export to Prompt Dialog -->
      <ExportToPromptDialog
        v-model:open="isExportToPromptDialogOpen"
        :container="container"
      />

      <!-- Export to CSV Dialog -->
      <ExportToCSVDialog
        v-model:open="isExportToCSVDialogOpen"
        :container="container"
      />

      <!-- AI Chat Dialog -->
      <AiChatDialog
        v-if="user?.isAdmin"
        v-model:open="isAiDialogOpen"
        :context="{ container_ids: [containerId] }"
      />
    </div>
  </AuthenticatedLayout>
</template>

