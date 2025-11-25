<script setup lang="ts">
import { Box, ChevronDown, ChevronRight, ChevronUp, Package } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import DataTable from '@/components/data-table/DataTable.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import TableEmptyDecorated from '@/components/ui/table/TableEmptyDecorated.vue'
import { ITEMS_TABLE_COLUMN_VISIBILITY_KEY } from '@/shared/config/config'
import type { IGearItem } from '../types/gear.types'
import { useGearSettings } from '../composables/useGearSettings'
import { GearRoutePath } from '../routes'
import { useGearStore } from '../store/useGearStore'
import { getPriorityVariant, getStatusVariant } from '../utils/badgeVariants'
import { EXPIRATION_WARNING_DAYS } from '../utils/constants'
import { calculateTotalWeightSync } from '../utils/containerCalculations'
import { COLOR_TEXT_CLASSES } from '../utils/containerColors'
import { formatCurrency, getCurrency } from '../utils/currencyFormatter'
import { formatWeightToPreferredUnit, formatWeightWithPreferredUnit } from '../utils/formatWeight'
import { createItemsColumns } from '../utils/itemsColumns'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'
import CategoryIcon from './CategoryIcon.vue'
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
const { customCategories } = useGearSettings()
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
    brand: false,
    color: false,
    wearable: false,
    consumable: false,
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

// Helper to get category label for filtering
const getCategoryLabel = (categoryValue: string): string => {
  const customCategory = customCategories.value.find(c => c.value === categoryValue)
  if (customCategory) {
    return customCategory.value
  }
  return t(`gear.item.categories.${categoryValue}`)
}

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
    router.push(GearRoutePath.ItemDetailById(props.containerId, item.id))
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
      <div class="flex items-center gap-2" :class="{ 'text-destructive font-semibold': isExpired(row.original), 'text-yellow-600': isExpiringSoon(row.original) }">
        <!-- Move up/down buttons (only in non-public mode) -->
        <div
          v-if="!publicMode"
          class="flex flex-col gap-0.5 shrink-0"
        >
          <Button
            variant="ghost"
            size="sm"
            class="size-5 p-0 h-4"
            :disabled="!canMoveUp(row.original)"
            @click.stop="handleMoveUp(row.original)"
          >
            <ChevronUp :size="12" class="text-muted-foreground" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            class="size-5 p-0 h-4"
            :disabled="!canMoveDown(row.original)"
            @click.stop="handleMoveDown(row.original)"
          >
            <ChevronDown :size="12" class="text-muted-foreground" />
          </Button>
        </div>
        <!-- Expand/Collapse button for nested containers -->
        <Button
          v-if="isNestedContainer(row.original)"
          variant="ghost"
          size="sm"
          class="size-6 p-0 shrink-0"
          @click.stop="toggleRowExpansion(row.original.id)"
        >
          <ChevronRight
            :size="16"
            class="text-muted-foreground transition-transform"
            :class="{ 'rotate-90': isRowExpanded(row.original.id) }"
          />
        </Button>

        <template v-if="isNestedContainer(row.original)">
          <Box :size="16" class="text-muted-foreground shrink-0" :class="COLOR_TEXT_CLASSES[getNestedContainer(row.original)?.color ?? 'default']" />
          <span
            class="font-semibold cursor-pointer text-foreground/80 hover:text-primary transition-colors"
            @click="navigateToNestedContainer(row.original)"
          >
            {{ row.original.name }}
          </span>
        </template>

        <span v-else class="cursor-pointer hover:text-primary transition-colors" @click="navigateToItem(row.original)">
          {{ row.original.name }}
        </span>

        <Badge v-if="isNestedContainer(row.original)" variant="outline" class="text-xs">
          {{ t('gear.item.nestedContainer') }}
        </Badge>
        <Badge v-if="isExpired(row.original)" variant="destructive" class="text-xs">
          {{ t('gear.item.expiration.expired') }}
        </Badge>
        <Badge v-if="isExpiringSoon(row.original)" variant="outline" class="text-xs text-yellow-600 border-yellow-600">
          {{ t('gear.item.expiration.expiringSoon') }}
        </Badge>
      </div>
    </template>

    <template #category="{ row }">
      <div class="flex items-center gap-2">
        <CategoryIcon :category="row.original.category" :size="16" class="text-muted-foreground" />
        <span>{{ getCategoryLabel(row.original.category) }}</span>
      </div>
    </template>

    <template #quantity="{ row }">
      {{ row.original.quantity }}
    </template>

    <template #weight="{ row }">
      <div class="text-end px-4">
        <template v-if="isNestedContainer(row.original)">
          {{ formatWeightToPreferredUnit(calculateTotalWeight(row.original.containerId!) * row.original.quantity, settings.preferredWeightUnit) }}
        </template>
        <template v-else>
          {{ formatWeightWithPreferredUnit(row.original.weight * row.original.quantity, row.original.weightUnit ?? 'g', settings.preferredWeightUnit) }}
        </template>
      </div>
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

