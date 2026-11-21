import { describe, expect, it } from 'vitest'
import { getDefaultItemValues } from './defaultValues'

describe('getDefaultItemValues (F013 regression)', () => {
  it('keeps legacy kg default when no preference is given', () => {
    expect(getDefaultItemValues()).toMatchObject({ weight: 0.1, weightUnit: 'kg' })
  })

  it('follows the preferred weight unit from gear settings', () => {
    expect(getDefaultItemValues('g')).toMatchObject({ weight: 100, weightUnit: 'g' })
    expect(getDefaultItemValues('oz')).toMatchObject({ weightUnit: 'oz' })
    expect(getDefaultItemValues('lb')).toMatchObject({ weightUnit: 'lb' })
  })

  it('resolves auto modes to their base unit', () => {
    expect(getDefaultItemValues('auto-g-kg').weightUnit).toBe('g')
    expect(getDefaultItemValues('auto-oz-lb').weightUnit).toBe('oz')
  })
})
