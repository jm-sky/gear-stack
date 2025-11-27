import { usePermissions } from '@/shared/composables/usePermissions'

/**
 * Composable for admin functionality
 * Provides admin access checks and utilities
 * 
 * @deprecated Use usePermissions() instead for centralized permission logic
 * This is kept for backward compatibility
 */
export function useAdmin() {
  const { isAdmin, canAccessAdminPanel, isAuthenticated } = usePermissions()

  const checkAdminAccess = (): boolean => {
    if (!isAuthenticated.value) {
      return false
    }
    return canAccessAdminPanel.value
  }

  return {
    isAdmin,
    checkAdminAccess,
  }
}
