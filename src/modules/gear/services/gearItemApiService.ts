import { apiClient } from '@/shared/services/apiClient'
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
  // Item operations
  async createItem(containerId: string, data: ICreateItemDto): Promise<IGearItem> {
    const response = await apiClient.post<IGearItem>(`/gear/containers/${containerId}/items`, data)
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
    const response = await apiClient.patch<IGearItem>(`/gear/items/${itemId}`, data)
    return response.data
  }

  async deleteItem(itemId: TUUID): Promise<void> {
    await apiClient.delete(`/gear/items/${itemId}`)
  }
}

export const gearItemApiService = new GearItemApiService()

