/**
 * TypeScript type definitions for catalogue_items.json
 *
 * This file defines types that match the structure of catalogue_items.json
 * Used for type safety when working with catalogue items data.
 */

import type catalogueItemsJson from './catalogue_items.json'

export interface CatalogueItemShop {
  url: string
  variant?: string
  price?: number
  currency?: string
  updated_at?: string
}

export interface CatalogueItem {
  id: string
  name: string
  category: string
  brand: string
  model: string
  description?: string
  price_tier?: 'low' | 'medium' | 'high'
  quality?: 'low' | 'medium' | 'high'
  weight?: number
  weight_unit?: string
  url?: string
  image_filename?: string
  color?: string
  shops?: CatalogueItemShop[]
}

export type CatalogueItemCategory =
  | 'fire'
  | 'tools'
  | 'water'
  | 'shelter'
  | 'light'
  | 'firstAid'
  | 'other'
  | 'food'
  | 'navigation'
  | 'communication'

export type PriceTier = 'low' | 'medium' | 'high'

export type Quality = 'low' | 'medium' | 'high'

/**
 * Type for the entire catalogue_items.json array
 */
export type CatalogueItems = typeof catalogueItemsJson

/**
 * Type for a single catalogue item from the JSON array
 */
export type CatalogueItemFromJson = CatalogueItems[number]

