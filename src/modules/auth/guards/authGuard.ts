// modules/auth/guards/authGuard.ts
import { isAxiosError } from 'axios'
import { AuthRouteNames } from '@/modules/auth/config/routes'
import { authService } from '@/modules/auth/services/authService'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { config } from '@/shared/config/config'
import type { NavigationGuardNext, RouteLocationNormalized, Router } from 'vue-router'

/**
 * Auth guard that handles:
 * - Protected routes (requiresAuth meta)
 * - Guest-only routes (requiresGuest meta)
 * - Auto-refresh user data when JWT exists but user data is missing
 * - Only active when backend is enabled
 */
export async function authGuard(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext,
): Promise<void> {
  // If backend is not enabled, skip auth checks
  if (!config.backend.enabled) {
    next()
    return
  }

  const requiresAuth = to.matched.some((r) => r.meta.requiresAuth)
  const requiresGuest = to.matched.some((r) => r.meta.requiresGuest)
  const authStore = useAuthStore()

  const hasToken: boolean = !!authStore.token
  const hasUser: boolean = !!authStore.user
  let isAuthenticated: boolean = hasToken && hasUser

  // Try to refetch user data if we have token but no user data
  // Only do this for routes that require auth (to avoid unnecessary API calls)
  if (hasToken && !hasUser && requiresAuth) {
    try {
      const user = await authService.getCurrentUser()
      authStore.setUser(user)
      isAuthenticated = true // User is now authenticated after successful fetch
    } catch (error) {
      if (isAxiosError(error)) {
        // Handle email verification requirement
        if (error.response?.status === 403 && error.response.data?.detail === 'Email verification required') {
          next({ name: AuthRouteNames.verifyEmail, query: { email: authStore.user?.email ?? '' } })
          return
        }
      }

      console.warn('[authGuard] Failed to fetch user data, logging out', error)
      authStore.logout()
      isAuthenticated = false
    }
  }

  // Check auth requirements and redirect if needed
  if (requiresAuth && !isAuthenticated) {
    next({ name: AuthRouteNames.login, query: { redirectTo: to.fullPath } })
    return
  }

  if (requiresGuest && isAuthenticated) {
    next({ name: AuthRouteNames.dashboard })
    return
  }

  // Allow navigation
  next()
}

/**
 * Helper to install auth guard on router
 * Usage: protectRoutes(router)
 */
export function protectRoutes(router: Router): void {
  router.beforeEach(authGuard)
}

