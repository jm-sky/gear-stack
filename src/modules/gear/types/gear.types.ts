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
export type TGearWeightUnit = 'g' | 'kg'

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
  // Extended fields
  brand?: string // Manufacturer/brand
  price?: number // Price in currency (optional)
  weight?: number // Container weight value
  weightUnit?: TGearWeightUnit // Container weight unit (g or kg)
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
  brand?: string
  price?: number
  weight?: number
  weightUnit?: TGearWeightUnit
  url?: string
}

// DTO dla aktualizacji kontenera
export interface IUpdateContainerDto {
  name?: string
  description?: string
  type?: TGearContainerType
  color?: TContainerColor
  parentContainerId?: TUUID
  brand?: string
  price?: number
  weight?: number
  weightUnit?: TGearWeightUnit
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
}

