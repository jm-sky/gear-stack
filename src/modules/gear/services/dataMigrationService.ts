import { useGearStore } from '../store/useGearStore'
// modules/gear/services/dataMigrationService.ts
import { gearContainerApiService } from './gearContainerApiService'
import { gearContainerLocalService } from './gearContainerLocalService'
import { gearItemApiService } from './gearItemApiService'

const STORAGE_KEY = 'gear-stack:containers'

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
    console.log('No local data to migrate')
    return
  }

  console.log(`Migrating ${localContainers.length} containers to API...`)
  
  const store = useGearStore()
  const migratedContainers = []

  for (const localContainer of localContainers) {
    try {
      // Create container via API
      // Note: We need to extract items first, as API expects separate creation
      const { items, ...containerData } = localContainer
      
      // Create container without items first
      const createdContainer = await gearContainerApiService.createContainer({
        name: containerData.name,
        description: containerData.description,
        type: containerData.type,
        parentContainerId: containerData.parentContainerId,
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
            console.warn(`Failed to migrate item ${item.name} for container ${createdContainer.name}:`, itemError)
            // Continue with other items
          }
        }
      }

      migratedContainers.push(createdContainer)
      console.log(`Migrated container: ${createdContainer.name}`)
    } catch (error) {
      console.error(`Failed to migrate container ${localContainer.name}:`, error)
      // Continue with other containers
    }
  }

  // Update store with migrated containers
  if (migratedContainers.length > 0) {
    // Fetch all containers from API to get complete data
    const allContainers = await gearContainerApiService.getContainers()
    store.setContainers(allContainers)
    console.log(`Migration complete: ${migratedContainers.length} containers migrated`)
  }
}

/**
 * Check if data should be migrated and prompt user
 * This is a helper that can be used in UI to show migration prompt
 */
export function shouldPromptForMigration(): boolean {
  return hasLocalData()
}

