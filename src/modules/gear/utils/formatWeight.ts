import type { TGearWeightUnit } from '../types/gear.types'
import { GRAMS_PER_KILOGRAM, GRAMS_PER_OUNCE, GRAMS_PER_POUND, WEIGHT_DECIMAL_PLACES } from './constants'

/**
 * Converts weight to grams for internal calculations
 * @param weight - Weight value
 * @param unit - Weight unit (g, kg, oz, or lb)
 * @returns Weight in grams
 */
export function convertToGrams(weight: number, unit: TGearWeightUnit): number {
  switch (unit) {
    case 'kg':
      return weight * GRAMS_PER_KILOGRAM
    case 'lb':
      return weight * GRAMS_PER_POUND
    case 'oz':
      return weight * GRAMS_PER_OUNCE
    case 'g':
    default:
      return weight
  }
}

/**
 * Converts weight from grams to specified unit
 * @param weightInGrams - Weight in grams
 * @param targetUnit - Target unit (g, kg, oz, or lb)
 * @returns Weight in target unit
 */
export function convertFromGrams(weightInGrams: number, targetUnit: TGearWeightUnit): number {
  switch (targetUnit) {
    case 'kg':
      return weightInGrams / GRAMS_PER_KILOGRAM
    case 'lb':
      return weightInGrams / GRAMS_PER_POUND
    case 'oz':
      return weightInGrams / GRAMS_PER_OUNCE
    case 'g':
    default:
      return weightInGrams
  }
}

/**
 * Formats weight value with unit to a display string
 * @param weight - Weight value
 * @param unit - Weight unit (g, kg, oz, or lb)
 * @returns Formatted weight string (e.g., "1.50 kg", "500 g", "16 oz", "2.5 lb")
 */
export function formatWeight(weight: number, unit: TGearWeightUnit): string {
  switch (unit) {
    case 'kg':
      return `${weight.toFixed(WEIGHT_DECIMAL_PLACES)} kg`
    case 'lb':
      return `${weight.toFixed(WEIGHT_DECIMAL_PLACES)} lb`
    case 'oz':
      return `${weight.toFixed(WEIGHT_DECIMAL_PLACES)} oz`
    case 'g':
    default:
      return `${weight} g`
  }
}

/**
 * Formats weight in grams to a formatted string (for backward compatibility)
 * Automatically chooses best unit (kg if >= 1000g, otherwise g)
 * @param weightInGrams - Weight in grams
 * @returns Formatted weight string (e.g., "1.50 kg" or "500 g")
 */
export function formatWeightFromGrams(weightInGrams: number): string {
  if (weightInGrams >= GRAMS_PER_KILOGRAM) {
    return `${(weightInGrams / GRAMS_PER_KILOGRAM).toFixed(WEIGHT_DECIMAL_PLACES)} kg`
  }
  return `${weightInGrams} g`
}

/**
 * Formats weight in grams to a formatted string using preferred unit
 * @param weightInGrams - Weight in grams
 * @param preferredUnit - Preferred weight unit (g, kg, oz, or lb)
 * @returns Formatted weight string (e.g., "1.50 kg", "500 g", "16 oz", "2.5 lb")
 */
export function formatWeightToPreferredUnit(weightInGrams: number, preferredUnit: TGearWeightUnit): string {
  switch (preferredUnit) {
    case 'kg': {
      const weightInKg = weightInGrams / GRAMS_PER_KILOGRAM
      return `${weightInKg.toFixed(WEIGHT_DECIMAL_PLACES)} kg`
    }
    case 'lb': {
      const weightInLb = weightInGrams / GRAMS_PER_POUND
      return `${weightInLb.toFixed(WEIGHT_DECIMAL_PLACES)} lb`
    }
    case 'oz': {
      const weightInOz = weightInGrams / GRAMS_PER_OUNCE
      return `${weightInOz.toFixed(WEIGHT_DECIMAL_PLACES)} oz`
    }
    case 'g':
    default:
      return `${weightInGrams.toFixed(WEIGHT_DECIMAL_PLACES)} g`
  }
}

/**
 * Formats weight value with original unit, converting to preferred unit for display
 * @param weight - Weight value
 * @param originalUnit - Original weight unit (g, kg, oz, or lb)
 * @param preferredUnit - Preferred weight unit (g, kg, oz, or lb)
 * @returns Formatted weight string in preferred unit
 */
export function formatWeightWithPreferredUnit(weight: number, originalUnit: TGearWeightUnit, preferredUnit: TGearWeightUnit): string {
  // Convert to grams first
  const weightInGrams = convertToGrams(weight, originalUnit)
  // Then format to preferred unit
  return formatWeightToPreferredUnit(weightInGrams, preferredUnit)
}

