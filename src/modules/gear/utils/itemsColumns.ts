import type { IGearItem } from '../types/gear.types'
import type { ColumnDef } from '@tanstack/vue-table'

export function createItemsColumns(
  t: (key: string, ...args: unknown[]) => string,
): ColumnDef<IGearItem>[] {
  return [
    {
      id: 'name',
      accessorKey: 'name',
      header: () => t('gear.item.name'),
      enableSorting: true,
    },
    {
      id: 'category',
      accessorKey: 'category',
      header: () => t('gear.item.category'),
      enableSorting: true,
    },
    {
      id: 'quantity',
      accessorKey: 'quantity',
      header: () => t('gear.item.quantity'),
      enableSorting: true,
    },
    {
      id: 'weight',
      accessorKey: 'weight',
      header: () => t('gear.item.weight'),
      enableSorting: true,
    },
    {
      id: 'priority',
      accessorKey: 'priority',
      header: () => t('gear.item.priority'),
      enableSorting: true,
    },
    {
      id: 'status',
      accessorKey: 'status',
      header: () => t('gear.item.status'),
      enableSorting: true,
    },
    {
      id: 'actions',
      enableSorting: false,
    },
  ]
}
