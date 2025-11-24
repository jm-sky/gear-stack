<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import { Package } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { IGearContainer } from '../types/gear.types'
import ContainersFilters from '../components/ContainersFilters.vue'
import PublicContainerCard from '../components/PublicContainerCard.vue'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { publicContainersService } from '../services/publicContainersService'

const { t } = useI18n()
const { getContainerTypeLabel } = useContainerTypeLabel()

const containers = ref<IGearContainer[]>([])
const loading = ref(true)

// Search filter
const searchQueryRaw = ref('')
const searchQuery = refDebounced(searchQueryRaw, 300)

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
      getContainerTypeLabel(container.type).toLowerCase().includes(query) ||
      container.authorName?.toLowerCase().includes(query)
    )
  })
})

const loadContainers = async () => {
  loading.value = true
  try {
    containers.value = await publicContainersService.getPublicContainers()
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Failed to load public containers:', error)
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  loadContainers()
}

onMounted(() => {
  loadContainers()
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <!-- Header -->
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold">
          {{ t('gear.publicContainers.title') }}
        </h1>
        <p class="text-muted-foreground mt-1 text-sm sm:text-base">
          {{ t('gear.publicContainers.description') }}
        </p>
      </div>

      <!-- Search and Filters -->
      <ContainersFilters
        v-model:search-query="searchQueryRaw"
        :loading
        @refresh="handleRefresh"
      />

      <!-- Loading State -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i" class="h-48 bg-muted rounded-lg animate-pulse" />
      </div>

      <!-- Containers Grid -->
      <div v-else-if="filteredContainers.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PublicContainerCard
          v-for="container in filteredContainers"
          :key="container.id"
          :container
        />
      </div>

      <!-- Empty State -->
      <div v-else class="flex flex-col items-center justify-center py-12 text-center">
        <div class="rounded-full bg-muted p-6 mb-4">
          <Package class="size-12 text-muted-foreground" />
        </div>
        <h3 class="text-lg font-semibold mb-2">
          {{ t('gear.publicContainers.empty') }}
        </h3>
        <p class="text-muted-foreground max-w-md">
          {{ t('gear.publicContainers.emptyDescription') }}
        </p>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
