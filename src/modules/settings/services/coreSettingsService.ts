import { config, CORE_SETTINGS_STORAGE_KEY, LOCALE_STORAGE_KEY, SETTINGS_STORAGE_KEY, type SupportedLocale } from '@/shared/config/config'
import type { ICoreSettings, IUpdateCoreSettingsDto } from '../types/coreSettings.types'

/**
 * Core Settings Service
 * Handles core application settings: locale, dark mode, preferred weight unit
 */
export class CoreSettingsService {
  private static readonly STORAGE_KEY = CORE_SETTINGS_STORAGE_KEY
  private static readonly OLD_STORAGE_KEY = SETTINGS_STORAGE_KEY // For migration

  /**
   * Migrate from old storage format if needed
   */
  private static migrateFromOldStorage(): Partial<ICoreSettings> | null {
    const oldStored = localStorage.getItem(this.OLD_STORAGE_KEY)
    if (!oldStored) return null

    try {
      const oldSettings = JSON.parse(oldStored)
      return {
        locale: oldSettings.locale,
        darkMode: oldSettings.darkMode,
        preferredWeightUnit: oldSettings.preferredWeightUnit,
      }
    } catch {
      return null
    }
  }

  /**
   * Load core settings from localStorage
   */
  static loadFromStorage(): ICoreSettings {
    const stored = localStorage.getItem(this.STORAGE_KEY)
    let settings: Partial<ICoreSettings> = {}

    if (stored) {
      try {
        settings = JSON.parse(stored)
      } catch (error) {
        console.error('Error loading core settings from storage:', error)
      }
    } else {
      // Try to migrate from old storage
      const migrated = this.migrateFromOldStorage()
      if (migrated) {
        settings = migrated
        // Save to new location
        this.saveToStorage({
          locale: migrated.locale ?? 'en',
          darkMode: migrated.darkMode ?? false,
          preferredWeightUnit: migrated.preferredWeightUnit ?? config.defaults.preferredWeightUnit,
        })
      }
    }

    // Sync locale from useLocale's localStorage key (single source of truth)
    const localeFromStorage = localStorage.getItem(LOCALE_STORAGE_KEY)
    const locale: SupportedLocale = (localeFromStorage && (localeFromStorage === 'en' || localeFromStorage === 'pl'))
      ? localeFromStorage as SupportedLocale
      : (settings.locale ?? 'en')

    return {
      locale,
      darkMode: settings.darkMode ?? false,
      preferredWeightUnit: (settings.preferredWeightUnit === 'g' || settings.preferredWeightUnit === 'kg' || settings.preferredWeightUnit === 'oz' || settings.preferredWeightUnit === 'lb')
        ? settings.preferredWeightUnit
        : config.defaults.preferredWeightUnit,
    }
  }

  /**
   * Save core settings to localStorage
   */
  static saveToStorage(settings: ICoreSettings): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify({
        locale: settings.locale,
        darkMode: settings.darkMode,
        preferredWeightUnit: settings.preferredWeightUnit,
      }))
      // Sync locale to useLocale's localStorage key (single source of truth)
      localStorage.setItem(LOCALE_STORAGE_KEY, settings.locale)
    } catch (error) {
      console.error('Error saving core settings to storage:', error)
    }
  }

  /**
   * Update core settings
   */
  static updateSettings(current: ICoreSettings, updates: IUpdateCoreSettingsDto): ICoreSettings {
    const updated: ICoreSettings = {
      locale: updates.locale ?? current.locale,
      darkMode: updates.darkMode ?? current.darkMode,
      preferredWeightUnit: updates.preferredWeightUnit ?? current.preferredWeightUnit,
    }

    this.saveToStorage(updated)
    return updated
  }
}
