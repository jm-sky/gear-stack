import type {
  ICreateItemDto,
  IGearContainer,
  IGearItem,
  IUpdateItemDto,
} from '../types/gear.types'
import { useGearStore } from '../store/useGearStore'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Gear Item Local Service (LocalStorage implementation)
 *
 * Provides methods to interact with item data stored in localStorage.
 * Pure implementation without feature flag logic.
 */
class GearItemLocalService {
  private get store() {
    return useGearStore()
  }

  // ========== Items CRUD ==========

  async createItem(containerId: TUUID, data: ICreateItemDto): Promise<IGearItem> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      throw new Error(`Container with id ${containerId} not found`)
    }

    const now = new Date().toISOString()
    
    // Calculate order: use provided order or assign max order + 1
    let order: number
    if (data.order !== undefined && data.order !== null) {
      order = data.order
    } else {
      const maxOrder = container.items.length > 0
        ? Math.max(...container.items.map(i => i.order ?? -1), -1)
        : -1
      order = maxOrder + 1
    }
    
    const item: IGearItem = {
      id: data.id ?? crypto.randomUUID(), // Use provided UUID if available, otherwise generate new one
      linkedItemId: data.linkedItemId, // Reference to original item when linking
      name: data.name,
      category: data.category,
      quantity: data.quantity,
      weight: data.weight,
      weightUnit: data.weightUnit,
      notes: data.notes,
      expirationDate: data.expirationDate,
      priority: data.priority,
      status: data.status,
      price: data.price,
      url: data.url,
      brand: data.brand,
      color: data.color,
      quality: data.quality,
      wearable: data.wearable,
      consumable: data.consumable,
      containerId: data.containerId && data.containerId.trim() !== '' ? data.containerId : undefined,
      order,
      createdAt: now,
      updatedAt: now,
    }

    const updatedContainer: IGearContainer = {
      ...container,
      items: [...container.items, item],
      updatedAt: now,
    }

    this.store.updateContainer(updatedContainer)
    return Promise.resolve(item)
  }

  async getItems(containerId: TUUID, skip = 0, limit = 100): Promise<IGearItem[]> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      throw new Error(`Container with id ${containerId} not found`)
    }
    return Promise.resolve(container.items.slice(skip, skip + limit))
  }

  async getItem(itemId: TUUID): Promise<IGearItem> {
    const allContainers = this.store.getAllContainers
    for (const container of allContainers) {
      const item = container.items.find(i => i.id === itemId)
      if (item) {
        return Promise.resolve(item)
      }
    }
    throw new Error(`Item with id ${itemId} not found`)
  }

  async updateItem(itemId: TUUID, data: IUpdateItemDto): Promise<IGearItem> {
    const allContainers = this.store.getAllContainers
    for (const container of allContainers) {
      const itemIndex = container.items.findIndex(item => item.id === itemId)
      if (itemIndex !== -1) {
        return this.updateItemInContainer(container.id, itemId, data)
      }
    }
    throw new Error(`Item with id ${itemId} not found`)
  }

  private async updateItemInContainer(containerId: TUUID, itemId: TUUID, data: IUpdateItemDto): Promise<IGearItem> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      throw new Error(`Container with id ${containerId} not found`)
    }

    const itemIndex = container.items.findIndex(item => item.id === itemId)
    if (itemIndex === -1) {
      throw new Error(`Item with id ${itemId} not found in container ${containerId}`)
    }

    const existingItem = container.items[itemIndex]
    if (!existingItem) {
      throw new Error(`Item with id ${itemId} not found in container ${containerId}`)
    }

    const updatedItem: IGearItem = {
      id: existingItem.id,
      linkedItemId: existingItem.linkedItemId,
      name: data.name ?? existingItem.name,
      category: data.category ?? existingItem.category,
      quantity: data.quantity ?? existingItem.quantity,
      weight: data.weight ?? existingItem.weight,
      weightUnit: data.weightUnit ?? existingItem.weightUnit ?? 'g',
      notes: data.notes ?? existingItem.notes,
      expirationDate: data.expirationDate ?? existingItem.expirationDate,
      priority: data.priority ?? existingItem.priority,
      status: data.status ?? existingItem.status,
      price: data.price ?? existingItem.price,
      currency: data.currency ?? existingItem.currency,
      url: data.url ?? existingItem.url,
      brand: data.brand ?? existingItem.brand,
      color: data.color ?? existingItem.color,
      quality: data.quality ?? existingItem.quality,
      wearable: data.wearable ?? existingItem.wearable,
      consumable: data.consumable ?? existingItem.consumable,
      containerId: data.containerId !== undefined && data.containerId !== null && data.containerId.trim() !== '' ? data.containerId : (data.containerId === '' ? undefined : existingItem.containerId),
      order: data.order !== undefined ? data.order : existingItem.order,
      createdAt: existingItem.createdAt,
      updatedAt: new Date().toISOString(),
    }

    const updatedContainer: IGearContainer = {
      ...container,
      items: [
        ...container.items.slice(0, itemIndex),
        updatedItem,
        ...container.items.slice(itemIndex + 1),
      ],
      updatedAt: new Date().toISOString(),
    }

    this.store.updateContainer(updatedContainer)
    return Promise.resolve(updatedItem)
  }

  async deleteItem(itemId: TUUID): Promise<void> {
    const allContainers = this.store.getAllContainers
    for (const container of allContainers) {
      const itemIndex = container.items.findIndex(item => item.id === itemId)
      if (itemIndex !== -1) {
        const updatedContainer: IGearContainer = {
          ...container,
          items: container.items.filter(i => i.id !== itemId),
          updatedAt: new Date().toISOString(),
        }
        this.store.updateContainer(updatedContainer)
        return Promise.resolve()
      }
    }
    throw new Error(`Item with id ${itemId} not found`)
  }

  async getItemById(containerId: TUUID, itemId: TUUID): Promise<IGearItem | undefined> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return Promise.resolve(undefined)
    }

    return Promise.resolve(container.items.find(item => item.id === itemId))
  }

  /**
   * Batch update items order
   * Updates multiple items' order field in a single operation
   */
  async batchUpdateOrder(items: IGearItem[]): Promise<IGearItem[]> {
    if (items.length === 0) {
      return Promise.resolve([])
    }

    // Group items by container
    const itemsByContainer = new Map<TUUID, IGearItem[]>()
    for (const item of items) {
      // Find container for this item
      const allContainers = this.store.getAllContainers
      for (const container of allContainers) {
        const existingItem = container.items.find(i => i.id === item.id)
        if (existingItem) {
          const containerId = container.id
          if (!itemsByContainer.has(containerId)) {
            itemsByContainer.set(containerId, [])
          }
          itemsByContainer.get(containerId)!.push(item)
          break
        }
      }
    }

    const updatedItems: IGearItem[] = []
    const now = new Date().toISOString()

    // Update each container
    for (const [containerId, containerItems] of itemsByContainer.entries()) {
      const container = this.store.getContainerById(containerId)
      if (!container) continue

      // Create a map of item updates
      const itemUpdates = new Map(containerItems.map(item => [item.id, item]))

      // Update items in container
      const updatedContainerItems = container.items.map(existingItem => {
        const update = itemUpdates.get(existingItem.id)
        if (update) {
          const updated: IGearItem = {
            ...existingItem,
            order: update.order,
            updatedAt: now,
          }
          updatedItems.push(updated)
          return updated
        }
        return existingItem
      })

      const updatedContainer: IGearContainer = {
        ...container,
        items: updatedContainerItems,
        updatedAt: now,
      }

      this.store.updateContainer(updatedContainer)
    }

    return Promise.resolve(updatedItems)
  }
}

export const gearItemLocalService = new GearItemLocalService()

