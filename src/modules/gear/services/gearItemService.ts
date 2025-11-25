import { useBackend } from '@/shared/composables/useBackend'
import { useGearStore } from '../store/useGearStore'
import { gearContainerApiService } from './gearContainerApiService'
import { gearItemApiService } from './gearItemApiService'
import { gearItemLocalService } from './gearItemLocalService'

/**
 * Gear Item Service Factory
 *
 * Returns appropriate service based on backend status and authentication.
 * When backend is enabled AND user is authenticated, uses API service and synchronizes with store.
 * Otherwise, uses localStorage service.
 */
export const gearItemService = () => {
  const { shouldUseAPI } = useBackend()
  
  if (shouldUseAPI.value) {
    // Wrap API service to sync store and localStorage as backup
    return {
      ...gearItemApiService,
      async createItem(containerId: Parameters<typeof gearItemApiService.createItem>[0], data: Parameters<typeof gearItemApiService.createItem>[1]) {
        try {
          const item = await gearItemApiService.createItem(containerId, data)
          // Refresh container from API to get updated items
          const container = await gearContainerApiService.getContainer(containerId)
          useGearStore().updateContainer(container)
          // Store automatically saves to localStorage via saveToStorage()
          return item
        } catch (error) {
          // Fallback to localStorage on API error
          console.warn('API failed, falling back to localStorage', error)
          return gearItemLocalService.createItem(containerId, data)
        }
      },
      async getItems(containerId: Parameters<typeof gearItemApiService.getItems>[0], skip = 0, limit = 100) {
        try {
          const items = await gearItemApiService.getItems(containerId, skip, limit)
          // Refresh container from API
          const container = await gearContainerApiService.getContainer(containerId)
          useGearStore().updateContainer(container)
          return items
        } catch (error) {
          // Fallback to localStorage on API error
          console.warn('API failed, falling back to localStorage', error)
          return gearItemLocalService.getItems(containerId, skip, limit)
        }
      },
      async updateItem(itemId: Parameters<typeof gearItemApiService.updateItem>[0], data: Parameters<typeof gearItemApiService.updateItem>[1]) {
        try {
          const item = await gearItemApiService.updateItem(itemId, data)
          // Find container and refresh it
          const store = useGearStore()
          const allContainers = store.getAllContainers
          for (const container of allContainers) {
            if (container.items.some(i => i.id === itemId)) {
              const updatedContainer = await gearContainerApiService.getContainer(container.id)
              store.updateContainer(updatedContainer)
              // Store automatically saves to localStorage via saveToStorage()
              break
            }
          }
          return item
        } catch (error) {
          // Fallback to localStorage on API error
          console.warn('API failed, falling back to localStorage', error)
          return gearItemLocalService.updateItem(itemId, data)
        }
      },
      async deleteItem(itemId: Parameters<typeof gearItemApiService.deleteItem>[0]) {
        try {
          await gearItemApiService.deleteItem(itemId)
          // Find container and refresh it
          const store = useGearStore()
          const allContainers = store.getAllContainers
          for (const container of allContainers) {
            if (container.items.some(i => i.id === itemId)) {
              const updatedContainer = await gearContainerApiService.getContainer(container.id)
              store.updateContainer(updatedContainer)
              // Also remove from localStorage
              gearItemLocalService.deleteItem(itemId).catch(err => {
                console.warn('Failed to remove item from localStorage backup:', err)
              })
              break
            }
          }
        } catch (error) {
          // Fallback to localStorage on API error
          console.warn('API failed, falling back to localStorage', error)
          await gearItemLocalService.deleteItem(itemId)
        }
      },
      // Delegate other methods
      getItem: gearItemApiService.getItem.bind(gearItemApiService),
      // Add method from local service that is not in API service
      getItemById: gearItemLocalService.getItemById.bind(gearItemLocalService),
      // Batch update order
      async batchUpdateOrder(items: Parameters<typeof gearItemApiService.batchUpdateOrder>[0]) {
        try {
          const updatedItems = await gearItemApiService.batchUpdateOrder(items)
          // Refresh container from API to get updated items
          const allContainers = useGearStore().getAllContainers
          for (const container of allContainers) {
            if (container.items.some(i => items.some(updated => updated.id === i.id))) {
              const updatedContainer = await gearContainerApiService.getContainer(container.id)
              useGearStore().updateContainer(updatedContainer)
              // Store automatically saves to localStorage via saveToStorage()
              break
            }
          }
          return updatedItems
        } catch (error) {
          // Fallback to localStorage on API error
          console.warn('API failed, falling back to localStorage', error)
          return gearItemLocalService.batchUpdateOrder(items)
        }
      },
    }
  }

  return gearItemLocalService
}

