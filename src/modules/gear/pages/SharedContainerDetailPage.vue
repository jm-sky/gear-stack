<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { IGearItemV2 } from '../types/gear.types.v2'
const CategoryPieChart = defineAsyncComponent(() => import('../components/CategoryPieChart.vue'))
import ContainerReadinessProgressBar from '../components/ContainerReadinessProgressBar.vue'
import ItemsTable from '../components/ItemsTable.vue'
import PublicContainerHeader from '../components/PublicContainerHeader.vue'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { sharedContainersService } from '../services/sharedContainersService'
import {
  calculateReadinessPercentageSyncV2,
  calculateTotalWeightSyncV2,
} from '../utils/containerCalculationsV2'
import { buildContainerTreeFromApi, type IContainerTreeAccessors } from '../utils/containerTree'
import { formatWeightToPreferredUnit } from '../utils/formatWeight'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const { settings: gearSettings } = useGearSettings()

const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

const token = route.params.token as string
const container = ref<IGearItemV2 | null>(null)
const isLoading = ref(true)
const accessors = ref<IContainerTreeAccessors | null>(null)

const loadContainer = async () => {
  try {
    const loadedContainer = await sharedContainersService.getSharedContainer(token)
    const tree = buildContainerTreeFromApi(loadedContainer)
    container.value = tree.container
    accessors.value = tree
  } catch (error) {
    console.error('Failed to load shared container:', error)
    toast.error(t('gear.sharedContainers.notFound'))
    router.push(GearRoutePath.PublicContainers)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadContainer()
})

const items = computed<IGearItemV2[]>(() => container.value?.children ?? [])

const totalWeight = computed<number>(() => {
  if (!container.value || !accessors.value) return 0
  return calculateTotalWeightSyncV2(
    container.value.id,
    accessors.value.getItemById,
    accessors.value.getChildrenOfItem,
  )
})

const readinessPercentage = computed<number>(() => {
  if (!container.value || !accessors.value) return 0
  return calculateReadinessPercentageSyncV2(
    container.value.id,
    accessors.value.getItemById,
    accessors.value.getChildrenOfItem,
  )
})

const formattedWeight = computed<string>(() => formatWeightToPreferredUnit(totalWeight.value, settings.value.preferredWeightUnit, locale.value))

const handleBack = () => {
  router.push(GearRoutePath.PublicContainers)
}
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="isLoading" class="space-y-6">
      <div class="h-12 bg-muted rounded animate-pulse" />
      <div class="h-64 bg-muted rounded animate-pulse" />
    </div>

    <div v-else-if="container" class="space-y-6 w-full max-w-full overflow-hidden">
      <!-- Header -->
      <PublicContainerHeader
        v-if="container"
        :container="container"
        :back-path="GearRoutePath.PublicContainers"
        @back="handleBack"
      />

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-card rounded-lg border p-4">
          <div class="text-sm text-muted-foreground mb-1">
            {{ t('gear.container.itemsCountLabel') }}
          </div>
          <div class="text-2xl font-bold">
            {{ items.length }}
          </div>
        </div>
        <div class="bg-card rounded-lg border p-4">
          <div class="text-sm text-muted-foreground mb-1">
            {{ t('gear.container.totalWeight') }}
          </div>
          <div class="text-2xl font-bold">
            {{ formattedWeight }}
          </div>
        </div>
        <div class="bg-card rounded-lg border p-4">
          <div class="text-sm text-muted-foreground mb-1">
            {{ t('gear.container.readiness') }}
          </div>
          <div class="text-2xl font-bold">
            {{ readinessPercentage }}%
          </div>
        </div>
      </div>

      <!-- Readiness Progress Bar -->
      <ContainerReadinessProgressBar :readiness-percentage />

      <!-- Items Table (read-only - no edit/delete actions) -->
      <ItemsTable
        :items="items"
        :public-mode="true"
        :container-id="container.id"
      />

      <!-- Category Pie Chart -->
      <CategoryPieChart
        v-if="container"
        :container="container"
        :items="items"
      />
    </div>
  </AuthenticatedLayout>
</template>
