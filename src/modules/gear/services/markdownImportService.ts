import type { ICreateItemDto } from '../types/gear.types'
import { SUGGESTED_BRANDS, SUGGESTED_COLORS } from '../utils/suggestedValues'

/**
 * Result of parsing markdown content
 */
export interface IMarkdownImportResult {
  containers: Array<{
    name: string
    id?: string // Container ID from [#id] in header
    items: Array<ICreateItemDto & { nestedContainerId?: string }> // nestedContainerId is temporary slug reference
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
    let currentContainer: { name: string; id?: string; items: ICreateItemDto[] } | null = null

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]?.trim()
      if (!line) continue

      // Container header (## Header [#id] (Type))
      if (line.startsWith('## ')) {
        if (currentContainer && currentContainer.items.length > 0) {
          result.containers.push(currentContainer)
        }

        let headerText = line.substring(3).trim()
        let containerId: string | undefined

        // Extract ID from [#id]
        const idMatch = headerText.match(/\[#([^\]]+)\]/)
        if (idMatch) {
          containerId = idMatch[1]?.trim()
          headerText = headerText.replace(idMatch[0] ?? '', '').trim()
        }

        // Extract container name (remove type in parentheses if present)
        const nameMatch = headerText.match(/^([^(]+)/)
        const containerName = (nameMatch ? nameMatch[1]?.trim() : headerText) || headerText

        currentContainer = {
          name: containerName,
          id: containerId,
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
   * New format: - **Item Name** x2 (Brand, Color) [#container-id] (Status) - 500g
   * Old format: - Item name **Brand** (params) x5
   * Flexible: Parser will try to guess all fields
   */
  private parseItemLine(line: string): (ICreateItemDto & { nestedContainerId?: string }) | null {
    if (!line) return null

    let workingLine = line
    let name = ''
    let brand: string | undefined
    let color: string | undefined
    let status: 'owned' | 'missing' | 'toBuy' = 'owned'
    let quantity = 1
    let weight = 100 // Default weight
    let weightUnit: 'g' | 'kg' = 'g'
    let expirationDate: string | undefined
    let url: string | undefined
    let nestedContainerId: string | undefined

    // 1. Extract bold text as item name (new format: **Item Name**)
    const boldMatch = workingLine.match(/\*\*([^*]+)\*\*/)
    if (boldMatch) {
      name = boldMatch[1]?.trim() ?? ''
      workingLine = workingLine.replace(boldMatch[0] ?? '', '').trim()
    }

    // 2. Extract weight at the end (- 500g or - 2.5kg)
    const weightMatch = workingLine.match(/[-–—]\s*(\d+(?:[.,]\d+)?)\s*(g|kg)\s*$/i)
    if (weightMatch) {
      weight = Number.parseFloat((weightMatch[1] ?? '100').replace(',', '.'))
      weightUnit = (weightMatch[2]?.toLowerCase() === 'kg' ? 'kg' : 'g') as 'g' | 'kg'
      workingLine = workingLine.substring(0, weightMatch.index).trim()
    }

    // 3. Extract container ID [#id] (for nested containers)
    const containerIdMatch = workingLine.match(/\[#([^\]]+)\]/)
    if (containerIdMatch) {
      nestedContainerId = containerIdMatch[1]?.trim()
      workingLine = workingLine.replace(containerIdMatch[0] ?? '', '').trim()
    }

    // 4. Extract URL (in angle brackets <url> or plain http://|https://|www.)
    const urlMatch = workingLine.match(/<([^>]+)>|(\bhttps?:\/\/[^\s]+)|(\bwww\.[^\s]+)/)
    if (urlMatch) {
      url = (urlMatch[1] ?? urlMatch[2] ?? urlMatch[3])?.trim()
      // Add protocol if missing (www. case)
      if (url && url.startsWith('www.') && !url.startsWith('http')) {
        url = `https://${url}`
      }
      workingLine = workingLine.replace(urlMatch[0] ?? '', '').trim()
    }

    // 4. Extract quantity (xN or ×N anywhere in the line)
    const quantityMatch = workingLine.match(/[x×](\d+)/i)
    if (quantityMatch) {
      quantity = Number.parseInt(quantityMatch[1] ?? '1', 10)
      workingLine = workingLine.replace(quantityMatch[0] ?? '', '').trim()
    }

    // 4. Extract all parentheses groups
    const parenthesesGroups: string[] = []
    let parenthesesMatch
    const parenthesesRegex = /\(([^)]+)\)/g
    while ((parenthesesMatch = parenthesesRegex.exec(workingLine)) !== null) {
      parenthesesGroups.push(parenthesesMatch[1] ?? '')
    }
    workingLine = workingLine.replace(/\([^)]*\)/g, '').trim()

    // 5. Parse parentheses groups
    // First group is typically (Brand, Color)
    // Second group is typically (Status) or (Expiration: date)
    if (parenthesesGroups.length > 0) {
      const firstGroup = parenthesesGroups[0] ?? ''
      const parts = firstGroup.split(',').map(p => p.trim())

      for (const part of parts) {
        // Check for expiration
        if (part.toLowerCase().includes('expiration:')) {
          const dateMatch = part.match(/expiration:\s*(\d{2}[./-]\d{2}[./-]\d{4})/i)
          if (dateMatch) {
            // Convert DD.MM.YYYY to ISO format
            const dateParts = dateMatch[1]?.split(/[./-]/)
            if (dateParts && dateParts.length === 3) {
              expirationDate = `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`
            }
          }
          continue
        }

        // Check for status
        const statusLower = part.toLowerCase()
        if (statusLower.includes('missing') || statusLower.includes('brakuje')) {
          status = 'missing'
          continue
        }
        if (statusLower.includes('to buy') || statusLower.includes('do kupienia')) {
          status = 'toBuy'
          continue
        }
        if (statusLower.includes('owned') || statusLower.includes('posiadane')) {
          status = 'owned'
          continue
        }

        // Check if it's a brand
        const matchedBrand = this.matchBrand(part)
        if (matchedBrand && !brand) {
          brand = matchedBrand
          continue
        }

        // Check if it's a color
        const matchedColor = this.matchColor(part)
        if (matchedColor && !color) {
          color = matchedColor
          continue
        }
      }
    }

    // Check second parentheses group for status/expiration
    if (parenthesesGroups.length > 1) {
      const secondGroup = parenthesesGroups[1] ?? ''
      const parts = secondGroup.split(',').map(p => p.trim())

      for (const part of parts) {
        // Check for expiration
        if (part.toLowerCase().includes('expiration:')) {
          const dateMatch = part.match(/expiration:\s*(\d{2}[./-]\d{2}[./-]\d{4})/i)
          if (dateMatch) {
            const dateParts = dateMatch[1]?.split(/[./-]/)
            if (dateParts && dateParts.length === 3) {
              expirationDate = `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`
            }
          }
          continue
        }

        // Check for status
        const statusLower = part.toLowerCase()
        if (statusLower.includes('missing') || statusLower.includes('brakuje')) {
          status = 'missing'
          continue
        }
        if (statusLower.includes('to buy') || statusLower.includes('do kupienia')) {
          status = 'toBuy'
          continue
        }
      }
    }

    // 6. If name is still empty, try old format (brand in bold)
    if (!name) {
      name = workingLine.trim()
      // In old format, bold was brand, so if we have bold text already extracted,
      // and name is empty, use the remaining line as name
    }

    // 7. Fallback: if still no name from bold, use remaining line
    if (!name) {
      name = workingLine.trim()
    }

    // 8. Determine category from name
    const category = this.matchCategory(name)

    const item: ICreateItemDto & { nestedContainerId?: string } = {
      name,
      category,
      quantity,
      weight,
      weightUnit,
      priority: 'medium',
      status,
      brand,
      color,
      expirationDate,
      url,
      nestedContainerId, // Temporary slug reference to container
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
