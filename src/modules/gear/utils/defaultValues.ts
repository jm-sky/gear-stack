import type { ICreateItemDto, TGearWeightUnit } from '../types/gear.types'
import { toBasicWeightUnit } from './weightUnits'

/**
 * Default values for creating new items
 * These values are pre-filled in the form to speed up item creation
 */
export const DEFAULT_ITEM_VALUES: ICreateItemDto = {
  name: '',
  quantity: 1,
  weight: 0.1, // 0.1 kg (100g) - reasonable default
  weightUnit: 'kg',
  status: 'owned',
  priority: 'medium',
  category: 'other',
}

/** Default weight (~100 g) expressed in each basic unit */
const DEFAULT_WEIGHT_BY_UNIT = { g: 100, kg: 0.1, oz: 3.5, lb: 0.22 } as const

/**
 * Get default values for a new item
 * @param preferredWeightUnit - User's preferred unit from gear settings; the default weight
 *   unit follows it (auto-* options resolve to their base unit). Falls back to kg when omitted.
 * @returns Default values object that can be spread into form initial values
 */
export function getDefaultItemValues(preferredWeightUnit?: TGearWeightUnit | null): ICreateItemDto {
  if (!preferredWeightUnit) return { ...DEFAULT_ITEM_VALUES }
  const weightUnit = toBasicWeightUnit(preferredWeightUnit)
  return { ...DEFAULT_ITEM_VALUES, weight: DEFAULT_WEIGHT_BY_UNIT[weightUnit], weightUnit }
}

