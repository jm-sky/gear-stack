/* eslint-disable @typescript-eslint/no-explicit-any */
import { isAxiosError } from 'axios'
import { AuthRouteNames } from '@/modules/auth/config/routes'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { config } from '@/shared/config/config'
import type { NavigationGuardNext, RouteLocationNormalized, Router } from 'vue-router'

/**
 * Admin guard that checks if user has admin access
 * Should be called after authGuard
 */
export async function adminGuard(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext,
): Promise<void> {
  // Skip admin checks if backend is disabled
  if (!config.backend.enabled) {
    next()
    return
  }

  const requiresAdmin = to.matched.some(r => r.meta.requiresAdmin)
  if (!requiresAdmin) {
    next()
    return
  }

  const authStore = useAuthStore()

  // Check if user is authenticated
  if (!authStore.isAuthenticated) {
    next({ name: AuthRouteNames.login, query: { redirectTo: to.fullPath } })
    return
  }

  // Check if user is admin
  if (!authStore.user?.isAdmin) {
    // Redirect to dashboard or home if not admin
    next({ name: 'home' })
    return
  }

  // Allow navigation
  next()
}

/**
 * Helper to install admin guard on router
 * Usage: protectAdminRoutes(router)
 * Should be called after protectRoutes
 */
export function protectAdminRoutes(router: Router): void {
  router.beforeEach(adminGuard)
}
