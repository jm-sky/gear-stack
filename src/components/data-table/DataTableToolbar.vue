<script setup lang="ts" generic="TData, TValue">
import { ChevronDown } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import type { Table } from '@tanstack/vue-table'

interface Props {
  table: Table<TData>
  searchPlaceholder?: string
  enableFiltering?: boolean
  enableColumnVisibility?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  searchPlaceholder: 'Filter...',
  enableFiltering: true,
  enableColumnVisibility: true,
})

const globalFilter = defineModel<string>('globalFilter', { default: '' })
const columnVisibility = defineModel<Record<string, boolean>>('columnVisibility', { default: {} })

const handleGlobalFilterChange = (value: string) => {
  globalFilter.value = value
}

const { t } = useI18n()

const handleColumnVisibilityChange = (columnId: string, visible: boolean) => {
  // Toggle column visibility in table
  const column = props.table.getColumn(columnId)
  if (column) {
    column.toggleVisibility(visible)
  }

  // Update parent state
  const newVisibility = { ...columnVisibility.value, [columnId]: visible }
  columnVisibility.value = newVisibility
}

// Helper to get column header text
const getColumnHeaderText = (column: ReturnType<Table<TData>['getColumn']>): string => {
  if (!column) return ''

  const headerDef = column.columnDef.header
  if (typeof headerDef === 'function') {
    // Try to get header context from table
    const headerGroups = props.table.getHeaderGroups()
    for (const headerGroup of headerGroups) {
      const header = headerGroup.headers.find(h => h.column.id === column.id)
      if (header) {
        try {
          const context = header.getContext()
          const result = headerDef(context)
          if (typeof result === 'string') {
            return result
          }
          // If it's a VNode, we can't easily extract text, so fall back to id
        } catch {
          // If header function fails, fall back to id
        }
        break
      }
    }
  } else if (typeof headerDef === 'string') {
    return headerDef
  }

  // Fallback to column id
  return column.id
}
</script>

<template>
  <div v-if="enableFiltering || enableColumnVisibility" class="flex items-center justify-between py-4">
    <!-- Global Filter Input -->
    <Input
      v-if="enableFiltering"
      :model-value="globalFilter"
      :placeholder="searchPlaceholder"
      class="max-w-sm"
      @update:model-value="(value: string | number) => handleGlobalFilterChange(String(value))"
    />

    <!-- Column Visibility Toggle -->
    <DropdownMenu v-if="enableColumnVisibility">
      <DropdownMenuTrigger as-child>
        <Button variant="outline" class="ml-auto">
          {{ t('common.columns') }}
          <ChevronDown class="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuCheckboxItem
          v-for="column in table.getAllColumns().filter((column) => column.getCanHide())"
          :key="column.id"
          class="capitalize"
          :checked="column.getIsVisible()"
          @update:model-value="(value: boolean) => handleColumnVisibilityChange(column.id, value)"
        >
          {{ getColumnHeaderText(column) }}
        </DropdownMenuCheckboxItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </div>
</template>
