import type { IGearContainer } from '../types/gear.types'
import type { IItemWithContainer } from './allItemsColumns'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Get all items from all containers with container information
 * @param containers - Array of containers to search
 * @param excludeContainerId - Optional container ID to exclude from results
 */
export function getAllItems(containers: IGearContainer[], excludeContainerId?: TUUID): IItemWithContainer[] {
  const allItems: IItemWithContainer[] = []

  containers.forEach(container => {
    // Skip items from excluded container
    if (excludeContainerId && container.id === excludeContainerId) {
      return
    }

    container.items.forEach(item => {
      allItems.push({
        id: item.id,
        name: item.name,
        category: item.category,
        containerId: container.id,
        containerName: container.name,
        containerColor: container.color ?? 'default',
        quantity: item.quantity,
        weight: item.weight,
        weightUnit: item.weightUnit ?? 'g',
        status: item.status,
        priority: item.priority,
        brand: item.brand ?? undefined,
        color: item.color ?? undefined,
        expirationDate: item.expirationDate ?? undefined,
        wearable: item.wearable ?? undefined,
        consumable: item.consumable ?? undefined,
      })
    })
  })

  return allItems
}

