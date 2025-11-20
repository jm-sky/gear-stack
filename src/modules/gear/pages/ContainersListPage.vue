<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import { ChevronDown, FileInput, Package, Plus, Sparkles, Trash2 } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useSettings } from '@/modules/settings/composables/useSettings'
import type { IGearContainer } from '../types/gear.types'
import ContainerCard from '../components/ContainerCard.vue'
import ContainersFilters from '../components/ContainersFilters.vue'
import ExportToPromptDialog from '../components/ExportToPromptDialog.vue'
import ImportMarkdownDialog from '../components/ImportMarkdownDialog.vue'
import { useGear } from '../composables/useGear'
import { exportContainersToPrompt } from '../utils/exportToPrompt'
import type { TUUID } from '@/shared/types/base.type'

const router = useRouter()
const { t } = useI18n()
const { containers, deleteContainer, deleteAllContainers, getRootContainers, getContainerById, calculateTotalWeight } = useGear()
const { customContainerTypes } = useSettings()

// Filters - using refs that will be bound to ContainersFilters via v-model
const searchQueryRaw = ref('')
const searchQuery = refDebounced(searchQueryRaw, 300)
const showOnlyRootContainers = ref(false)

// Dialogs
const importDialogOpen = ref(false)
const isExportToPromptDialogOpen = ref(false)
const exportMarkdown = ref('')

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

const handleDeleteAll = () => {
  if (confirm(t('gear.container.deleteAllConfirm'))) {
    try {
      deleteAllContainers()
      toast.success(t('gear.container.deleteAllSuccess'))
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

  try {
    const markdown = exportContainersToPrompt(containers.value, {
      t,
      getContainerTypeLabel,
      getContainerById,
      calculateTotalWeight,
    })

    exportMarkdown.value = markdown
    isExportToPromptDialogOpen.value = true
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error exporting to prompt:', error)
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
        <div class="flex gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="outline" class="sm:shrink-0">
                <Plus class="size-4" />
                {{ t('gear.container.create.title') }}
                <ChevronDown class="size-4 ml-1" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem @click="handleCreate">
                <Plus class="size-4 mr-2" />
                {{ t('gear.container.create.new') }}
              </DropdownMenuItem>
              <DropdownMenuItem @click="handleImport">
                <FileInput class="size-4 mr-2" />
                {{ t('gear.import.fromMarkdown') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator v-if="containers.length > 0" />
              <DropdownMenuItem
                v-if="containers.length > 0"
                @click="handleExportAllToPrompt"
              >
                <Sparkles class="size-4 mr-2" />
                {{ t('gear.export.allToPrompt') }}
              </DropdownMenuItem>
              <DropdownMenuSeparator v-if="containers.length > 0" />
              <DropdownMenuItem
                v-if="containers.length > 0"
                class="text-destructive focus:text-destructive"
                @click="handleDeleteAll"
              >
                <Trash2 class="size-4 mr-2" />
                {{ t('gear.container.deleteAll') }}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
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
        <Button @click="handleCreate">
          <Plus class="size-4" />
          {{ t('gear.container.create.title') }}
        </Button>
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
      :markdown="exportMarkdown"
    />
  </AuthenticatedLayout>
</template>

