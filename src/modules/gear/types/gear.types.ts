import type { TDateTime, TUUID } from '@/shared/types/base.type'

// Typ kontenera - może być domyślny lub własny (custom)
export type TGearContainerType =
  | 'backpack'
  | 'bag'
  | 'pouch'
  | 'box'
  | 'cabinet'
  | 'vehicle'
  | 'shelf'
  | 'drawer'
  | 'case'
  | 'trunk'
  | 'other'
  | string // Allow custom container types

// Status przedmiotu
export type TGearItemStatus = 'owned' | 'missing' | 'toBuy'

// Priorytet przedmiotu
export type TGearItemPriority = 'critical' | 'high' | 'medium' | 'low'

// Półka cenowa / jakość
export type TGearItemQuality = 'low' | 'medium' | 'high'

// Jednostka wagi
export type TGearWeightUnit = 'g' | 'kg' | 'oz' | 'lb'

// Container color options
export type TContainerColor =
  | 'default'  // No color (gray/neutral)
  | 'blue'
  | 'green'
  | 'red'
  | 'yellow'
  | 'purple'
  | 'orange'
  | 'pink'
  | 'teal'
  | 'indigo'

// Kategoria przedmiotu - może być domyślna lub własna (custom)
export type TGearItemCategory =
  | 'water'
  | 'food'
  | 'shelter'
  | 'fire'
  | 'firstAid'
  | 'tools'
  | 'navigation'
  | 'communication'
  | 'clothing'
  | 'hygiene'
  | 'light'
  | 'other'
  | string // Allow custom categories

// Pojedynczy przedmiot
export interface IGearItem {
  id: TUUID
  name: string
  category: TGearItemCategory
  quantity: number
  weight: number // wartość wagi
  weightUnit: TGearWeightUnit // jednostka wagi (g lub kg)
  notes?: string
  expirationDate?: TDateTime // ISO date string
  priority: TGearItemPriority
  status: TGearItemStatus
  containerId?: TUUID // Reference to a nested container (if this item is a container)
  // Extended fields
  price?: number // Price in currency (optional)
  url?: string // Link to product, review, etc.
  brand?: string // Manufacturer/brand
  color?: string // Item color
  quality?: TGearItemQuality // Price tier / quality
  wearable?: boolean // Item is worn/carried on person (e.g., clothing, watch)
  consumable?: boolean // Item is consumed/used up (e.g., food, medicine, fuel)
  createdAt: TDateTime
  updatedAt: TDateTime
}

// Kontener (plecak/zestaw)
export interface IGearContainer {
  id: TUUID
  name: string
  description?: string
  type: TGearContainerType
  color?: TContainerColor  // Optional, defaults to 'default'
  parentContainerId?: TUUID // Parent container ID (if this container is nested)
  hideWhenNested?: boolean // Hide from main list when nested in another container
  // Extended fields
  brand?: string // Manufacturer/brand
  price?: number // Price in currency (optional)
  weight?: number // Container weight value
  weightUnit?: TGearWeightUnit // Container weight unit (g or kg)
  maxWeight?: number // Maximum weight limit value
  maxWeightUnit?: TGearWeightUnit // Maximum weight unit (g or kg)
  url?: string // Link to product, review, etc.
  items: IGearItem[]
  createdAt: TDateTime
  updatedAt: TDateTime
}

// DTO dla tworzenia kontenera
export interface ICreateContainerDto {
  name: string
  description?: string
  type: TGearContainerType
  color?: TContainerColor
  parentContainerId?: TUUID
  hideWhenNested?: boolean
  brand?: string
  price?: number
  weight?: number
  weightUnit?: TGearWeightUnit
  maxWeight?: number
  maxWeightUnit?: TGearWeightUnit
  url?: string
}

// DTO dla aktualizacji kontenera
export interface IUpdateContainerDto {
  name?: string
  description?: string
  type?: TGearContainerType
  color?: TContainerColor
  parentContainerId?: TUUID
  hideWhenNested?: boolean
  brand?: string
  price?: number
  weight?: number
  weightUnit?: TGearWeightUnit
  maxWeight?: number
  maxWeightUnit?: TGearWeightUnit
  url?: string
}

// DTO dla tworzenia przedmiotu
export interface ICreateItemDto {
  name: string
  category: TGearItemCategory
  quantity: number
  weight: number
  weightUnit: TGearWeightUnit
  notes?: string
  expirationDate?: TDateTime
  priority: TGearItemPriority
  status: TGearItemStatus
  containerId?: TUUID // Reference to a nested container (if this item is a container)
  price?: number
  url?: string
  brand?: string
  color?: string
  quality?: TGearItemQuality
  wearable?: boolean
  consumable?: boolean
}

// DTO dla aktualizacji przedmiotu
export interface IUpdateItemDto {
  name?: string
  category?: TGearItemCategory
  quantity?: number
  weight?: number
  weightUnit?: TGearWeightUnit
  notes?: string
  expirationDate?: TDateTime
  priority?: TGearItemPriority
  status?: TGearItemStatus
  containerId?: TUUID // Reference to a nested container (if this item is a container)
  price?: number
  url?: string
  brand?: string
  color?: string
  quality?: TGearItemQuality
  wearable?: boolean
  consumable?: boolean
}

// Service interface for gear operations
// This interface defines the common contract for both localStorage and API implementations
export interface IGearService {
  // Container operations (CRUD)
  createContainer(data: ICreateContainerDto): Promise<IGearContainer>
  getContainers(skip?: number, limit?: number): Promise<IGearContainer[]>
  getContainer(id: TUUID): Promise<IGearContainer>
  updateContainer(id: TUUID, data: IUpdateContainerDto): Promise<IGearContainer>
  deleteContainer(id: TUUID): Promise<void>

  // Item operations (CRUD)
  createItem(containerId: TUUID, data: ICreateItemDto): Promise<IGearItem>
  getItems(containerId: TUUID, skip?: number, limit?: number): Promise<IGearItem[]>
  getItem(itemId: TUUID): Promise<IGearItem>
  updateItem(itemId: TUUID, data: IUpdateItemDto): Promise<IGearItem>
  deleteItem(itemId: TUUID): Promise<void>

  // Statistics operations (from API or calculated locally)
  getContainerWeight(containerId: TUUID): Promise<{ grams: number; kilograms: number }>
  getContainerReadiness(containerId: TUUID): Promise<{
    totalItems: number
    ownedItems: number
    missingItems: number
    toBuyItems: number
    readinessPercentage: number
  }>
}

// Extended interface for localStorage-specific operations
// These methods are only available in localStorage implementation
// API implementation may throw "Not implemented" or provide fallback behavior
export interface IGearServiceExtended extends IGearService {
  // Additional container operations (localStorage-specific)
  getAllContainers(): Promise<IGearContainer[]>
  getRootContainers(): Promise<IGearContainer[]>
  getNestedContainers(containerId: TUUID): Promise<IGearContainer[]>
  deleteAllContainers(): Promise<void>

  // Additional item operations (localStorage-specific)
  getItemById(containerId: TUUID, itemId: TUUID): Promise<IGearItem | undefined>

  // Business logic operations (calculated locally)
  calculateTotalWeight(containerId: TUUID): Promise<number>
  calculateReadinessPercentage(containerId: TUUID): Promise<number>
  calculateWeightLimitPercentage(containerId: TUUID): Promise<number | null>
  isWeightLimitExceeded(containerId: TUUID): Promise<boolean>
  getItemsByStatus(containerId: TUUID, status: TGearItemStatus): Promise<IGearItem[]>
  getExpiredItems(containerId: TUUID): Promise<IGearItem[]>
  getExpiringSoonItems(containerId: TUUID, days?: number): Promise<IGearItem[]>
  moveItem(containerId: TUUID, itemId: TUUID, newContainerId: TUUID): Promise<void>

  // Import/Export operations (localStorage-specific)
  exportData(): Promise<string>
  importData(json: string): Promise<void>
}

