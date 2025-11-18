import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type { IGearContainer, IUpdateContainerDto } from '../types/gear.types'
import { useGear } from './useGear'
import type { TUUID } from '@/shared/types/base.type'

export function useContainer(containerId?: TUUID) {
  const route = useRoute()
  const { getContainerById, updateContainer, deleteContainer, calculateTotalWeight, calculateReadinessPercentage } = useGear()

  // Pobierz ID z route jeśli nie podano
  const id = computed<TUUID>(() => containerId || (route.params.id as string))

  // Container data
  const container = computed<IGearContainer | undefined>(() => {
    return getContainerById(id.value)
  })

  // Computed properties
  const totalWeight = computed<number>(() => {
    if (!container.value) return 0
    return calculateTotalWeight(container.value.id)
  })

  const readinessPercentage = computed<number>(() => {
    if (!container.value) return 0
    return calculateReadinessPercentage(container.value.id)
  })

  const itemsCount = computed<number>(() => {
    return container.value?.items.length || 0
  })

  // Actions
  const update = (data: IUpdateContainerDto): IGearContainer | undefined => {
    if (!container.value) return undefined
    return updateContainer(container.value.id, data)
  }

  const remove = (): void => {
    if (!container.value) return
    deleteContainer(container.value.id)
  }

  return {
    container,
    totalWeight,
    readinessPercentage,
    itemsCount,
    update,
    remove,
  }
}

