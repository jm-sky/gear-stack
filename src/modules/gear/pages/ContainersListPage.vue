<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import { Package, Plus, PlusIcon, Sparkles } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { IGearContainer } from '../types/gear.types'
import ContainerCard from '../components/ContainerCard.vue'
import ContainersFilters from '../components/ContainersFilters.vue'
import ContainersListPageDropdown from '../components/ContainersListPageDropdown.vue'
import ExportToPromptDialog from '../components/ExportToPromptDialog.vue'
import ImportMarkdownDialog from '../components/ImportMarkdownDialog.vue'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
import { generateSampleSet } from '../services/sampleSetGenerator'
import type { TUUID } from '@/shared/types/base.type'

const router = useRouter()
const { t } = useI18n()
const { containers, deleteContainer, getRootContainers } = useGear()
const { customContainerTypes } = useGearSettings()

// Filters - using refs that will be bound to ContainersFilters via v-model
const searchQueryRaw = ref('')
const searchQuery = refDebounced(searchQueryRaw, 300)
const showOnlyRootContainers = ref(false)

// Dialogs
const importDialogOpen = ref(false)
const isExportToPromptDialogOpen = ref(false)

// Helper to get container type label for filtering
const getContainerTypeLabel = (typeKey: string): string => {
  const customType = customContainerTypes.value.find(t => t.key === typeKey)
  if (customType) {
    return customType.label
  }
  return t(`gear.container.types.${typeKey}`)
}

// Filtered containers
const filteredContainers = computed<IGearContainer[]>(() => {
  // First filter by root containers if enabled
  let baseContainers = containers.value
  if (showOnlyRootContainers.value) {
    baseContainers = getRootContainers()
  }

  // Then filter by search query
  if (!searchQuery.value.trim()) {
    return baseContainers
  }

  const query = searchQuery.value.toLowerCase()
  return baseContainers.filter(container => {
    return (
      container.name.toLowerCase().includes(query) ||
      container.description?.toLowerCase().includes(query) ||
      getContainerTypeLabel(container.type).toLowerCase().includes(query)
    )
  })
})

// Actions
const handleCreate = () => {
  router.push('/gear/new')
}

const handleImport = () => {
  importDialogOpen.value = true
}

const handleImportComplete = () => {
  // Refresh is automatic via store reactivity
}

const handleDelete = (id: TUUID) => {
  if (confirm(t('gear.container.deleteConfirm'))) {
    try {
      deleteContainer(id)
      toast.success(t('common.success'))
    } catch {
      toast.error(t('common.error'))
    }
  }
}

const handleExportAllToPrompt = () => {
  if (containers.value.length === 0) {
    toast.error(t('gear.export.noContainers'))
    return
  }

  isExportToPromptDialogOpen.value = true
}

const handleGenerateSampleSet = () => {
  try {
    generateSampleSet(t)
    toast.success(t('gear.sampleSet.success'))
  } catch (error) {
    console.error('Error generating sample set:', error)
    toast.error(t('common.error'))
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-bold">
            {{ t('gear.page.containers') }}
          </h1>
          <p class="text-muted-foreground mt-1">
            {{ t('gear.page.title') }}
          </p>
        </div>
        <div class="flex flex-col sm:flex-row gap-2">
          <div class="flex gap-2">
            <Button
              v-tooltip.bottom="t('gear.export.allToPrompt')"
              variant="outline"
              class="shrink-0"
              @click="handleExportAllToPrompt"
            >
              <Sparkles class="size-4" />
            </Button>
            <Button
              v-tooltip.bottom="t('gear.container.create.title')"
              variant="default"
              class="shrink-0 flex-1 sm:flex-none"
              @click="handleCreate"
            >
              <PlusIcon class="size-4" />
              {{ t('gear.container.create.title') }}
            </Button>
            <ContainersListPageDropdown @export-all-to-prompt="handleExportAllToPrompt" @import="handleImport" />
          </div>
          <Button
            variant="outline"
            class="w-full sm:w-auto shrink-0"
            @click="handleGenerateSampleSet"
          >
            {{ t('gear.sampleSet.generateButton') }}
          </Button>
        </div>
      </div>

      <!-- Search and Filters -->
      <ContainersFilters
        v-model:search-query="searchQueryRaw"
        v-model:show-only-root-containers="showOnlyRootContainers"
      />

      <!-- Containers Grid -->
      <div v-if="filteredContainers.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ContainerCard
          v-for="container in filteredContainers"
          :key="container.id"
          :container="container"
          @delete="handleDelete"
        />
      </div>

      <!-- Empty State -->
      <div v-else class="flex flex-col items-center justify-center py-12 text-center">
        <div class="rounded-full bg-muted p-6 mb-4">
          <Package class="size-12 text-muted-foreground" />
        </div>
        <h3 class="text-lg font-semibold mb-2">
          {{ t('gear.container.empty') }}
        </h3>
        <p class="text-muted-foreground mb-6 max-w-md">
          {{ t('gear.container.emptyDescription') }}
        </p>
        <div class="flex flex-col md:flex-row flex-wrap gap-2">
          <Button @click="handleCreate">
            <Plus class="size-4" />
            {{ t('gear.container.create.title') }}
          </Button>
          <Button variant="outline" @click="handleGenerateSampleSet">
            {{ t('gear.sampleSet.generateButton') }}
          </Button>
        </div>
      </div>
    </div>

    <!-- Import Dialog -->
    <ImportMarkdownDialog
      v-model:open="importDialogOpen"
      @import-complete="handleImportComplete"
    />

    <!-- Export to Prompt Dialog -->
    <ExportToPromptDialog
      v-model:open="isExportToPromptDialogOpen"
      :containers="containers"
    />
  </AuthenticatedLayout>
</template>

