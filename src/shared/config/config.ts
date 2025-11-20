// shared/config/config.ts

// Supported locales type (defined here to avoid cyclic dependencies)
export type SupportedLocale = 'en' | 'pl'

export type TGearWeightUnit = 'g' | 'kg' | 'oz' | 'lb'

export const config = {
  app: {
    id: import.meta.env.VITE_APP_ID ?? 'gear-stack',
    name: import.meta.env.VITE_APP_NAME ?? 'Gear Stack',
    description: import.meta.env.VITE_APP_DESCRIPTION ?? 'Gear Stack for managing survival gear and bug-out bag equipment.',
  },
  i18n: {
    defaultLocale: (import.meta.env.VITE_DEFAULT_LOCALE ?? 'en') as SupportedLocale,
    fallbackLocale: (import.meta.env.VITE_FALLBACK_LOCALE ?? 'en') as SupportedLocale,
  },
  contact: {
    email: import.meta.env.VITE_CONTACT_EMAIL ?? 'contact@dev-made.it',
  },
  defaults: {
    preferredWeightUnit: 'g' as TGearWeightUnit,
  },
}

// osobna zmienna do użycia w localStorage / store
export const DARK_MODE_STORAGE_KEY = `${config.app.id}:dark-mode`
export const JWT_STORE_KEY = `${config.app.id}:token`
export const LOCALE_STORAGE_KEY = `${config.app.id}:locale`
export const SETTINGS_STORAGE_KEY = `${config.app.id}:settings`
export const USER_STORAGE_KEY = `${config.app.id}:user`
export const ITEMS_TABLE_COLUMN_VISIBILITY_KEY = `${config.app.id}:items-table-column-visibility`
export const ALL_ITEMS_TABLE_COLUMN_VISIBILITY_KEY = `${config.app.id}:all-items-table-column-visibility`
