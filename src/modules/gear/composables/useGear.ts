import { computed } from 'vue'
import type {
  ICreateContainerDto,
  ICreateItemDto,
  IGearContainer,
  IGearItem,
  IUpdateContainerDto,
  IUpdateItemDto,
} from '../types/gear.types'
import { gearService } from '../services/gearService'
import { useGearStore } from '../store/useGearStore'
import type { TUUID } from '@/shared/types/base.type'

export function useGear() {
  const store = useGearStore()

  // Reactive state z store
  const containers = computed<IGearContainer[]>(() => store.getAllContainers)

  // ========== Container Operations ==========

  const createContainer = async (data: ICreateContainerDto): Promise<IGearContainer> => {
    return await gearService.createContainer(data)
  }

  const updateContainer = async (id: TUUID, data: IUpdateContainerDto): Promise<IGearContainer> => {
    return await gearService.updateContainer(id, data)
  }

  const deleteContainer = async (id: TUUID): Promise<void> => {
    await gearService.deleteContainer(id)
  }

  const deleteAllContainers = async (): Promise<void> => {
    await gearService.deleteAllContainers()
  }

  const getContainerById = async (id: TUUID): Promise<IGearContainer | undefined> => {
    try {
      return await gearService.getContainer(id)
    } catch {
      return undefined
    }
  }

  const getRootContainers = async (): Promise<IGearContainer[]> => {
    return await gearService.getRootContainers()
  }

  const getNestedContainers = async (containerId: TUUID): Promise<IGearContainer[]> => {
    return await gearService.getNestedContainers(containerId)
  }

  // ========== Item Operations ==========

  const createItem = async (containerId: TUUID, data: ICreateItemDto): Promise<IGearItem> => {
    return await gearService.createItem(containerId, data)
  }

  const updateItem = async (itemId: TUUID, data: IUpdateItemDto): Promise<IGearItem> => {
    return await gearService.updateItem(itemId, data)
  }

  const deleteItem = async (itemId: TUUID): Promise<void> => {
    await gearService.deleteItem(itemId)
  }

  const getItemById = async (containerId: TUUID, itemId: TUUID): Promise<IGearItem | undefined> => {
    return await gearService.getItemById(containerId, itemId)
  }

  // ========== Business Logic ==========

  const calculateTotalWeight = async (containerId: TUUID): Promise<number> => {
    return await gearService.calculateTotalWeight(containerId)
  }

  const calculateReadinessPercentage = async (containerId: TUUID): Promise<number> => {
    return await gearService.calculateReadinessPercentage(containerId)
  }

  const calculateWeightLimitPercentage = async (containerId: TUUID): Promise<number | null> => {
    return await gearService.calculateWeightLimitPercentage(containerId)
  }

  const isWeightLimitExceeded = async (containerId: TUUID): Promise<boolean> => {
    return await gearService.isWeightLimitExceeded(containerId)
  }

  const getItemsByStatus = async (containerId: TUUID, status: 'owned' | 'missing' | 'toBuy'): Promise<IGearItem[]> => {
    return await gearService.getItemsByStatus(containerId, status)
  }

  const getExpiredItems = async (containerId: TUUID): Promise<IGearItem[]> => {
    return await gearService.getExpiredItems(containerId)
  }

  const getExpiringSoonItems = async (containerId: TUUID, days: number = 30): Promise<IGearItem[]> => {
    return await gearService.getExpiringSoonItems(containerId, days)
  }

  const moveItem = async (containerId: TUUID, itemId: TUUID, newContainerId: TUUID): Promise<void> => {
    await gearService.moveItem(containerId, itemId, newContainerId)
  }

  // ========== Import/Export ==========

  const exportData = async (): Promise<string> => {
    return await gearService.exportData()
  }

  const importData = async (json: string): Promise<void> => {
    await gearService.importData(json)
  }

  // ========== Clone/Duplicate ==========

  const cloneContainer = async (
    containerId: TUUID,
    options: {
      newName: string
      includeNestedContainers?: boolean
      includePrices?: boolean
    },
  ): Promise<IGearContainer> => {
    return await gearService.cloneContainer(containerId, options)
  }

  return {
    // State
    containers,

    // Container Actions
    createContainer,
    updateContainer,
    deleteContainer,
    deleteAllContainers,
    getContainerById,
    getRootContainers,
    getNestedContainers,

    // Item Actions
    createItem,
    updateItem,
    deleteItem,
    getItemById,

    // Business Logic
    calculateTotalWeight,
    calculateReadinessPercentage,
    calculateWeightLimitPercentage,
    isWeightLimitExceeded,
    getItemsByStatus,
    getExpiredItems,
    getExpiringSoonItems,
    moveItem,

    // Import/Export
    exportData,
    importData,

    // Clone/Duplicate
    cloneContainer,
  }
}

