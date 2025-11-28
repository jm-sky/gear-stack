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
   * - Remove undefined values (for optional fields)
   * - Empty strings are converted to null by backend middleware
   * - Backend handles all weight units (g, kg, oz, lb)
   */
  private cleanItemData(data: ICreateItemDto): ICreateItemDto {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const cleaned: any = {}

    // Optional UUID field (for import/update workflow)
    if (isSet(data.id)) {
      cleaned.id = data.id
    }

    // Required fields
    cleaned.name = data.name
    cleaned.category = data.category
    cleaned.quantity = data.quantity
    cleaned.weight = data.weight
    // Backend handles all weight units (g, kg, oz, lb)
    cleaned.weightUnit = data.weightUnit
    cleaned.priority = data.priority
    cleaned.status = data.status

    // Optional fields - only include if set (not undefined and not null)
    // Middleware handles empty string to null conversion
    if (isSet(data.linkedItemId)) {
      cleaned.linkedItemId = data.linkedItemId
    }
    if (isSet(data.notes)) {
      cleaned.notes = data.notes
    }
    if (isSet(data.expirationDate)) {
      cleaned.expirationDate = data.expirationDate
    }
    if (isSet(data.containerId)) {
      cleaned.containerId = data.containerId
    }
    if (isSet(data.price)) {
      cleaned.price = data.price
    }
    if (isSet(data.url)) {
      cleaned.url = data.url
    }
    if (isSet(data.brand)) {
      cleaned.brand = data.brand
    }
    if (isSet(data.color)) {
      cleaned.color = data.color
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
    if (isSet(data.showOnContainer)) {
      cleaned.showOnContainer = data.showOnContainer
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
    // Axios automatically omits undefined, middleware converts empty strings to null
    // Backend handles all weight units (g, kg, oz, lb)
    const response = await apiClient.patch<IGearItem>(`/gear/items/${itemId}`, data)
    return response.data
  }

  async deleteItem(itemId: TUUID): Promise<void> {
    await apiClient.delete(`/gear/items/${itemId}`)
  }

  /**
   * Batch update items order
   * Updates multiple items' order field using batch API endpoint
   */
  async batchUpdateOrder(items: IGearItem[]): Promise<IGearItem[]> {
    if (items.length === 0) {
      return Promise.resolve([])
    }

    // Prepare batch request payload
    const batchRequest = {
      items: items.map(item => ({
        id: item.id,
        order: item.order ?? 0,
      })),
    }

    // Call batch endpoint
    const response = await apiClient.patch<IGearItem[]>('/gear/items/batch-order', batchRequest)
    return response.data
  }
}

export const gearItemApiService = new GearItemApiService()

