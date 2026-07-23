import { describe, expect, it } from 'vitest'
import { getVisualizationZone, resolveZoneId } from './visualizationZones'

describe('visualizationZones', () => {
  describe('getVisualizationZone (containerType -> default zone)', () => {
    it('maps trunk to vehicle (not carry)', () => {
      expect(getVisualizationZone('trunk')).toBe('vehicle')
    })

    it('maps vehicle to vehicle', () => {
      expect(getVisualizationZone('vehicle')).toBe('vehicle')
    })

    it('maps backpack to carry', () => {
      expect(getVisualizationZone('backpack')).toBe('carry')
    })

    it('falls back to other for unknown types', () => {
      expect(getVisualizationZone('unknown-type')).toBe('other')
    })
  })

  describe('resolveZoneId (placement override vs type default)', () => {
    it('uses the type default when there is no placement override', () => {
      const container = { id: 'container-1', containerType: 'trunk' }
      expect(resolveZoneId(container, {})).toBe('vehicle')
    })

    it('uses the placement override when present, ignoring the type default', () => {
      const container = { id: 'container-1', containerType: 'trunk' }
      const placements = { 'container-1': 'custom-zone-id' }
      expect(resolveZoneId(container, placements)).toBe('custom-zone-id')
    })

    it('ignores placement overrides for other containers', () => {
      const container = { id: 'container-2', containerType: 'backpack' }
      const placements = { 'container-1': 'custom-zone-id' }
      expect(resolveZoneId(container, placements)).toBe('carry')
    })

    it('falls back to "other" when containerType is missing', () => {
      const container = { id: 'container-1' }
      expect(resolveZoneId(container, {})).toBe('other')
    })
  })
})
