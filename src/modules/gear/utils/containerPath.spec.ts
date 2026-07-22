import { describe, expect, it } from 'vitest'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { buildContainerPath, buildParentContainerPath } from './containerPath'

function makeContainer(id: string, name: string, parentItemId: string | null = null): IGearItemV2 {
  return {
    id,
    userId: 'u1',
    itemType: 'container',
    parentItemId,
    name,
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
  } as IGearItemV2
}

describe('containerPath', () => {
  const byId = new Map<string, IGearItemV2>([
    ['d', makeContainer('d', 'Deep', 'n')],
    ['n', makeContainer('n', 'Nested', 'r')],
    ['r', makeContainer('r', 'Root')],
  ])

  it('buildContainerPath returns full breadcrumb', () => {
    expect(buildContainerPath('d', byId)).toBe('Root › Nested › Deep')
    expect(buildContainerPath('r', byId)).toBe('Root')
  })

  it('buildParentContainerPath excludes the container itself', () => {
    expect(buildParentContainerPath('d', byId)).toBe('Root › Nested')
    expect(buildParentContainerPath('r', byId)).toBe('')
  })
})
