<script setup lang="ts">
// File operations handled via native input element
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useBackend } from '@/shared/composables/useBackend'
import type { IGearItem } from '../types/gear.types'
import AddNestedContainerDialog from '../components/AddNestedContainerDialog.vue'
import CategoryPieChart from '../components/CategoryPieChart.vue'
import ContainerHeader from '../components/ContainerHeader.vue'
import ExportToPromptDialog from '../components/ExportToPromptDialog.vue'
import ItemsTable from '../components/ItemsTable.vue'
import SortConfirmationAlert from '../components/SortConfirmationAlert.vue'
import { useContainer } from '../composables/useContainer'
import { useGear } from '../composables/useGear'
import { gearItemService } from '../services/gearItemService'
import { useGearStore } from '../store/useGearStore'
import { recognizeParameters, recognizeParametersForItems } from '../utils/parameterRecognition'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const store = useGearStore()
const { shouldUseAPI } = useBackend()
const { container } = useContainer()
const { deleteItem, updateItem, exportData, importData, createItem } = useGear()

const containerId = route.params.id as string

// Dialog state
const isAddContainerDialogOpen = ref(false)
const isExportToPromptDialogOpen = ref(false)

// File operations handled in handleImport

// Items
const items = computed<IGearItem[]>(() => container.value?.items ?? [])

// Pending sorting changes (for batch save when backend enabled)
const pendingSortingChanges = ref<IGearItem[]>([])
const isSavingSorting = ref(false)

// Actions
const handleEditItem = (item: IGearItem) => {
  router.push(`/gear/${containerId}/items/${item.id}/edit`)
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

const handleReorder = async (reorderedItems: IGearItem[]) => {
  try {
    // If backend enabled, use batch update
    if (shouldUseAPI.value) {
      const service = gearItemService()
      if ('batchUpdateOrder' in service && typeof service.batchUpdateOrder === 'function') {
        await service.batchUpdateOrder(reorderedItems)
        toast.success(t('gear.item.reorderSuccess', 'Kolejność przedmiotów została zaktualizowana'))
        return
      }
    }
    
    // Fallback: Update all items with new order values (for localStorage)
    await Promise.all(
      reorderedItems.map(item =>
        updateItem(item.id, { order: item.order }),
      ),
    )
  } catch {
    toast.error(t('common.error'))
  }
}

const handleSortingChange = async (sortedItems: IGearItem[]) => {
  // If sorting was cleared (empty array), clear pending changes
  if (sortedItems.length === 0) {
    pendingSortingChanges.value = []
    return
  }
  
  // Always update locally first (for immediate UI feedback and persistence)
  // This ensures sorting persists even if user navigates away
  await Promise.all(
    sortedItems.map(item =>
      updateItem(item.id, { order: item.order }),
    ),
  )
  
  // If backend enabled, also show confirmation alert for batch save
  if (shouldUseAPI.value) {
    pendingSortingChanges.value = sortedItems
  }
}

const handleSaveSorting = async () => {
  if (pendingSortingChanges.value.length === 0) return
  
  try {
    isSavingSorting.value = true
    const service = gearItemService()
    if ('batchUpdateOrder' in service && typeof service.batchUpdateOrder === 'function') {
      await service.batchUpdateOrder(pendingSortingChanges.value)
      toast.success(t('gear.item.reorderSuccess', 'Kolejność przedmiotów została zaktualizowana'))
      pendingSortingChanges.value = []
    } else {
      // Fallback
      await handleReorder(pendingSortingChanges.value)
      pendingSortingChanges.value = []
    }
  } catch {
    toast.error(t('common.error'))
  } finally {
    isSavingSorting.value = false
  }
}

const handleCancelSorting = () => {
  pendingSortingChanges.value = []
  // Optionally reload container to reset sorting
  // For now, just clear pending changes - user can manually reset sorting
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
  router.push('/gear')
}
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="container" class="space-y-6 w-full max-w-full overflow-hidden">
      <ContainerHeader
        :container="container"
        @export="handleExport"
        @import="handleImport"
        @add-container="handleAddContainer"
        @export-to-prompt="handleExportToPrompt"
        @recognize-parameters-all="handleRecognizeParametersAll"
      />

      <!-- Sort Confirmation Alert (only when backend enabled) -->
      <SortConfirmationAlert
        v-if="shouldUseAPI"
        :pending-items="pendingSortingChanges"
        :loading="isSavingSorting"
        @save="handleSaveSorting"
        @cancel="handleCancelSorting"
      />

      <!-- Items Table -->
      <ItemsTable
        :items="items"
        @edit="handleEditItem"
        @delete="handleDeleteItem"
        @status-change="handleStatusChange"
        @recognize-parameters="handleRecognizeParameters"
        @reorder="handleReorder"
        @sorting-change="handleSortingChange"
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
    </div>
  </AuthenticatedLayout>
</template>

