<script setup lang="ts">
import { Package } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import DataTable from '@/components/data-table/DataTable.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import TableEmpty from '@/components/ui/table/TableEmpty.vue'
import { useSettings } from '@/modules/settings/composables/useSettings'
import type { IGearItem } from '../types/gear.types'
import { getPriorityVariant, getStatusVariant } from '../utils/badgeVariants'
import { EXPIRATION_WARNING_DAYS } from '../utils/constants'
import { formatWeight } from '../utils/formatWeight'
import { createItemsColumns } from '../utils/itemsColumns'
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
}>()

const { t } = useI18n()
const { customCategories } = useSettings()

// Helper to get category label for filtering
const getCategoryLabel = (categoryKey: string): string => {
  console.log('[getCategoryLabel]', categoryKey)
  const customCategory = customCategories.value.find(c => c.key === categoryKey)
  console.log('[customCategory]', customCategory)
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
</script>

<template>
  <DataTable
    :columns="columns"
    :data="props.items"
    :search-placeholder="t('gear.filters.search')"
    :global-filter-fn="globalFilterFn"
    :enable-sorting="true"
    :enable-filtering="true"
    :enable-pagination="true"
    :initial-page-size="10"
  >
    <template #name="{ row }">
      <div class="flex items-center gap-2" :class="{ 'text-destructive font-semibold': isExpired(row.original), 'text-yellow-600': isExpiringSoon(row.original) }">
        {{ row.original.name }}
        <Badge v-if="isExpired(row.original)" variant="destructive" class="text-xs">
          {{ t('gear.item.expiration.expired') }}
        </Badge>
        <Badge v-if="isExpiringSoon(row.original)" variant="outline" class="text-xs text-yellow-600 border-yellow-600">
          {{ t('gear.item.expiration.expiringSoon') }}
        </Badge>
      </div>
    </template>

    <template #category="{ row }">
      {{ getCategoryLabel(row.original.category) }}
    </template>

    <template #quantity="{ row }">
      {{ row.original.quantity }}
    </template>

    <template #weight="{ row }">
      {{ formatWeight(row.original.weight * row.original.quantity, row.original.weightUnit ?? 'g') }}
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

    <template #actions="{ row }">
      <ItemsTableRowActions
        :row="row.original"
        @edit="emit('edit', row.original)"
        @delete="emit('delete', row.original)"
        @status-change="(status) => emit('statusChange', row.original, status)"
      />
    </template>
    <template #empty>
      <TableEmpty :colspan="columns.length">
        <div class="flex flex-col items-center justify-center text-center">
          <div class="rounded-full bg-muted p-6 mb-4">
            <Package class="h-12 w-12 text-muted-foreground" />
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

