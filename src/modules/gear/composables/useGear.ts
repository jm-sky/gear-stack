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

  const createContainer = (data: ICreateContainerDto): IGearContainer => {
    return gearService.createContainer(data)
  }

  const updateContainer = (id: TUUID, data: IUpdateContainerDto): IGearContainer => {
    return gearService.updateContainer(id, data)
  }

  const deleteContainer = (id: TUUID): void => {
    gearService.deleteContainer(id)
  }

  const deleteAllContainers = (): void => {
    gearService.deleteAllContainers()
  }

  const getContainerById = (id: TUUID): IGearContainer | undefined => {
    return gearService.getContainerById(id)
  }

  const getRootContainers = (): IGearContainer[] => {
    return gearService.getRootContainers()
  }

  const getNestedContainers = (containerId: TUUID): IGearContainer[] => {
    return gearService.getNestedContainers(containerId)
  }

  // ========== Item Operations ==========

  const createItem = (containerId: TUUID, data: ICreateItemDto): IGearItem => {
    return gearService.createItem(containerId, data)
  }

  const updateItem = (containerId: TUUID, itemId: TUUID, data: IUpdateItemDto): IGearItem => {
    return gearService.updateItem(containerId, itemId, data)
  }

  const deleteItem = (containerId: TUUID, itemId: TUUID): void => {
    gearService.deleteItem(containerId, itemId)
  }

  const getItemById = (containerId: TUUID, itemId: TUUID): IGearItem | undefined => {
    return gearService.getItemById(containerId, itemId)
  }

  // ========== Business Logic ==========

  const calculateTotalWeight = (containerId: TUUID): number => {
    return gearService.calculateTotalWeight(containerId)
  }

  const calculateReadinessPercentage = (containerId: TUUID): number => {
    return gearService.calculateReadinessPercentage(containerId)
  }

  const calculateWeightLimitPercentage = (containerId: TUUID): number | null => {
    return gearService.calculateWeightLimitPercentage(containerId)
  }

  const isWeightLimitExceeded = (containerId: TUUID): boolean => {
    return gearService.isWeightLimitExceeded(containerId)
  }

  const getItemsByStatus = (containerId: TUUID, status: 'owned' | 'missing' | 'toBuy') => {
    return gearService.getItemsByStatus(containerId, status)
  }

  const getExpiredItems = (containerId: TUUID): IGearItem[] => {
    return gearService.getExpiredItems(containerId)
  }

  const getExpiringSoonItems = (containerId: TUUID, days: number = 30): IGearItem[] => {
    return gearService.getExpiringSoonItems(containerId, days)
  }

  const moveItem = (containerId: TUUID, itemId: TUUID, newContainerId: TUUID): void => {
    gearService.moveItem(containerId, itemId, newContainerId)
  }

  // ========== Import/Export ==========

  const exportData = (): string => {
    return gearService.exportData()
  }

  const importData = (json: string): void => {
    gearService.importData(json)
  }

  // ========== Clone/Duplicate ==========

  const cloneContainer = (
    containerId: TUUID,
    options: {
      newName: string
      includeNestedContainers?: boolean
      includePrices?: boolean
    },
  ): IGearContainer => {
    return gearService.cloneContainer(containerId, options)
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

