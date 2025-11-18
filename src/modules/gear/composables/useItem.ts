import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type { IGearContainer, IGearItem, IUpdateItemDto } from '../types/gear.types'
import { EXPIRATION_SOON_DAYS, MILLISECONDS_PER_DAY } from '../utils/constants'
import { useGear } from './useGear'
import type { TUUID } from '@/shared/types/base.type'

export function useItem(containerId?: TUUID, itemId?: TUUID) {
  const route = useRoute()
  const { getContainerById, getItemById, updateItem, deleteItem } = useGear()

  // Pobierz ID z route jeśli nie podano
  const containerIdValue = computed<TUUID>(() => containerId || (route.params.containerId as string))
  const itemIdValue = computed<TUUID>(() => itemId || (route.params.itemId as string))

  // Item data
  const item = computed<IGearItem | undefined>(() => {
    return getItemById(containerIdValue.value, itemIdValue.value)
  })

  const container = computed<IGearContainer | undefined>(() => {
    return getContainerById(containerIdValue.value)
  })

  // Computed properties
  const totalWeight = computed<number>(() => {
    if (!item.value) return 0
    return item.value.weight * item.value.quantity
  })

  const isExpired = computed<boolean>(() => {
    if (!item.value?.expirationDate) return false
    return new Date(item.value.expirationDate) < new Date()
  })

  const isExpiringSoon = computed<boolean>(() => {
    if (!item.value?.expirationDate) return false
    const expirationDate = new Date(item.value.expirationDate)
    const now = new Date()
    const daysUntilExpiration = Math.ceil((expirationDate.getTime() - now.getTime()) / MILLISECONDS_PER_DAY)
    return daysUntilExpiration > 0 && daysUntilExpiration <= EXPIRATION_SOON_DAYS
  })

  // Actions
  const update = (data: IUpdateItemDto): IGearItem | undefined => {
    if (!item.value) return undefined
    return updateItem(containerIdValue.value, item.value.id, data)
  }

  const remove = (): void => {
    if (!item.value) return
    deleteItem(containerIdValue.value, item.value.id)
  }

  return {
    item,
    container,
    totalWeight,
    isExpired,
    isExpiringSoon,
    update,
    remove,
  }
}

