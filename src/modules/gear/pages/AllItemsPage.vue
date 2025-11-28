<script setup lang="ts">
import { Box, Package, RefreshCcwIcon } from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'
import DataTable from '@/components/data-table/DataTable.vue'
import AllItemsFilters from '@/components/layout/AllItemsFilters.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'
import TableEmptyDecorated from '@/components/ui/table/TableEmptyDecorated.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { ALL_ITEMS_PAGE_FILTERS_KEY, ALL_ITEMS_TABLE_COLUMN_VISIBILITY_KEY, config } from '@/shared/config/config'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import CategoryIcon from '../components/CategoryIcon.vue'
import ItemPriorityBadge from '../components/ItemPriorityBadge.vue'
import ItemsTableImageCell from '../components/items-table/ItemsTableImageCell.vue'
import ItemStatusBadge from '../components/ItemStatusBadge.vue'
import { useCategoryLabel } from '../composables/useCategoryLabel'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { formatItemWeight } from '../composables/useFormattedItemWeight'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { gearContainerService } from '../services/gearContainerService'
import { createAllItemsColumns } from '../utils/allItemsColumns'
import { COLOR_DOT_CLASSES, COLOR_TEXT_CLASSES } from '../utils/containerColors'
import { getAllItems } from '../utils/getAllItems'
import { createNavigationQuery } from '../utils/navigationParams'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'

const router = useRouter()
const { t } = useI18n()
const { containers } = useGear()
const { getCategoryLabel } = useCategoryLabel()
const { settings: gearSettings } = useGearSettings()
const { getContainerTypeLabel } = useContainerTypeLabel()
const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

// Loading state for refresh
const loading = ref(false)

// Filter type: 'all' | 'containers' | 'items'
const filterType = ref<'all' | 'containers' | 'items'>('all')

// Global filter (search) for DataTable
const globalFilter = ref('')

// Helper to load filters from localStorage
interface FiltersState {
  globalFilter: string
  filterType: 'all' | 'containers' | 'items'
}

function loadFiltersFromStorage(): FiltersState | null {
  const stored = localStorage.getItem(ALL_ITEMS_PAGE_FILTERS_KEY)
  if (stored) {
    try {
      return JSON.parse(stored) as FiltersState
    } catch (error) {
      console.error('Error loading filters from storage:', error)
    }
  }
  return null
}

// Helper to save filters to localStorage
function saveFiltersToStorage(): void {
  try {
    const filters: FiltersState = {
      globalFilter: globalFilter.value,
      filterType: filterType.value,
    }
    localStorage.setItem(ALL_ITEMS_PAGE_FILTERS_KEY, JSON.stringify(filters))
  } catch (error) {
    console.error('Error saving filters to storage:', error)
  }
}

// Load filters from storage on mount
onMounted(() => {
  const savedFilters = loadFiltersFromStorage()
  if (savedFilters) {
    globalFilter.value = savedFilters.globalFilter
    filterType.value = savedFilters.filterType
  }
})

// Watch filters and save to localStorage
watch([globalFilter, filterType], () => {
  saveFiltersToStorage()
}, { deep: true })

// Get all items from all containers (includes containers as items)
const allItemsRaw = computed<IItemWithContainer[]>(() => {
  return getAllItems(containers.value)
})

// Refresh items from API/localStorage
async function refreshItems() {
  try {
    loading.value = true
    await gearContainerService().getContainers()
    // Store will automatically update containers.value, which triggers allItemsRaw recomputation
  } catch (error) {
    console.error('Failed to refresh items:', error)
  } finally {
    loading.value = false
  }
}

// Filter items based on filterType
const allItems = computed<IItemWithContainer[]>(() => {
  if (filterType.value === 'all') {
    return allItemsRaw.value
  } else if (filterType.value === 'containers') {
    return allItemsRaw.value.filter(item => item.isContainer === true)
  } else {
    return allItemsRaw.value.filter(item => item.isContainer !== true)
  }
})

// Column visibility
function loadColumnVisibility(): Record<string, boolean> {
  try {
    const stored = localStorage.getItem(ALL_ITEMS_TABLE_COLUMN_VISIBILITY_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      if (typeof parsed === 'object' && parsed !== null) {
        return parsed
      }
    }
  } catch (error) {
    console.error('Error loading column visibility from storage:', error)
  }
  return {
    image: false,
    brand: false,
    color: false,
    wearable: false,
    consumable: false,
  }
}

const columnVisibility = ref<Record<string, boolean>>(loadColumnVisibility())

// Save column visibility to localStorage when it changes
watch(
  columnVisibility,
  (newValue) => {
    try {
      localStorage.setItem(ALL_ITEMS_TABLE_COLUMN_VISIBILITY_KEY, JSON.stringify(newValue))
    } catch (error) {
      console.error('Error saving column visibility to storage:', error)
    }
  },
  { deep: true },
)

// Columns
const columns = computed(() => createAllItemsColumns(t))

// Global filter function
const globalFilterFn = (row: IItemWithContainer, filterValue: string) => {
  const query = filterValue.toLowerCase()
  return (
    row.name.toLowerCase().includes(query) ||
    row.containerName.toLowerCase().includes(query) ||
    getCategoryLabel(row.category).toLowerCase().includes(query) ||
    t(`gear.item.statuses.${row.status}`).toLowerCase().includes(query) ||
    (row.brand?.toLowerCase().includes(query) ?? false) ||
    (row.color?.toLowerCase().includes(query) ?? false)
  )
}

// Navigate to container
function navigateToContainer(containerId: string) {
  router.push(GearRoutePath.ContainerDetailById(containerId))
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight flex items-center gap-3">
            <Package class="size-8 text-primary" />
            {{ t('gear.allItems.title', 'All Items') }}
          </h1>
          <p class="text-muted-foreground mt-2">
            {{ t('gear.allItems.subtitle', 'View and manage all items from all containers') }}
          </p>
        </div>
        <div class="flex flex-row items-center justify-end gap-2">
          <Button
            variant="ghost"
            size="icon"
            @click="refreshItems"
          >
            <RefreshCcwIcon class="size-4" :class="{ 'animate-spin': loading }" />
          </Button>
        </div>
      </div>

      <!-- Table -->
      <DataTable
        v-model:column-visibility="columnVisibility"
        v-model:global-filter="globalFilter"
        :columns="columns"
        :data="allItems"
        :search-placeholder="t('gear.filters.search')"
        :global-filter-fn="globalFilterFn"
        :enable-sorting="true"
        :enable-filtering="true"
        :enable-pagination="true"
        :enable-column-visibility="true"
        :initial-page-size="20"
      >
        <template #toolbar-filters>
          <AllItemsFilters v-model:filter-type="filterType" />
        </template>

        <template #image="{ row }">
          <ItemsTableImageCell
            :item-id="row.original.id"
            :container-id="row.original.containerId"
            :primary-image-url="row.original.primaryImageUrl"
          />
        </template>

        <template #category="{ row }">
          <div class="flex items-center gap-2">
            <template v-if="row.original.isContainer">
              <Box :size="16" class="text-muted-foreground shrink-0" :class="COLOR_TEXT_CLASSES[row.original.containerColor]" />
              <span>{{ getContainerTypeLabel(row.original.containerType ?? 'other') }}</span>
            </template>
            <template v-else>
              <CategoryIcon :category="row.original.category" :size="16" class="text-muted-foreground" />
              <span>{{ getCategoryLabel(row.original.category) }}</span>
            </template>
          </div>
        </template>

        <template #name="{ row }">
          <div class="flex items-center gap-2">
            <RouterLink
              :to="row.original.isContainer ? GearRoutePath.ContainerDetailById(row.original.id) : { path: GearRoutePath.ItemDetailById(row.original.containerId, row.original.id), query: createNavigationQuery(undefined, 'all-items') }"
              class="font-medium hover:text-primary hover:underline transition-colors"
            >
              {{ row.original.name }}
            </RouterLink>
            <Badge v-if="row.original.isContainer" variant="outline" class="text-xs">
              {{ t('gear.item.container', 'Container') }}
            </Badge>
          </div>
        </template>

        <template #container="{ row }">
          <button
            type="button"
            class="flex items-center gap-2 cursor-pointer hover:underline font-medium"
            :class="COLOR_TEXT_CLASSES[row.original.containerColor]"
            @click="navigateToContainer(row.original.containerId)"
          >
            <div
              class="size-2 rounded-full shrink-0"
              :class="COLOR_DOT_CLASSES[row.original.containerColor]"
            />
            {{ row.original.containerName }}
          </button>
        </template>

        <template #quantity="{ row }">
          {{ row.original.quantity }}
        </template>

        <template #weight="{ row }">
          {{ formatItemWeight(row.original, true, settings.preferredWeightUnit ?? config.defaults.preferredWeightUnit) }}
        </template>

        <template #status="{ row }">
          <ItemStatusBadge :status="row.original.status" />
        </template>

        <template #priority="{ row }">
          <ItemPriorityBadge :priority="row.original.priority" />
        </template>

        <template #brand="{ row }">
          {{ row.original.brand ?? '-' }}
        </template>

        <template #color="{ row }">
          <div v-if="row.original.color" class="flex items-center gap-2">
            <div
              class="size-3 rounded-full shrink-0 border border-border"
              :style="{
                backgroundColor: getColorHex(row.original.color) ?? DEFAULT_COLOR,
              }"
            />
            <span>{{ row.original.color }}</span>
          </div>
          <span v-else>-</span>
        </template>

        <template #wearable="{ row }">
          <Badge v-if="row.original.wearable" variant="outline" class="text-xs">
            {{ t('gear.item.wearable') }}
          </Badge>
          <span v-else>-</span>
        </template>

        <template #consumable="{ row }">
          <Badge v-if="row.original.consumable" variant="outline" class="text-xs">
            {{ t('gear.item.consumable') }}
          </Badge>
          <span v-else>-</span>
        </template>

        <template #empty>
          <TableEmptyDecorated
            :colspan="columns.length"
            :title="t('gear.allItems.empty', 'No items found')"
            :description="t('gear.allItems.emptyDescription', 'Create containers and add items to see them here.')"
          />
        </template>
      </DataTable>
    </div>
  </AuthenticatedLayout>
</template>

