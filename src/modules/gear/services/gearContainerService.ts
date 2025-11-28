import { useBackend } from '@/shared/composables/useBackend'
import { useGearStore } from '../store/useGearStore'
import { gearContainerApiService } from './gearContainerApiService'
import { gearContainerLocalService } from './gearContainerLocalService'

/**
 * Gear Container Service Factory
 *
 * Returns appropriate service based on backend status and authentication.
 * When backend is enabled AND user is authenticated, uses API service and synchronizes with store.
 * Otherwise, uses localStorage service.
 */
export const gearContainerService = () => {
  const { shouldUseAPI } = useBackend()
  
  if (shouldUseAPI.value) {
    // Wrap API service to sync store and localStorage as backup
    return {
      ...gearContainerApiService,
      async createContainer(data: Parameters<typeof gearContainerApiService.createContainer>[0]) {
        try {
          const container = await gearContainerApiService.createContainer(data)
          const store = useGearStore()
          store.addContainer(container)
          // Store automatically saves to localStorage via saveToStorage()
          return container
        } catch (error) {
          // Fallback to localStorage on API error
          console.warn('API failed, falling back to localStorage', error)
          return gearContainerLocalService.createContainer(data)
        }
      },
      async updateContainer(id: Parameters<typeof gearContainerApiService.updateContainer>[0], data: Parameters<typeof gearContainerApiService.updateContainer>[1]) {
        try {
          const container = await gearContainerApiService.updateContainer(id, data)
          const store = useGearStore()
          store.updateContainer(container)
          // Store automatically saves to localStorage via saveToStorage()
          return container
        } catch (error) {
          // Fallback to localStorage on API error
          console.warn('API failed, falling back to localStorage', error)
          return gearContainerLocalService.updateContainer(id, data)
        }
      },
      async deleteContainer(id: Parameters<typeof gearContainerApiService.deleteContainer>[0]) {
        try {
          await gearContainerApiService.deleteContainer(id)
          useGearStore().removeContainer(id)
          // Also remove from localStorage
          gearContainerLocalService.deleteContainer(id).catch(err => {
            console.warn('Failed to remove container from localStorage backup:', err)
          })
        } catch (error) {
          // Fallback to localStorage on API error
          console.warn('API failed, falling back to localStorage', error)
          await gearContainerLocalService.deleteContainer(id)
        }
      },
      async getContainers(skip = 0, limit = 100) {
        try {
          const containers = await gearContainerApiService.getContainers(skip, limit)
          useGearStore().setContainers(containers)
          return containers
        } catch (error) {
          // Fallback to localStorage on API error
          console.warn('API failed, falling back to localStorage', error)
          return gearContainerLocalService.getContainers(skip, limit)
        }
      },
      async getContainer(id: Parameters<typeof gearContainerApiService.getContainer>[0]) {
        try {
          const container = await gearContainerApiService.getContainer(id)
          const store = useGearStore()
          const existing = store.getContainerById(id)
          if (existing) {
            store.updateContainer(container)
          } else {
            store.addContainer(container)
          }
          return container
        } catch (error) {
          // Fallback to localStorage on API error
          console.warn('API failed, falling back to localStorage', error)
          return gearContainerLocalService.getContainer(id)
        }
      },
      // Delegate statistics methods
      getContainerWeight: gearContainerApiService.getContainerWeight.bind(gearContainerApiService),
      getContainerReadiness: gearContainerApiService.getContainerReadiness.bind(gearContainerApiService),
      // Add methods from local service that are not in API service
      async deleteAllContainers() {
        const store = useGearStore()
        
        try {
          // Delete all containers via API using dedicated endpoint
          await gearContainerApiService.deleteAllContainers()
          
          // Clear store and localStorage after successful API deletion
          store.clearAllContainers()
        } catch (error) {
          // Fallback to localStorage on API error
          console.warn('API failed, falling back to localStorage', error)
          await gearContainerLocalService.deleteAllContainers()
        }
      },
      getAllContainers: gearContainerLocalService.getAllContainers.bind(gearContainerLocalService),
      getRootContainers: gearContainerLocalService.getRootContainers.bind(gearContainerLocalService),
      getNestedContainers: gearContainerLocalService.getNestedContainers.bind(gearContainerLocalService),
      calculateTotalWeight: gearContainerLocalService.calculateTotalWeight.bind(gearContainerLocalService),
      calculateReadinessPercentage: gearContainerLocalService.calculateReadinessPercentage.bind(gearContainerLocalService),
      calculateWeightLimitPercentage: gearContainerLocalService.calculateWeightLimitPercentage.bind(gearContainerLocalService),
      isWeightLimitExceeded: gearContainerLocalService.isWeightLimitExceeded.bind(gearContainerLocalService),
      getItemsByStatus: gearContainerLocalService.getItemsByStatus.bind(gearContainerLocalService),
      getExpiredItems: gearContainerLocalService.getExpiredItems.bind(gearContainerLocalService),
      getExpiringSoonItems: gearContainerLocalService.getExpiringSoonItems.bind(gearContainerLocalService),
      moveItem: gearContainerLocalService.moveItem.bind(gearContainerLocalService),
      exportData: gearContainerLocalService.exportData.bind(gearContainerLocalService),
      importData: gearContainerLocalService.importData.bind(gearContainerLocalService),
      cloneContainer: gearContainerLocalService.cloneContainer.bind(gearContainerLocalService),
      // Item Catalog Operations
      getAllItemsForCatalog: gearContainerLocalService.getAllItemsForCatalog.bind(gearContainerLocalService),
      getItemWithContainer: gearContainerLocalService.getItemWithContainer.bind(gearContainerLocalService),
    }
  }

  return gearContainerLocalService
}

