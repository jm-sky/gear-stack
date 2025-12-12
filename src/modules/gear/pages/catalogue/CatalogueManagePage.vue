<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import { BookIcon, Package, Plus } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import Button from '@/components/ui/button/Button.vue'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import CatalogueFilters from '@/modules/gear/components/catalogue/CatalogueFilters.vue'
import CatalogueItemCard from '@/modules/gear/components/catalogue/CatalogueItemCard.vue'
import { useCatalogue } from '@/modules/gear/composables/catalogue/useCatalogue'
import { GearRoutePath } from '@/modules/gear/routes'
import type { TCataloguePriceTier } from '@/modules/gear/types/catalogue.types'
import type { TGearItemCategory, TGearItemQuality } from '@/modules/gear/types/gear.types'

const { t } = useI18n()
const {
  catalogueItems,
  isLoadingItems,
  updateSearchParams,
  clearFilters,
  refetchItems,
} = useCatalogue({ enableItemsQuery: true })

const searchQueryRaw = ref('')
const searchQuery = refDebounced(searchQueryRaw, 300)

const selectedCategory = ref<TGearItemCategory | null>(null)

const brandFilterRaw = ref('')
const brandFilter = refDebounced(brandFilterRaw, 300)

const priceTierFilter = ref<TCataloguePriceTier | null>(null)
const qualityFilter = ref<TGearItemQuality | null>(null)

type TActiveFilter = 'all' | 'active' | 'inactive'
const activeFilter = ref<TActiveFilter>('all')

watch(
  [searchQuery, selectedCategory, brandFilter, priceTierFilter, qualityFilter, activeFilter],
  () => {
    updateSearchParams({
      query: searchQuery.value || null,
      category: selectedCategory.value,
      brand: brandFilter.value || null,
      priceTier: priceTierFilter.value,
      quality: qualityFilter.value,
      isActive: activeFilter.value === 'all' ? null : activeFilter.value === 'active',
      skip: 0,
    })
  },
  { immediate: true },
)

const handleClearFilters = () => {
  searchQueryRaw.value = ''
  selectedCategory.value = null
  brandFilterRaw.value = ''
  priceTierFilter.value = null
  qualityFilter.value = null
  activeFilter.value = 'all'
  clearFilters()
  updateSearchParams({ isActive: null })
}

const handleRefresh = () => {
  refetchItems()
}

const hasActiveFilters = computed(() => {
  return (
    searchQueryRaw.value !== ''
    || selectedCategory.value !== null
    || brandFilterRaw.value !== ''
    || priceTierFilter.value !== null
    || qualityFilter.value !== null
    || activeFilter.value !== 'all'
  )
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="w-full max-w-full space-y-6">
      <CommonPageHeader
        :icon="BookIcon"
        :label="t('gear.catalogue.title')"
        :description="t('gear.catalogue.subtitle')"
      >
        <template #top-actions>
          <RouterLink :to="GearRoutePath.CatalogueItemNew">
            <Button size="sm">
              <Plus class="size-4" />
              {{ t('gear.actions.add', 'Add') }}
            </Button>
          </RouterLink>
        </template>
      </CommonPageHeader>

      <div class="space-y-4">
        <CatalogueFilters
          v-model:search-query="searchQueryRaw"
          v-model:category="selectedCategory"
          v-model:brand="brandFilterRaw"
          v-model:price-tier="priceTierFilter"
          v-model:quality="qualityFilter"
          :loading="isLoadingItems"
          :has-active-filters
          @clear-filters="handleClearFilters"
          @refresh="handleRefresh"
        />

        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div class="space-y-1.5">
            <Label class="text-xs text-muted-foreground">
              {{ t('gear.catalogue.isActive') }}
            </Label>
            <Select v-model="activeFilter">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">
                  {{ t('gear.filters.all') }}
                </SelectItem>
                <SelectItem value="active">
                  {{ t('gear.catalogue.makeActive') }}
                </SelectItem>
                <SelectItem value="inactive">
                  {{ t('gear.catalogue.makeInactive') }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <div v-if="isLoadingItems" class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div v-for="i in 6" :key="i" class="h-64 animate-pulse rounded-lg bg-muted" />
      </div>

      <div v-else-if="catalogueItems.length > 0" class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <CatalogueItemCard v-for="item in catalogueItems" :key="item.id" :item />
      </div>

      <div v-else class="flex flex-col items-center justify-center py-12 text-center">
        <div class="mb-4 rounded-full bg-muted p-6">
          <Package class="size-12 text-muted-foreground" />
        </div>
        <h3 class="mb-2 text-lg font-semibold">
          {{ hasActiveFilters ? t('gear.catalogue.noResults') : t('gear.catalogue.empty') }}
        </h3>
        <p class="max-w-md text-muted-foreground">
          {{ hasActiveFilters ? t('gear.catalogue.noResultsDescription') : t('gear.catalogue.emptyDescription') }}
        </p>
      </div>
    </div>
  </AuthenticatedLayout>
</template>

