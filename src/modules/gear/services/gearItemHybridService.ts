import { logger } from '@/shared/utils/logger'
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
      logger.warn('API failed, falling back to localStorage', error)
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
      logger.warn('API failed, falling back to localStorage', error)
      return this.gearItemLocalService.getItems(containerId, skip, limit)
    }
  }

  async updateItem(itemId: TULID, data: IUpdateItemDto): Promise<IGearItem> {
    try {
      const store = useGearStore()
      // CRITICAL FIX: Get container ID BEFORE update to prevent race condition
      const containerId = store.getContainerIdByItemId(itemId)

      if (!containerId) {
        logger.warn('Container not found for item, falling back to localStorage', itemId)
        return this.gearItemLocalService.updateItem(itemId, data)
      }

      const item = await this.gearItemApiService.updateItem(itemId, data)

      // Refresh the correct container (no loop needed, no race condition)
      const updatedContainer = await gearContainerApiService.getContainer(containerId)
      store.updateContainer(updatedContainer)
      // Store automatically saves to localStorage via saveToStorage()

      return item
    } catch (error) {
      // Fallback to localStorage on API error
      logger.warn('API failed, falling back to localStorage', error)
      return this.gearItemLocalService.updateItem(itemId, data)
    }
  }

  async deleteItem(itemId: TULID): Promise<void> {
    try {
      const store = useGearStore()
      // CRITICAL FIX: Get container ID BEFORE deletion to prevent race condition
      const containerId = store.getContainerIdByItemId(itemId)

      if (!containerId) {
        logger.warn('Container not found for item, falling back to localStorage', itemId)
        return this.gearItemLocalService.deleteItem(itemId)
      }

      await this.gearItemApiService.deleteItem(itemId)

      // Refresh the correct container (no loop needed, no race condition)
      const updatedContainer = await gearContainerApiService.getContainer(containerId)
      store.updateContainer(updatedContainer)

      // Also remove from localStorage backup
      this.gearItemLocalService.deleteItem(itemId).catch(err => {
        logger.warn('Failed to remove item from localStorage backup:', err)
      })
    } catch (error) {
      // Fallback to localStorage on API error
      logger.warn('API failed, falling back to localStorage', error)
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
      const store = useGearStore()
      // CRITICAL FIX: Get container ID BEFORE batch update to prevent race condition
      // Assume all items in batch belong to same container (standard practice)
      const containerId = items.length > 0 ? store.getContainerIdByItemId(items[0]!.id) : undefined

      if (!containerId) {
        logger.warn('Container not found for items, falling back to localStorage')
        return this.gearItemLocalService.batchUpdateOrder(items)
      }

      const updatedItems = await this.gearItemApiService.batchUpdateOrder(items)

      // Refresh the correct container (no loop needed, no race condition)
      const updatedContainer = await gearContainerApiService.getContainer(containerId)
      store.updateContainer(updatedContainer)
      // Store automatically saves to localStorage via saveToStorage()

      return updatedItems
    } catch (error) {
      // Fallback to localStorage on API error
      logger.warn('API failed, falling back to localStorage', error)
      return this.gearItemLocalService.batchUpdateOrder(items)
    }
  }
}
