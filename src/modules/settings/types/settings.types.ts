import type { SupportedLocale } from '@/shared/i18n'

export interface IUserCategory {
  id: string
  key: string // unique identifier (e.g., 'custom1', 'custom2')
  label: string
  createdAt: string
  updatedAt: string
}

export interface IUserContainerType {
  id: string
  key: string // unique identifier (e.g., 'custom1', 'custom2')
  label: string
  createdAt: string
  updatedAt: string
}

export interface ISettings {
  locale: SupportedLocale
  darkMode: boolean
  customCategories: IUserCategory[]
  customContainerTypes: IUserContainerType[]
}

export interface IUpdateSettingsDto {
  locale?: SupportedLocale
  darkMode?: boolean
  customCategories?: IUserCategory[]
  customContainerTypes?: IUserContainerType[]
}

