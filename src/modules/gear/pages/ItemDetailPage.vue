<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { useBackend } from '@/shared/composables/useBackend'
import { usePageTitle } from '@/shared/composables/usePageTitle'
import { config } from '@/shared/config/config'
import type { IGearContainer, IGearItem } from '../types/gear.types'
import ItemHeader from '../components/ItemHeader.vue'
import SearchImagesButton from '../components/SearchImagesButton.vue'

// Lazy load ItemImageGallery - not critical for initial render
const ItemImageGallery = defineAsyncComponent(() => import('../components/ItemImageGallery.vue'))
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import { useExpiration } from '../composables/useExpiration'
import { useFormattedItemPrice } from '../composables/useFormattedItemPrice'
import { useFormattedItemWeight } from '../composables/useFormattedItemWeight'
import { GearRoutePath } from '../routes'
import { gearContainerService } from '../services/gearContainerService'
import { gearItemService } from '../services/gearItemService'
import { useGearStore } from '../store/useGearStore'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const store = useGearStore()
const { shouldUseAPI } = useBackend()
const { user, isAuthenticated } = useAuth()
const { setTitle } = usePageTitle()

const containerId = route.params.containerId as string
const itemId = route.params.itemId as string
const item = ref<IGearItem | null>(null)
const container = ref<IGearContainer | null>(null)
const isLoading = ref(true)

// Set dynamic page title
watchEffect(() => {
  if (item.value?.name) {
    setTitle('gear.pages.itemDetail', { name: item.value.name })
  }
})

const { isExpired, isExpiringSoon } = useExpiration(item)

// Check if user is admin
const isAdmin = computed(() => user.value?.isAdmin ?? false)

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

// Callback to refresh item after catalogue operations
const handleItemUpdated = async () => {
  await loadItem()
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

    <div v-else-if="item" class="w-full max-w-full space-y-6">
      <!-- Header -->
      <ItemHeader
        :container-id
        :item-id
        :item
        @item-updated="handleItemUpdated"
      />

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
              <div class="font-medium" :class="{ 'text-destructive': isExpired, 'text-yellow-600': isExpiringSoon }">
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
            <MarkdownRenderer
              :content="item.notes"
              class="text-sm"
            />
          </div>
        </template>

        <template v-else>
          <div class="py-4 text-center text-muted-foreground">
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
