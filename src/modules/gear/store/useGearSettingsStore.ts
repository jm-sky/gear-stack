import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'
import type { IGearSettings, IUpdateGearSettingsDto, IUserBrand, IUserCategory, IUserContainerType } from '../types/gearSettings.types'
import { GearSettingsService } from '../services/gearSettingsService'

export const useGearSettingsStore = defineStore('gearSettings', () => {
  const state = reactive<IGearSettings>(GearSettingsService.loadFromStorage())

  const getAllCategories = computed<IUserCategory[]>(() => state.customCategories)
  const getAllContainerTypes = computed<IUserContainerType[]>(() => state.customContainerTypes)
  const getAllBrands = computed<IUserBrand[]>(() => state.customBrands)

  // Actions
  function updateSettings(updates: IUpdateGearSettingsDto): void {
    const updated = GearSettingsService.updateSettings(state, updates)
    state.customCategories = updated.customCategories
    state.customContainerTypes = updated.customContainerTypes
    state.customBrands = updated.customBrands
  }

  function addCategory(category: IUserCategory): void {
    const updated = GearSettingsService.addCategory(state, category)
    state.customCategories = updated.customCategories
  }

  function updateCategory(category: IUserCategory): void {
    const updated = GearSettingsService.updateCategory(state, category)
    state.customCategories = updated.customCategories
  }

  function removeCategory(categoryId: string): void {
    const updated = GearSettingsService.removeCategory(state, categoryId)
    state.customCategories = updated.customCategories
  }

  function addContainerType(containerType: IUserContainerType): void {
    const updated = GearSettingsService.addContainerType(state, containerType)
    state.customContainerTypes = updated.customContainerTypes
  }

  function updateContainerType(containerType: IUserContainerType): void {
    const updated = GearSettingsService.updateContainerType(state, containerType)
    state.customContainerTypes = updated.customContainerTypes
  }

  function removeContainerType(containerTypeId: string): void {
    const updated = GearSettingsService.removeContainerType(state, containerTypeId)
    state.customContainerTypes = updated.customContainerTypes
  }

  function addBrand(brand: IUserBrand): void {
    const updated = GearSettingsService.addBrand(state, brand)
    state.customBrands = updated.customBrands
  }

  function updateBrand(brand: IUserBrand): void {
    const updated = GearSettingsService.updateBrand(state, brand)
    state.customBrands = updated.customBrands
  }

  function removeBrand(brandId: string): void {
    const updated = GearSettingsService.removeBrand(state, brandId)
    state.customBrands = updated.customBrands
  }

  function loadFromStorageAction(): void {
    const loaded = GearSettingsService.loadFromStorage()
    state.customCategories = loaded.customCategories
    state.customContainerTypes = loaded.customContainerTypes
    state.customBrands = loaded.customBrands
  }

  return {
    // State
    customCategories: computed(() => state.customCategories),
    customContainerTypes: computed(() => state.customContainerTypes),
    customBrands: computed(() => state.customBrands),

    // Getters
    getAllCategories,
    getAllContainerTypes,
    getAllBrands,

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
    loadFromStorage: loadFromStorageAction,
  }
})

