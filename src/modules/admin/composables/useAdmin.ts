import { computed } from 'vue'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { useUserStore } from '@/modules/user/store/useUserStore'

/**
 * Composable for admin functionality
 * Provides admin access checks and utilities
 */
export function useAdmin() {
  const authStore = useAuthStore()
  const userStore = useUserStore()

  const isAdmin = computed(() => {
    // Check authStore first (in-memory, most up-to-date)
    // Fall back to userStore (persisted in localStorage)
    return authStore.user?.isAdmin ?? userStore.user?.isAdmin ?? false
  })

  const checkAdminAccess = (): boolean => {
    if (!authStore.isAuthenticated) {
      return false
    }
    return isAdmin.value
  }

  return {
    isAdmin,
    checkAdminAccess,
  }
}
