import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'
import type { ICoreSettings, IUpdateCoreSettingsDto } from '../types/coreSettings.types'
import { CoreSettingsService } from '../services/coreSettingsService'

export const useCoreSettingsStore = defineStore('coreSettings', () => {
  const state = reactive<ICoreSettings>(CoreSettingsService.loadFromStorage())

  // Actions
  function updateSettings(updates: IUpdateCoreSettingsDto): void {
    const updated = CoreSettingsService.updateSettings(state, updates)
    state.locale = updated.locale
    state.darkMode = updated.darkMode
    state.preferredWeightUnit = updated.preferredWeightUnit
  }

  function loadFromStorageAction(): void {
    const loaded = CoreSettingsService.loadFromStorage()
    state.locale = loaded.locale
    state.darkMode = loaded.darkMode
    state.preferredWeightUnit = loaded.preferredWeightUnit
  }

  return {
    // State
    locale: computed(() => state.locale),
    darkMode: computed(() => state.darkMode),
    preferredWeightUnit: computed(() => state.preferredWeightUnit),

    // Actions
    updateSettings,
    loadFromStorage: loadFromStorageAction,
  }
})

