<script setup lang="ts">
import { Box, ChevronRight, Package } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import DataTable from '@/components/data-table/DataTable.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import TableEmpty from '@/components/ui/table/TableEmpty.vue'
import { useCoreSettings } from '@/modules/settings/composables/useCoreSettings'
import { ITEMS_TABLE_COLUMN_VISIBILITY_KEY } from '@/shared/config/config'
import type { IGearItem } from '../types/gear.types'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
import { getPriorityVariant, getStatusVariant } from '../utils/badgeVariants'
import { EXPIRATION_WARNING_DAYS } from '../utils/constants'
import { COLOR_TEXT_CLASSES } from '../utils/containerColors'
import { formatWeightToPreferredUnit, formatWeightWithPreferredUnit } from '../utils/formatWeight'
import { createItemsColumns } from '../utils/itemsColumns'
import { DEFAULT_COLOR, getColorHex } from '../utils/suggestedValues'
import CategoryIcon from './CategoryIcon.vue'
import ItemsTableNestedContainerRow from './ItemsTableNestedContainerRow.vue'
import ItemsTableRowActions from './ItemsTableRowActions.vue'

const props = withDefaults(
  defineProps<{
    items: IGearItem[]
    loading?: boolean
  }>(),
  {
    loading: false,
  },
)

const emit = defineEmits<{
  edit: [item: IGearItem]
  delete: [item: IGearItem]
  statusChange: [item: IGearItem, status: IGearItem['status']]
  recognizeParameters: [item: IGearItem]
}>()

const { t } = useI18n()
const router = useRouter()
const { settings: coreSettings } = useCoreSettings()
const { customCategories } = useGearSettings()
const settings = computed(() => ({ preferredWeightUnit: coreSettings.value.preferredWeightUnit }))
const { getContainerById, calculateTotalWeight } = useGear()

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
  // Default: hide brand and color by default
  return {
    brand: false,
    color: false,
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
const getCategoryLabel = (categoryKey: string): string => {
  const customCategory = customCategories.value.find(c => c.key === categoryKey)
  if (customCategory) {
    return customCategory.label
  }
  return t(`gear.item.categories.${categoryKey}`)
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
    router.push(`/gear/${item.containerId}`)
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
  const container = getContainerById(item.containerId)
  return container?.items ?? []
}

// Get nested container
function getNestedContainer(item: IGearItem) {
  if (!item.containerId) return undefined
  return getContainerById(item.containerId)
}
</script>

<template>
  <DataTable
    v-model:column-visibility="columnVisibility"
    :columns="columns"
    :data="props.items"
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

        <span v-else class="cursor-pointer hover:text-primary transition-colors" @click="emit('edit', row.original)">
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

    <template #actions="{ row }">
      <ItemsTableRowActions
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
      <TableEmpty :colspan="columns.length">
        <div class="flex flex-col items-center justify-center text-center">
          <div class="rounded-full bg-muted p-6 mb-4">
            <Package class="size-12 text-muted-foreground" />
          </div>
          <h3 class="text-lg font-semibold mb-2">
            {{ t('gear.item.empty') }}
          </h3>
          <p class="text-muted-foreground">
            {{ t('gear.item.emptyDescription') }}
          </p>
        </div>
      </TableEmpty>
    </template>
  </DataTable>
</template>

