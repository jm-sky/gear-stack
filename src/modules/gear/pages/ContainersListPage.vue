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
const { containers, deleteContainer } = useGear()
const { customContainerTypes } = useSettings()

// Search
const searchQueryRaw = ref('')
const searchQuery = refDebounced(searchQueryRaw, 300)

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
  if (!searchQuery.value.trim()) {
    return containers.value
  }

  const query = searchQuery.value.toLowerCase()
  return containers.value.filter(container => {
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
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold">
            {{ t('gear.page.containers') }}
          </h1>
          <p class="text-muted-foreground mt-1">
            {{ t('gear.page.title') }}
          </p>
        </div>
        <Button @click="handleCreate">
          <Plus class="size-4" />
          {{ t('gear.container.create') }}
        </Button>
      </div>

      <!-- Search -->
      <div class="relative">
        <Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          v-model="searchQueryRaw"
          :placeholder="t('gear.filters.search')"
          class="pl-9"
        />
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
          {{ t('gear.container.create') }}
        </Button>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

