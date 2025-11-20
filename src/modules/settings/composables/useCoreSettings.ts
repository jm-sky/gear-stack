import { computed } from 'vue'
import type { IUpdateCoreSettingsDto } from '../types/coreSettings.types'
import { useCoreSettingsStore } from '../store/useCoreSettingsStore'

/**
 * Composable for core settings (locale, dark mode, preferred weight unit)
 */
export function useCoreSettings() {
  const store = useCoreSettingsStore()

  const settings = computed(() => ({
    locale: store.locale,
    darkMode: store.darkMode,
    preferredWeightUnit: store.preferredWeightUnit,
  }))

  const updateSettings = (data: IUpdateCoreSettingsDto): void => {
    store.updateSettings(data)
  }

  return {
    settings,
    updateSettings,
  }
}

