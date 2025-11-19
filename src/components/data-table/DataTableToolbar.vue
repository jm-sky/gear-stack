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

const handleGlobalFilterChange = (value: string) => {
  globalFilter.value = value
}

const { t } = useI18n()

const handleColumnVisibilityChange = (columnId: string, visible: boolean) => {
  // Update column visibility through table state - this will trigger onColumnVisibilityChange
  const currentState = props.table.getState().columnVisibility || {}
  const newState = {
    ...currentState,
    [columnId]: visible,
  }

  // Use table.setColumnVisibility to update state - this properly triggers onColumnVisibilityChange
  props.table.setColumnVisibility(newState)
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
          // If it's a VNode, try to extract text or fall back
        } catch {
          // If header function fails with context, try without context
          try {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const result = headerDef({} as any)
            if (typeof result === 'string') {
              return result
            }
          } catch {
            // If that also fails, fall back to id
          }
        }
        break
      }
    }
    // If no header found in groups, try calling function directly
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const result = headerDef({} as any)
      if (typeof result === 'string') {
        return result
      }
    } catch {
      // Fall through to fallback
    }
  } else if (typeof headerDef === 'string') {
    return headerDef
  }

  // Fallback to column id
  return column.id
}
</script>

<template>
  <div v-if="enableFiltering || enableColumnVisibility" class="flex items-center gap-4 py-4">
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
        <Button variant="outline" class="ml-auto shrink-0">
          {{ t('common.columns') }}
          <ChevronDown class="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuCheckboxItem
          v-for="column in table.getAllColumns().filter((column) => column.getCanHide())"
          :key="column.id"
          class="capitalize"
          :model-value="column.getIsVisible()"
          @update:model-value="(value: boolean) => handleColumnVisibilityChange(column.id, value)"
        >
          {{ getColumnHeaderText(column) }}
        </DropdownMenuCheckboxItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </div>
</template>
