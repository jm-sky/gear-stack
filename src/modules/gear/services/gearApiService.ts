import { apiClient } from '@/shared/services/apiClient'
import type {
  ICreateContainerDto,
  ICreateItemDto,
  IGearContainer,
  IGearItem,
  IUpdateContainerDto,
  IUpdateItemDto,
} from '@/modules/gear/types/gear.types'

/**
 * Gear API Service
 *
 * Provides methods to interact with the gear management API endpoints.
 * All methods require authentication (token is added automatically via interceptor).
 */
class GearApiService {
  // Container operations
  async createContainer(data: ICreateContainerDto): Promise<IGearContainer> {
    const response = await apiClient.post<IGearContainer>('/gear/containers', data)
    return response.data
  }

  async getContainers(skip = 0, limit = 100): Promise<IGearContainer[]> {
    const response = await apiClient.get<IGearContainer[]>('/gear/containers', {
      params: { skip, limit },
    })
    return response.data
  }

  async getContainer(containerId: string): Promise<IGearContainer> {
    const response = await apiClient.get<IGearContainer>(`/gear/containers/${containerId}`)
    return response.data
  }

  async updateContainer(containerId: string, data: IUpdateContainerDto): Promise<IGearContainer> {
    const response = await apiClient.patch<IGearContainer>(`/gear/containers/${containerId}`, data)
    return response.data
  }

  async deleteContainer(containerId: string): Promise<void> {
    await apiClient.delete(`/gear/containers/${containerId}`)
  }

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

  async getItem(itemId: string): Promise<IGearItem> {
    const response = await apiClient.get<IGearItem>(`/gear/items/${itemId}`)
    return response.data
  }

  async updateItem(itemId: string, data: IUpdateItemDto): Promise<IGearItem> {
    const response = await apiClient.patch<IGearItem>(`/gear/items/${itemId}`, data)
    return response.data
  }

  async deleteItem(itemId: string): Promise<void> {
    await apiClient.delete(`/gear/items/${itemId}`)
  }

  // Statistics operations
  async getContainerWeight(containerId: string): Promise<{ grams: number; kilograms: number }> {
    const response = await apiClient.get<{ grams: number; kilograms: number }>(
      `/gear/containers/${containerId}/stats/weight`,
    )
    return response.data
  }

  async getContainerReadiness(containerId: string): Promise<{
    totalItems: number
    ownedItems: number
    missingItems: number
    toBuyItems: number
    readinessPercentage: number
  }> {
    const response = await apiClient.get<{
      totalItems: number
      ownedItems: number
      missingItems: number
      toBuyItems: number
      readinessPercentage: number
    }>(`/gear/containers/${containerId}/stats/readiness`)
    return response.data
  }
}

export const gearApiService = new GearApiService()
