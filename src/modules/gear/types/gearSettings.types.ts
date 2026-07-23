import type { TGearWeightUnit } from './gear.types'

export interface IUserCategory {
  id: string
  value: string
  createdAt: string
  updatedAt: string
}

export interface IUserContainerType {
  id: string
  value: string
  createdAt: string
  updatedAt: string
}

export interface IUserBrand {
  id: string
  value: string
  createdAt: string
  updatedAt: string
}

export interface IVisualizationCustomZone {
  id: string
  name: string
  iconKey: string
  createdAt: string
  updatedAt: string
}

// containerId -> zoneId (default zone id or custom zone id) DnD override
export type TVisualizationPlacements = Record<string, string>

export interface IGearSettings {
  customCategories: IUserCategory[]
  customContainerTypes: IUserContainerType[]
  customBrands: IUserBrand[]
  visualizationCustomZones: IVisualizationCustomZone[]
  visualizationPlacements: TVisualizationPlacements
  preferredWeightUnit?: TGearWeightUnit
  defaultCurrency?: string
}

export interface IUpdateGearSettingsDto {
  customCategories?: IUserCategory[]
  customContainerTypes?: IUserContainerType[]
  customBrands?: IUserBrand[]
  visualizationCustomZones?: IVisualizationCustomZone[]
  visualizationPlacements?: TVisualizationPlacements
  preferredWeightUnit?: TGearWeightUnit
  defaultCurrency?: string
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

  // Visualization custom zone operations
  addVisualizationZone(settings: IGearSettings, zone: IVisualizationCustomZone): Promise<IGearSettings>
  updateVisualizationZone(settings: IGearSettings, zone: IVisualizationCustomZone): Promise<IGearSettings>
  removeVisualizationZone(settings: IGearSettings, zoneId: string): Promise<IGearSettings>

  // Visualization placement (DnD override) operations
  setContainerZone(settings: IGearSettings, containerId: string, zoneId: string): Promise<IGearSettings>
}

