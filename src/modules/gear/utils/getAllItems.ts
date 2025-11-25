import type { IGearContainer } from '../types/gear.types'
import type { IItemWithContainer } from './allItemsColumns'
import { calculateTotalWeightSync } from './containerCalculations'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Get all items from all containers with container information
 * Also includes containers themselves as items (containers are items too)
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

    // Add container itself as an item (containers are items too)
    // Calculate total weight (container weight + all items weight) in grams
    const containerTotalWeightGrams = calculateTotalWeightSync(container, containers)
    // Use container's weight unit if set, otherwise use grams
    const displayWeightUnit = container.weightUnit ?? 'g'
    // Convert total weight from grams to display unit
    let displayWeight = containerTotalWeightGrams
    if (displayWeightUnit === 'kg') {
      displayWeight = containerTotalWeightGrams / 1000
    } else if (displayWeightUnit === 'oz') {
      displayWeight = containerTotalWeightGrams / 28.3495
    } else if (displayWeightUnit === 'lb') {
      displayWeight = containerTotalWeightGrams / 453.592
    }

    allItems.push({
      id: container.id,
      name: container.name,
      category: 'other', // Containers use 'other' category
      containerId: container.id,
      containerName: container.name,
      containerColor: container.color ?? 'default',
      quantity: 1,
      weight: displayWeight,
      weightUnit: displayWeightUnit,
      status: 'owned', // Containers are always owned
      priority: 'medium', // Default priority for containers
      brand: container.brand ?? undefined,
      color: undefined, // Containers don't have color field (they have containerColor)
      expirationDate: undefined,
      wearable: false,
      consumable: false,
      isContainer: true,
      containerType: container.type,
    })

    // Add regular items from container
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
        isContainer: false,
      })
    })
  })

  return allItems
}

