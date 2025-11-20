<script setup lang="ts">
import { Package } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import DataTable from '@/components/data-table/DataTable.vue'
import Badge from '@/components/ui/badge/Badge.vue'
import TableEmpty from '@/components/ui/table/TableEmpty.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useCoreSettings } from '@/modules/settings/composables/useCoreSettings'
import { ALL_ITEMS_TABLE_COLUMN_VISIBILITY_KEY } from '@/shared/config/config'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import CategoryIcon from '../components/CategoryIcon.vue'
import { useGear } from '../composables/useGear'
import { useGearSettings } from '../composables/useGearSettings'
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
const { settings: coreSettings } = useCoreSettings()
const settings = computed(() => ({ preferredWeightUnit: coreSettings.value.preferredWeightUnit }))

// Get all items from all containers
const allItems = computed<IItemWithContainer[]>(() => {
  return getAllItems(containers.value)
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
const getCategoryLabel = (categoryKey: string): string => {
  const customCategory = customCategories.value.find(c => c.key === categoryKey)
  if (customCategory) {
    return customCategory.label
  }
  return t(`gear.item.categories.${categoryKey}`)
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
  router.push(`/gear/${containerId}`)
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
        <template #category="{ row }">
          <div class="flex items-center gap-2">
            <CategoryIcon :category="row.original.category" :size="16" class="text-muted-foreground" />
            <span>{{ getCategoryLabel(row.original.category) }}</span>
          </div>
        </template>

        <template #name="{ row }">
          <span class="font-medium">{{ row.original.name }}</span>
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
          {{ formatWeightWithPreferredUnit(row.original.weight * row.original.quantity, row.original.weightUnit, settings.preferredWeightUnit) }}
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
          <TableEmpty>
            <Package class="size-12 text-muted-foreground mb-4" />
            <h3 class="text-lg font-semibold mb-2">
              {{ t('gear.allItems.empty', 'No items found') }}
            </h3>
            <p class="text-muted-foreground">
              {{ t('gear.allItems.emptyDescription', 'Create containers and add items to see them here.') }}
            </p>
          </TableEmpty>
        </template>
      </DataTable>
    </div>
  </AuthenticatedLayout>
</template>

