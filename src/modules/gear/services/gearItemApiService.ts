import { apiClient } from '@/shared/services/apiClient'
import { isSet } from '../utils/helpers'
import type {
  ICreateItemDto,
  IGearItem,
  IUpdateItemDto,
} from '@/modules/gear/types/gear.types'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Gear Item API Service
 *
 * Provides methods to interact with item API endpoints.
 * All methods require authentication (token is added automatically via interceptor).
 */
class GearItemApiService {
  /**
   * Clean data before sending to API:
   * - Remove undefined values
   * - Convert empty strings to null
   * - Filter out unsupported weight units (only 'g' and 'kg' are supported)
   */
  private cleanItemData(data: ICreateItemDto): ICreateItemDto {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const cleaned: any = {}

    // Required fields
    cleaned.name = data.name
    cleaned.category = data.category
    cleaned.quantity = data.quantity
    cleaned.weight = data.weight
    cleaned.weightUnit = data.weightUnit
    cleaned.priority = data.priority
    cleaned.status = data.status

    // Optional fields - only include if set (not undefined and not null)
    // Convert empty strings to null for string fields
    if (isSet(data.linkedItemId)) {
      cleaned.linkedItemId = data.linkedItemId || null
    }
    if (isSet(data.notes)) {
      cleaned.notes = data.notes || null
    }
    if (isSet(data.expirationDate)) {
      // Convert empty string to null for date fields
      cleaned.expirationDate = data.expirationDate && data.expirationDate.trim() !== '' ? data.expirationDate : null
    }
    if (isSet(data.containerId)) {
      cleaned.containerId = data.containerId || null
    }
    if (isSet(data.price)) {
      cleaned.price = data.price
    }
    if (isSet(data.url)) {
      cleaned.url = data.url || null
    }
    if (isSet(data.brand)) {
      cleaned.brand = data.brand || null
    }
    if (isSet(data.color)) {
      cleaned.color = data.color || null
    }
    if (isSet(data.quality)) {
      cleaned.quality = data.quality
    }
    if (isSet(data.wearable)) {
      cleaned.wearable = data.wearable
    }
    if (isSet(data.consumable)) {
      cleaned.consumable = data.consumable
    }
    if (isSet(data.order)) {
      cleaned.order = data.order
    }

    return cleaned
  }

  /**
   * Clean update data before sending to API
   */
  private cleanItemUpdateData(data: IUpdateItemDto): IUpdateItemDto {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const cleaned: any = {}

    // Only include set fields (not undefined and not null)
    if (isSet(data.name)) {
      cleaned.name = data.name
    }
    if (isSet(data.category)) {
      cleaned.category = data.category
    }
    if (isSet(data.quantity)) {
      cleaned.quantity = data.quantity
    }
    if (isSet(data.weight)) {
      cleaned.weight = data.weight
    }
    // Only include weightUnit if it's 'g' or 'kg' (backend doesn't support 'oz' or 'lb')
    if (isSet(data.weightUnit) && (data.weightUnit === 'g' || data.weightUnit === 'kg')) {
      cleaned.weightUnit = data.weightUnit
    }
    if (isSet(data.notes)) {
      cleaned.notes = data.notes || null
    }
    if (isSet(data.expirationDate)) {
      // Convert empty string to null for date fields
      cleaned.expirationDate = data.expirationDate && data.expirationDate.trim() !== '' ? data.expirationDate : null
    }
    if (isSet(data.priority)) {
      cleaned.priority = data.priority
    }
    if (isSet(data.status)) {
      cleaned.status = data.status
    }
    if (isSet(data.containerId)) {
      cleaned.containerId = data.containerId || null
    }
    if (isSet(data.price)) {
      cleaned.price = data.price
    }
    if (isSet(data.url)) {
      cleaned.url = data.url || null
    }
    if (isSet(data.brand)) {
      cleaned.brand = data.brand || null
    }
    if (isSet(data.color)) {
      cleaned.color = data.color || null
    }
    if (isSet(data.quality)) {
      cleaned.quality = data.quality
    }
    if (isSet(data.wearable)) {
      cleaned.wearable = data.wearable
    }
    if (isSet(data.consumable)) {
      cleaned.consumable = data.consumable
    }
    if (isSet(data.order)) {
      cleaned.order = data.order
    }

    return cleaned
  }

  // Item operations
  async createItem(containerId: string, data: ICreateItemDto): Promise<IGearItem> {
    const cleanedData = this.cleanItemData(data)
    const response = await apiClient.post<IGearItem>(`/gear/containers/${containerId}/items`, cleanedData)
    return response.data
  }

  async getItems(containerId: string, skip = 0, limit = 100): Promise<IGearItem[]> {
    const response = await apiClient.get<IGearItem[]>(`/gear/containers/${containerId}/items`, {
      params: { skip, limit },
    })
    return response.data
  }

  async getItem(itemId: TUUID): Promise<IGearItem> {
    const response = await apiClient.get<IGearItem>(`/gear/items/${itemId}`)
    return response.data
  }

  async updateItem(itemId: TUUID, data: IUpdateItemDto): Promise<IGearItem> {
    const cleanedData = this.cleanItemUpdateData(data)
    const response = await apiClient.patch<IGearItem>(`/gear/items/${itemId}`, cleanedData)
    return response.data
  }

  async deleteItem(itemId: TUUID): Promise<void> {
    await apiClient.delete(`/gear/items/${itemId}`)
  }

  /**
   * Batch update items order
   * Updates multiple items' order field using parallel API calls
   */
  async batchUpdateOrder(items: IGearItem[]): Promise<IGearItem[]> {
    if (items.length === 0) {
      return Promise.resolve([])
    }

    // Update all items in parallel
    const updatePromises = items.map(item =>
      this.updateItem(item.id, { order: item.order }),
    )

    return Promise.all(updatePromises)
  }
}

export const gearItemApiService = new GearItemApiService()

