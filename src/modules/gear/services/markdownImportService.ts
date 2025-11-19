import type { ICreateItemDto } from '../types/gear.types'
import { SUGGESTED_BRANDS, SUGGESTED_COLORS } from '../utils/suggestedValues'

/**
 * Result of parsing markdown content
 */
export interface IMarkdownImportResult {
  containers: Array<{
    name: string
    items: ICreateItemDto[]
  }>
  errors: string[]
}

/**
 * Parsed item parameters from parentheses
 */
interface IItemParams {
  brand?: string
  color?: string
  category?: string
  quantity?: number
  weight?: number
  weightUnit?: 'g' | 'kg'
}

/**
 * Service for parsing markdown format into gear containers and items
 *
 * Format:
 * ## Container Name
 * - Item name **Brand Name** (param1, param2) x5
 * - Another item **Brand** ~25 m (color)
 *
 * Supported parameters in parentheses:
 * - Brand names (matched against SUGGESTED_BRANDS)
 * - Colors (matched against SUGGESTED_COLORS)
 * - Categories (matched against category keywords)
 * - Measurements like "~25 m", "195×60 cm"
 *
 * Supported patterns:
 * - xN or ×N at the end = quantity
 * - **Brand** in bold = brand name
 * - ~N m/cm/kg/g = weight/measurement
 */
class MarkdownImportService {
  private categoryKeywords: Record<string, string[]> = {
    water: ['butelka', 'bottle', 'water', 'woda', 'filtr'],
    food: ['racje', 'jedzenie', 'food', 'menażka', 'kubek', 'kuchenka', 'palnik', 'gaz'],
    shelter: ['namiot', 'tent', 'tarp', 'poncho', 'płaszcz', 'materac', 'mata', 'śpiwór', 'sleeping bag', 'worek', 'folia'],
    fire: ['zapalniczka', 'lighter', 'krzesiwo', 'fire', 'zapałki', 'matches', 'świeczka'],
    firstAid: ['apteczka', 'first aid', 'bandaż', 'plaster', 'gazik', 'elektrolity', 'tabletki', 'maseczka', 'rękawiczki nitrylowe'],
    tools: ['nóż', 'knife', 'multitool', 'scyzoryk', 'siekiera', 'axe', 'piła', 'saw', 'saperka', 'ostrzałka', 'osełka', 'kompas', 'compass', 'linijka'],
    navigation: ['kompas', 'compass', 'mapa', 'map', 'gps', 'lornetka', 'luneta'],
    communication: ['radio', 'telefon', 'phone', 'powerbank', 'ładowarka'],
    clothing: ['rękawice', 'gloves', 'chusta', 'bandana'],
    hygiene: ['chusteczki', 'tissues', 'szczoteczka', 'toothbrush', 'mydło'],
    light: ['latarka', 'flashlight', 'czołówka', 'headlamp', 'baterie', 'batteries', 'akumulator'],
    other: [],
  }

  /**
   * Parse markdown content into containers and items
   */
  parseMarkdown(markdown: string): IMarkdownImportResult {
    const result: IMarkdownImportResult = {
      containers: [],
      errors: [],
    }

    const lines = markdown.split('\n')
    let currentContainer: { name: string; items: ICreateItemDto[] } | null = null

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]?.trim()
      if (!line) continue

      // Container header (## Header)
      if (line.startsWith('## ')) {
        if (currentContainer && currentContainer.items.length > 0) {
          result.containers.push(currentContainer)
        }

        currentContainer = {
          name: line.substring(3).trim(),
          items: [],
        }
        continue
      }

      // Item line (- Item)
      if (line.startsWith('- ') && currentContainer) {
        try {
          const item = this.parseItemLine(line.substring(2).trim())
          if (item) {
            currentContainer.items.push(item)
          }
        } catch (error) {
          result.errors.push(`Line ${i + 1}: ${error instanceof Error ? error.message : 'Unknown error'}`)
        }
      }
    }

    // Add last container
    if (currentContainer && currentContainer.items.length > 0) {
      result.containers.push(currentContainer)
    }

    return result
  }

  /**
   * Parse a single item line
   * Format: Item name **Brand** (params) x5
   */
  private parseItemLine(line: string): ICreateItemDto | null {
    if (!line) return null

    // Extract quantity (xN or ×N at the end)
    let quantity = 1
    const quantityMatch = line.match(/[x×](\d+)\s*$/i)
    if (quantityMatch) {
      quantity = Number.parseInt(quantityMatch[1] ?? '1', 10)
      line = line.substring(0, quantityMatch.index).trim()
    }

    // Extract brand from **Bold**
    let brand: string | undefined
    const brandMatch = line.match(/\*\*([^*]+)\*\*/)
    if (brandMatch) {
      brand = this.matchBrand(brandMatch[1] ?? '')
      line = line.replace(brandMatch[0] ?? '', '').trim()
    }

    // Extract parameters from parentheses
    const params = this.parseParentheses(line)
    line = line.replace(/\([^)]*\)/g, '').trim()

    // Extract measurements like ~25 m, 195×60 cm
    const measurementMatch = line.match(/[~]?\s*(\d+(?:[.,]\d+)?)\s*([×x]\s*\d+(?:[.,]\d+)?)?\s*(m|cm|kg|g|mm|l|ml)/i)
    let weight = 100 // Default weight: 100g
    let weightUnit: 'g' | 'kg' = 'g'

    if (measurementMatch) {
      const value = Number.parseFloat((measurementMatch[1] ?? '0').replace(',', '.'))
      const unit = measurementMatch[3]?.toLowerCase()

      if (unit === 'kg') {
        weight = value
        weightUnit = 'kg'
      } else if (unit === 'g') {
        weight = value
        weightUnit = 'g'
      }

      line = line.replace(measurementMatch[0] ?? '', '').trim()
    }

    // Override with params if provided
    if (params.weight !== undefined) {
      weight = params.weight
    }
    if (params.weightUnit !== undefined) {
      weightUnit = params.weightUnit
    }
    if (params.brand !== undefined) {
      brand = params.brand
    }

    // Clean up name
    const name = line.trim()

    // Determine category
    const category = params.category ?? this.matchCategory(name)

    // Determine color
    const color = params.color

    const item: ICreateItemDto = {
      name,
      category,
      quantity: params.quantity ?? quantity,
      weight,
      weightUnit,
      priority: 'medium',
      status: 'owned',
      brand,
      color,
    }

    return item
  }

  /**
   * Parse content inside parentheses for parameters
   * Example: (olive, knife, 500g, x2)
   */
  private parseParentheses(line: string): IItemParams {
    const params: IItemParams = {}
    const match = line.match(/\(([^)]+)\)/)

    if (!match || !match[1]) {
      return params
    }

    const content = match[1].trim()
    const parts = content.split(',').map(p => p.trim())

    for (const part of parts) {
      // Try to match brand
      const brand = this.matchBrand(part)
      if (brand && !params.brand) {
        params.brand = brand
        continue
      }

      // Try to match color
      const color = this.matchColor(part)
      if (color && !params.color) {
        params.color = color
        continue
      }

      // Try to match category
      const category = this.matchCategory(part)
      if (category !== 'other' && !params.category) {
        params.category = category
        continue
      }

      // Try to match quantity (xN)
      const qtyMatch = part.match(/^[x×]?(\d+)$/i)
      if (qtyMatch) {
        params.quantity = Number.parseInt(qtyMatch[1] ?? '1', 10)
        continue
      }

      // Try to match weight (Ng, Nkg)
      const weightMatch = part.match(/^(\d+(?:[.,]\d+)?)\s*(g|kg)$/i)
      if (weightMatch) {
        params.weight = Number.parseFloat((weightMatch[1] ?? '0').replace(',', '.'))
        params.weightUnit = (weightMatch[2]?.toLowerCase() === 'kg' ? 'kg' : 'g') as 'g' | 'kg'
        continue
      }
    }

    return params
  }

  /**
   * Match text against known brands (case-insensitive, fuzzy)
   */
  private matchBrand(text: string): string | undefined {
    const normalized = text.toLowerCase().trim()

    // Exact match
    for (const brand of SUGGESTED_BRANDS) {
      if (brand.toLowerCase() === normalized) {
        return brand
      }
    }

    // Fuzzy match (contains)
    for (const brand of SUGGESTED_BRANDS) {
      if (normalized.includes(brand.toLowerCase()) || brand.toLowerCase().includes(normalized)) {
        return brand
      }
    }

    // If not matched, return as-is (custom brand)
    return text.trim() || undefined
  }

  /**
   * Match text against known colors (case-insensitive)
   */
  private matchColor(text: string): string | undefined {
    const normalized = text.toLowerCase().trim()

    for (const color of SUGGESTED_COLORS) {
      if (color.toLowerCase() === normalized) {
        return color
      }
    }

    // If not in suggested colors, return as-is (custom color)
    return text.trim() || undefined
  }

  /**
   * Match text against category keywords
   */
  private matchCategory(text: string): string {
    const normalized = text.toLowerCase()

    for (const [category, keywords] of Object.entries(this.categoryKeywords)) {
      for (const keyword of keywords) {
        if (normalized.includes(keyword)) {
          return category
        }
      }
    }

    return 'other'
  }
}

export const markdownImportService = new MarkdownImportService()
