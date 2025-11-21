import { SUGGESTED_BRANDS, SUGGESTED_COLORS } from './suggestedValues'

/**
 * Result of parameter recognition
 */
export interface IRecognizedParameters {
  brand?: string
  color?: string
}

/**
 * Recognize parameters (brand, color) from item name
 * Uses fuzzy matching against SUGGESTED_BRANDS (and custom brands) and SUGGESTED_COLORS
 *
 * @param name - Item name to analyze
 * @param customBrands - Optional array of custom user brands to include in matching
 * @returns Recognized parameters (brand and/or color)
 */
export function recognizeParameters(
  name: string,
  customBrands?: Array<{ label: string }>
): IRecognizedParameters {
  if (!name || name.trim().length === 0) {
    return {}
  }

  const normalizedName = name.toLowerCase().trim()
  const result: IRecognizedParameters = {}

  // Combine default and custom brands
  const allBrands = [
    ...SUGGESTED_BRANDS,
    ...(customBrands?.map(b => b.label) ?? []),
  ]

  // Match brand - check for brand names in the item name
  // Sort brands by length (longest first) to match longer names first
  const brandsByLength = [...allBrands].sort((a, b) => b.length - a.length)

  for (const brand of brandsByLength) {
    const normalizedBrand = brand.toLowerCase().trim()

    // Exact match (case-insensitive)
    if (normalizedName === normalizedBrand) {
      result.brand = brand
      break
    }

    // Contains match (fuzzy)
    // Check if brand name is contained in item name or vice versa
    const firstWord = normalizedName.split(' ')[0]
    if (
      normalizedName.includes(normalizedBrand) ||
      (firstWord && normalizedBrand.includes(firstWord)) // First word matches
    ) {
      // Avoid false positives - brand should be significant part
      if (normalizedBrand.length >= 3 && normalizedName.includes(normalizedBrand)) {
        result.brand = brand
        break
      }
    }
  }

  // Match color - check for color names in the item name
  // Sort colors by length (longest first) to match longer names first
  const colorsByLength = [...SUGGESTED_COLORS].sort((a, b) => b.length - a.length)

  for (const color of colorsByLength) {
    const normalizedColor = color.toLowerCase().trim()

    // Exact match (case-insensitive)
    if (normalizedName === normalizedColor) {
      result.color = color
      break
    }

    // Contains match (fuzzy)
    // Check if color name is contained in item name
    if (normalizedName.includes(normalizedColor)) {
      // Avoid false positives - color should be significant part
      if (normalizedColor.length >= 3) {
        result.color = color
        break
      }
    }
  }

  return result
}

/**
 * Recognize parameters for multiple items
 *
 * @param items - Array of items with names
 * @returns Map of item IDs to recognized parameters
 */
export function recognizeParametersForItems(
  items: Array<{ id: string; name: string }>
): Map<string, IRecognizedParameters> {
  const result = new Map<string, IRecognizedParameters>()

  for (const item of items) {
    const params = recognizeParameters(item.name)
    if (params.brand || params.color) {
      result.set(item.id, params)
    }
  }

  return result
}
