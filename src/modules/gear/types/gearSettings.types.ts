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
}

export interface IUpdateGearSettingsDto {
  customCategories?: IUserCategory[]
  customContainerTypes?: IUserContainerType[]
  customBrands?: IUserBrand[]
}

