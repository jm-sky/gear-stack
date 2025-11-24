<script setup lang="ts">
import { ArrowLeft, Clock } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { smallDateTime } from '@/shared/utils/smallDateTime'
import type { IGearContainer } from '../types/gear.types'
import CategoryPieChart from '../components/CategoryPieChart.vue'
import ContainerReadinessProgressBar from '../components/ContainerReadinessProgressBar.vue'
import ItemsTable from '../components/ItemsTable.vue'
import PublicContainerAuthorBadge from '../components/PublicContainerAuthorBadge.vue'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { useGearSettings } from '../composables/useGearSettings'
import { publicContainersService } from '../services/publicContainersService'
import { useGearStore } from '../store/useGearStore'
import {
  calculateReadinessPercentageSync,
  calculateTotalWeightSync,
} from '../utils/containerCalculations'
import { formatWeightToPreferredUnit } from '../utils/formatWeight'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { isAuthenticated } = useAuth()
const store = useGearStore()
const { settings: gearSettings } = useGearSettings()

const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

const containerId = route.params.id as string
const container = ref<IGearContainer | null>(null)
const isLoading = ref(true)

const { typeLabel } = useContainerTypeLabel(computed(() => container.value?.type ?? ''))

const loadContainer = async () => {
  try {
    container.value = await publicContainersService.getPublicContainer(containerId)
    // Filter nested containers - only show items if nested container is public
    if (container.value) {
      container.value.items = container.value.items.filter(item => {
        if (item.containerId) {
          // Check if nested container is public
          const nestedContainer = store.getContainerById(item.containerId)
          return nestedContainer?.isPublic ?? false
        }
        return true
      })
    }
  } catch (error) {
    console.error('Failed to load public container:', error)
    toast.error(t('common.error'))
    router.push('/gear/public')
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadContainer()
})

const items = computed<IGearContainer['items']>(() => container.value?.items ?? [])

const totalWeight = computed<number>(() => {
  if (!container.value) return 0
  return calculateTotalWeightSync(container.value, store.getAllContainers)
})

const readinessPercentage = computed<number>(() => {
  if (!container.value) return 0
  return calculateReadinessPercentageSync(container.value)
})

const formattedWeight = computed<string>(() => formatWeightToPreferredUnit(totalWeight.value, settings.value.preferredWeightUnit))

const handleBack = () => {
  router.push('/gear/public')
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
      <div class="space-y-4">
        <Button variant="ghost" size="sm" @click="handleBack">
          <ArrowLeft class="size-4" />
          {{ t('common.back') }}
        </Button>

        <div>
          <h1 class="text-2xl sm:text-3xl font-bold mb-2 wrap-break-word">
            {{ container.name }}
          </h1>
          <p v-if="container.description" class="text-muted-foreground mb-3 text-sm sm:text-base wrap-break-word">
            {{ container.description }}
          </p>
          <div class="flex items-center gap-2 flex-wrap">
            <Badge variant="outline">
              {{ typeLabel }}
            </Badge>
            <PublicContainerAuthorBadge
              v-if="container.authorName && container.authorId && isAuthenticated"
              :author-name="container.authorName"
              :author-id="container.authorId"
              as-link
            />
            <PublicContainerAuthorBadge
              v-else-if="container.authorName && !isAuthenticated"
              :author-name="container.authorName"
            />
            <Badge variant="secondary" class="text-xs">
              <Clock class="size-3" />
              {{ smallDateTime(container.createdAt) }}
            </Badge>
          </div>
        </div>
      </div>

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
      />

      <!-- Category Pie Chart -->
      <CategoryPieChart :container="container" />
    </div>
  </AuthenticatedLayout>
</template>
