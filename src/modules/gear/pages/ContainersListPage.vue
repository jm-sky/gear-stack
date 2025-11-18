<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import { Package, Plus, Search } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useSettings } from '@/modules/settings/composables/useSettings'
import type { IGearContainer } from '../types/gear.types'
import ContainerCard from '../components/ContainerCard.vue'
import { useGear } from '../composables/useGear'
import type { TUUID } from '@/shared/types/base.type'

const router = useRouter()
const { t } = useI18n()
const { containers, deleteContainer, getRootContainers } = useGear()
const { customContainerTypes } = useSettings()

// Search
const searchQueryRaw = ref('')
const searchQuery = refDebounced(searchQueryRaw, 300)

// Filter: show only root containers
const showOnlyRootContainers = ref(false)

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
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6">
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
        <Button class="sm:shrink-0" @click="handleCreate">
          <Plus class="size-4" />
          {{ t('gear.container.create.title') }}
        </Button>
      </div>

      <!-- Search and Filters -->
      <div class="space-y-4">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            v-model="searchQueryRaw"
            :placeholder="t('gear.filters.search')"
            class="pl-9"
          />
        </div>
        <div class="flex items-center gap-2">
          <input
            id="root-containers-filter"
            v-model="showOnlyRootContainers"
            type="checkbox"
            class="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
          />
          <label for="root-containers-filter" class="text-sm text-muted-foreground cursor-pointer">
            {{ t('gear.container.showOnlyRootContainers') }}
          </label>
        </div>
      </div>

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
          <Package class="h-12 w-12 text-muted-foreground" />
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
  </AuthenticatedLayout>
</template>

