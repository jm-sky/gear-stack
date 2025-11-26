<script setup lang="ts">
import { Package } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import DataTable from '@/components/data-table/DataTable.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import TableEmptyDecorated from '@/components/ui/table/TableEmptyDecorated.vue'
import { ITEMS_TABLE_COLUMN_VISIBILITY_KEY } from '@/shared/config/config'
import type { IGearItem } from '../types/gear.types'
import { useCategoryLabel } from '../composables/useCategoryLabel'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { useGearStore } from '../store/useGearStore'
import { getPriorityVariant, getStatusVariant } from '../utils/badgeVariants'
import { EXPIRATION_WARNING_DAYS } from '../utils/constants'
import { calculateTotalWeightSync } from '../utils/containerCalculations'
import { formatCurrency, getCurrency } from '../utils/currencyFormatter'
import { createItemsColumns } from '../utils/itemsColumns'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'
import ItemsTableCategoryCell from './items-table/ItemsTableCategoryCell.vue'
import ItemsTableImageCell from './items-table/ItemsTableImageCell.vue'
import ItemsTableNameCell from './items-table/ItemsTableNameCell.vue'
import ItemsTableWeightCell from './items-table/ItemsTableWeightCell.vue'
import ItemsTableNestedContainerRow from './ItemsTableNestedContainerRow.vue'
import ItemsTableRowActions from './ItemsTableRowActions.vue'
import type { SortingState } from '@tanstack/vue-table'

const props = withDefaults(
  defineProps<{
    items: IGearItem[]
    loading?: boolean
    publicMode?: boolean
    containerId?: string
  }>(),
  {
    loading: false,
    publicMode: false,
    containerId: undefined,
  },
)

const emit = defineEmits<{
  edit: [item: IGearItem]
  delete: [item: IGearItem]
  statusChange: [item: IGearItem, status: IGearItem['status']]
  recognizeParameters: [item: IGearItem]
  reorder: [items: IGearItem[]]
  sortingChange: [items: IGearItem[]]
}>()

const { t } = useI18n()
const router = useRouter()
const store = useGearStore()

const { settings: gearSettings, defaultCurrency } = useGearSettings()
const { getCategoryLabel } = useCategoryLabel()

const settings = computed(() => ({ preferredWeightUnit: gearSettings.value.preferredWeightUnit }))

// Expanded rows state (which containers are expanded)
const expandedRows = ref<Set<string>>(new Set())

// Load column visibility from localStorage
function loadColumnVisibility(): Record<string, boolean> {
  try {
    const stored = localStorage.getItem(ITEMS_TABLE_COLUMN_VISIBILITY_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      // Validate that it's an object with boolean values
      if (typeof parsed === 'object' && parsed !== null) {
        return parsed
      }
    }
  } catch (error) {
    console.error('Error loading column visibility from storage:', error)
  }
  // Default: hide brand, color, wearable, and consumable by default
  return {
    image: false,
    brand: false,
    color: false,
    wearable: false,
    consumable: false,
    order: false,
    price: false,
  }
}

// Column visibility state - load from localStorage or use defaults
const columnVisibility = ref<Record<string, boolean>>(loadColumnVisibility())

// Save column visibility to localStorage when it changes
watch(
  columnVisibility,
  (newValue) => {
    try {
      localStorage.setItem(ITEMS_TABLE_COLUMN_VISIBILITY_KEY, JSON.stringify(newValue))
    } catch (error) {
      console.error('Error saving column visibility to storage:', error)
    }
  },
  { deep: true },
)

// Columns
const columns = computed<ReturnType<typeof createItemsColumns>>(() => {
  return createItemsColumns(t)
})

// Custom filter function for searching
const globalFilterFn = (row: IGearItem, filterValue: string) => {
  const query = filterValue.toLowerCase()
  return (
    row.name.toLowerCase().includes(query) ||
    row.notes?.toLowerCase().includes(query) ||
    getCategoryLabel(row.category).toLowerCase().includes(query) ||
    t(`gear.item.statuses.${row.status}`).toLowerCase().includes(query)
  )
}

// Helper do sprawdzania czy przedmiot jest przeterminowany
function isExpired(item: IGearItem): boolean {
  if (!item.expirationDate) return false
  return new Date(item.expirationDate) < new Date()
}

// Helper do sprawdzania czy przedmiot wygasa wkrótce
function isExpiringSoon(item: IGearItem, days: number = EXPIRATION_WARNING_DAYS): boolean {
  if (!item.expirationDate) return false
  const expirationDate = new Date(item.expirationDate)
  const now = new Date()
  const MILLISECONDS_PER_DAY = 1000 * 60 * 60 * 24
  const daysUntilExpiration = Math.ceil((expirationDate.getTime() - now.getTime()) / MILLISECONDS_PER_DAY)
  return daysUntilExpiration > 0 && daysUntilExpiration <= days
}

// Helper to check if item is a nested container
function isNestedContainer(item: IGearItem): boolean {
  return !!item.containerId
}

// Navigate to nested container
function navigateToNestedContainer(item: IGearItem) {
  if (item.containerId) {
    if (props.publicMode) {
      router.push(GearRoutePath.PublicContainerDetailById(item.containerId))
    } else {
      router.push(GearRoutePath.ContainerDetailById(item.containerId))
    }
  }
}

// Navigate to item detail page
function navigateToItem(item: IGearItem) {
  if (props.publicMode && props.containerId) {
    router.push(GearRoutePath.PublicItemDetailById(props.containerId, item.id))
  } else if (props.containerId) {
    router.push({
      path: GearRoutePath.ItemDetailById(props.containerId, item.id),
      query: { from: 'container' },
    })
  } else {
    // Fallback: emit edit event if containerId is not available
    emit('edit', item)
  }
}

// Toggle row expansion
function toggleRowExpansion(itemId: string) {
  if (expandedRows.value.has(itemId)) {
    expandedRows.value.delete(itemId)
  } else {
    expandedRows.value.add(itemId)
  }
}

// Check if row is expanded
function isRowExpanded(itemId: string): boolean {
  return expandedRows.value.has(itemId)
}

// Get nested container items
function getNestedContainerItems(item: IGearItem): IGearItem[] {
  if (!item.containerId) return []
  const container = store.getContainerById(item.containerId)
  return container?.items ?? []
}

// Get nested container
function getNestedContainer(item: IGearItem) {
  if (!item.containerId) return undefined
  return store.getContainerById(item.containerId)
}

// Calculate total weight for nested container (sync helper)
function calculateTotalWeight(containerId: string): number {
  const container = store.getContainerById(containerId)
  if (!container) return 0
  return calculateTotalWeightSync(container, store.getAllContainers)
}

// Sorting state from DataTable
const tableSorting = ref<SortingState>([])

// Sort items by order (default sorting) or by table sorting
const sortedItems = computed<IGearItem[]>(() => {
  const items = [...props.items]

  // If table has active sorting, apply it
  if (tableSorting.value.length > 0) {
    const sortConfig = tableSorting.value[0]
    if (!sortConfig) return items

    const columnId = sortConfig.id
    const direction = sortConfig.desc ? -1 : 1

    return items.sort((a, b) => {
      const aValue: unknown = a[columnId as keyof IGearItem]
      const bValue: unknown = b[columnId as keyof IGearItem]

      // Handle different data types
      const aVal = aValue === null || aValue === undefined ? '' : aValue
      const bVal = bValue === null || bValue === undefined ? '' : bValue

      // String comparison
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return aVal.localeCompare(bVal) * direction
      }

      // Number comparison
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return (aVal - bVal) * direction
      }

      // Fallback
      return String(aVal).localeCompare(String(bVal)) * direction
    })
  }

  // Default: Sort by order (null/undefined items go to end)
  return items.sort((a, b) => {
    const orderA = a.order ?? Number.MAX_SAFE_INTEGER
    const orderB = b.order ?? Number.MAX_SAFE_INTEGER
    return orderA - orderB
  })
})

// Track previous sorting to detect changes
const previousSorting = ref<SortingState>([])

// Watch for sorting changes and update local order
watch(
  tableSorting,
  (newSorting) => {
    // Check if sorting actually changed
    const sortingChanged = JSON.stringify(newSorting) !== JSON.stringify(previousSorting.value)
    previousSorting.value = [...newSorting]

    if (!sortingChanged) return

    // If sorting was cleared (back to default), emit empty array to clear pending changes
    if (newSorting.length === 0 && !props.publicMode) {
      emit('sortingChange', [])
      return
    }

    // Only emit if sorting is active (not default order sorting) and not in public mode
    if (newSorting.length > 0 && !props.publicMode) {
      // Get current sorted items based on new sorting
      const items = [...props.items]
      const sortConfig = newSorting[0]
      if (!sortConfig) return

      const columnId = sortConfig.id
      const direction = sortConfig.desc ? -1 : 1

      // Apply sorting
      const sorted = items.sort((a, b) => {
        const aValue: unknown = a[columnId as keyof IGearItem]
        const bValue: unknown = b[columnId as keyof IGearItem]

        const aVal = aValue === null || aValue === undefined ? '' : aValue
        const bVal = bValue === null || bValue === undefined ? '' : bValue

        if (typeof aVal === 'string' && typeof bVal === 'string') {
          return aVal.localeCompare(bVal) * direction
        }

        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return (aVal - bVal) * direction
        }

        return String(aVal).localeCompare(String(bVal)) * direction
      })

      // Update order field based on current sorted order
      const updatedItems = sorted.map((item, index) => ({
        ...item,
        order: index,
      }))

      // Emit event for batch save (parent will handle saving)
      emit('sortingChange', updatedItems)
    }
  },
  { deep: true },
)

// Handle move up
function handleMoveUp(item: IGearItem) {
  const currentIndex = sortedItems.value.findIndex(i => i.id === item.id)
  if (currentIndex <= 0) return

  const reordered = [...sortedItems.value]
  const movedItem = reordered[currentIndex]
  if (!movedItem) return

  reordered.splice(currentIndex, 1)
  reordered.splice(currentIndex - 1, 0, movedItem)

  // Recalculate order values
  const updatedItems = reordered.map((item, index) => ({
    ...item,
    order: index,
  }))

  emit('reorder', updatedItems)
}

// Handle move down
function handleMoveDown(item: IGearItem) {
  const currentIndex = sortedItems.value.findIndex(i => i.id === item.id)
  if (currentIndex < 0 || currentIndex >= sortedItems.value.length - 1) return

  const reordered = [...sortedItems.value]
  const movedItem = reordered[currentIndex]
  if (!movedItem) return

  reordered.splice(currentIndex, 1)
  reordered.splice(currentIndex + 1, 0, movedItem)

  // Recalculate order values
  const updatedItems = reordered.map((item, index) => ({
    ...item,
    order: index,
  }))

  emit('reorder', updatedItems)
}

// Check if item can move up
function canMoveUp(item: IGearItem): boolean {
  const currentIndex = sortedItems.value.findIndex(i => i.id === item.id)
  return currentIndex > 0
}

// Check if item can move down
function canMoveDown(item: IGearItem): boolean {
  const currentIndex = sortedItems.value.findIndex(i => i.id === item.id)
  return currentIndex >= 0 && currentIndex < sortedItems.value.length - 1
}
</script>

<template>
  <DataTable
    v-model:column-visibility="columnVisibility"
    v-model:sorting="tableSorting"
    :columns="columns"
    :data="sortedItems"
    :search-placeholder="t('gear.filters.search')"
    :global-filter-fn="globalFilterFn"
    :enable-sorting="true"
    :enable-filtering="true"
    :enable-pagination="true"
    :enable-column-visibility="true"
    :initial-page-size="10"
  >
    <template #name="{ row }">
      <ItemsTableNameCell
        :item="row.original"
        :public-mode="publicMode"
        :is-expired="isExpired(row.original)"
        :is-expiring-soon="isExpiringSoon(row.original)"
        :is-nested-container="isNestedContainer(row.original)"
        :is-row-expanded="isRowExpanded(row.original.id)"
        :can-move-up="canMoveUp(row.original)"
        :can-move-down="canMoveDown(row.original)"
        :nested-container="getNestedContainer(row.original)"
        @move-up="handleMoveUp(row.original)"
        @move-down="handleMoveDown(row.original)"
        @navigate="navigateToItem(row.original)"
        @navigate-to-nested-container="navigateToNestedContainer(row.original)"
        @toggle-expand="toggleRowExpansion(row.original.id)"
      />
    </template>

    <template #image="{ row }">
      <ItemsTableImageCell
        :item-id="row.original.id"
        :container-id="containerId"
        :public-mode="publicMode"
      />
    </template>

    <template #category="{ row }">
      <ItemsTableCategoryCell :category="row.original.category" />
    </template>

    <template #quantity="{ row }">
      {{ row.original.quantity }}
    </template>

    <template #weight="{ row }">
      <ItemsTableWeightCell
        :item="row.original"
        :is-nested-container="isNestedContainer(row.original)"
        :total-weight="isNestedContainer(row.original) ? calculateTotalWeight(row.original.containerId!) : undefined"
        :preferred-weight-unit="settings.preferredWeightUnit"
      />
    </template>

    <template #priority="{ row }">
      <Badge :variant="getPriorityVariant(row.original.priority)">
        {{ t(`gear.item.priorities.${row.original.priority}`) }}
      </Badge>
    </template>

    <template #status="{ row }">
      <Badge :variant="getStatusVariant(row.original.status)">
        {{ t(`gear.item.statuses.${row.original.status}`) }}
      </Badge>
    </template>

    <template #price="{ row }">
      <div v-if="row.original.price != null" class="text-end px-4">
        {{ formatCurrency(row.original.price, getCurrency(row.original.currency, defaultCurrency)) }}
      </div>
      <span v-else class="text-muted-foreground">-</span>
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

    <template #actions="{ row }">
      <ItemsTableRowActions
        v-if="!publicMode"
        :row="row.original"
        @edit="emit('edit', row.original)"
        @delete="emit('delete', row.original)"
        @status-change="(status) => emit('statusChange', row.original, status)"
        @view-container="navigateToNestedContainer"
        @recognize-parameters="emit('recognizeParameters', row.original)"
      />
    </template>

    <!-- Expanded content for nested containers (rendered after each row) -->
    <template #row-after="{ row }">
      <ItemsTableNestedContainerRow
        v-if="isNestedContainer(row.original) && isRowExpanded(row.original.id)"
        :nested-items="getNestedContainerItems(row.original)"
        :columns-length="columns.length"
        :container="getNestedContainer(row.original)"
      />
    </template>

    <template #empty>
      <TableEmptyDecorated
        :colspan="columns.length"
        :icon="Package"
        :title="t('gear.item.empty')"
        :description="t('gear.item.emptyDescription')"
      />
    </template>
  </DataTable>
</template>

