import { describe, expect, it } from 'vitest'
import type { IGearContainer } from '../types/gear.types'
import { getAllItems } from './getAllItems'

describe('getAllItems', () => {
  const createMockContainer = (
    id: string,
    name: string,
    items: IGearContainer['items'] = [],
  ): IGearContainer => ({
    id,
    name,
    type: 'backpack',
    isPublic: false,
    favorite: false,
    items,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  })

  const createMockItem = (
    id: string,
    name: string,
    overrides: Partial<IGearContainer['items'][0]> = {},
  ): IGearContainer['items'][0] => ({
    id,
    name,
    category: 'other',
    quantity: 1,
    weight: 100,
    weightUnit: 'g',
    priority: 'medium',
    status: 'owned',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
    ...overrides,
  })

  it('should return empty array for empty containers', () => {
    const containers: IGearContainer[] = []
    const result = getAllItems(containers)
    expect(result).toEqual([])
  })

  it('should return all items from single container', () => {
    const container = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Water Bottle'),
      createMockItem('item-2', 'Knife'),
    ])

    const result = getAllItems([container])

    expect(result).toHaveLength(2)
    expect(result[0]?.name).toBe('Water Bottle')
    expect(result[0]?.containerId).toBe('container-1')
    expect(result[0]?.containerName).toBe('Backpack')
    expect(result[1]?.name).toBe('Knife')
  })

  it('should return all items from multiple containers', () => {
    const container1 = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Water Bottle'),
    ])
    const container2 = createMockContainer('container-2', 'Pouch', [
      createMockItem('item-2', 'Knife'),
      createMockItem('item-3', 'Flashlight'),
    ])

    const result = getAllItems([container1, container2])

    expect(result).toHaveLength(3)
    expect(result[0]?.containerName).toBe('Backpack')
    expect(result[1]?.containerName).toBe('Pouch')
    expect(result[2]?.containerName).toBe('Pouch')
  })

  it('should exclude items from specified container', () => {
    const container1 = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Water Bottle'),
    ])
    const container2 = createMockContainer('container-2', 'Pouch', [
      createMockItem('item-2', 'Knife'),
    ])

    const result = getAllItems([container1, container2], 'container-1')

    expect(result).toHaveLength(1)
    expect(result[0]?.name).toBe('Knife')
    expect(result[0]?.containerId).toBe('container-2')
  })

  it('should include all item properties', () => {
    const container = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Water Bottle', {
        category: 'water',
        quantity: 2,
        weight: 500,
        weightUnit: 'g',
        status: 'owned',
        priority: 'high',
        brand: 'CamelBak',
        color: 'Black',
        expirationDate: '2025-12-31',
        wearable: false,
        consumable: true,
      }),
    ])

    const result = getAllItems([container])

    expect(result[0]).toMatchObject({
      id: 'item-1',
      name: 'Water Bottle',
      category: 'water',
      containerId: 'container-1',
      containerName: 'Backpack',
      quantity: 2,
      weight: 500,
      weightUnit: 'g',
      status: 'owned',
      priority: 'high',
      brand: 'CamelBak',
      color: 'Black',
      expirationDate: '2025-12-31',
      wearable: false,
      consumable: true,
    })
  })

  it('should handle optional fields with defaults', () => {
    const container = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Item', {
        weightUnit: undefined,
        brand: null,
        color: null,
        expirationDate: null,
        wearable: null,
        consumable: null,
      }),
    ])

    const result = getAllItems([container])

    expect(result[0]?.weightUnit).toBe('g') // Default
    expect(result[0]?.brand).toBeUndefined()
    expect(result[0]?.color).toBeUndefined()
    expect(result[0]?.expirationDate).toBeUndefined()
    expect(result[0]?.wearable).toBeUndefined()
    expect(result[0]?.consumable).toBeUndefined()
  })

  it('should handle container color with default', () => {
    const container = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'Item'),
    ])
    container.color = undefined

    const result = getAllItems([container])

    expect(result[0]?.containerColor).toBe('default')
  })

  it('should handle container with no items', () => {
    const container = createMockContainer('container-1', 'Empty Backpack', [])

    const result = getAllItems([container])

    expect(result).toHaveLength(0)
  })

  it('should preserve item order from containers', () => {
    const container = createMockContainer('container-1', 'Backpack', [
      createMockItem('item-1', 'First'),
      createMockItem('item-2', 'Second'),
      createMockItem('item-3', 'Third'),
    ])

    const result = getAllItems([container])

    expect(result[0]?.name).toBe('First')
    expect(result[1]?.name).toBe('Second')
    expect(result[2]?.name).toBe('Third')
  })
})

