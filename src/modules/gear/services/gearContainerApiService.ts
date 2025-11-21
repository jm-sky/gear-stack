import { apiClient } from '@/shared/services/apiClient'
import type {
  ICreateContainerDto,
  IGearContainer,
  IUpdateContainerDto,
} from '@/modules/gear/types/gear.types'
import type { TUUID } from '@/shared/types/base.type'

/**
 * Gear Container API Service
 *
 * Provides methods to interact with container API endpoints.
 * All methods require authentication (token is added automatically via interceptor).
 */
class GearContainerApiService {
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

  async getContainer(id: TUUID): Promise<IGearContainer> {
    const response = await apiClient.get<IGearContainer>(`/gear/containers/${id}`)
    return response.data
  }

  async updateContainer(id: TUUID, data: IUpdateContainerDto): Promise<IGearContainer> {
    const response = await apiClient.patch<IGearContainer>(`/gear/containers/${id}`, data)
    return response.data
  }

  async deleteContainer(id: TUUID): Promise<void> {
    await apiClient.delete(`/gear/containers/${id}`)
  }

  // Statistics operations
  async getContainerWeight(containerId: TUUID): Promise<{ grams: number; kilograms: number }> {
    const response = await apiClient.get<{ grams: number; kilograms: number }>(
      `/gear/containers/${containerId}/stats/weight`,
    )
    return response.data
  }

  async getContainerReadiness(containerId: TUUID): Promise<{
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

export const gearContainerApiService = new GearContainerApiService()

