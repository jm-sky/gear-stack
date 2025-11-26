<script setup lang="ts">
import { Box, Package } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'
import DataTable from '@/components/data-table/DataTable.vue'
import AllItemsFilters from '@/components/layout/AllItemsFilters.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import TableEmptyDecorated from '@/components/ui/table/TableEmptyDecorated.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { ALL_ITEMS_TABLE_COLUMN_VISIBILITY_KEY } from '@/shared/config/config'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import CategoryIcon from '../components/CategoryIcon.vue'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { createAllItemsColumns } from '../utils/allItemsColumns'
import { getPriorityVariant, getStatusVariant } from '../utils/badgeVariants'
import { COLOR_DOT_CLASSES, COLOR_TEXT_CLASSES } from '../utils/containerColors'
import { formatWeightWithPreferredUnit } from '../utils/formatWeight'
import { getAllItems } from '../utils/getAllItems'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'

const router = useRouter()
const { t } = useI18n()
const { containers } = useGear()
const { customCategories } = useGearSettings()
const { settings: gearSettings } = useGearSettings()
const { getContainerTypeLabel } = useContainerTypeLabel()
const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

// Filter type: 'all' | 'containers' | 'items'
const filterType = ref<'all' | 'containers' | 'items'>('all')

// Get all items from all containers (includes containers as items)
const allItemsRaw = computed<IItemWithContainer[]>(() => {
  return getAllItems(containers.value)
})

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

// Helper to get category label
const getCategoryLabel = (categoryValue: string): string => {
  const customCategory = customCategories.value.find(c => c.value === categoryValue)
  if (customCategory) {
    return customCategory.value
  }
  return t(`gear.item.categories.${categoryValue}`)
}

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
    <div class="space-y-6 w-full max-w-full overflow-hidden">
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
      </div>

      <!-- Table -->
      <DataTable
        v-model:column-visibility="columnVisibility"
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
              :to="row.original.isContainer ? GearRoutePath.ContainerDetailById(row.original.id) : { path: GearRoutePath.ItemDetailById(row.original.containerId, row.original.id), query: { from: 'all-items' } }"
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
          {{ formatWeightWithPreferredUnit(row.original.weight * row.original.quantity, row.original.weightUnit, settings.preferredWeightUnit ?? 'g') }}
        </template>

        <template #status="{ row }">
          <Badge :variant="getStatusVariant(row.original.status)">
            {{ t(`gear.item.statuses.${row.original.status}`) }}
          </Badge>
        </template>

        <template #priority="{ row }">
          <Badge :variant="getPriorityVariant(row.original.priority)">
            {{ t(`gear.item.priorities.${row.original.priority}`) }}
          </Badge>
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

