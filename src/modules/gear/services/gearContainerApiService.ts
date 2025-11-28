import { apiClient } from '@/shared/services/apiClient'
import { isSet } from '../utils/helpers'
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
  /**
   * Clean data before sending to API:
   * - Remove undefined values (for optional fields)
   * - Empty strings are converted to null by backend middleware
   * - Backend handles all weight units (g, kg, oz, lb)
   */
  private cleanContainerData(data: ICreateContainerDto): ICreateContainerDto {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const cleaned: any = {}

    // Optional UUID field (for import/update workflow)
    if (isSet(data.id)) {
      cleaned.id = data.id
    }

    // Required fields
    cleaned.name = data.name
    cleaned.type = data.type

    // Optional fields - only include if set (not undefined and not null)
    // Middleware handles empty string to null conversion
    if (isSet(data.description)) {
      cleaned.description = data.description
    }
    if (isSet(data.color)) {
      cleaned.color = data.color
    }
    if (isSet(data.parentContainerId)) {
      cleaned.parentContainerId = data.parentContainerId
    }
    if (isSet(data.hideWhenNested)) {
      cleaned.hideWhenNested = data.hideWhenNested
    }
    if (isSet(data.brand)) {
      cleaned.brand = data.brand
    }
    if (isSet(data.price)) {
      cleaned.price = data.price
    }
    if (isSet(data.weight)) {
      cleaned.weight = data.weight
    }
    // Backend handles all weight units (g, kg, oz, lb)
    if (isSet(data.weightUnit)) {
      cleaned.weightUnit = data.weightUnit
    }
    if (isSet(data.maxWeight)) {
      cleaned.maxWeight = data.maxWeight
    }
    if (isSet(data.maxWeightUnit)) {
      cleaned.maxWeightUnit = data.maxWeightUnit
    }
    if (isSet(data.url)) {
      cleaned.url = data.url
    }
    if (data.isPublic !== undefined && data.isPublic !== null) {
      cleaned.isPublic = data.isPublic
    }
    if (data.favorite !== undefined && data.favorite !== null) {
      cleaned.favorite = data.favorite
    }
    if (data.showItemImages !== undefined && data.showItemImages !== null) {
      cleaned.showItemImages = data.showItemImages
    }

    return cleaned
  }

  // Container operations
  async createContainer(data: ICreateContainerDto): Promise<IGearContainer> {
    const cleanedData = this.cleanContainerData(data)
    const response = await apiClient.post<IGearContainer>('/gear/containers', cleanedData)
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
    // Axios automatically omits undefined, middleware converts empty strings to null
    // Backend handles all weight units (g, kg, oz, lb)
    const response = await apiClient.patch<IGearContainer>(`/gear/containers/${id}`, data)
    return response.data
  }

  async deleteContainer(id: TUUID): Promise<void> {
    await apiClient.delete(`/gear/containers/${id}`)
  }

  async deleteAllContainers(): Promise<void> {
    await apiClient.delete('/gear/containers')
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

