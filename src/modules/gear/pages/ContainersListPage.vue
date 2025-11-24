<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import { Package, Plus, PlusIcon, Sparkles } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { config } from '@/shared/config/config'
import type { IGearContainer } from '../types/gear.types'
import ContainerCard from '../components/ContainerCard.vue'
import ContainersFilters from '../components/ContainersFilters.vue'
import ContainersListPageDropdown from '../components/ContainersListPageDropdown.vue'
import ExportToPromptDialog from '../components/ExportToPromptDialog.vue'
import ImportMarkdownDialog from '../components/ImportMarkdownDialog.vue'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { useGear } from '../composables/useGear'
import { gearContainerService } from '../services/gearContainerService'
import { generateSampleSet } from '../services/sampleSetGenerator'
import { getRootContainers as getRootContainersUtil } from '../utils/containerNesting'
import type { TUUID } from '@/shared/types/base.type'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { containers, deleteContainer } = useGear()
const { getContainerTypeLabel } = useContainerTypeLabel()

// Filters - using refs that will be bound to ContainersFilters via v-model
const loading = ref(false)
const searchQueryRaw = ref('')
const searchQuery = refDebounced(searchQueryRaw, 300)
const showOnlyRootContainers = ref(false)

// Dialogs
const importDialogOpen = ref(false)
const isExportToPromptDialogOpen = ref(false)

// Check for import query parameter and open dialog, and load containers from API
onMounted(async () => {
  if (route.query.import === 'true') {
    importDialogOpen.value = true
    // Remove query parameter from URL
    router.replace({ query: { ...route.query, import: undefined } })
  }

  // Load containers from API on mount (when backend is enabled)
  if (config.backend.enabled) {
    try {
      loading.value = true
      await gearContainerService().getContainers()
    } catch (error) {
      console.error('Failed to load containers from API:', error)
      // Fallback to localStorage is handled by store initialization
    } finally {
      loading.value = false
    }
  }
})

// Watch for route changes (in case user navigates back/forward)
watch(() => route.query.import, (shouldImport) => {
  if (shouldImport === 'true') {
    importDialogOpen.value = true
    // Remove query parameter from URL
    router.replace({ query: { ...route.query, import: undefined } })
  }
})

// Filtered containers
const filteredContainers = computed<IGearContainer[]>(() => {
  // First filter by root containers if enabled
  let baseContainers = containers.value
  if (showOnlyRootContainers.value) {
    baseContainers = getRootContainersUtil(containers.value)
  } else {
    // Hide containers with hideWhenNested=true AND parentContainerId set
    baseContainers = baseContainers.filter(container => {
      if (container.hideWhenNested && container.parentContainerId) {
        return false // Hide this container
      }
      return true
    })
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

const handleDelete = async (id: TUUID) => {
  if (confirm(t('gear.container.deleteConfirm'))) {
    try {
      await deleteContainer(id)
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

const handleGenerateSampleSet = async () => {
  try {
    await generateSampleSet(t)
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
              v-if="containers.length > 0"
              v-tooltip.bottom="t('gear.export.allToPrompt')"
              variant="outline"
              class="shrink-0"
              :aria-label="$t('gear.export.allToPrompt')"
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
        </div>
      </div>

      <!-- Search and Filters -->
      <ContainersFilters
        v-model:search-query="searchQueryRaw"
        v-model:show-only-root-containers="showOnlyRootContainers"
        root-containers-filter
        :loading
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

