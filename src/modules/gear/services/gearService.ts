import type {
  ICreateContainerDto,
  ICreateItemDto,
  IGearContainer,
  IGearItem,
  IUpdateContainerDto,
  IUpdateItemDto,
  TGearItemStatus,
} from '../types/gear.types'
import { useGearStore } from '../store/useGearStore'
import { getAllNestedContainers, getRootContainers, wouldCreateCircularReference } from '../utils/containerNesting'
import { convertToGrams } from '../utils/formatWeight'
import type { TUUID } from '@/shared/types/base.type'

class GearService {
  private get store() {
    return useGearStore()
  }

  // ========== Containers CRUD ==========

  createContainer(data: ICreateContainerDto): IGearContainer {
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
      items: [],
      createdAt: now,
      updatedAt: now,
    }

    this.store.addContainer(container)
    return container
  }

  updateContainer(id: TUUID, data: IUpdateContainerDto): IGearContainer {
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
    return updated
  }

  deleteContainer(id: TUUID): void {
    this.store.removeContainer(id)
  }

  getContainerById(id: TUUID): IGearContainer | undefined {
    return this.store.getContainerById(id)
  }

  getAllContainers(): IGearContainer[] {
    return this.store.getAllContainers
  }

  getRootContainers(): IGearContainer[] {
    return getRootContainers(this.store.getAllContainers)
  }

  getNestedContainers(containerId: TUUID): IGearContainer[] {
    return getAllNestedContainers(containerId, this.store.getAllContainers)
  }

  // ========== Items CRUD ==========

  createItem(containerId: TUUID, data: ICreateItemDto): IGearItem {
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
    return item
  }

  updateItem(containerId: TUUID, itemId: TUUID, data: IUpdateItemDto): IGearItem {
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
    return updatedItem
  }

  deleteItem(containerId: TUUID, itemId: TUUID): void {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      throw new Error(`Container with id ${containerId} not found`)
    }

    const updatedContainer: IGearContainer = {
      ...container,
      items: container.items.filter(item => item.id !== itemId),
      updatedAt: new Date().toISOString(),
    }

    this.store.updateContainer(updatedContainer)
  }

  getItemById(containerId: TUUID, itemId: TUUID): IGearItem | undefined {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return undefined
    }

    return container.items.find(item => item.id === itemId)
  }

  // ========== Business Logic ==========

  calculateTotalWeight(containerId: TUUID): number {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return 0
    }

    // Calculate weight of direct items
    const totalWeight = container.items.reduce((total, item) => {
      // If item is a nested container, calculate its total weight recursively
      if (item.containerId) {
        const nestedContainerWeight = this.calculateTotalWeight(item.containerId)
        return total + nestedContainerWeight * item.quantity
      }
      
      // Regular item weight
      const weightInGrams = convertToGrams(item.weight, item.weightUnit ?? 'g')
      return total + weightInGrams * item.quantity
    }, 0)

    return totalWeight
  }

  calculateReadinessPercentage(containerId: TUUID): number {
    const container = this.store.getContainerById(containerId)
    if (!container || container.items.length === 0) {
      return 0
    }

    const ownedItems = container.items.filter(item => item.status === 'owned').length
    return Math.round((ownedItems / container.items.length) * 100)
  }

  getItemsByStatus(containerId: TUUID, status: TGearItemStatus): IGearItem[] {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return []
    }

    return container.items.filter(item => item.status === status)
  }

  getExpiredItems(containerId: TUUID): IGearItem[] {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return []
    }

    const now = new Date()

    return container.items.filter(item => {
      if (!item.expirationDate) {
        return false
      }

      const expirationDate = new Date(item.expirationDate)
      return expirationDate < now
    })
  }

  getExpiringSoonItems(containerId: TUUID, days: number = 30): IGearItem[] {
    const container = this.store.getContainerById(containerId)
    if (!container) {
      return []
    }

    const now = new Date()
    const futureDate = new Date()
    futureDate.setDate(now.getDate() + days)

    return container.items.filter(item => {
      if (!item.expirationDate) {
        return false
      }

      const expirationDate = new Date(item.expirationDate)
      return expirationDate >= now && expirationDate <= futureDate
    })
  }

  moveItem(containerId: TUUID, itemId: TUUID, newContainerId: TUUID): void {
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
  }

  // ========== Import/Export ==========

  exportData(): string {
    const containers = this.store.getAllContainers
    return JSON.stringify(containers, null, 2)
  }

  importData(json: string): void {
    try {
      const containers: IGearContainer[] = JSON.parse(json)
      // Walidacja podstawowa
      if (!Array.isArray(containers)) {
        throw new Error('Invalid data format')
      }
      this.store.setContainers(containers)
    } catch (error) {
      throw new Error(`Failed to import data: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }
}

export const gearService = new GearService()

