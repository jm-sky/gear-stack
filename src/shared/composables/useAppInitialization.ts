/**
 * App initialization composable
 *
 * Handles application-level initialization tasks such as:
 * - Loading user settings (locale, theme)
 * - Setting up global configuration
 * - Pre-fetching critical data
 *
 * This separates initialization logic from App.vue for better
 * code organization, testability, and reusability.
 */

import { computed, watchEffect } from 'vue'
import { useSettingsQuery } from '@/modules/settings/composables/useSettings'
import { useLocale } from '@/shared/i18n'
import type { Settings } from '@/modules/settings/types/settings.type'

export interface AppInitializationState {
  /**
   * Whether the app has finished initializing
   */
  isInitialized: boolean
  /**
   * Initialization error if any
   */
  error: unknown
  /**
   * Settings data
   */
  settings?: Settings
}

/**
 * Initialize application settings and configuration
 *
 * This composable:
 * 1. Loads user settings from the backend
 * 2. Applies locale/language preferences
 * 3. Returns initialization state
 *
 * Usage in App.vue:
 * ```ts
 * const { isInitialized, error } = useAppInitialization()
 * ```
 */
export function useAppInitialization() {
  const { setLocale } = useLocale()
  const settingsQuery = useSettingsQuery()

  // Watch settings data and apply locale when available
  watchEffect(() => {
    if (settingsQuery.data.value?.locale) {
      setLocale(settingsQuery.data.value.locale)
    }
  })

  // Computed: App is initialized when settings query has finished (success or error)
  // Note: settingsQuery.isPending is already a Ref from vue-query
  const isInitialized = computed(() => !settingsQuery.isPending.value)

  return {
    isInitialized,
    error: settingsQuery.error,
    settings: settingsQuery.data,
    // Expose query state for advanced use cases
    isLoading: settingsQuery.isPending,
    isError: settingsQuery.isError,
  }
}

