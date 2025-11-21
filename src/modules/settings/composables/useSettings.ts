import { computed } from 'vue'
import type { IUpdateSettingsDto, IUserCategory, IUserContainerType } from '../types/settings.types'
import { useSettingsStore } from '../store/useSettingsStore'

export function useSettings() {
  const store = useSettingsStore()

  const settings = computed(() => ({
    locale: store.locale,
    darkMode: store.darkMode,
    preferredWeightUnit: store.preferredWeightUnit,
    customCategories: store.customCategories,
    customContainerTypes: store.customContainerTypes,
  }))

  const customCategories = computed<IUserCategory[]>(() => store.getAllCategories)
  const customContainerTypes = computed<IUserContainerType[]>(() => store.getAllContainerTypes)

  const updateSettings = (data: IUpdateSettingsDto): void => {
    store.updateSettings(data)
  }

  const addCategory = (category: IUserCategory): void => {
    store.addCategory(category)
  }

  const updateCategory = (category: IUserCategory): void => {
    store.updateCategory(category)
  }

  const removeCategory = (id: string): void => {
    store.removeCategory(id)
  }

  const addContainerType = (containerType: IUserContainerType): void => {
    store.addContainerType(containerType)
  }

  const updateContainerType = (containerType: IUserContainerType): void => {
    store.updateContainerType(containerType)
  }

  const removeContainerType = (id: string): void => {
    store.removeContainerType(id)
  }

  return {
    settings,
    customCategories,
    customContainerTypes,
    updateSettings,
    addCategory,
    updateCategory,
    removeCategory,
    addContainerType,
    updateContainerType,
    removeContainerType,
  }
}

