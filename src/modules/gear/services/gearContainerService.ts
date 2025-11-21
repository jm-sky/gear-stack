import { config } from '@/shared/config/config'
import { useGearStore } from '../store/useGearStore'
import { gearContainerApiService } from './gearContainerApiService'
import { gearContainerLocalService } from './gearContainerLocalService'

/**
 * Gear Container Service Factory
 *
 * Returns appropriate service based on feature flag.
 * When backend is enabled, uses API service and synchronizes with store.
 * When backend is disabled, uses localStorage service.
 */
export const gearContainerService = () => {
  if (config.backend.enabled) {
    // Wrap API service to sync store
    return {
      ...gearContainerApiService,
      async createContainer(data: Parameters<typeof gearContainerApiService.createContainer>[0]) {
        const container = await gearContainerApiService.createContainer(data)
        useGearStore().addContainer(container)
        return container
      },
      async updateContainer(id: Parameters<typeof gearContainerApiService.updateContainer>[0], data: Parameters<typeof gearContainerApiService.updateContainer>[1]) {
        const container = await gearContainerApiService.updateContainer(id, data)
        useGearStore().updateContainer(container)
        return container
      },
      async deleteContainer(id: Parameters<typeof gearContainerApiService.deleteContainer>[0]) {
        await gearContainerApiService.deleteContainer(id)
        useGearStore().removeContainer(id)
      },
      async getContainers(skip = 0, limit = 100) {
        const containers = await gearContainerApiService.getContainers(skip, limit)
        useGearStore().setContainers(containers)
        return containers
      },
      async getContainer(id: Parameters<typeof gearContainerApiService.getContainer>[0]) {
        const container = await gearContainerApiService.getContainer(id)
        const store = useGearStore()
        const existing = store.getContainerById(id)
        if (existing) {
          store.updateContainer(container)
        } else {
          store.addContainer(container)
        }
        return container
      },
      // Delegate statistics methods
      getContainerWeight: gearContainerApiService.getContainerWeight.bind(gearContainerApiService),
      getContainerReadiness: gearContainerApiService.getContainerReadiness.bind(gearContainerApiService),
      // Add methods from local service that are not in API service
      deleteAllContainers: gearContainerLocalService.deleteAllContainers.bind(gearContainerLocalService),
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
    }
  }

  return gearContainerLocalService
}

