import {
  Backpack,
  Bike,
  Car,
  Home,
  Package,
  PersonStanding,
  Plane,
  Ship,
  Tent,
  TentTree,
  Warehouse,
} from 'lucide-vue-next'
import type { Component } from 'vue'

export type TVisualizationZone = 'body' | 'carry' | 'vehicle' | 'home' | 'other'

const CONTAINER_TYPE_TO_ZONE: Record<string, TVisualizationZone> = {
  pouch: 'body',
  ubranie: 'body',
  backpack: 'carry',
  bag: 'carry',
  case: 'carry',
  trunk: 'vehicle',
  vehicle: 'vehicle',
  cabinet: 'home',
  shelf: 'home',
  drawer: 'home',
  box: 'home',
  naczynie: 'home',
  other: 'other',
}

export function getVisualizationZone(containerType: string): TVisualizationZone {
  return CONTAINER_TYPE_TO_ZONE[containerType] ?? 'other'
}

export interface IVisualizationZoneConfig {
  id: TVisualizationZone
  labelKey: string
}

export const ZONE_CONFIG: IVisualizationZoneConfig[] = [
  { id: 'body', labelKey: 'gear.visualization.zones.body' },
  { id: 'carry', labelKey: 'gear.visualization.zones.carry' },
  { id: 'vehicle', labelKey: 'gear.visualization.zones.vehicle' },
  { id: 'home', labelKey: 'gear.visualization.zones.home' },
  { id: 'other', labelKey: 'gear.visualization.zones.other' },
]

export const DEFAULT_ZONE_IDS: TVisualizationZone[] = ZONE_CONFIG.map(zone => zone.id)

/**
 * Resolves the zone a container should render in: a manual DnD placement
 * override (containerId -> zoneId) takes priority over the containerType default.
 */
export function resolveZoneId(
  container: { id: string, containerType?: string | null },
  placements: Record<string, string>,
): string {
  return placements[container.id] ?? getVisualizationZone(container.containerType ?? 'other')
}

// Curated lucide icon allowlist for default + custom zones
export const ZONE_ICON_KEYS = [
  'personStanding',
  'backpack',
  'car',
  'warehouse',
  'package',
  'tent',
  'tentTree',
  'ship',
  'bike',
  'plane',
  'home',
] as const

export type TZoneIconKey = typeof ZONE_ICON_KEYS[number]

const ZONE_ICONS: Record<TZoneIconKey, Component> = {
  personStanding: PersonStanding,
  backpack: Backpack,
  car: Car,
  warehouse: Warehouse,
  package: Package,
  tent: Tent,
  tentTree: TentTree,
  ship: Ship,
  bike: Bike,
  plane: Plane,
  home: Home,
}

const DEFAULT_ZONE_ICON_KEYS: Record<TVisualizationZone, TZoneIconKey> = {
  body: 'personStanding',
  carry: 'backpack',
  vehicle: 'car',
  home: 'warehouse',
  other: 'package',
}

/**
 * Icon for a default zone (by zone id) or a custom zone (by its stored iconKey).
 * Falls back to the "other" default icon for unknown keys.
 */
export function getZoneIcon(iconKey: string): Component {
  return ZONE_ICONS[iconKey as TZoneIconKey] ?? ZONE_ICONS.package
}

export function getDefaultZoneIcon(zoneId: TVisualizationZone): Component {
  return getZoneIcon(DEFAULT_ZONE_ICON_KEYS[zoneId])
}
