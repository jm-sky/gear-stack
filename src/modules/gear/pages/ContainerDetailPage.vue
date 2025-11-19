<script setup lang="ts">
// File operations handled via native input element
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { IGearItem } from '../types/gear.types'
import AddNestedContainerDialog from '../components/AddNestedContainerDialog.vue'
import CategoryPieChart from '../components/CategoryPieChart.vue'
import ContainerHeader from '../components/ContainerHeader.vue'
import ItemsTable from '../components/ItemsTable.vue'
import { useContainer } from '../composables/useContainer'
import { useGear } from '../composables/useGear'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { container } = useContainer()
const { deleteItem, updateItem, exportData, importData, createItem, getContainerById } = useGear()

const containerId = route.params.id as string

// Dialog state
const isAddContainerDialogOpen = ref(false)

// File operations handled in handleImport

// Items
const items = computed<IGearItem[]>(() => container.value?.items ?? [])

// Actions
const handleEditItem = (item: IGearItem) => {
  router.push(`/gear/${containerId}/items/${item.id}/edit`)
}

const handleDeleteItem = (item: IGearItem) => {
  if (!confirm(t('gear.item.deleteConfirm'))) return
  try {
    deleteItem(containerId, item.id)
    toast.success(t('common.success'))
  } catch {
    toast.error(t('common.error'))
  }
}

const handleStatusChange = (item: IGearItem, status: IGearItem['status']) => {
  try {
    updateItem(containerId, item.id, { status })
    toast.success(t('common.success'))
  } catch {
    toast.error(t('common.error'))
  }
}

const handleExport = () => {
  try {
    const json = exportData()
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
    reader.onload = (event) => {
      try {
        const json = event.target?.result as string
        importData(json)
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

const handleAddNestedContainer = (nestedContainerId: string) => {
  try {
    const nestedContainer = getContainerById(nestedContainerId)
    if (!nestedContainer) {
      toast.error(t('common.error'))
      return
    }

    // Create an item that references the nested container
    // Use container name as item name
    createItem(containerId, {
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

// Redirect if container not found
if (!container.value) {
  router.push('/gear')
}
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="container" class="space-y-6">
      <ContainerHeader
        :container="container"
        @export="handleExport"
        @import="handleImport"
        @add-container="handleAddContainer"
      />

      <!-- Items Table -->
      <div class="bg-card rounded-lg border p-4 sm:p-6 overflow-x-auto">
        <ItemsTable
          :items="items"
          @edit="handleEditItem"
          @delete="handleDeleteItem"
          @status-change="handleStatusChange"
        />
      </div>

      <!-- Category Pie Chart -->
      <CategoryPieChart :container="container" />

      <!-- Add Nested Container Dialog -->
      <AddNestedContainerDialog
        v-model:open="isAddContainerDialogOpen"
        :current-container-id="containerId"
        @confirm="handleAddNestedContainer"
      />
    </div>
  </AuthenticatedLayout>
</template>

