import { logger } from '@/shared/utils/logger'
import type { IGearContainer } from '../types/gear.types'
import { useGearStore } from '../store/useGearStore'
import { validateContainerDto, validateItemDto } from '../utils/validation'
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
  // Make a deep copy to avoid modifying original containers during sorting
  const sortedContainers = sortContainersByDependency(localContainers.map(c => ({ ...c })))
  logger.info('Containers sorted by dependency order')

  const store = useGearStore()
  const migratedContainers = []
  // Map old IDs to new IDs for parent reference updates
  const idMapping = new Map<string, string>()

  for (let i = 0; i < sortedContainers.length; i++) {
    const localContainer = sortedContainers[i]
    if (!localContainer) {
      logger.warn(`Container at index ${i} is undefined, skipping`)
      continue
    }
    try {
      // Create container via API
      // Note: We need to extract items first, as API expects separate creation
      const { items, ...containerData } = localContainer

      // CRITICAL FIX: Map old parent ID to new API-generated ID
      let parentContainerId = containerData.parentContainerId

      if (parentContainerId) {
        // Check if this is a valid ULID (backend) or UUID (frontend offline) format
        // Backend uses ULID (26 chars base32), frontend offline uses UUID (8-4-4-4-12 hex)
        const isUlid = /^[0-9A-HJKMNP-TV-Z]{26}$/i.test(parentContainerId)
        const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(parentContainerId)
        const isValidId = isUlid || isUuid

        if (idMapping.has(parentContainerId)) {
          // Parent ID found in mapping - use mapped ID (this is the correct API-generated ID)
          const mappedId = idMapping.get(parentContainerId) ?? null
          // Check if mapped ID is a valid ULID (backend) or UUID (frontend offline)
          // Backend returns ULID (26 chars base32), frontend offline uses UUID (8-4-4-4-12 hex)
          const isMappedIdUlid = mappedId ? /^[0-9A-HJKMNP-TV-Z]{26}$/i.test(mappedId) : false
          const isMappedIdUuid = mappedId ? /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(mappedId) : false
          if (mappedId && !isMappedIdUlid && !isMappedIdUuid) {
            // Mapped ID is neither ULID nor UUID - this shouldn't happen in real scenarios
            // but could happen in tests with incorrect mocks
            logger.warn(`Mapped parent ID ${mappedId} for ${containerData.name} is not a valid ULID or UUID. Setting to null to avoid validation error.`)
            parentContainerId = null
          } else {
            parentContainerId = mappedId
          }
        } else if (!isValidId) {
          // Parent ID is not in mapping and not a UUID - this is an old localStorage ID
          // Check if parent is in sorted containers before current index
          const parentIndex = sortedContainers.findIndex(c => c.id === parentContainerId)
          if (parentIndex === -1) {
            // Parent doesn't exist - already handled by sorting (should be null), but handle edge case
            logger.warn(`Parent container ${parentContainerId} not found in sorted containers. Setting parent to null for ${containerData.name}.`)
            parentContainerId = null
          } else if (parentIndex < i) {
            // Parent should have been processed already - check if mapping exists for parent's old ID
            const parentContainer = sortedContainers[parentIndex]
            if (!parentContainer) {
              logger.warn(`Parent container at index ${parentIndex} is undefined. Setting parent to null for ${containerData.name}.`)
              parentContainerId = null
            } else {

            if (idMapping.has(parentContainer.id)) {
              // Parent was processed and mapping exists - use mapped ID
              const mappedId = idMapping.get(parentContainer.id) ?? null
              // Check if mapped ID is a valid ULID (backend) or UUID (frontend offline)
              const isMappedIdUlid = mappedId ? /^[0-9A-HJKMNP-TV-Z]{26}$/i.test(mappedId) : false
              const isMappedIdUuid = mappedId ? /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(mappedId) : false
              if (mappedId && !isMappedIdUlid && !isMappedIdUuid) {
                logger.warn(`Mapped parent ID ${mappedId} for ${containerData.name} is not a valid ULID or UUID. Setting to null to avoid validation error.`)
                parentContainerId = null
              } else {
                parentContainerId = mappedId
              }
            } else {
                // Parent was processed but mapping not set - parent may have failed to migrate
                logger.warn(`Parent container ${parentContainerId} was processed before ${containerData.name} (index ${parentIndex} < ${i}) but mapping not set. Parent may have failed to migrate. Setting parent to null.`)
                parentContainerId = null
              }
            }
          } else {
            // Parent comes after current container - this shouldn't happen with correct sorting
            logger.error(`Parent container ${parentContainerId} comes after ${containerData.name} in sorted order (index ${parentIndex} >= ${i}). Sorting may have failed. Setting parent to null.`)
            parentContainerId = null
          }
        } else {
          // Parent ID is a valid ULID/UUID but not in mapping - this shouldn't happen in normal flow
          // but could happen if ULID/UUID was passed directly. Check if parent exists in sorted containers.
          const parentIndex = sortedContainers.findIndex(c => c.id === parentContainerId)
          if (parentIndex === -1 || parentIndex >= i) {
            // Parent doesn't exist or comes after - set to null
            logger.warn(`Parent container ID ${parentContainerId} (ULID/UUID) not found or not yet processed. Setting parent to null for ${containerData.name}.`)
            parentContainerId = null
          }
        }
      }

      // M6 FIX: Validate container data before service call
      const containerDto = validateContainerDto({
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

      // Create container without items first
      const createdContainer = await gearContainerApiService.createContainer(containerDto)

      // CRITICAL FIX: Store ID mapping for child containers
      idMapping.set(localContainer.id, createdContainer.id)

      // Create items for this container
      if (items && items.length > 0) {
        for (const item of items) {
          try {
            // M6 FIX: Validate item data before service call
            const itemDto = validateItemDto({
              name: item.name,
              category: item.category,
              quantity: item.quantity ?? 1,
              weight: item.weight ?? 0,
              weightUnit: item.weightUnit ?? 'g',
              status: item.status,
              notes: item.notes ?? undefined,
              expirationDate: item.expirationDate ?? undefined,
              priority: item.priority ?? 'medium',
              brand: item.brand ?? undefined,
              color: item.color ?? undefined,
              price: item.price ?? undefined,
              url: item.url ?? undefined,
              quality: item.quality ?? undefined,
              wearable: item.wearable ?? undefined,
              consumable: item.consumable ?? undefined,
            })

            await gearItemApiService.createItem(createdContainer.id, itemDto)
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

