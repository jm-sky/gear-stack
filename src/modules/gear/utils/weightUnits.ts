/**
 * Weight units utilities
 * Single source of truth for weight units enum and validation
 */
import { z } from 'zod'
import type { TGearWeightUnit } from '../types/gear.types'

/**
 * Supported weight units as array for iteration
 */
export const WEIGHT_UNITS = ['g', 'kg', 'oz', 'lb'] as const

/**
 * Zod enum for weight unit validation
 * Use this for form validation schemas
 */
export const weightUnitEnum = z.enum(WEIGHT_UNITS)

/**
 * Type guard to check if a string is a valid weight unit
 */
export function isWeightUnit(value: string): value is TGearWeightUnit {
  return WEIGHT_UNITS.includes(value as TGearWeightUnit)
}

