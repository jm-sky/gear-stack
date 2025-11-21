import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'
import type { Settings, UpdateSettingsData } from '../types/settings.type'
import { SettingsService } from '../services/settingsService'

export const useSettingsStore = defineStore('settings', () => {
  const state = reactive<Settings>(SettingsService.loadFromStorage())

  // Actions
  function updateSettings(updates: UpdateSettingsData): void {
    const updated = SettingsService.updateSettings(state, updates)
    state.locale = updated.locale
    state.darkMode = updated.darkMode
  }

  function loadFromStorageAction(): void {
    const loaded = SettingsService.loadFromStorage()
    state.locale = loaded.locale
    state.darkMode = loaded.darkMode
  }

  return {
    // State
    locale: computed(() => state.locale),
    darkMode: computed(() => state.darkMode),

    // Actions
    updateSettings,
    loadFromStorage: loadFromStorageAction,
  }
})

