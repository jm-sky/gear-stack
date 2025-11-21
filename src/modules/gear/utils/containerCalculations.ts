import type { IGearContainer } from '../types/gear.types'
import { convertToGrams } from './formatWeight'
import { isSet } from './helpers'

/**
 * Calculate total weight of a container synchronously (for use in computed)
 * @param container - Container to calculate weight for
 * @param allContainers - All containers (for nested container calculations)
 * @returns Total weight in grams
 */
export function calculateTotalWeightSync(
  container: IGearContainer,
  allContainers: IGearContainer[],
): number {
  // Start with container's own weight (if set)
  let totalWeight = 0
  if (isSet(container.weight) && isSet(container.weightUnit)) {
    totalWeight = convertToGrams(container.weight, container.weightUnit)
  }

  // Add weight of direct items
  for (const item of container.items) {
    // If item is a nested container, calculate its total weight recursively
    if (item.containerId) {
      const nestedContainer = allContainers.find(c => c.id === item.containerId)
      if (nestedContainer) {
        const nestedContainerWeight = calculateTotalWeightSync(nestedContainer, allContainers)
        totalWeight += nestedContainerWeight * item.quantity
      }
    } else {
      // Regular item weight
      const weightInGrams = convertToGrams(item.weight, item.weightUnit ?? 'g')
      totalWeight += weightInGrams * item.quantity
    }
  }

  return totalWeight
}

/**
 * Calculate readiness percentage synchronously (for use in computed)
 * @param container - Container to calculate readiness for
 * @returns Readiness percentage (0-100)
 */
export function calculateReadinessPercentageSync(container: IGearContainer): number {
  if (!container || container.items.length === 0) {
    return 0
  }

  const ownedItems = container.items.filter(item => item.status === 'owned').length
  return Math.round((ownedItems / container.items.length) * 100)
}

/**
 * Calculate weight limit percentage synchronously (for use in computed)
 * @param container - Container to calculate weight limit for
 * @param allContainers - All containers (for nested container calculations)
 * @returns Weight limit percentage (0-100+) or null if no limit
 */
export function calculateWeightLimitPercentageSync(
  container: IGearContainer,
  allContainers: IGearContainer[],
): number | null {
  if (!container || !isSet(container.maxWeight)) {
    return null
  }

  const totalWeight = calculateTotalWeightSync(container, allContainers)
  const maxWeightInGrams = convertToGrams(container.maxWeight, container.maxWeightUnit ?? 'g')

  if (maxWeightInGrams === 0) {
    return 0
  }

  return Math.round((totalWeight / maxWeightInGrams) * 100)
}

