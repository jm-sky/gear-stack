export type TVisualizationZone = 'body' | 'carry' | 'vehicle' | 'home' | 'other'

const CONTAINER_TYPE_TO_ZONE: Record<string, TVisualizationZone> = {
  pouch: 'body',
  ubranie: 'body',
  backpack: 'carry',
  bag: 'carry',
  case: 'carry',
  trunk: 'carry',
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
