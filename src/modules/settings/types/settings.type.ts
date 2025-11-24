import type { SupportedLocale } from '@/shared/i18n'

export type Theme = 'light' | 'dark'

export interface Settings {
  darkMode: boolean
  locale: SupportedLocale
  defaultContainersPublic: boolean
  profilePublic: boolean
  emailPublic: boolean
}

export interface UpdateSettingsData {
  darkMode?: boolean
  locale?: SupportedLocale
  defaultContainersPublic?: boolean
  profilePublic?: boolean
  emailPublic?: boolean
}

export interface ISettingsService {
  getSettings(): Promise<Settings>
  updateSettings(data: UpdateSettingsData): Promise<Settings>
}
