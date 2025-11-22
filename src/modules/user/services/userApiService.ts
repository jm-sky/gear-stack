// modules/user/services/userApiService.ts
import { apiClient } from '@/shared/services/apiClient'
import type { IUpdateUserDto, IUser } from '../types/user.types'

/**
 * Backend API response type (from /me endpoint)
 */
interface UserResponse {
  id: string
  email: string
  name: string
  role?: string
  isActive?: boolean
  isEmailVerified?: boolean
  avatarUrl?: string
  createdAt: string
  updatedAt: string
}

/**
 * User API Service
 * Handles API calls for user data when backend is enabled and user is authenticated
 */
class UserApiService {
  /**
   * Get current user from API
   */
  async getUser(): Promise<IUser> {
    const response = await apiClient.get<UserResponse>('/users/me')
    return this.mapToIUser(response.data)
  }

  /**
   * Update current user profile
   */
  async updateUser(data: IUpdateUserDto): Promise<IUser> {
    console.log('userApiService.updateUser called with data:', data)
    console.log('Making PATCH request to /users/me')
    const response = await apiClient.patch<UserResponse>('/users/me', data)
    console.log('API response received:', response.data)
    return this.mapToIUser(response.data)
  }

  /**
   * Map backend UserResponse to frontend IUser
   */
  private mapToIUser(response: UserResponse): IUser {
    return {
      id: response.id,
      name: response.name,
      email: response.email,
      avatar: response.avatarUrl,
      createdAt: response.createdAt,
      updatedAt: response.updatedAt,
    }
  }
}

export const userApiService = new UserApiService()

