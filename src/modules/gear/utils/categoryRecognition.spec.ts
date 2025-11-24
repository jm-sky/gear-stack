import { describe, expect, it } from 'vitest'
import { recognizeCategory } from './categoryRecognition'

describe('categoryRecognition', () => {
  it('should return null for empty string', () => {
    expect(recognizeCategory('')).toBeNull()
    expect(recognizeCategory('   ')).toBeNull()
  })

  it('should recognize water category', () => {
    expect(recognizeCategory('Water Bottle')).toBe('water')
    expect(recognizeCategory('Canteen')).toBe('water')
    expect(recognizeCategory('Butelka')).toBe('water')
  })

  it('should recognize food category', () => {
    expect(recognizeCategory('Energy Bar')).toBe('food')
    expect(recognizeCategory('Meal Ration')).toBe('food')
    expect(recognizeCategory('Jedzenie')).toBe('food')
  })

  it('should recognize shelter category', () => {
    expect(recognizeCategory('Tent')).toBe('shelter')
    expect(recognizeCategory('Sleeping Bag')).toBe('shelter')
    expect(recognizeCategory('Namiot')).toBe('shelter')
  })

  it('should recognize fire category', () => {
    expect(recognizeCategory('Lighter')).toBe('fire')
    expect(recognizeCategory('Matches')).toBe('fire')
    expect(recognizeCategory('Zapałki')).toBe('fire')
  })

  it('should recognize firstAid category', () => {
    expect(recognizeCategory('First Aid Kit')).toBe('firstAid')
    expect(recognizeCategory('Medical Kit')).toBe('firstAid')
    expect(recognizeCategory('Apteczka')).toBe('firstAid')
  })

  it('should recognize tools category', () => {
    expect(recognizeCategory('Knife')).toBe('tools')
    expect(recognizeCategory('Multitool')).toBe('tools')
    expect(recognizeCategory('Nóż')).toBe('tools')
  })

  it('should recognize navigation category', () => {
    expect(recognizeCategory('Compass')).toBe('navigation')
    expect(recognizeCategory('GPS Device')).toBe('navigation')
    expect(recognizeCategory('Kompas')).toBe('navigation')
  })

  it('should recognize communication category', () => {
    expect(recognizeCategory('Radio')).toBe('communication')
    expect(recognizeCategory('Phone')).toBe('communication')
    expect(recognizeCategory('Telefon')).toBe('communication')
  })

  it('should recognize clothing category', () => {
    expect(recognizeCategory('Jacket')).toBe('clothing')
    expect(recognizeCategory('Boots')).toBe('clothing')
    expect(recognizeCategory('Kurtka')).toBe('clothing')
  })

  it('should recognize hygiene category', () => {
    expect(recognizeCategory('Soap')).toBe('hygiene')
    expect(recognizeCategory('Toothbrush')).toBe('hygiene')
    expect(recognizeCategory('Mydło')).toBe('hygiene')
  })

  it('should recognize light category', () => {
    expect(recognizeCategory('Flashlight')).toBe('light')
    expect(recognizeCategory('Headlamp')).toBe('light')
    expect(recognizeCategory('Latarka')).toBe('light')
  })

  it('should be case-insensitive', () => {
    expect(recognizeCategory('WATER BOTTLE')).toBe('water')
    expect(recognizeCategory('knife')).toBe('tools')
    expect(recognizeCategory('FlashLight')).toBe('light')
  })

  it('should match longer keywords first', () => {
    // "first aid" should match before just "first"
    expect(recognizeCategory('First Aid Kit')).toBe('firstAid')
  })

  it('should return null for unrecognized category', () => {
    expect(recognizeCategory('Random Item')).toBeNull()
    expect(recognizeCategory('Unknown Thing')).toBeNull()
  })

  it('should handle keywords in the middle of name', () => {
    expect(recognizeCategory('Tactical Knife')).toBe('tools')
    expect(recognizeCategory('Emergency Water Bottle')).toBe('water')
  })

  it('should handle Polish keywords', () => {
    expect(recognizeCategory('Woda')).toBe('water')
    expect(recognizeCategory('Jedzenie')).toBe('food')
    expect(recognizeCategory('Nóż')).toBe('tools')
    expect(recognizeCategory('Apteczka')).toBe('firstAid')
  })

  it('should handle partial matches', () => {
    expect(recognizeCategory('Hydration System')).toBe('water')
    expect(recognizeCategory('Fire Starter')).toBe('fire')
  })
})

