<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import type { IGearItem } from '../types/gear.types'
import CategoryIcon from '../components/CategoryIcon.vue'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { publicContainersService } from '../services/publicContainersService'
import { getPriorityVariant, getStatusVariant } from '../utils/badgeVariants'
import { EXPIRATION_WARNING_DAYS } from '../utils/constants'
import { formatCurrency, getCurrency } from '../utils/currencyFormatter'
import { formatWeightWithPreferredUnit } from '../utils/formatWeight'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { settings: gearSettings, defaultCurrency, customCategories } = useGearSettings()

const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

const containerId = route.params.containerId as string
const itemId = route.params.itemId as string
const item = ref<IGearItem | null>(null)
const isLoading = ref(true)

// Helper to get category label
const getCategoryLabel = (categoryValue: string): string => {
  const customCategory = customCategories.value.find(c => c.value === categoryValue)
  if (customCategory) {
    return customCategory.value
  }
  return t(`gear.item.categories.${categoryValue}`)
}

// Helper to check if item is expired
function isExpired(item: IGearItem): boolean {
  if (!item.expirationDate) return false
  return new Date(item.expirationDate) < new Date()
}

// Helper to check if item is expiring soon
function isExpiringSoon(item: IGearItem, days: number = EXPIRATION_WARNING_DAYS): boolean {
  if (!item.expirationDate) return false
  const expirationDate = new Date(item.expirationDate)
  const now = new Date()
  const MILLISECONDS_PER_DAY = 1000 * 60 * 60 * 24
  const daysUntilExpiration = Math.ceil((expirationDate.getTime() - now.getTime()) / MILLISECONDS_PER_DAY)
  return daysUntilExpiration > 0 && daysUntilExpiration <= days
}

const loadItem = async () => {
  try {
    // Load container to get the item
    const container = await publicContainersService.getPublicContainer(containerId)
    const foundItem = container.items.find(i => i.id === itemId)
    
    if (!foundItem) {
      toast.error(t('common.error'))
      router.push(GearRoutePath.PublicContainerDetailById(containerId))
      return
    }
    
    item.value = foundItem
  } catch (error) {
    console.error('Failed to load public item:', error)
    toast.error(t('common.error'))
    router.push(GearRoutePath.PublicContainers)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadItem()
})

const handleBack = () => {
  router.push(GearRoutePath.PublicContainerDetailById(containerId))
}

const formattedWeight = computed<string>(() => {
  if (!item.value) return '-'
  return formatWeightWithPreferredUnit(
    item.value.weight * item.value.quantity,
    item.value.weightUnit ?? 'g',
    settings.value.preferredWeightUnit
  )
})

const formattedPrice = computed<string>(() => {
  if (!item.value?.price) return '-'
  return formatCurrency(item.value.price, getCurrency(item.value.currency, defaultCurrency.value))
})

// Check if there are any details to display
const hasDetails = computed<boolean>(() => {
  if (!item.value) return false
  return !!(
    item.value.brand ||
    item.value.color ||
    item.value.expirationDate ||
    item.value.url ||
    item.value.notes
  )
})
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="isLoading" class="space-y-6">
      <div class="h-12 bg-muted rounded animate-pulse" />
      <div class="h-64 bg-muted rounded animate-pulse" />
    </div>

    <div v-else-if="item" class="space-y-6 w-full max-w-full overflow-hidden">
      <!-- Header -->
      <div class="space-y-4">
        <Button variant="ghost" size="sm" @click="handleBack">
          <ArrowLeft class="size-4" />
          {{ t('common.back') }}
        </Button>

        <div>
          <h1 class="text-2xl sm:text-3xl font-bold mb-2 wrap-break-word" :class="{ 'text-destructive': isExpired(item), 'text-yellow-600': isExpiringSoon(item) }">
            {{ item.name }}
          </h1>
          <div class="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" class="flex items-center gap-2">
              <CategoryIcon :category="item.category" :size="14" />
              {{ getCategoryLabel(item.category) }}
            </Badge>
            <Badge :variant="getPriorityVariant(item.priority)">
              {{ t(`gear.item.priorities.${item.priority}`) }}
            </Badge>
            <Badge :variant="getStatusVariant(item.status)">
              {{ t(`gear.item.statuses.${item.status}`) }}
            </Badge>
            <Badge v-if="isExpired(item)" variant="destructive" class="text-xs">
              {{ t('gear.item.expiration.expired') }}
            </Badge>
            <Badge v-if="isExpiringSoon(item)" variant="outline" class="text-xs text-yellow-600 border-yellow-600">
              {{ t('gear.item.expiration.expiringSoon') }}
            </Badge>
            <Badge v-if="item.wearable" variant="outline" class="text-xs">
              {{ t('gear.item.wearable') }}
            </Badge>
            <Badge v-if="item.consumable" variant="outline" class="text-xs">
              {{ t('gear.item.consumable') }}
            </Badge>
          </div>
        </div>
      </div>

      <!-- Main Info -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-card rounded-lg border p-4">
          <div class="text-sm text-muted-foreground mb-1">
            {{ t('gear.item.quantity') }}
          </div>
          <div class="text-2xl font-bold">
            {{ item.quantity }}
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
        <div v-if="item.price != null" class="bg-card rounded-lg border p-4">
          <div class="text-sm text-muted-foreground mb-1">
            {{ t('gear.item.price') }}
          </div>
          <div class="text-2xl font-bold">
            {{ formattedPrice }}
          </div>
        </div>
        <div v-if="item.quality" class="bg-card rounded-lg border p-4">
          <div class="text-sm text-muted-foreground mb-1">
            {{ t('gear.item.quality') }}
          </div>
          <div class="text-2xl font-bold">
            {{ t(`gear.item.qualities.${item.quality}`) }}
          </div>
        </div>
      </div>

      <!-- Details -->
      <div class="bg-card rounded-lg border p-6 space-y-4">
        <h2 class="text-lg font-semibold">
          {{ t('gear.item.details') }}
        </h2>

        <template v-if="hasDetails">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div v-if="item.brand">
              <div class="text-sm text-muted-foreground mb-1">
                {{ t('gear.item.brand') }}
              </div>
              <div class="font-medium">
                {{ item.brand }}
              </div>
            </div>
            <div v-if="item.color">
              <div class="text-sm text-muted-foreground mb-1">
                {{ t('gear.item.color') }}
              </div>
              <div class="flex items-center gap-2">
                <div
                  class="size-4 rounded-full shrink-0 border border-border"
                  :style="{
                    backgroundColor: getColorHex(item.color) ?? DEFAULT_COLOR,
                  }"
                />
                <span class="font-medium">{{ item.color }}</span>
              </div>
            </div>
            <div v-if="item.expirationDate">
              <div class="text-sm text-muted-foreground mb-1">
                {{ t('gear.item.expirationDate') }}
              </div>
              <div class="font-medium" :class="{ 'text-destructive': isExpired(item), 'text-yellow-600': isExpiringSoon(item) }">
                {{ new Date(item.expirationDate).toLocaleDateString() }}
              </div>
            </div>
            <div v-if="item.url">
              <div class="text-sm text-muted-foreground mb-1">
                {{ t('gear.item.url') }}
              </div>
              <div>
                <a
                  :href="item.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-primary hover:underline font-medium"
                >
                  {{ t('gear.item.openLink') }}
                </a>
              </div>
            </div>
          </div>

          <div v-if="item.notes" class="pt-4 border-t">
            <div class="text-sm text-muted-foreground mb-2">
              {{ t('gear.item.notes') }}
            </div>
            <div class="text-sm whitespace-pre-wrap">
              {{ item.notes }}
            </div>
          </div>
        </template>

        <template v-else>
          <div class="text-center py-8 text-muted-foreground">
            <p class="text-sm">
              {{ t('gear.item.noDetails') }}
            </p>
          </div>
        </template>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

