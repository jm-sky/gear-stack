import type {
  ICreateContainerDto,
  ICreateItemDto,
  IGearContainer,
  IGearItem,
  IGearServiceExtended,
  IUpdateContainerDto,
  IUpdateItemDto,
  TGearItemStatus,
} from '../types/gear.types'
import { useGearStore } from '../store/useGearStore'
import { getAllNestedContainers, getRootContainers, wouldCreateCircularReference } from '../utils/containerNesting'
import { convertToGrams } from '../utils/formatWeight'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Gear Service (LocalStorage implementation)
 *
 * Provides methods to interact with gear data stored in localStorage.
 * Implements IGearServiceExtended interface for localStorage-based operations.
 */
class GearService implements IGearServiceExtended {
  private get store() {
    return useGearStore()
  }

  // ========== Containers CRUD ==========

  async createContainer(data: ICreateContainerDto): Promise<IGearContainer> {
    // Validate parent relationship if provided
    if (data.parentContainerId) {
      const allContainers = this.store.getAllContainers
      const newContainerId = crypto.randomUUID() // Generate ID before validation

      if (wouldCreateCircularReference(newContainerId, data.parentContainerId, allContainers)) {
        throw new Error('Cannot create container: would create circular reference')
      }

      // Verify parent exists
      const parent = this.store.getContainerById(data.parentContainerId)
      if (!parent) {
        throw new Error(`Parent container with id ${data.parentContainerId} not found`)
      }
    }

    const now = new Date().toISOString()
    const container: IGearContainer = {
      id: crypto.randomUUID(),
      name: data.name,
      description: data.description,
      type: data.type,
      color: data.color,
      parentContainerId: data.parentContainerId,
      brand: data.brand,
      price: data.price,
      weight: data.weight,
      weightUnit: data.weightUnit,
      url: data.url,
      items: [],
      createdAt: now,
      updatedAt: now,
    }

    this.store.addContainer(container)
    return Promise.resolve(container)
  }

  async updateContainer(id: TUUID, data: IUpdateContainerDto): Promise<IGearContainer> {
    const container = this.store.getContainerById(id)
    if (!container) {
      throw new Error(`Container with id ${id} not found`)
    }

    // Validate parent relationship change if provided
    if (data.parentContainerId !== undefined) {
      const allContainers = this.store.getAllContainers

      if (data.parentContainerId) {
        if (wouldCreateCircularReference(id, data.parentContainerId, allContainers)) {
          throw new Error('Cannot update container: would create circular reference')
        }

        // Verify parent exists
        const parent = this.store.getContainerById(data.parentContainerId)
        if (!parent) {
          throw new Error(`Parent container with id ${data.parentContainerId} not found`)
        }
      }
    }

    const updated: IGearContainer = {
      ...container,
      ...data,
      updatedAt: new Date().toISOString(),
    }

    this.store.updateContainer(updated)
    return Promise.resolve(updated)
  }

  async deleteContainer(id: TUUID): Promise<void> {
    this.store.removeContainer(id)
    return Promise.resolve()
  }

  async getContainers(skip = 0, limit = 100): Promise<IGearContainer[]> {
    const all = this.store.getAllContainers
    return Promise.resolve(all.slice(skip, skip + limit))
  }

  async getContainer(id: TUUID): Promise<IGearContainer> {
    const container = this.store.getContainerById(id)
    if (!container) {
      throw new Error(`Container with id ${id} not found`)
    }
    return Promise.resolve(container)
  }

  async deleteAllContainers(): Promise<void> {
    this.store.clearAllContainers()
    return Promise.resolve()
  }

  async getAllContainers(): Promise<IGearContainer[]> {
    return Promise.resolve(this.store.getAllContainers)
  }

  async getRootContainers(): Promise<IGearContainer[]> {
    return Promise.resolve(getRootContainers(this.store.getAllContainers))
  }

  async getNestedContainers(containerId: TUUID): Promise<IGearContainer[]> {
    return Promise.resolve(getAllNestedContainers(containerId, this.store.getAllContainers))
  }

  // ========== Items CRUD ==========

  async createItem(containerId: TUUID, data: ICreateItemDto): Promise<IGearItem> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      throw new Error(`Container with id ${containerId} not found`)
    }

    const now = new Date().toISOString()
    const item: IGearItem = {
      id: crypto.randomUUID(),
      name: data.name,
      category: data.category,
      quantity: data.quantity,
      weight: data.weight,
      weightUnit: data.weightUnit,
      notes: data.notes,
      expirationDate: data.expirationDate,
      priority: data.priority,
      status: data.status,
      containerId: data.containerId && data.containerId.trim() !== '' ? data.containerId : undefined, // Reference to nested container
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
    // In localStorage, we need to search through all containers
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
    // Find the container containing this item
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
      url: data.url ?? existingItem.url,
      brand: data.brand ?? existingItem.brand,
      color: data.color ?? existingItem.color,
      quality: data.quality ?? existingItem.quality,
      containerId: data.containerId !== undefined && data.containerId !== null && data.containerId.trim() !== '' ? data.containerId : (data.containerId === '' ? undefined : existingItem.containerId),
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
    // Find the container containing this item
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

  // ========== Statistics Operations ==========

  async getContainerWeight(containerId: TUUID): Promise<{ grams: number; kilograms: number }> {
    const grams = await this.calculateTotalWeight(containerId)
    return Promise.resolve({
      grams,
      kilograms: grams / 1000,
    })
  }

  async getContainerReadiness(containerId: TUUID): Promise<{
    totalItems: number
    ownedItems: number
    missingItems: number
    toBuyItems: number
    readinessPercentage: number
  }> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      throw new Error(`Container with id ${containerId} not found`)
    }

    const totalItems = container.items.length
    const ownedItems = container.items.filter(item => item.status === 'owned').length
    const missingItems = container.items.filter(item => item.status === 'missing').length
    const toBuyItems = container.items.filter(item => item.status === 'toBuy').length
    const readinessPercentage = totalItems > 0 ? Math.round((ownedItems / totalItems) * 100) : 0

    return Promise.resolve({
      totalItems,
      ownedItems,
      missingItems,
      toBuyItems,
      readinessPercentage,
    })
  }

  // ========== Business Logic ==========

  async calculateTotalWeight(containerId: TUUID): Promise<number> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return Promise.resolve(0)
    }

    // Start with container's own weight (if defined)
    let totalWeight = 0
    if (container.weight !== undefined && container.weightUnit) {
      totalWeight = convertToGrams(container.weight, container.weightUnit)
    }

    // Add weight of direct items
    for (const item of container.items) {
      // If item is a nested container, calculate its total weight recursively
      if (item.containerId) {
        const nestedContainerWeight = await this.calculateTotalWeight(item.containerId)
        totalWeight += nestedContainerWeight * item.quantity
      } else {
        // Regular item weight
        const weightInGrams = convertToGrams(item.weight, item.weightUnit ?? 'g')
        totalWeight += weightInGrams * item.quantity
      }
    }

    return Promise.resolve(totalWeight)
  }

  async calculateReadinessPercentage(containerId: TUUID): Promise<number> {
    const container = this.store.getContainerById(containerId)
    if (!container || container.items.length === 0) {
      return 0
    }

    const ownedItems = container.items.filter(item => item.status === 'owned').length
    return Promise.resolve(Math.round((ownedItems / container.items.length) * 100))
  }

  async calculateWeightLimitPercentage(containerId: TUUID): Promise<number | null> {
    const container = this.store.getContainerById(containerId)
    if (!container || !container.maxWeight) {
      return null
    }

    const totalWeight = await this.calculateTotalWeight(containerId)
    const maxWeightInGrams = convertToGrams(container.maxWeight, container.maxWeightUnit ?? 'g')

    if (maxWeightInGrams === 0) {
      return Promise.resolve(0)
    }

    return Promise.resolve(Math.round((totalWeight / maxWeightInGrams) * 100))
  }

  async isWeightLimitExceeded(containerId: TUUID): Promise<boolean> {
    const percentage = await this.calculateWeightLimitPercentage(containerId)
    return Promise.resolve(percentage !== null && percentage > 100)
  }

  async getItemsByStatus(containerId: TUUID, status: TGearItemStatus): Promise<IGearItem[]> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return []
    }

    return Promise.resolve(container.items.filter(item => item.status === status))
  }

  async getExpiredItems(containerId: TUUID): Promise<IGearItem[]> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return []
    }

    const now = new Date()

    return Promise.resolve(container.items.filter(item => {
      if (!item.expirationDate) {
        return false
      }

      const expirationDate = new Date(item.expirationDate)
      return expirationDate < now
    }))
  }

  async getExpiringSoonItems(containerId: TUUID, days: number = 30): Promise<IGearItem[]> {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return []
    }

    const now = new Date()
    const futureDate = new Date()
    futureDate.setDate(now.getDate() + days)

    return Promise.resolve(container.items.filter(item => {
      if (!item.expirationDate) {
        return false
      }

      const expirationDate = new Date(item.expirationDate)
      return expirationDate >= now && expirationDate <= futureDate
    }))
  }

  async moveItem(containerId: TUUID, itemId: TUUID, newContainerId: TUUID): Promise<void> {
    const sourceContainer = this.store.getContainerById(containerId)
    const targetContainer = this.store.getContainerById(newContainerId)

    if (!sourceContainer || !targetContainer) {
      throw new Error('Source or target container not found')
    }

    const item = sourceContainer.items.find(i => i.id === itemId)
    if (!item) {
      throw new Error(`Item with id ${itemId} not found`)
    }

    // Usuń z źródłowego kontenera
    const updatedSource: IGearContainer = {
      ...sourceContainer,
      items: sourceContainer.items.filter(i => i.id !== itemId),
      updatedAt: new Date().toISOString(),
    }

    // Dodaj do docelowego kontenera
    const updatedTarget: IGearContainer = {
      ...targetContainer,
      items: [...targetContainer.items, item],
      updatedAt: new Date().toISOString(),
    }

    this.store.updateContainer(updatedSource)
    this.store.updateContainer(updatedTarget)
    return Promise.resolve()
  }

  // ========== Import/Export ==========

  async exportData(): Promise<string> {
    const containers = this.store.getAllContainers
    return Promise.resolve(JSON.stringify(containers, null, 2))
  }

  async importData(json: string): Promise<void> {
    try {
      const containers: IGearContainer[] = JSON.parse(json)
      // Walidacja podstawowa
      if (!Array.isArray(containers)) {
        throw new Error('Invalid data format')
      }
      this.store.setContainers(containers)
      return Promise.resolve()
    } catch (error) {
      throw new Error(`Failed to import data: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }
}

export const gearService = new GearService()

