<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import type { IGearItemV2, TRatingType, TRatingValue } from '../types/gear.types.v2'
const CategoryPieChart = defineAsyncComponent(() => import('../components/CategoryPieChart.vue'))
import ContainerRatingCard from '../components/ContainerRatingCard.vue'
import ContainerReadinessProgressBar from '../components/ContainerReadinessProgressBar.vue'
import ItemsTable from '../components/ItemsTable.vue'
import PublicContainerHeader from '../components/PublicContainerHeader.vue'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { gearContainerApiService } from '../services/gearContainerApiService'
import { publicContainersService } from '../services/publicContainersService'
import { useGearStore } from '../store/useGearStore'
import {
  calculateReadinessPercentageSync,
  calculateTotalWeightSync,
} from '../utils/containerCalculations'
import { formatWeightToPreferredUnit } from '../utils/formatWeight'
import { convertV1ContainerToV2 } from '../utils/typeConverters'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const store = useGearStore()
const { settings: gearSettings } = useGearSettings()
const { user } = useAuth()

const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

const containerId = route.params.id as string
const container = ref<IGearItemV2 | null>(null)
const isLoading = ref(true)
const isRatingLoading = ref(false)

const isOwner = computed(() => {
  if (!user.value || !container.value) {
    return false
  }
  // For public containers, check authorId
  if (container.value.authorId) {
    return container.value.authorId === user.value.id
  }
  // If no authorId, user is not the owner (public container from another user)
  return false
})
const isPublic = computed(() => {
  return container.value?.isPublic ?? false
})

// Convert V1 container to V2 for components that use V2 types
const containerV2 = computed(() => {
  return container.value ? convertV1ContainerToV2(container.value) : null
})

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
  if (!container.value) return 0
  return calculateTotalWeightSync(container.value, store.getAllContainers)
})

const readinessPercentage = computed<number>(() => {
  if (!container.value) return 0
  return calculateReadinessPercentageSync(container.value)
})

const formattedWeight = computed<string>(() => formatWeightToPreferredUnit(totalWeight.value, settings.value.preferredWeightUnit, locale.value))

const handleBack = () => {
  router.push(GearRoutePath.PublicContainers)
}

const handleRate = async (rating: TRatingValue, type: TRatingType) => {
  if (!container.value) return

  isRatingLoading.value = true
  try {
    await gearContainerApiService.rateContainer(
      container.value.id,
      rating,
      type
    )
    // Refresh container data
    await loadContainer()
    toast.success(t('gear.container.ratingUpdated'))
  } catch (error) {
    console.error('Failed to rate container:', error)
    toast.error(t('gear.errors.ratingFailed'))
  } finally {
    isRatingLoading.value = false
  }
}

const handleDeleteRating = async (type: TRatingType) => {
  if (!container.value) return

  isRatingLoading.value = true
  try {
    await gearContainerApiService.deleteContainerRating(
      container.value.id,
      type
    )
    // Refresh container data
    await loadContainer()
    toast.success(t('gear.container.ratingDeleted'))
  } catch (error) {
    console.error('Failed to delete rating:', error)
    toast.error(t('gear.errors.deleteRatingFailed'))
  } finally {
    isRatingLoading.value = false
  }
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
        v-if="containerV2"
        :container="containerV2"
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
        :container-id="containerId"
      />

      <!-- Rating Section -->
      <Card>
        <CardHeader>
          <CardTitle>{{ t('gear.container.ratings') }}</CardTitle>
        </CardHeader>
        <CardContent>
          <ContainerRatingCard
            v-if="containerV2"
            :container="containerV2"
            :is-owner="isOwner"
            :is-public="isPublic"
            :loading="isRatingLoading"
            @rate="handleRate"
            @delete-rating="handleDeleteRating"
          />
        </CardContent>
      </Card>

      <!-- Category Pie Chart -->
      <CategoryPieChart v-if="containerV2" :container="containerV2" />
    </div>
  </AuthenticatedLayout>
</template>
