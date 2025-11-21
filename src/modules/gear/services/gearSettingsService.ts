import { GEAR_SETTINGS_STORAGE_KEY, SETTINGS_STORAGE_KEY } from '@/shared/config/config'
import type { IGearSettings, IUpdateGearSettingsDto, IUserCategory, IUserContainerType } from '../types/gearSettings.types'

/**
 * Gear Settings Service
 * Handles gear-specific settings: custom categories and container types
 */
export class GearSettingsService {
  private static readonly STORAGE_KEY = GEAR_SETTINGS_STORAGE_KEY
  private static readonly OLD_STORAGE_KEY = SETTINGS_STORAGE_KEY // For migration

  /**
   * Migrate from old storage format if needed
   */
  private static migrateFromOldStorage(): Partial<IGearSettings> | null {
    const oldStored = localStorage.getItem(this.OLD_STORAGE_KEY)
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
  static loadFromStorage(): IGearSettings {
    const stored = localStorage.getItem(this.STORAGE_KEY)
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
        this.saveToStorage({
          customCategories: migrated.customCategories ?? [],
          customContainerTypes: migrated.customContainerTypes ?? [],
        })
      }
    }

    return {
      customCategories: settings.customCategories ?? [],
      customContainerTypes: settings.customContainerTypes ?? [],
    }
  }

  /**
   * Save gear settings to localStorage
   */
  static saveToStorage(settings: IGearSettings): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify({
        customCategories: settings.customCategories,
        customContainerTypes: settings.customContainerTypes,
      }))
    } catch (error) {
      console.error('Error saving gear settings to storage:', error)
    }
  }

  /**
   * Update gear settings
   */
  static updateSettings(current: IGearSettings, updates: IUpdateGearSettingsDto): IGearSettings {
    const updated: IGearSettings = {
      customCategories: updates.customCategories ?? current.customCategories,
      customContainerTypes: updates.customContainerTypes ?? current.customContainerTypes,
    }

    this.saveToStorage(updated)
    return updated
  }

  /**
   * Add a custom category
   */
  static addCategory(settings: IGearSettings, category: IUserCategory): IGearSettings {
    const updated = {
      ...settings,
      customCategories: [...settings.customCategories, category],
    }
    this.saveToStorage(updated)
    return updated
  }

  /**
   * Update a custom category
   */
  static updateCategory(settings: IGearSettings, category: IUserCategory): IGearSettings {
    const updated = {
      ...settings,
      customCategories: settings.customCategories.map(c => c.id === category.id ? category : c),
    }
    this.saveToStorage(updated)
    return updated
  }

  /**
   * Remove a custom category
   */
  static removeCategory(settings: IGearSettings, categoryId: string): IGearSettings {
    const updated = {
      ...settings,
      customCategories: settings.customCategories.filter(c => c.id !== categoryId),
    }
    this.saveToStorage(updated)
    return updated
  }

  /**
   * Add a custom container type
   */
  static addContainerType(settings: IGearSettings, containerType: IUserContainerType): IGearSettings {
    const updated = {
      ...settings,
      customContainerTypes: [...settings.customContainerTypes, containerType],
    }
    this.saveToStorage(updated)
    return updated
  }

  /**
   * Update a custom container type
   */
  static updateContainerType(settings: IGearSettings, containerType: IUserContainerType): IGearSettings {
    const updated = {
      ...settings,
      customContainerTypes: settings.customContainerTypes.map(t => t.id === containerType.id ? containerType : t),
    }
    this.saveToStorage(updated)
    return updated
  }

  /**
   * Remove a custom container type
   */
  static removeContainerType(settings: IGearSettings, containerTypeId: string): IGearSettings {
    const updated = {
      ...settings,
      customContainerTypes: settings.customContainerTypes.filter(t => t.id !== containerTypeId),
    }
    this.saveToStorage(updated)
    return updated
  }
}
