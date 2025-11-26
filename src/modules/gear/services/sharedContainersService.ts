/**
 * Shared Containers API Service
 *
 * Provides methods to interact with shared container API endpoints.
 * Shared containers are accessed via tokens, allowing read-only access to non-public containers.
 */

import { apiClient } from '@/shared/services/apiClient'
import type { IGearContainer } from '../types/gear.types'

class SharedContainersApiService {
  /**
   * Get a shared container by token
   * @param token - Share token
   * @returns Shared container
   */
  async getSharedContainer(token: string): Promise<IGearContainer> {
    const response = await apiClient.get<IGearContainer>(`/gear/shared/containers/${token}`)
    return response.data
  }
}

export const sharedContainersService = new SharedContainersApiService()
