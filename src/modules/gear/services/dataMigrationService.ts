import { logger } from '@/shared/utils/logger'
import type { IGearContainer } from '../types/gear.types'
import { useGearStore } from '../store/useGearStore'
// modules/gear/services/dataMigrationService.ts
import { gearContainerApiService } from './gearContainerApiService'
import { gearContainerLocalService } from './gearContainerLocalService'
import { gearItemApiService } from './gearItemApiService'

const STORAGE_KEY = 'gear-stack:containers'

/**
 * CRITICAL FIX: Sort containers by dependency order (topological sort)
 * This ensures parent containers are created before their children
 * Prevents circular dependency issues and orphaned containers
 */
function sortContainersByDependency(containers: IGearContainer[]): IGearContainer[] {
  const sorted: IGearContainer[] = []
  const visited = new Set<string>()
  const visiting = new Set<string>() // For cycle detection

  function visit(container: IGearContainer): void {
    if (visited.has(container.id)) return

    // Detect circular dependencies
    if (visiting.has(container.id)) {
      logger.warn(`Circular dependency detected for container: ${container.name}`)
      // Break the cycle by setting parentContainerId to null
      container.parentContainerId = null
      return
    }

    visiting.add(container.id)

    // Visit parent first if it exists
    if (container.parentContainerId) {
      const parent = containers.find(c => c.id === container.parentContainerId)
      if (parent) {
        visit(parent)
      } else {
        // Parent not found - orphaned container, set parent to null
        logger.warn(`Parent container not found for ${container.name}, setting parent to null`)
        container.parentContainerId = null
      }
    }

    visiting.delete(container.id)
    visited.add(container.id)
    sorted.push(container)
  }

  // Visit all containers
  containers.forEach(container => visit(container))

  return sorted
}

/**
 * Check if there are containers in localStorage
 */
export function hasLocalData(): boolean {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (!stored) return false
  
  try {
    const containers = JSON.parse(stored) as unknown[]
    return Array.isArray(containers) && containers.length > 0
  } catch {
    return false
  }
}

/**
 * Migrate data from localStorage to API
 * This is called after successful login when local data exists
 * 
 * Strategy:
 * 1. Load containers from localStorage
 * 2. For each container, try to create it via API
 * 3. If container already exists (by name or other criteria), skip or update
 * 4. Update store with migrated containers
 * 
 * @returns Promise that resolves when migration is complete
 */
export async function migrateLocalDataToAPI(): Promise<void> {
  const localContainers = await gearContainerLocalService.getAllContainers()

  if (localContainers.length === 0) {
    logger.info('No local data to migrate')
    return
  }

  logger.info(`Migrating ${localContainers.length} containers to API...`)

  // CRITICAL FIX: Sort containers by dependency to avoid orphaned containers
  const sortedContainers = sortContainersByDependency([...localContainers])
  logger.info('Containers sorted by dependency order')

  const store = useGearStore()
  const migratedContainers = []
  // Map old IDs to new IDs for parent reference updates
  const idMapping = new Map<string, string>()

  for (const localContainer of sortedContainers) {
    try {
      // Create container via API
      // Note: We need to extract items first, as API expects separate creation
      const { items, ...containerData } = localContainer

      // CRITICAL FIX: Map old parent ID to new API-generated ID
      let parentContainerId = containerData.parentContainerId
      if (parentContainerId && idMapping.has(parentContainerId)) {
        parentContainerId = idMapping.get(parentContainerId) ?? null
      }

      // Create container without items first
      const createdContainer = await gearContainerApiService.createContainer({
        name: containerData.name,
        description: containerData.description,
        type: containerData.type,
        parentContainerId, // Use mapped ID
        maxWeight: containerData.maxWeight,
        maxWeightUnit: containerData.maxWeightUnit,
        weight: containerData.weight,
        weightUnit: containerData.weightUnit,
        color: containerData.color,
        brand: containerData.brand,
        price: containerData.price,
        url: containerData.url,
        hideWhenNested: containerData.hideWhenNested,
      })

      // CRITICAL FIX: Store ID mapping for child containers
      idMapping.set(localContainer.id, createdContainer.id)

      // Create items for this container
      if (items && items.length > 0) {
        for (const item of items) {
          try {
            await gearItemApiService.createItem(createdContainer.id, {
              name: item.name,
              category: item.category,
              quantity: item.quantity ?? 1,
              weight: item.weight ?? 0,
              weightUnit: item.weightUnit ?? 'g',
              status: item.status,
              notes: item.notes ?? null,
              expirationDate: item.expirationDate ?? null,
              priority: item.priority ?? 'medium',
              brand: item.brand ?? null,
              color: item.color ?? null,
              price: item.price ?? null,
              url: item.url ?? null,
              quality: item.quality ?? null,
              wearable: item.wearable ?? null,
              consumable: item.consumable ?? null,
            })
          } catch (itemError) {
            logger.warn(`Failed to migrate item ${item.name} for container ${createdContainer.name}:`, itemError)
            // Continue with other items
          }
        }
      }

      migratedContainers.push(createdContainer)
      logger.info(`Migrated container: ${createdContainer.name}`)
    } catch (error) {
      logger.error(`Failed to migrate container ${localContainer.name}:`, error)
      // Continue with other containers
    }
  }

  // Update store with migrated containers
  if (migratedContainers.length > 0) {
    // Fetch all containers from API to get complete data
    const allContainers = await gearContainerApiService.getContainers()
    store.setContainers(allContainers)
    logger.info(`Migration complete: ${migratedContainers.length} containers migrated`)
  }
}

/**
 * Check if data should be migrated and prompt user
 * This is a helper that can be used in UI to show migration prompt
 */
export function shouldPromptForMigration(): boolean {
  return hasLocalData()
}

