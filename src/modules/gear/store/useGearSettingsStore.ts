import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'
import type { IGearSettings, IUpdateGearSettingsDto, IUserCategory, IUserContainerType } from '../types/gearSettings.types'
import { gearSettingsService } from '../services/gearSettingsService'

// Helper to load settings synchronously for initial state
// This is a workaround for store initialization - in the future this should be async
function loadSettingsSync(): IGearSettings {
  const stored = localStorage.getItem('gear-stack:gear-settings')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      return {
        customCategories: parsed.customCategories ?? [],
        customContainerTypes: parsed.customContainerTypes ?? [],
        preferredWeightUnit: parsed.preferredWeightUnit,
      }
    } catch {
      // Fall through to default
    }
  }
  return {
    customCategories: [],
    customContainerTypes: [],
  }
}

export const useGearSettingsStore = defineStore('gearSettings', () => {
  const state = reactive<IGearSettings>(loadSettingsSync())

  const getAllCategories = computed<IUserCategory[]>(() => state.customCategories)
  const getAllContainerTypes = computed<IUserContainerType[]>(() => state.customContainerTypes)

  // Actions
  async function updateSettings(updates: IUpdateGearSettingsDto): Promise<void> {
    const updated = await gearSettingsService.updateSettings(state, updates)
    state.customCategories = updated.customCategories
    state.customContainerTypes = updated.customContainerTypes
    state.preferredWeightUnit = updated.preferredWeightUnit
  }

  async function addCategory(category: IUserCategory): Promise<void> {
    const updated = await gearSettingsService.addCategory(state, category)
    state.customCategories = updated.customCategories
  }

  async function updateCategory(category: IUserCategory): Promise<void> {
    const updated = await gearSettingsService.updateCategory(state, category)
    state.customCategories = updated.customCategories
  }

  async function removeCategory(categoryId: string): Promise<void> {
    const updated = await gearSettingsService.removeCategory(state, categoryId)
    state.customCategories = updated.customCategories
  }

  async function addContainerType(containerType: IUserContainerType): Promise<void> {
    const updated = await gearSettingsService.addContainerType(state, containerType)
    state.customContainerTypes = updated.customContainerTypes
  }

  async function updateContainerType(containerType: IUserContainerType): Promise<void> {
    const updated = await gearSettingsService.updateContainerType(state, containerType)
    state.customContainerTypes = updated.customContainerTypes
  }

  async function removeContainerType(containerTypeId: string): Promise<void> {
    const updated = await gearSettingsService.removeContainerType(state, containerTypeId)
    state.customContainerTypes = updated.customContainerTypes
  }

  async function loadFromStorageAction(): Promise<void> {
    const loaded = await gearSettingsService.loadFromStorage()
    state.customCategories = loaded.customCategories
    state.customContainerTypes = loaded.customContainerTypes
    state.preferredWeightUnit = loaded.preferredWeightUnit
  }

  return {
    // State
    customCategories: computed(() => state.customCategories),
    customContainerTypes: computed(() => state.customContainerTypes),
    preferredWeightUnit: computed(() => state.preferredWeightUnit),

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
  }
})

