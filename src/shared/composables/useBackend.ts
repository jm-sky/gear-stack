// shared/composables/useBackend.ts
import { computed } from 'vue'
import { config } from '@/shared/config/config'

/**
 * Composable to check if backend is enabled
 * 
 * @example
 * ```ts
 * const { isBackendEnabled, backendUrl } = useBackend()
 * 
 * if (isBackendEnabled.value) {
 *   // Use backend API
 *   await apiClient.post('/auth/login', credentials)
 * } else {
 *   // Use localStorage
 *   localStorage.setItem('user', JSON.stringify(user))
 * }
 * ```
 */
export function useBackend() {
  const isBackendEnabled = computed(() => config.backend.enabled)
  const backendUrl = computed(() => config.backend.baseUrl)

  return {
    isBackendEnabled,
    backendUrl,
  }
}

