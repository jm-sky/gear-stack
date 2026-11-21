import { describe, expect, it } from 'vitest'
import type { IGearContainer, IGearItem } from '../types/gear.types'
import { calculateReadinessPercentageSyncV2, calculateTotalWeightSyncV2 } from './containerCalculationsV2'
import { buildContainerTreeFromApi } from './containerTree'

const makeItem = (overrides: Partial<IGearItem>): IGearItem => ({
  id: 'item-1',
  name: 'Item',
  category: 'other',
  quantity: 1,
  weight: 100,
  weightUnit: 'g',
  priority: 'medium',
  status: 'owned',
  createdAt: '2026-01-01T00:00:00Z',
  updatedAt: '2026-01-01T00:00:00Z',
  ...overrides,
})

const makeContainer = (items: IGearItem[]): IGearContainer => ({
  id: 'c-1',
  name: 'Shared bag',
  type: 'backpack',
  isPublic: true,
  favorite: false,
  items,
  createdAt: '2026-01-01T00:00:00Z',
  updatedAt: '2026-01-01T00:00:00Z',
})

describe('buildContainerTreeFromApi (F001/F020 regression)', () => {
  it('preserves primaryImageUrl when converting API items', () => {
    const tree = buildContainerTreeFromApi(makeContainer([
      makeItem({ id: 'a', primaryImageUrl: 'https://example.com/a.jpg' }),
      makeItem({ id: 'b' }),
    ]))

    expect(tree.items[0]?.primaryImageUrl).toBe('https://example.com/a.jpg')
    expect(tree.items[1]?.primaryImageUrl).toBeNull()
  })

  it('exposes API items as children of the container (previously dropped)', () => {
    const tree = buildContainerTreeFromApi(makeContainer([
      makeItem({ id: 'a', name: 'Tent' }),
      makeItem({ id: 'b', name: 'Stove' }),
    ]))

    expect(tree.items).toHaveLength(2)
    expect(tree.container.children?.map(c => c.name)).toEqual(['Tent', 'Stove'])
    expect(tree.items.every(i => i.itemType === 'item' && i.parentItemId === 'c-1')).toBe(true)
  })

  it('handles a container without items', () => {
    const tree = buildContainerTreeFromApi(makeContainer([]))
    expect(tree.items).toEqual([])
    expect(tree.container.children).toEqual([])
  })

  it('computes weight and readiness from local data, not the viewer store (F007)', () => {
    const tree = buildContainerTreeFromApi(makeContainer([
      makeItem({ id: 'a', weight: 500, weightUnit: 'g', status: 'owned' }),
      makeItem({ id: 'b', weight: 1, weightUnit: 'kg', quantity: 2, status: 'toBuy' }),
    ]))

    expect(calculateTotalWeightSyncV2('c-1', tree.getItemById, tree.getChildrenOfItem)).toBe(2500)
    expect(calculateReadinessPercentageSyncV2('c-1', tree.getItemById, tree.getChildrenOfItem)).toBe(50)
  })
})
