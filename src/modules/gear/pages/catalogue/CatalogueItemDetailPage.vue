<script setup lang="ts">
import { ArrowLeft, Package } from 'lucide-vue-next'
import { computed, ref, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Badge } from '@/components/ui/badge'
import Button from '@/components/ui/button/Button.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import AddCatalogueItemToContainerDialog from '@/modules/gear/components/catalogue/AddCatalogueItemToContainerDialog.vue'
import ColorDot from '@/modules/gear/components/ColorDot.vue'
import MarkdownRenderer from '@/modules/gear/components/MarkdownRenderer.vue'
import { useCatalogue } from '@/modules/gear/composables/catalogue/useCatalogue'
import { useCategoryLabel } from '@/modules/gear/composables/useCategoryLabel'
import { usePriceTierLabel } from '@/modules/gear/composables/usePriceTierLabel'
import { GearRoutePath } from '@/modules/gear/routes'
import { DEFAULT_COLOR, getColorHex } from '@/modules/gear/utils/suggestedValues'
import { usePageTitle } from '@/shared/composables/usePageTitle'
import type { TContainerColor } from '@/modules/gear/types/gear.types'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { setTitle } = usePageTitle()
const { getCategoryLabel } = useCategoryLabel()
const { getPriceTierLabel } = usePriceTierLabel()

const catalogueItemId = route.params.id as string
const { getCatalogueItem } = useCatalogue()

const {
  data: item,
  isLoading,
  error,
} = getCatalogueItem(catalogueItemId)

const showAddDialog = ref(false)

// Set dynamic page title
watchEffect(() => {
  if (item.value?.name) {
    setTitle('gear.catalogue.itemDetail', { name: item.value.name })
  }
})

// Handle error
watchEffect(() => {
  if (error.value) {
    toast.error(t('common.error'))
    router.push(GearRoutePath.CatalogueBrowser)
  }
})

// Computed properties
const categoryLabel = computed(() => {
  if (!item.value) return ''
  return getCategoryLabel(item.value.category)
})

const priceTierLabel = computed(() => {
  if (!item.value?.priceTier) return null
  return getPriceTierLabel(item.value.priceTier)
})

const qualityLabel = computed(() => {
  if (!item.value?.quality) return null
  return t(`gear.item.qualities.${item.value.quality}`)
})

// Check if there are any details to display
const hasDetails = computed<boolean>(() => {
  if (!item.value) return false
  return !!(
    item.value.brand
    || item.value.model
    || item.value.color
    || item.value.url
    || item.value.description
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

const goBack = () => {
  router.push(GearRoutePath.CatalogueBrowser)
}

const handleAddToContainer = () => {
  showAddDialog.value = true
}
</script>

<template>
  <AuthenticatedLayout>
    <div v-if="isLoading" class="space-y-6">
      <div class="h-12 animate-pulse rounded bg-muted" />
      <div class="h-64 animate-pulse rounded bg-muted" />
    </div>

    <div v-else-if="item" class="w-full max-w-full space-y-6">
      <!-- Header -->
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-3">
          <Button variant="ghost" size="icon" @click="goBack">
            <ArrowLeft class="size-5" />
          </Button>
          <div class="flex items-center gap-2">
            <ColorDot :color="(item.color as TContainerColor) ?? undefined" />
            <Package class="size-6" />
            <h1 class="text-2xl font-bold sm:text-3xl">
              {{ item.name }}
            </h1>
          </div>
        </div>
        <Button @click="handleAddToContainer">
          {{ t('gear.catalogue.addToContainer') }}
        </Button>
      </div>

      <!-- Primary Image -->
      <div v-if="item.primaryImageUrl" class="flex items-center justify-center overflow-hidden rounded-lg border bg-muted">
        <img
          :src="item.primaryImageUrl"
          :alt="item.name"
          class="max-h-96 w-full object-contain"
        />
      </div>

      <!-- Badges -->
      <div class="flex flex-wrap gap-2">
        <Badge variant="secondary">
          {{ categoryLabel }}
        </Badge>
        <Badge v-if="item.brand" variant="outline">
          {{ t('gear.catalogue.brand') }}: {{ item.brand }}
        </Badge>
        <Badge v-if="priceTierLabel" variant="outline">
          {{ t('gear.catalogue.priceTier') }}: {{ priceTierLabel }}
        </Badge>
        <Badge v-if="qualityLabel" variant="outline">
          {{ t('gear.catalogue.quality') }}: {{ qualityLabel }}
        </Badge>
        <Badge v-if="!item.isActive" variant="destructive">
          {{ t('gear.catalogue.isActive') }}: {{ item.isActive }}
        </Badge>
      </div>

      <!-- Main Info -->
      <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div class="rounded-lg border bg-card p-4">
          <div class="mb-1 text-sm text-muted-foreground">
            {{ t('gear.item.weight') }}
          </div>
          <div class="text-2xl font-bold">
            {{ item.weight }}{{ item.weightUnit }}
          </div>
        </div>
        <div v-if="item.model" class="rounded-lg border bg-card p-4">
          <div class="mb-1 text-sm text-muted-foreground">
            Model
          </div>
          <div class="text-2xl font-bold">
            {{ item.model }}
          </div>
        </div>
        <div class="rounded-lg border bg-card p-4">
          <div class="mb-1 text-sm text-muted-foreground">
            {{ t('gear.catalogue.version') }}
          </div>
          <div class="text-2xl font-bold">
            v{{ item.version }}
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
            <div v-if="item.model">
              <div class="mb-1 text-sm text-muted-foreground">
                Model
              </div>
              <div class="font-medium">
                {{ item.model }}
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
            <div v-if="item.createdBy">
              <div class="mb-1 text-sm text-muted-foreground">
                {{ t('gear.catalogue.createdBy') }}
              </div>
              <div class="font-medium">
                {{ item.createdBy }}
              </div>
            </div>
          </div>

          <div v-if="item.description" class="border-t pt-4">
            <div class="mb-2 text-sm text-muted-foreground">
              {{ t('gear.container.description') }}
            </div>
            <MarkdownRenderer :content="item.description" class="text-sm" />
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

      <!-- Metadata -->
      <div class="rounded-lg border bg-card p-6">
        <h2 class="mb-4 text-lg font-semibold">
          Metadata
        </h2>
        <div class="grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
          <div>
            <span class="text-muted-foreground">Created:</span>
            <span class="ml-2 font-medium">{{ new Date(item.createdAt).toLocaleString() }}</span>
          </div>
          <div>
            <span class="text-muted-foreground">Updated:</span>
            <span class="ml-2 font-medium">{{ new Date(item.updatedAt).toLocaleString() }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Add to Container Dialog -->
    <AddCatalogueItemToContainerDialog
      v-if="item"
      :open="showAddDialog"
      :catalogue-item="item"
      @update:open="showAddDialog = $event"
    />
  </AuthenticatedLayout>
</template>
