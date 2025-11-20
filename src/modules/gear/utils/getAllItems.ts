import type { IGearContainer } from '../types/gear.types'
import type { IItemWithContainer } from './allItemsColumns'

/**
 * Get all items from all containers with container information
 */
export function getAllItems(containers: IGearContainer[]): IItemWithContainer[] {
  const allItems: IItemWithContainer[] = []

  containers.forEach(container => {
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
        brand: item.brand,
        color: item.color,
        expirationDate: item.expirationDate,
        wearable: item.wearable,
        consumable: item.consumable,
      })
    })
  })

  return allItems
}

