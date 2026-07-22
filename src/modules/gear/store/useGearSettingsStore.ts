import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'
import type { IGearSettings, IUpdateGearSettingsDto, IUserBrand, IUserCategory, IUserContainerType, IVisualizationCustomZone } from '../types/gearSettings.types'
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
        customBrands: parsed.customBrands ?? [],
        visualizationCustomZones: parsed.visualizationCustomZones ?? [],
        visualizationPlacements: parsed.visualizationPlacements ?? {},
        preferredWeightUnit: parsed.preferredWeightUnit,
        defaultCurrency: parsed.defaultCurrency,
      }
    } catch {
      // Fall through to default
    }
  }
  return {
    customCategories: [],
    customContainerTypes: [],
    customBrands: [],
    visualizationCustomZones: [],
    visualizationPlacements: {},
    defaultCurrency: undefined,
  }
}

export const useGearSettingsStore = defineStore('gearSettings', () => {
  const state = reactive<IGearSettings>(loadSettingsSync())

  const getAllCategories = computed<IUserCategory[]>(() => state.customCategories)
  const getAllContainerTypes = computed<IUserContainerType[]>(() => state.customContainerTypes)
  const getAllBrands = computed<IUserBrand[]>(() => state.customBrands)
  const getAllVisualizationZones = computed<IVisualizationCustomZone[]>(() => state.visualizationCustomZones)

  // Actions
  async function updateSettings(updates: IUpdateGearSettingsDto): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.updateSettings(state, updates)
    state.customCategories = updated.customCategories
    state.customContainerTypes = updated.customContainerTypes
    state.customBrands = updated.customBrands
    state.visualizationCustomZones = updated.visualizationCustomZones
    state.visualizationPlacements = updated.visualizationPlacements
    state.preferredWeightUnit = updated.preferredWeightUnit
    state.defaultCurrency = updated.defaultCurrency
  }

  async function addCategory(category: IUserCategory): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.addCategory(state, category)
    state.customCategories = updated.customCategories
  }

  async function updateCategory(category: IUserCategory): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.updateCategory(state, category)
    state.customCategories = updated.customCategories
  }

  async function removeCategory(categoryId: string): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.removeCategory(state, categoryId)
    state.customCategories = updated.customCategories
  }

  async function addContainerType(containerType: IUserContainerType): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.addContainerType(state, containerType)
    state.customContainerTypes = updated.customContainerTypes
  }

  async function updateContainerType(containerType: IUserContainerType): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.updateContainerType(state, containerType)
    state.customContainerTypes = updated.customContainerTypes
  }

  async function removeContainerType(containerTypeId: string): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.removeContainerType(state, containerTypeId)
    state.customContainerTypes = updated.customContainerTypes
  }

  async function addBrand(brand: IUserBrand): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.addBrand(state, brand)
    state.customBrands = updated.customBrands
  }

  async function updateBrand(brand: IUserBrand): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.updateBrand(state, brand)
    state.customBrands = updated.customBrands
  }

  async function removeBrand(brandId: string): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.removeBrand(state, brandId)
    state.customBrands = updated.customBrands
  }

  async function addVisualizationZone(zone: IVisualizationCustomZone): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.addVisualizationZone(state, zone)
    state.visualizationCustomZones = updated.visualizationCustomZones
  }

  async function updateVisualizationZone(zone: IVisualizationCustomZone): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.updateVisualizationZone(state, zone)
    state.visualizationCustomZones = updated.visualizationCustomZones
  }

  async function removeVisualizationZone(zoneId: string): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.removeVisualizationZone(state, zoneId)
    state.visualizationCustomZones = updated.visualizationCustomZones
    state.visualizationPlacements = updated.visualizationPlacements
  }

  async function setContainerZone(containerId: string, zoneId: string): Promise<void> {
    const service = gearSettingsService()
    const updated = await service.setContainerZone(state, containerId, zoneId)
    state.visualizationPlacements = updated.visualizationPlacements
  }

  async function loadFromStorageAction(): Promise<void> {
    const service = gearSettingsService()
    const loaded = await service.loadFromStorage()
    state.customCategories = loaded.customCategories
    state.customContainerTypes = loaded.customContainerTypes
    state.customBrands = loaded.customBrands
    state.visualizationCustomZones = loaded.visualizationCustomZones
    state.visualizationPlacements = loaded.visualizationPlacements
    state.preferredWeightUnit = loaded.preferredWeightUnit
    state.defaultCurrency = loaded.defaultCurrency
  }

  return {
    // State
    customCategories: computed(() => state.customCategories),
    customContainerTypes: computed(() => state.customContainerTypes),
    customBrands: computed(() => state.customBrands),
    visualizationCustomZones: computed(() => state.visualizationCustomZones),
    visualizationPlacements: computed(() => state.visualizationPlacements),
    preferredWeightUnit: computed(() => state.preferredWeightUnit),
    defaultCurrency: computed(() => state.defaultCurrency),

    // Getters
    getAllCategories,
    getAllContainerTypes,
    getAllBrands,
    getAllVisualizationZones,

    // Actions
    updateSettings,
    addCategory,
    updateCategory,
    removeCategory,
    addContainerType,
    updateContainerType,
    removeContainerType,
    addBrand,
    updateBrand,
    removeBrand,
    addVisualizationZone,
    updateVisualizationZone,
    removeVisualizationZone,
    setContainerZone,
    loadFromStorage: loadFromStorageAction,
  }
})

