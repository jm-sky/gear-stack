<script setup lang="ts">
import { ArrowLeft, Pencil } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { useBackend } from '@/shared/composables/useBackend'
import { config } from '@/shared/config/config'
import type { IGearContainer, IGearItem } from '../types/gear.types'
import CategoryIcon from '../components/CategoryIcon.vue'
import ItemImageGallery from '../components/ItemImageGallery.vue'
import SearchImagesButton from '../components/SearchImagesButton.vue'
import { useFormattedItemPrice } from '../composables/useFormattedItemPrice'
import { useFormattedItemWeight } from '../composables/useFormattedItemWeight'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { gearContainerService } from '../services/gearContainerService'
import { gearItemService } from '../services/gearItemService'
import { useGearStore } from '../store/useGearStore'
import { getPriorityVariant, getStatusVariant } from '../utils/badgeVariants'
import { EXPIRATION_WARNING_DAYS } from '../utils/constants'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const store = useGearStore()
const { shouldUseAPI } = useBackend()
const { customCategories } = useGearSettings()
const { user, isAuthenticated } = useAuth()

const containerId = route.params.containerId as string
const itemId = route.params.itemId as string
const item = ref<IGearItem | null>(null)
const container = ref<IGearContainer | null>(null)
const isLoading = ref(true)

// Check if user is admin
const isAdmin = computed(() => {
  return user.value?.isAdmin ?? false
})

// Check if user is owner of the container
const isOwner = computed(() => {
  if (!isAuthenticated.value || !user.value || !container.value) {
    return false
  }
  // For public containers, check authorId
  if (container.value.authorId) {
    return container.value.authorId === user.value.id
  }
  // For private containers (no authorId), if we can access the container,
  // it means we own it (backend handles authorization)
  // For localStorage, all containers are considered owned by current user
  return true
})

// Check if user can manage images (admin AND owner)
const canManageImages = computed(() => {
  return isAdmin.value && isOwner.value
})

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
  if (!item.expirationDate)
    return false
  return new Date(item.expirationDate) < new Date()
}

// Helper to check if item is expiring soon
function isExpiringSoon(item: IGearItem, days: number = EXPIRATION_WARNING_DAYS): boolean {
  if (!item.expirationDate)
    return false
  const expirationDate = new Date(item.expirationDate)
  const now = new Date()
  const MILLISECONDS_PER_DAY = 1000 * 60 * 60 * 24
  const daysUntilExpiration = Math.ceil((expirationDate.getTime() - now.getTime()) / MILLISECONDS_PER_DAY)
  return daysUntilExpiration > 0 && daysUntilExpiration <= days
}

const loadItem = async () => {
  try {
    const service = gearItemService()

    if (shouldUseAPI.value && 'getItem' in service) {
      // Load from API
      item.value = await service.getItem(itemId)
      // Load container to check ownership
      const containerService = gearContainerService()
      const containerData = await store.getContainerById(containerId) || await containerService.getContainer(containerId)
      container.value = containerData || null
    } else {
      // Load from localStorage
      const containerData = store.getContainerById(containerId)
      container.value = containerData || null
      const foundItem = containerData?.items.find(i => i.id === itemId)

      if (!foundItem) {
        toast.error(t('common.error'))
        router.push(GearRoutePath.ContainerDetailById(containerId))
        return
      }

      item.value = foundItem
    }
  } catch (error) {
    console.error('Failed to load item:', error)
    toast.error(t('common.error'))
    router.push(GearRoutePath.ContainerDetailById(containerId))
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadItem()
})

// Determine back navigation target based on query parameter
const backTo = computed<string>(() => {
  if ((route.query.from as string | undefined) === 'all-items') {
    return GearRoutePath.AllItems
  }
  return GearRoutePath.ContainerDetailById(containerId)
})

const handleEdit = () => {
  const from = route.query.from as string | undefined
  router.push({
    path: GearRoutePath.ItemEditById(containerId, itemId),
    query: {
      returnTo: 'detail',
      ...(from && { from }),
    },
  })
}

const { formattedWeight } = useFormattedItemWeight(item)
const { formattedPrice } = useFormattedItemPrice(item)

// Check if there are any details to display
const hasDetails = computed<boolean>(() => {
  if (!item.value) return false
  return !!(
    item.value.brand
    || item.value.color
    || item.value.expirationDate
    || item.value.url
    || item.value.notes
  )
})

// Extract domain from URL
const getUrlDomain = (url: string): string => {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

const urlDomain = computed<string>(() => {
  if (!item.value?.url) return ''
  return getUrlDomain(item.value.url)
})
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="isLoading" class="space-y-6">
      <div class="h-12 animate-pulse rounded bg-muted" />
      <div class="h-64 animate-pulse rounded bg-muted" />
    </div>

    <div v-else-if="item" class="w-full max-w-full space-y-6 overflow-hidden">
      <!-- Header -->
      <div class="space-y-4">
        <div class="flex items-center justify-between gap-4">
          <ButtonLink :to="backTo" variant="ghost" size="sm">
            <ArrowLeft class="size-4" />
            {{ t('common.back') }}
          </ButtonLink>

          <Button size="sm" @click="handleEdit">
            <Pencil class="size-4" />
            {{ t('common.edit') }}
          </Button>
        </div>

        <div class="flex flex-col gap-2">
          <h1 class="wrap-break-word mb-2 text-2xl font-bold sm:text-3xl" :class="{ 'text-destructive': isExpired(item), 'text-yellow-600': isExpiringSoon(item) }">
            {{ item.name }}
          </h1>
          <div class="flex flex-wrap items-center gap-2">
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
            <Badge v-if="isExpiringSoon(item)" variant="outline" class="text-xs border-yellow-600 text-yellow-600">
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
      <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div class="rounded-lg border bg-card p-4">
          <div class="mb-1 text-sm text-muted-foreground">
            {{ t('gear.item.quantity') }}
          </div>
          <div class="text-2xl font-bold">
            {{ item.quantity }}
          </div>
        </div>
        <div class="rounded-lg border bg-card p-4">
          <div class="mb-1 text-sm text-muted-foreground">
            {{ t('gear.container.totalWeight') }}
          </div>
          <div class="text-2xl font-bold">
            {{ formattedWeight }}
          </div>
        </div>
        <div v-if="item.price != null" class="rounded-lg border bg-card p-4">
          <div class="mb-1 text-sm text-muted-foreground">
            {{ t('gear.item.price') }}
          </div>
          <div class="text-2xl font-bold">
            {{ formattedPrice }}
          </div>
        </div>
        <div v-if="item.quality" class="rounded-lg border bg-card p-4">
          <div class="mb-1 text-sm text-muted-foreground">
            {{ t('gear.item.quality') }}
          </div>
          <div class="text-2xl font-bold">
            {{ t(`gear.item.qualities.${item.quality}`) }}
          </div>
        </div>
      </div>

      <!-- Details -->
      <div class="space-y-4 rounded-lg border bg-card p-6">
        <h2 class="text-lg font-semibold">
          {{ t('gear.item.details') }}
        </h2>

        <template v-if="hasDetails">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div v-if="item.brand">
              <div class="mb-1 text-sm text-muted-foreground">
                {{ t('gear.item.brand') }}
              </div>
              <div class="font-medium">
                {{ item.brand }}
              </div>
            </div>
            <div v-if="item.color">
              <div class="mb-1 text-sm text-muted-foreground">
                {{ t('gear.item.color') }}
              </div>
              <div class="flex items-center gap-2">
                <div
                  class="size-4 shrink-0 rounded-full border border-border"
                  :style="{
                    backgroundColor: getColorHex(item.color) ?? DEFAULT_COLOR,
                  }"
                />
                <span class="font-medium">{{ item.color }}</span>
              </div>
            </div>
            <div v-if="item.expirationDate">
              <div class="mb-1 text-sm text-muted-foreground">
                {{ t('gear.item.expirationDate') }}
              </div>
              <div class="font-medium" :class="{ 'text-destructive': isExpired(item), 'text-yellow-600': isExpiringSoon(item) }">
                {{ new Date(item.expirationDate).toLocaleDateString() }}
              </div>
            </div>
            <div v-if="item.url">
              <div class="mb-1 text-sm text-muted-foreground">
                {{ t('gear.item.url') }}
              </div>
              <div>
                <a
                  :href="item.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="font-medium text-primary hover:underline"
                >
                  <span class="sm:hidden">{{ t('gear.item.openLink') }}</span>
                  <span class="hidden sm:inline">{{ urlDomain }}</span>
                </a>
              </div>
            </div>
          </div>

          <div v-if="item.notes" class="border-t pt-4">
            <div class="mb-2 text-sm text-muted-foreground">
              {{ t('gear.item.notes') }}
            </div>
            <div class="whitespace-pre-wrap text-sm">
              {{ item.notes }}
            </div>
          </div>
        </template>

        <template v-else>
          <div class="py-8 text-center text-muted-foreground">
            <p class="text-sm">
              {{ t('gear.item.noDetails') }}
            </p>
          </div>
        </template>
      </div>

      <!-- Image Gallery -->
      <div class="rounded-lg border bg-card p-6">
        <ItemImageGallery
          :item-id="itemId"
          :editable="canManageImages"
        >
          <template #header-actions>
            <SearchImagesButton
              v-if="canManageImages && shouldUseAPI && config.features.imageSearch.enabled"
              :item-id="item.id"
              @reload="loadItem"
            />
          </template>
        </ItemImageGallery>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
