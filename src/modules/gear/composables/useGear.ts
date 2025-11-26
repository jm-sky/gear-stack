import { computed } from 'vue'
import { useBackend } from '@/shared/composables/useBackend'
import type {
  ICreateContainerDto,
  ICreateItemDto,
  IGearContainer,
  IGearItem,
  IUpdateContainerDto,
  IUpdateItemDto,
} from '../types/gear.types'
import type { IItemWithContainer } from '../utils/allItemsColumns'
import { gearContainerService } from '../services/gearContainerService'
import { gearItemService } from '../services/gearItemService'
import { useGearStore } from '../store/useGearStore'
import type { TUUID } from '@/shared/types/base.type'

export function useGear() {
  const store = useGearStore()

  // Reactive state z store
  const containers = computed<IGearContainer[]>(() => store.getAllContainers)

  // ========== Container Operations ==========

  const createContainer = async (data: ICreateContainerDto): Promise<IGearContainer> => {
    return await gearContainerService().createContainer(data)
  }

  const updateContainer = async (id: TUUID, data: IUpdateContainerDto): Promise<IGearContainer> => {
    return await gearContainerService().updateContainer(id, data)
  }

  const deleteContainer = async (id: TUUID): Promise<void> => {
    await gearContainerService().deleteContainer(id)
  }

  const deleteAllContainers = async (): Promise<void> => {
    await gearContainerService().deleteAllContainers()
  }

  const getContainerById = async (id: TUUID): Promise<IGearContainer | undefined> => {
    try {
      return await gearContainerService().getContainer(id)
    } catch {
      return undefined
    }
  }

  const getRootContainers = async (): Promise<IGearContainer[]> => {
    return await gearContainerService().getRootContainers()
  }

  const getNestedContainers = async (containerId: TUUID): Promise<IGearContainer[]> => {
    return await gearContainerService().getNestedContainers(containerId)
  }

  // ========== Item Operations ==========

  const createItem = async (containerId: TUUID, data: ICreateItemDto): Promise<IGearItem> => {
    return await gearItemService().createItem(containerId, data)
  }

  const updateItem = async (itemId: TUUID, data: IUpdateItemDto): Promise<IGearItem> => {
    const service = gearItemService()
    const { shouldUseAPI } = useBackend()

    // Backend automatycznie propaguje zmiany do wszystkich linkowanych itemów
    // Więc dla API wystarczy jedno wywołanie
    if (shouldUseAPI.value) {
      return await service.updateItem(itemId, data)
    }

    // Dla localStorage musimy ręcznie zaktualizować wszystkie linkowane itemy
    const allContainers = store.getAllContainers
    let masterItemId: TUUID | null = null

    for (const container of allContainers) {
      const found = container.items.find(item => item.id === itemId)
      if (found) {
        masterItemId = (found.linkedItemId as TUUID | null) ?? found.id
        break
      }
    }

    // Fallback: jeśli nie znaleziono w store, pobierz z serwisu
    if (!masterItemId) {
      try {
        const current = await service.getItem(itemId)
        masterItemId = (current.linkedItemId as TUUID | null) ?? current.id
      } catch {
        // Jeśli z jakiegoś powodu nie uda się pobrać, zaktualizuj tylko pojedynczy item
        return await service.updateItem(itemId, data)
      }
    }

    // Znajdź wszystkie itemy należące do tej samej grupy linkowania:
    // - sam "master" (id === masterItemId)
    // - wszystkie, które wskazują na niego przez linkedItemId
    const targetIds = new Set<TUUID>()

    for (const container of allContainers) {
      for (const item of container.items) {
        if (item.id === masterItemId || item.linkedItemId === masterItemId) {
          targetIds.add(item.id)
        }
      }
    }

    // Jeśli nie znaleziono innych powiązań, aktualizujemy tylko wskazany item
    if (targetIds.size === 0 || (targetIds.size === 1 && targetIds.has(itemId))) {
      return await service.updateItem(itemId, data)
    }

    // Zaktualizuj wszystkie powiązane itemy (ta sama paczka zmian)
    const updatedItems: IGearItem[] = []
    for (const targetId of targetIds) {
      // Reuse tego samego payloadu dla wszystkich referencji
      // (zgodnie z wymaganiem: zmiana w jednym → zmiana we wszystkich)

      const updated = await service.updateItem(targetId, data)
      updatedItems.push(updated)
    }

    // Zwróć zaktualizowany item odpowiadający oryginalnemu itemId (albo pierwszy z listy)
    return updatedItems.find(item => item.id === itemId) ?? updatedItems[0]!
  }

  const deleteItem = async (itemId: TUUID): Promise<void> => {
    await gearItemService().deleteItem(itemId)
  }

  const getItemById = async (containerId: TUUID, itemId: TUUID): Promise<IGearItem | undefined> => {
    return await gearItemService().getItemById(containerId, itemId)
  }

  // ========== Business Logic ==========

  const calculateTotalWeight = async (containerId: TUUID): Promise<number> => {
    return await gearContainerService().calculateTotalWeight(containerId)
  }

  const calculateReadinessPercentage = async (containerId: TUUID): Promise<number> => {
    return await gearContainerService().calculateReadinessPercentage(containerId)
  }

  const calculateWeightLimitPercentage = async (containerId: TUUID): Promise<number | null> => {
    return await gearContainerService().calculateWeightLimitPercentage(containerId)
  }

  const isWeightLimitExceeded = async (containerId: TUUID): Promise<boolean> => {
    return await gearContainerService().isWeightLimitExceeded(containerId)
  }

  const getItemsByStatus = async (containerId: TUUID, status: 'owned' | 'missing' | 'toBuy'): Promise<IGearItem[]> => {
    return await gearContainerService().getItemsByStatus(containerId, status)
  }

  const getExpiredItems = async (containerId: TUUID): Promise<IGearItem[]> => {
    return await gearContainerService().getExpiredItems(containerId)
  }

  const getExpiringSoonItems = async (containerId: TUUID, days: number = 30): Promise<IGearItem[]> => {
    return await gearContainerService().getExpiringSoonItems(containerId, days)
  }

  const moveItem = async (containerId: TUUID, itemId: TUUID, newContainerId: TUUID): Promise<void> => {
    await gearContainerService().moveItem(containerId, itemId, newContainerId)
  }

  // ========== Import/Export ==========

  const exportData = async (): Promise<string> => {
    return await gearContainerService().exportData()
  }

  const importData = async (json: string): Promise<void> => {
    await gearContainerService().importData(json)
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
    return await gearContainerService().cloneContainer(containerId, options)
  }

  // ========== Item Catalog Operations ==========

  const getAllItemsForCatalog = (excludeContainerId?: TUUID): IItemWithContainer[] => {
    return gearContainerService().getAllItemsForCatalog(excludeContainerId)
  }

  const getItemWithContainer = (itemId: TUUID): IItemWithContainer | undefined => {
    return gearContainerService().getItemWithContainer(itemId)
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

    // Item Catalog
    getAllItemsForCatalog,
    getItemWithContainer,
  }
}

