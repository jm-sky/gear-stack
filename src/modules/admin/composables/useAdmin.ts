import { computed } from 'vue'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'

/**
 * Composable for admin functionality
 * Provides admin access checks and utilities
 */
export function useAdmin() {
  const authStore = useAuthStore()

  const isAdmin = computed(() => {
    return authStore.user?.isAdmin ?? false
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
