import type { TGearWeightUnit } from '../types/gear.types'
import { GRAMS_PER_KILOGRAM, WEIGHT_DECIMAL_PLACES } from './constants'

/**
 * Converts weight to grams for internal calculations
 * @param weight - Weight value
 * @param unit - Weight unit (g or kg)
 * @returns Weight in grams
 */
export function convertToGrams(weight: number, unit: TGearWeightUnit): number {
  if (unit === 'kg') {
    return weight * GRAMS_PER_KILOGRAM
  }
  return weight
}

/**
 * Converts weight from grams to specified unit
 * @param weightInGrams - Weight in grams
 * @param targetUnit - Target unit (g or kg)
 * @returns Weight in target unit
 */
export function convertFromGrams(weightInGrams: number, targetUnit: TGearWeightUnit): number {
  if (targetUnit === 'kg') {
    return weightInGrams / GRAMS_PER_KILOGRAM
  }
  return weightInGrams
}

/**
 * Formats weight value with unit to a display string
 * @param weight - Weight value
 * @param unit - Weight unit (g or kg)
 * @returns Formatted weight string (e.g., "1.50 kg" or "500 g")
 */
export function formatWeight(weight: number, unit: TGearWeightUnit): string {
  if (unit === 'kg') {
    return `${weight.toFixed(WEIGHT_DECIMAL_PLACES)} kg`
  }
  return `${weight} g`
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
 * @param preferredUnit - Preferred weight unit (g or kg)
 * @returns Formatted weight string (e.g., "1.50 kg" or "500 g")
 */
export function formatWeightToPreferredUnit(weightInGrams: number, preferredUnit: TGearWeightUnit): string {
  if (preferredUnit === 'kg') {
    const weightInKg = weightInGrams / GRAMS_PER_KILOGRAM
    return `${weightInKg.toFixed(WEIGHT_DECIMAL_PLACES)} kg`
  }
  return `${weightInGrams} g`
}

/**
 * Formats weight value with original unit, converting to preferred unit for display
 * @param weight - Weight value
 * @param originalUnit - Original weight unit (g or kg)
 * @param preferredUnit - Preferred weight unit (g or kg)
 * @returns Formatted weight string in preferred unit
 */
export function formatWeightWithPreferredUnit(weight: number, originalUnit: TGearWeightUnit, preferredUnit: TGearWeightUnit): string {
  // Convert to grams first
  const weightInGrams = convertToGrams(weight, originalUnit)
  // Then format to preferred unit
  return formatWeightToPreferredUnit(weightInGrams, preferredUnit)
}

