import type { IGearItemV2 } from '../types/gear.types.v2'
import type { TUUID } from '@/shared/types/base.type'

const PATH_SEPARATOR = ' › '

/**
 * Build a breadcrumb path from root to the given container (inclusive).
 */
export function buildContainerPath(
  containerId: TUUID,
  byId: Map<string, IGearItemV2>,
): string {
  const parts: string[] = []
  let current: IGearItemV2 | undefined = byId.get(containerId)

  while (current) {
    parts.unshift(current.name)
    current = current.parentItemId ? byId.get(current.parentItemId) : undefined
  }

  return parts.join(PATH_SEPARATOR)
}

/**
 * Parent breadcrumb for a nested container row (excludes the container itself).
 */
export function buildParentContainerPath(
  containerId: TUUID,
  byId: Map<string, IGearItemV2>,
): string {
  const container = byId.get(containerId)
  if (!container?.parentItemId) {
    return ''
  }
  return buildContainerPath(container.parentItemId, byId)
}
