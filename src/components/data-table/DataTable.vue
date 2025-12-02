<script setup lang="ts" generic="TData, TValue">
import {
  FlexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useVueTable,
} from '@tanstack/vue-table'
import { ArrowUpDown } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { TableLoadingSkeleton } from '@/components/ui/table'
import { valueUpdater } from '@/lib/utils'
import DataTableEmpty from './DataTableEmpty.vue'
import DataTableToolbar from './DataTableToolbar.vue'
import Pagination from './Pagination.vue'
import type {
  ColumnDef,
  RowSelectionState,
  SortingState,
  VisibilityState,
} from '@tanstack/vue-table'

// Props
interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  // Loading state
  loading?: boolean
  // Feature toggles
  enableSorting?: boolean
  enableFiltering?: boolean
  enablePagination?: boolean
  enableRowSelection?: boolean
  enableColumnVisibility?: boolean
  // Filtering
  searchPlaceholder?: string
  globalFilterFn?: (row: TData, filterValue: string) => boolean
  // Pagination
  initialPageSize?: number
  pageSizeOptions?: number[]
  // Accessibility
  ariaLabel?: string
  ariaLabelledby?: string
  // Server-side pagination
  total?: number
  // Events
  onPageChange?: (page: number) => void
  onPageSizeChange?: (pageSize: number) => void
}

const props = withDefaults(defineProps<DataTableProps<TData, TValue>>(), {
  loading: false,
  enableSorting: true,
  enableFiltering: true,
  enablePagination: true,
  enableRowSelection: false,
  enableColumnVisibility: true,
  searchPlaceholder: 'Filter...',
  initialPageSize: 10,
  pageSizeOptions: () => [10, 20, 50, 100, 500],
})

// v-model support using defineModel
const page = defineModel<number>('page', { default: 1 })
const pageSize = defineModel<number>('pageSize', { default: 10 })
const rowSelection = defineModel<RowSelectionState>('rowSelection', { default: {} })
const columnVisibilityModel = defineModel<VisibilityState>('columnVisibility', { default: () => ({}) })
const globalFilterModel = defineModel<string>('globalFilter', { default: '' })

// Emits for non-v-model events
const emit = defineEmits<{
  'update:sorting': [sorting: SortingState]
  'update:globalFilter': [filter: string]
  'update:columnVisibility': [visibility: VisibilityState]
  'update:page': [page: number]
  'update:pageSize': [pageSize: number]
  'empty-action': []
}>()

// State
const sorting = ref<SortingState>([])
const globalFilter = ref(globalFilterModel.value || '')
// Use model value if provided, otherwise use internal ref
const columnVisibility = ref<VisibilityState>({ ...(columnVisibilityModel.value || {}) })

// Sync model with internal ref only on initial mount or when model changes externally
// Don't sync when table updates (that's handled by onColumnVisibilityChange)
let isInternalUpdate = false
watch(columnVisibilityModel, (newValue) => {
  if (isInternalUpdate) {
    isInternalUpdate = false
    return
  }

  // Only sync if the new value is different and not empty
  if (newValue && Object.keys(newValue).length > 0) {
    // Compare actual values
    const currentStr = JSON.stringify(columnVisibility.value)
    const newStr = JSON.stringify(newValue)
    if (currentStr !== newStr) {
      columnVisibility.value = { ...newValue }
    }
  }
}, { immediate: true, deep: true })

// Pagination state (client-side or server-side)
const isServerSide = computed(() => props.total !== undefined)
const currentPage = computed({
  get: () => isServerSide.value ? page.value : page.value,
  set: (value) => {
    page.value = value
    if (isServerSide.value) {
      emit('update:page', value)
      props.onPageChange?.(value)
    }
  }
})
const currentPageSize = computed({
  get: () => isServerSide.value ? pageSize.value : pageSize.value,
  set: (value) => {
    pageSize.value = value
    if (isServerSide.value) {
      emit('update:pageSize', value)
      props.onPageSizeChange?.(value)
    }
  }
})

// Table instance
const table = useVueTable({
  get data() {
    return props.data
  },
  get columns() {
    return props.columns
  },
  getCoreRowModel: getCoreRowModel(),
  enableRowSelection: props.enableRowSelection,
  enableMultiRowSelection: props.enableRowSelection,
  getSortedRowModel: props.enableSorting ? getSortedRowModel() : undefined,
  getFilteredRowModel: props.enableFiltering ? getFilteredRowModel() : undefined,
  getPaginationRowModel: props.enablePagination ? getPaginationRowModel() : undefined,
  globalFilterFn: props.globalFilterFn ? (row, columnId, filterValue) => {
    return props.globalFilterFn ? props.globalFilterFn(row.original, filterValue) : false
  } : 'includesString',
  onSortingChange: props.enableSorting
    ? (updaterOrValue) => {
        valueUpdater(updaterOrValue, sorting)
        emit('update:sorting', sorting.value)
      }
    : undefined,
  onGlobalFilterChange: props.enableFiltering
    ? (value) => {
        globalFilter.value = value
        globalFilterModel.value = value
        emit('update:globalFilter', value)
      }
    : undefined,
  onColumnVisibilityChange: props.enableColumnVisibility
    ? (updaterOrValue) => {
        valueUpdater(updaterOrValue, columnVisibility)
        // Update model after state is updated - mark as internal to prevent watch loop
        isInternalUpdate = true
        columnVisibilityModel.value = { ...columnVisibility.value }
        emit('update:columnVisibility', columnVisibility.value)
      }
    : undefined,
  onRowSelectionChange: props.enableRowSelection
    ? (updaterOrValue) => {
        valueUpdater(updaterOrValue, rowSelection)
      }
    : undefined,
  onPaginationChange: props.enablePagination && !isServerSide.value
    ? (updater) => {
        const newPagination = typeof updater === 'function'
          ? updater({ pageIndex: currentPage.value - 1, pageSize: currentPageSize.value })
          : updater

        currentPage.value = newPagination.pageIndex + 1
        currentPageSize.value = newPagination.pageSize
      }
    : undefined,
  state: {
    get sorting() { return props.enableSorting ? sorting.value : undefined },
    get globalFilter() { return props.enableFiltering ? globalFilter.value : undefined },
    get columnVisibility() { return props.enableColumnVisibility ? columnVisibility.value : undefined },
    get rowSelection() { return props.enableRowSelection ? rowSelection.value : undefined },
    get pagination() {
      return props.enablePagination ? {
        pageIndex: currentPage.value - 1,
        pageSize: currentPageSize.value,
      } : undefined
    },
  },
  initialState: {
    ...(props.enablePagination ? {
      pagination: {
        pageIndex: 0,
        pageSize: currentPageSize.value,
      },
    } : {}),
    ...(props.enableColumnVisibility && Object.keys(columnVisibility.value).length > 0 ? {
      columnVisibility: columnVisibility.value,
    } : {}),
    ...(props.enableFiltering && globalFilter.value ? {
      globalFilter: globalFilter.value,
    } : {}),
  },
})

// Sync globalFilterModel with internal ref (after table is created)
watch(globalFilterModel, (newValue) => {
  if (globalFilter.value !== newValue) {
    globalFilter.value = newValue || ''
    if (props.enableFiltering) {
      table.setGlobalFilter(newValue || '')
    }
  }
})

// Computed values
const totalRows = computed(() => isServerSide.value ? (props.total ?? 0) : props.data.length)
const isEmpty = computed(() => table.getRowModel().rows.length === 0)
const selectedRowsCount = computed(() => Object.keys(rowSelection.value).length)

// Event handlers
const handlePageChange = (newPage: number) => {
  currentPage.value = newPage
  if (!isServerSide.value) {
    table.setPageIndex(newPage - 1)
  }
}

const handlePageSizeChange = (newPageSize: number) => {
  currentPageSize.value = newPageSize
  if (!isServerSide.value) {
    table.setPageSize(newPageSize)
    currentPage.value = 1
    table.setPageIndex(0)
  }
}
</script>

<template>
  <div class="space-y-4 w-full max-w-full">
    <!-- Toolbar Slot -->
    <slot
      name="toolbar"
      :table="table"
      :global-filter="globalFilter"
      :column-visibility="columnVisibility"
    >
      <DataTableToolbar
        v-model:global-filter="globalFilter"
        v-model:column-visibility="columnVisibility"
        :table="table"
        :search-placeholder="searchPlaceholder"
        :enable-filtering="enableFiltering"
        :enable-column-visibility="enableColumnVisibility"
      >
        <template #filters>
          <slot name="toolbar-filters" />
        </template>
      </DataTableToolbar>
    </slot>

    <!-- Table -->
    <div class="border rounded-md overflow-hidden relative">
      <div class="overflow-x-auto">
        <!-- Horizontal scroll indicator (gradient hint on right side for mobile) -->
        <div class="absolute right-0 top-0 bottom-0 w-12 pointer-events-none z-10 bg-linear-to-l from-black/5 dark:from-muted/60 to-transparent md:hidden" aria-hidden="true" />
        <Table
          :aria-label
          :aria-labelledby
        >
          <TableHeader>
            <TableRow v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
              <TableHead v-for="header in headerGroup.headers" :key="header.id">
                <slot
                  :name="`header-${header.column.id}`"
                  :header="header"
                  :column="header.column"
                >
                  <!-- Default sortable header -->
                  <template v-if="!header.isPlaceholder && enableSorting && header.column.getCanSort()">
                    <Button
                      variant="ghost"
                      class="group -ml-3 h-8 data-[state=open]:bg-accent"
                      @click="header.column.toggleSorting(header.column.getIsSorted() === 'asc')"
                    >
                      <FlexRender
                        :render="header.column.columnDef.header"
                        :props="header.getContext()"
                      />
                      <ArrowUpDown
                        class="ml-2 size-4 group-hover:opacity-100 transition-opacity"
                        :class="header.column.getIsSorted() ? 'opacity-60' : 'opacity-0'"
                      />
                    </Button>
                  </template>
                  <!-- Default non-sortable header -->
                  <FlexRender
                    v-else-if="!header.isPlaceholder"
                    :render="header.column.columnDef.header"
                    :props="header.getContext()"
                  />
                </slot>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <!-- Loading State -->
            <template v-if="loading">
              <slot name="loading" :table="table" :columns="columns">
                <TableLoadingSkeleton :colspan="columns.length" />
              </slot>
            </template>
            <!-- Data Rows -->
            <template v-else-if="!isEmpty">
              <template v-for="row in table.getRowModel().rows" :key="row.id">
                <TableRow
                  :data-state="row.getIsSelected() ? 'selected' : undefined"
                >
                  <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id">
                    <slot
                      :name="cell.column.columnDef.id"
                      :row="row"
                      :cell="cell"
                    >
                      <FlexRender
                        :render="cell.column.columnDef.cell"
                        :props="cell.getContext()"
                      />
                    </slot>
                  </TableCell>
                </TableRow>
                <!-- Slot for content after each row (e.g., expandable content) -->
                <slot name="row-after" :row="row" :columns="columns" />
              </template>
            </template>
            <!-- Empty State -->
            <template v-else>
              <slot name="empty" :table="table" :columns="columns">
                <DataTableEmpty
                  :table="table"
                  :columns="columns"
                  @action="$emit('empty-action')"
                />
              </slot>
            </template>
          </TableBody>
        </Table>
      </div>
    </div>

    <!-- Pagination Slot -->
    <slot
      name="pagination"
      :table="table"
      :page="currentPage"
      :page-size="currentPageSize"
      :total="totalRows"
      :handle-page-change="handlePageChange"
      :handle-page-size-change="handlePageSizeChange"
    >
      <Pagination
        v-if="enablePagination"
        :page="currentPage"
        :page-size="currentPageSize"
        :total="totalRows"
        :page-size-options="pageSizeOptions"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </slot>

    <!-- Row Selection Info Slot -->
    <slot
      name="selection-info"
      :table="table"
      :selected-count="selectedRowsCount"
      :total-count="table.getFilteredRowModel().rows.length"
    >
      <div v-if="enableRowSelection && selectedRowsCount > 0" class="flex-1 text-sm text-muted-foreground">
        {{ selectedRowsCount }} of {{ table.getFilteredRowModel().rows.length }} row(s) selected.
      </div>
    </slot>
  </div>
</template>
