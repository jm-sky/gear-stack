 
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

  // IMPORTANT: authGuard should have already fetched user data at this point
  // but let's add a safety check with a small delay to ensure user data is loaded
  // This prevents race conditions after page refresh
  if (!authStore.user) {
    // Wait a bit for authGuard to finish loading user data
    let retries = 0
    const maxRetries = 10
    while (!authStore.user && retries < maxRetries) {
      await new Promise(resolve => setTimeout(resolve, 50))
      retries++
    }

    // If still no user after waiting, redirect to login
    if (!authStore.user) {
      console.warn('[adminGuard] User data not loaded after authGuard, redirecting to login')
      next({ name: AuthRouteNames.login, query: { redirectTo: to.fullPath } })
      return
    }
  }

  // Check if user is admin
  if (!authStore.user.isAdmin) {
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
