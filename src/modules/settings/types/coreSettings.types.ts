import type { TGearWeightUnit } from '@/modules/gear/types/gear.types'
import type { SupportedLocale } from '@/shared/i18n'

export interface ICoreSettings {
  locale: SupportedLocale
  darkMode: boolean
  preferredWeightUnit: TGearWeightUnit
}

export interface IUpdateCoreSettingsDto {
  locale?: SupportedLocale
  darkMode?: boolean
  preferredWeightUnit?: TGearWeightUnit
}

