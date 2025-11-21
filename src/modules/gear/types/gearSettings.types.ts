import type { TGearWeightUnit } from './gear.types'

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

export interface IUserBrand {
  id: string
  key: string // unique identifier (e.g., 'custom_brand_1')
  label: string
  createdAt: string
  updatedAt: string
}

export interface IGearSettings {
  customCategories: IUserCategory[]
  customContainerTypes: IUserContainerType[]
  customBrands: IUserBrand[]
  preferredWeightUnit?: TGearWeightUnit
}

export interface IUpdateGearSettingsDto {
  customCategories?: IUserCategory[]
  customContainerTypes?: IUserContainerType[]
  customBrands?: IUserBrand[]
  preferredWeightUnit?: TGearWeightUnit
}

// Service interface for gear settings operations
export interface IGearSettingsService {
  // Core operations
  loadFromStorage(): Promise<IGearSettings>
  saveToStorage(settings: IGearSettings): Promise<void>
  updateSettings(current: IGearSettings, updates: IUpdateGearSettingsDto): Promise<IGearSettings>

  // Category operations
  addCategory(settings: IGearSettings, category: IUserCategory): Promise<IGearSettings>
  updateCategory(settings: IGearSettings, category: IUserCategory): Promise<IGearSettings>
  removeCategory(settings: IGearSettings, categoryId: string): Promise<IGearSettings>

  // Container type operations
  addContainerType(settings: IGearSettings, containerType: IUserContainerType): Promise<IGearSettings>
  updateContainerType(settings: IGearSettings, containerType: IUserContainerType): Promise<IGearSettings>
  removeContainerType(settings: IGearSettings, containerTypeId: string): Promise<IGearSettings>

  // Brand operations
  addBrand(settings: IGearSettings, brand: IUserBrand): Promise<IGearSettings>
  updateBrand(settings: IGearSettings, brand: IUserBrand): Promise<IGearSettings>
  removeBrand(settings: IGearSettings, brandId: string): Promise<IGearSettings>
}

