import { apiClient } from '@/shared/services/apiClient'
import type { TRatingType, TRatingValue } from '@/modules/gear/types/gear.types'
import type { IContentReport, ICreateReportRequest } from '@/modules/gear/types/reports.types'

/**
 * Gear Container API Service
 *
 * Provides methods to interact with container rating/reporting API endpoints.
 * Container CRUD lives on the V2 API (useGearV2 / useContainerOperationsV2) -- this service
 * only covers the two backend features that don't have a V2 equivalent yet
 * (docs/plans/2026-07-23-gear-backend-v1-v2-unification.md).
 * All methods require authentication (token is added automatically via interceptor).
 */
class GearContainerApiService {
  // Rating operations
  async rateContainer(
    containerId: string,
    rating: TRatingValue,
    ratingType: TRatingType = 'user'
  ): Promise<{
    rating: TRatingValue
    ratingType: TRatingType
    ownerRating: TRatingValue | null
    averageUserRating: number | null
    userRatingCount: number
  }> {
    const response = await apiClient.post(
      `/gear/containers/${containerId}/rating`,
      {
        rating,
        ratingType
      }
    )
    return response.data
  }

  async deleteContainerRating(
    containerId: string,
    ratingType: TRatingType = 'user'
  ): Promise<{
    message: string
    ownerRating: TRatingValue | null
    averageUserRating: number | null
    userRatingCount: number
  }> {
    const response = await apiClient.delete(
      `/gear/containers/${containerId}/rating`,
      {
        params: { rating_type: ratingType }
      }
    )
    return response.data
  }

  /**
   * Report a public container for inappropriate content.
   *
   * @param containerId - Container ID to report
   * @param reportData - Report data (reason and optional additional info)
   * @returns Created report
   */
  async reportPublicContainer(
    containerId: string,
    reportData: ICreateReportRequest
  ): Promise<IContentReport> {
    const response = await apiClient.post<IContentReport>(
      `/gear/containers/${containerId}/report`,
      reportData
    )
    return response.data
  }

  /**
   * Get user's report status for a container
   *
   * @param containerId - Container ID
   * @returns Object with hasReported boolean
   */
  async getReportStatus(containerId: string): Promise<{ hasReported: boolean }> {
    const response = await apiClient.get<{ hasReported: boolean }>(
      `/gear/containers/${containerId}/report/status`
    )
    return response.data
  }

  /**
   * Withdraw (delete) user's report for a container
   *
   * @param containerId - Container ID
   */
  async withdrawReport(containerId: string): Promise<void> {
    await apiClient.delete(`/gear/containers/${containerId}/report`)
  }
}

export const gearContainerApiService = new GearContainerApiService()
