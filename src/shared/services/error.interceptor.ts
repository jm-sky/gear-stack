/**
 * Axios error response interceptor
 *
 * Handles HTTP error responses globally:
 * - 401 Unauthorized: Try to refresh token automatically, if that fails open login modal
 * - Other errors: Pass through to be handled locally
 *
 * This provides centralized error handling with automatic token refresh
 * and allows users to re-authenticate without losing their current context.
 *
 * FIXED: Moved mutable state to Pinia store to prevent race conditions
 */

import { HttpStatusCode } from 'axios'
import { authService } from '@/modules/auth/services/authService'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { useLoginModal } from '@/shared/composables/useLoginModal'
import { config } from '@/shared/config/config'
import { useTokenRefreshStore } from '@/shared/store/useTokenRefreshStore'
import { apiClient } from './apiClient'
import type { AxiosError, InternalAxiosRequestConfig } from 'axios'

/**
 * Handle axios response errors
 *
 * @param error - Axios error object
 * @returns Rejected promise with the error
 */
export async function errorResponseInterceptor(error: AxiosError) {
  const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

  // Only handle 401 if backend is enabled
  if (!config.backend.enabled) {
    // Pass error through for local handling
    return Promise.reject(error)
  }

  // Handle 401 Unauthorized errors
  if (
    error.response?.status === HttpStatusCode.Unauthorized &&
    originalRequest &&
    !originalRequest._retry
  ) {
    const authStore = useAuthStore()
    const refreshStore = useTokenRefreshStore()
    const refreshToken = authStore.refreshToken

    // If we have a refresh token, try to refresh the access token
    if (refreshToken) {
      // If already refreshing, queue this request
      if (refreshStore.isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshStore.addToQueue({ resolve, reject })
        })
          .then(() => {
            // Retry with new token (auth interceptor will add the new token automatically)
            return apiClient(originalRequest)
          })
          .catch((err) => {
            return Promise.reject(err)
          })
      }

      // Mark that we're refreshing
      originalRequest._retry = true
      refreshStore.setRefreshing(true)

      try {
        // Try to refresh the access token
        const response = await authService.refreshAccessToken(refreshToken)

        // Update tokens in store
        authStore.setToken(response.accessToken)
        authStore.setRefreshToken(response.refreshToken)

        // Process queued requests (they will be retried with new token via auth interceptor)
        refreshStore.processQueue(null)

        // Retry the original request with new token (auth interceptor will add it)
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed - clear tokens, process queue with error, and show login modal
        refreshStore.processQueue(refreshError as Error)
        authStore.clearToken()
        authStore.clearRefreshToken()
        authStore.clearUser()

        // Open login modal with retry callback
        const loginModal = useLoginModal()
        loginModal.open({
          onSuccess: async () => {
            try {
              // After successful login, retry the original request
              // Auth interceptor will add the new token automatically
              originalRequest._retry = false // Reset retry flag for new attempt
              return await apiClient(originalRequest)
            } catch (retryError) {
              console.error('Failed to retry request after re-authentication', retryError)
              throw retryError
            }
          },
        })

        return Promise.reject(refreshError)
      } finally {
        refreshStore.setRefreshing(false)
      }
    } else {
      // No refresh token - clear auth data, clear queue, and show login modal
      authStore.clearToken()
      authStore.clearUser()

      // Clear the failed queue since we can't proceed without refresh token
      refreshStore.processQueue(new Error('No refresh token available'))

      // Open login modal with retry callback
      const loginModal = useLoginModal()
      loginModal.open({
        onSuccess: async () => {
          try {
            // After successful login, retry the original request
            // Auth interceptor will add the new token automatically
            originalRequest._retry = false // Reset retry flag
            return await apiClient(originalRequest)
          } catch (retryError) {
            console.error('Failed to retry request after re-authentication', retryError)
            throw retryError
          }
        },
      })

      // Reject the original request
      return Promise.reject(new Error('Authentication required'))
    }
  }

  // Pass error through for local handling
  return Promise.reject(error)
}

