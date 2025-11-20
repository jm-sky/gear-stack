import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'
import { config, LOCALE_STORAGE_KEY, SETTINGS_STORAGE_KEY, type SupportedLocale } from '@/shared/config/config'
import type { ISettings, IUserCategory, IUserContainerType } from '../types/settings.types'


function loadFromStorage(): ISettings {
  const stored = localStorage.getItem(SETTINGS_STORAGE_KEY)
  let settings: Partial<ISettings> = {}

  if (stored) {
    try {
      settings = JSON.parse(stored)
    } catch (error) {
      console.error('Error loading settings from storage:', error)
    }
  }

  // Sync locale from useLocale's localStorage key (single source of truth)
  const localeFromStorage = localStorage.getItem(LOCALE_STORAGE_KEY)
  const locale: SupportedLocale = (localeFromStorage && (localeFromStorage === 'en' || localeFromStorage === 'pl'))
    ? localeFromStorage as SupportedLocale
    : (settings.locale ?? 'en')

  // Default settings
  return {
    locale,
    darkMode: settings.darkMode ?? false,
    customCategories: settings.customCategories ?? [],
    customContainerTypes: settings.customContainerTypes ?? [],
    preferredWeightUnit: (settings.preferredWeightUnit === 'g' || settings.preferredWeightUnit === 'kg')
      ? settings.preferredWeightUnit
      : config.defaults.preferredWeightUnit, // Default to grams
  }
}

export const useSettingsStore = defineStore('settings', () => {
  const state = reactive<ISettings>(loadFromStorage())

  const getAllCategories = computed<IUserCategory[]>(() => state.customCategories)
  const getAllContainerTypes = computed<IUserContainerType[]>(() => state.customContainerTypes)

  // Actions
  function updateSettings(settings: Partial<ISettings>): void {
    if (settings.locale !== undefined) {
      state.locale = settings.locale
      // Sync with useLocale's localStorage key (single source of truth)
      localStorage.setItem(LOCALE_STORAGE_KEY, settings.locale)
    }
    state.darkMode = settings.darkMode ?? state.darkMode
    if (settings.preferredWeightUnit !== undefined) {
      state.preferredWeightUnit = settings.preferredWeightUnit
    }
    if (settings.customCategories) {
      state.customCategories = settings.customCategories
    }
    if (settings.customContainerTypes) {
      state.customContainerTypes = settings.customContainerTypes
    }
    saveToStorage()
  }

  function addCategory(category: IUserCategory): void {
    state.customCategories.push(category)
    saveToStorage()
  }

  function updateCategory(category: IUserCategory): void {
    const index = state.customCategories.findIndex(c => c.id === category.id)
    if (index !== -1) {
      state.customCategories[index] = category
      saveToStorage()
    }
  }

  function removeCategory(id: string): void {
    state.customCategories = state.customCategories.filter(c => c.id !== id)
    saveToStorage()
  }

  function addContainerType(containerType: IUserContainerType): void {
    state.customContainerTypes.push(containerType)
    saveToStorage()
  }

  function updateContainerType(containerType: IUserContainerType): void {
    const index = state.customContainerTypes.findIndex(t => t.id === containerType.id)
    if (index !== -1) {
      state.customContainerTypes[index] = containerType
      saveToStorage()
    }
  }

  function removeContainerType(id: string): void {
    state.customContainerTypes = state.customContainerTypes.filter(t => t.id !== id)
    saveToStorage()
  }

  function loadFromStorageAction(): void {
    const loaded = loadFromStorage()
    state.locale = loaded.locale
    state.darkMode = loaded.darkMode
    state.preferredWeightUnit = loaded.preferredWeightUnit
    state.customCategories = loaded.customCategories
    state.customContainerTypes = loaded.customContainerTypes ?? []
    // Sync locale to useLocale's localStorage key
    localStorage.setItem(LOCALE_STORAGE_KEY, state.locale)
  }

  function saveToStorage(): void {
    try {
      localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify({
        locale: state.locale,
        darkMode: state.darkMode,
        preferredWeightUnit: state.preferredWeightUnit,
        customCategories: state.customCategories,
        customContainerTypes: state.customContainerTypes,
      }))
    } catch (error) {
      console.error('Error saving settings to storage:', error)
    }
  }

  return {
    // State - Pinia automatycznie udostępnia reactive properties
    locale: computed(() => state.locale),
    darkMode: computed(() => state.darkMode),
    preferredWeightUnit: computed(() => state.preferredWeightUnit),
    customCategories: computed(() => state.customCategories),
    customContainerTypes: computed(() => state.customContainerTypes),

    // Getters
    getAllCategories,
    getAllContainerTypes,

    // Actions
    updateSettings,
    addCategory,
    updateCategory,
    removeCategory,
    addContainerType,
    updateContainerType,
    removeContainerType,
    loadFromStorage: loadFromStorageAction,
    saveToStorage,
  }
})
