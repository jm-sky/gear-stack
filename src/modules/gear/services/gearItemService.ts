import { config } from '@/shared/config/config'
import { useGearStore } from '../store/useGearStore'
import { gearContainerApiService } from './gearContainerApiService'
import { gearItemApiService } from './gearItemApiService'
import { gearItemLocalService } from './gearItemLocalService'

/**
 * Gear Item Service Factory
 *
 * Returns appropriate service based on feature flag.
 * When backend is enabled, uses API service and synchronizes with store.
 * When backend is disabled, uses localStorage service.
 */
export const gearItemService = () => {
  if (config.backend.enabled) {
    // Wrap API service to sync store
    return {
      ...gearItemApiService,
      async createItem(containerId: Parameters<typeof gearItemApiService.createItem>[0], data: Parameters<typeof gearItemApiService.createItem>[1]) {
        const item = await gearItemApiService.createItem(containerId, data)
        // Refresh container from API to get updated items
        const container = await gearContainerApiService.getContainer(containerId)
        useGearStore().updateContainer(container)
        return item
      },
      async getItems(containerId: Parameters<typeof gearItemApiService.getItems>[0], skip = 0, limit = 100) {
        const items = await gearItemApiService.getItems(containerId, skip, limit)
        // Refresh container from API
        const container = await gearContainerApiService.getContainer(containerId)
        useGearStore().updateContainer(container)
        return items
      },
      async updateItem(itemId: Parameters<typeof gearItemApiService.updateItem>[0], data: Parameters<typeof gearItemApiService.updateItem>[1]) {
        const item = await gearItemApiService.updateItem(itemId, data)
        // Find container and refresh it
        const store = useGearStore()
        const allContainers = store.getAllContainers
        for (const container of allContainers) {
          if (container.items.some(i => i.id === itemId)) {
            const updatedContainer = await gearContainerApiService.getContainer(container.id)
            store.updateContainer(updatedContainer)
            break
          }
        }
        return item
      },
      async deleteItem(itemId: Parameters<typeof gearItemApiService.deleteItem>[0]) {
        await gearItemApiService.deleteItem(itemId)
        // Find container and refresh it
        const store = useGearStore()
        const allContainers = store.getAllContainers
        for (const container of allContainers) {
          if (container.items.some(i => i.id === itemId)) {
            const updatedContainer = await gearContainerApiService.getContainer(container.id)
            store.updateContainer(updatedContainer)
            break
          }
        }
      },
      // Delegate other methods
      getItem: gearItemApiService.getItem.bind(gearItemApiService),
      // Add method from local service that is not in API service
      getItemById: gearItemLocalService.getItemById.bind(gearItemLocalService),
    }
  }

  return gearItemLocalService
}

