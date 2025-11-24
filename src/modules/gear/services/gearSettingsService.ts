import { GEAR_SETTINGS_STORAGE_KEY, SETTINGS_STORAGE_KEY } from '@/shared/config/config'
import type {
  IGearSettings,
  IGearSettingsService,
  IUpdateGearSettingsDto,
  IUserBrand,
  IUserCategory,
  IUserContainerType,
} from '../types/gearSettings.types'

/**
 * Gear Settings Service (LocalStorage implementation)
 * Handles gear-specific settings: custom categories and container types
 * Implements IGearSettingsService interface for localStorage-based operations.
 */
class GearSettingsService implements IGearSettingsService {
  private static readonly STORAGE_KEY = GEAR_SETTINGS_STORAGE_KEY
  private static readonly OLD_STORAGE_KEY = SETTINGS_STORAGE_KEY // For migration

  /**
   * Migrate from old storage format if needed
   */
  private migrateFromOldStorage(): Partial<IGearSettings> | null {
    const oldStored = localStorage.getItem(GearSettingsService.OLD_STORAGE_KEY)
    if (!oldStored) return null

    try {
      const oldSettings = JSON.parse(oldStored)
      return {
        customCategories: oldSettings.customCategories,
        customContainerTypes: oldSettings.customContainerTypes,
      }
    } catch {
      return null
    }
  }

  /**
   * Load gear settings from localStorage
   */
  async loadFromStorage(): Promise<IGearSettings> {
    const stored = localStorage.getItem(GearSettingsService.STORAGE_KEY)
    let settings: Partial<IGearSettings> = {}

    if (stored) {
      try {
        settings = JSON.parse(stored)
      } catch (error) {
        console.error('Error loading gear settings from storage:', error)
      }
    } else {
      // Try to migrate from old storage
      const migrated = this.migrateFromOldStorage()
      if (migrated) {
        settings = migrated
        // Save to new location
        await this.saveToStorage({
          customCategories: migrated.customCategories ?? [],
          customContainerTypes: migrated.customContainerTypes ?? [],
          customBrands: [],
        })
      }
    }

    return Promise.resolve({
      customCategories: settings.customCategories ?? [],
      customContainerTypes: settings.customContainerTypes ?? [],
      customBrands: settings.customBrands ?? [],
      preferredWeightUnit: settings.preferredWeightUnit,
      defaultCurrency: settings.defaultCurrency,
    })
  }

  /**
   * Save gear settings to localStorage
   */
  async saveToStorage(settings: IGearSettings): Promise<void> {
    try {
      localStorage.setItem(GearSettingsService.STORAGE_KEY, JSON.stringify({
        customCategories: settings.customCategories,
        customContainerTypes: settings.customContainerTypes,
        customBrands: settings.customBrands,
        preferredWeightUnit: settings.preferredWeightUnit,
        defaultCurrency: settings.defaultCurrency,
      }))
      return Promise.resolve()
    } catch (error) {
      console.error('Error saving gear settings to storage:', error)
      return Promise.reject(error)
    }
  }

  /**
   * Update gear settings
   */
  async updateSettings(current: IGearSettings, updates: IUpdateGearSettingsDto): Promise<IGearSettings> {
    const updated: IGearSettings = {
      customCategories: updates.customCategories ?? current.customCategories,
      customContainerTypes: updates.customContainerTypes ?? current.customContainerTypes,
      customBrands: updates.customBrands ?? current.customBrands,
      preferredWeightUnit: updates.preferredWeightUnit ?? current.preferredWeightUnit,
      defaultCurrency: updates.defaultCurrency ?? current.defaultCurrency,
    }

    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Add a custom category
   */
  async addCategory(settings: IGearSettings, category: IUserCategory): Promise<IGearSettings> {
    const updated = {
      ...settings,
      customCategories: [...settings.customCategories, category],
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Update a custom category
   */
  async updateCategory(settings: IGearSettings, category: IUserCategory): Promise<IGearSettings> {
    const updated = {
      ...settings,
      customCategories: settings.customCategories.map(c => c.id === category.id ? category : c),
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Remove a custom category
   */
  async removeCategory(settings: IGearSettings, categoryId: string): Promise<IGearSettings> {
    const updated = {
      ...settings,
      customCategories: settings.customCategories.filter(c => c.id !== categoryId),
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Add a custom container type
   */
  async addContainerType(settings: IGearSettings, containerType: IUserContainerType): Promise<IGearSettings> {
    const updated = {
      ...settings,
      customContainerTypes: [...settings.customContainerTypes, containerType],
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Update a custom container type
   */
  async updateContainerType(settings: IGearSettings, containerType: IUserContainerType): Promise<IGearSettings> {
    const updated = {
      ...settings,
      customContainerTypes: settings.customContainerTypes.map(t => t.id === containerType.id ? containerType : t),
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Remove a custom container type
   */
  async removeContainerType(settings: IGearSettings, containerTypeId: string): Promise<IGearSettings> {
    const updated = {
      ...settings,
      customContainerTypes: settings.customContainerTypes.filter(t => t.id !== containerTypeId),
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Add a custom brand
   */
  async addBrand(settings: IGearSettings, brand: IUserBrand): Promise<IGearSettings> {
    const updated = {
      ...settings,
      customBrands: [...settings.customBrands, brand],
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Update a custom brand
   */
  async updateBrand(settings: IGearSettings, brand: IUserBrand): Promise<IGearSettings> {
    const updated = {
      ...settings,
      customBrands: settings.customBrands.map(b => b.id === brand.id ? brand : b),
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  /**
   * Remove a custom brand
   */
  async removeBrand(settings: IGearSettings, brandId: string): Promise<IGearSettings> {
    const updated = {
      ...settings,
      customBrands: settings.customBrands.filter(b => b.id !== brandId),
    }
    await this.saveToStorage(updated)
    return Promise.resolve(updated)
  }

  // Static helper methods for backward compatibility
  // These methods create an instance and call the instance methods
  static async loadFromStorage(): Promise<IGearSettings> {
    const instance = new GearSettingsService()
    return instance.loadFromStorage()
  }

  static async saveToStorage(settings: IGearSettings): Promise<void> {
    const instance = new GearSettingsService()
    return instance.saveToStorage(settings)
  }

  static async updateSettings(current: IGearSettings, updates: IUpdateGearSettingsDto): Promise<IGearSettings> {
    const instance = new GearSettingsService()
    return instance.updateSettings(current, updates)
  }

  static async addCategory(settings: IGearSettings, category: IUserCategory): Promise<IGearSettings> {
    const instance = new GearSettingsService()
    return instance.addCategory(settings, category)
  }

  static async updateCategory(settings: IGearSettings, category: IUserCategory): Promise<IGearSettings> {
    const instance = new GearSettingsService()
    return instance.updateCategory(settings, category)
  }

  static async removeCategory(settings: IGearSettings, categoryId: string): Promise<IGearSettings> {
    const instance = new GearSettingsService()
    return instance.removeCategory(settings, categoryId)
  }

  static async addContainerType(settings: IGearSettings, containerType: IUserContainerType): Promise<IGearSettings> {
    const instance = new GearSettingsService()
    return instance.addContainerType(settings, containerType)
  }

  static async updateContainerType(settings: IGearSettings, containerType: IUserContainerType): Promise<IGearSettings> {
    const instance = new GearSettingsService()
    return instance.updateContainerType(settings, containerType)
  }

  static async removeContainerType(settings: IGearSettings, containerTypeId: string): Promise<IGearSettings> {
    const instance = new GearSettingsService()
    return instance.removeContainerType(settings, containerTypeId)
  }

  static async addBrand(settings: IGearSettings, brand: IUserBrand): Promise<IGearSettings> {
    const instance = new GearSettingsService()
    return instance.addBrand(settings, brand)
  }

  static async updateBrand(settings: IGearSettings, brand: IUserBrand): Promise<IGearSettings> {
    const instance = new GearSettingsService()
    return instance.updateBrand(settings, brand)
  }

  static async removeBrand(settings: IGearSettings, brandId: string): Promise<IGearSettings> {
    const instance = new GearSettingsService()
    return instance.removeBrand(settings, brandId)
  }
}

export { GearSettingsService }
export const gearSettingsService = new GearSettingsService()
