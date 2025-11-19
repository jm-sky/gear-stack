/**
 * Axios error response interceptor
 *
 * Handles HTTP error responses globally:
 * - 401 Unauthorized: Clear auth and redirect to login
 * - Other errors: Pass through to be handled locally
 *
 * Note: This is a simplified version. For advanced features like
 * automatic token refresh, see the test/frontend implementation.
 */

import { HttpStatusCode } from 'axios'
import { JWT_STORE_KEY, USER_STORAGE_KEY } from '@/shared/config/config'
import type { AxiosError } from 'axios'

/**
 * Handle axios response errors
 *
 * @param error - Axios error object
 * @returns Rejected promise with the error
 */
export async function errorResponseInterceptor(error: AxiosError) {
  // Handle 401 Unauthorized errors
  if (error.response?.status === HttpStatusCode.Unauthorized) {
    // Clear authentication data
    localStorage.removeItem(JWT_STORE_KEY)
    localStorage.removeItem(USER_STORAGE_KEY)

    // Redirect to login or show login modal
    // For now, just reload to trigger auth check
    if (window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
  }

  // Pass error through for local handling
  return Promise.reject(error)
}
