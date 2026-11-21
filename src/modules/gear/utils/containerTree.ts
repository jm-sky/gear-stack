import type { IGearContainer } from '../types/gear.types'
import type { IGearItemV2 } from '../types/gear.types.v2'
import { convertV1ContainerToV2, convertV1ItemToV2 } from './typeConverters'
import type { TUUID } from '@/shared/types/base.type'

export interface IContainerTreeAccessors {
  getItemById: (id: TUUID) => IGearItemV2 | undefined
  getChildrenOfItem: (id: TUUID) => IGearItemV2[]
}

export interface IContainerTree extends IContainerTreeAccessors {
  container: IGearItemV2
  items: IGearItemV2[]
}

/**
 * Build store-independent accessors for a container and its direct children.
 * Used on public/shared pages where the viewer's own gear store does not hold the data.
 */
export function createTreeAccessors(container: IGearItemV2, items: IGearItemV2[]): IContainerTreeAccessors {
  const byId = new Map<TUUID, IGearItemV2>([[container.id, container], ...items.map(item => [item.id, item] as [TUUID, IGearItemV2])])
  return {
    getItemById: (id) => byId.get(id),
    getChildrenOfItem: (id) => (id === container.id ? items : []),
  }
}

/**
 * Convert the API container payload (V1 shape with `items`) of a public/shared container
 * into a V2 container with `children` plus local accessors for weight/readiness calculations.
 * The API returns only regular items (nested containers are not included).
 */
export function buildContainerTreeFromApi(response: IGearContainer): IContainerTree {
  const container = convertV1ContainerToV2(response)
  const items = (response.items ?? []).map(item => convertV1ItemToV2(item, container.id))
  container.children = items
  return { container, items, ...createTreeAccessors(container, items) }
}
