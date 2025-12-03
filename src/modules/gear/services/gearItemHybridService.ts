import type { ICreateItemDto, IGearItem, IGearItemService, IUpdateItemDto } from '../types/gear.types'
import type { GearItemLocalService } from './gearItemLocalService'
import { useGearStore } from '../store/useGearStore'
import { gearContainerApiService } from './gearContainerApiService'
import { GearItemApiService } from './gearItemApiService'
import type { TULID } from '@/shared/types/base.type'

export class GearItemHybridService implements IGearItemService {
  private readonly gearItemLocalService: GearItemLocalService
  private readonly gearItemApiService: GearItemApiService

  constructor(gearItemLocalService: GearItemLocalService, gearItemApiService: GearItemApiService) {
    this.gearItemLocalService = gearItemLocalService
    this.gearItemApiService = gearItemApiService
  }

  async createItem(containerId: TULID, data: ICreateItemDto): Promise<IGearItem> {
    try {
      const item = await this.gearItemApiService.createItem(containerId, data)
      // Refresh container from API to get updated items
      const container = await gearContainerApiService.getContainer(containerId)
      useGearStore().updateContainer(container)
      // Store automatically saves to localStorage via saveToStorage()
      return item
    } catch (error) {
      // Fallback to localStorage on API error
      console.warn('API failed, falling back to localStorage', error)
      return this.gearItemLocalService.createItem(containerId, data)
    }
  }

  async getItems(containerId: TULID, skip = 0, limit = 100): Promise<IGearItem[]> {
    try {
      const items = await this.gearItemApiService.getItems(containerId, skip, limit)
      // Refresh container from API
      const container = await gearContainerApiService.getContainer(containerId)
      useGearStore().updateContainer(container)
      return items
    } catch (error) {
      // Fallback to localStorage on API error
      console.warn('API failed, falling back to localStorage', error)
      return this.gearItemLocalService.getItems(containerId, skip, limit)
    }
  }

  async updateItem(itemId: TULID, data: IUpdateItemDto): Promise<IGearItem> {
    try {
      const item = await this.gearItemApiService.updateItem(itemId, data)
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
      return this.gearItemLocalService.updateItem(itemId, data)
    }
  }

  async deleteItem(itemId: TULID): Promise<void> {
    try {
      await this.gearItemApiService.deleteItem(itemId)
      // Find container and refresh it
      const store = useGearStore()
      const allContainers = store.getAllContainers
      for (const container of allContainers) {
        if (container.items.some(i => i.id === itemId)) {
          const updatedContainer = await gearContainerApiService.getContainer(container.id)
          store.updateContainer(updatedContainer)
          // Also remove from localStorage
          this.gearItemLocalService.deleteItem(itemId).catch(err => {
            console.warn('Failed to remove item from localStorage backup:', err)
          })
          break
        }
      }
    } catch (error) {
      // Fallback to localStorage on API error
      console.warn('API failed, falling back to localStorage', error)
      await this.gearItemLocalService.deleteItem(itemId)
    }
  }

  async getItem(itemId: TULID): Promise<IGearItem> {
    return this.gearItemApiService.getItem(itemId)
  }

  async getItemFromContainer(containerId: TULID, itemId: TULID): Promise<IGearItem | undefined> {
    return this.gearItemApiService.getItemFromContainer(containerId, itemId)
  }

  // Batch update order
  async batchUpdateOrder(items: IGearItem[]): Promise<IGearItem[]> {
    try {
      const updatedItems = await this.gearItemApiService.batchUpdateOrder(items)
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
      return this.gearItemLocalService.batchUpdateOrder(items)
    }
  }
}
