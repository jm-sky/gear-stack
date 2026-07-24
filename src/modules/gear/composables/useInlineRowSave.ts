import { ref } from 'vue'
import type { IGearItemV2, IUpdateGearItemV2Dto } from '../types/gear.types.v2'
import type { InlineRowSaveStatus } from '../types/inlineEditing.types'
import { useGearMutations } from './useGearMutations'
import type { TUUID } from '@/shared/types/base.type'

const AUTO_SAVE_DEBOUNCE_MS = 450
const SAVED_FLASH_MS = 1800

type SaveCallbacks = {
  onSaved?: (item: IGearItemV2) => void
  onError?: (itemId: TUUID, error: unknown) => void
}

function hasMeaningfulChanges(changes: IUpdateGearItemV2Dto): boolean {
  return Object.keys(changes).some((key) => {
    const value = changes[key as keyof IUpdateGearItemV2Dto]
    return value !== undefined
  })
}

/**
 * Debounced auto-save for inline row edits (strategy D).
 * Accumulates per-row patches, flushes after idle or on demand (Enter / retry).
 */
export function useInlineRowSave(callbacks: SaveCallbacks = {}) {
  const { updateItem } = useGearMutations()

  const dirtyChanges = ref<Map<TUUID, IUpdateGearItemV2Dto>>(new Map())
  const rowStatus = ref<Map<TUUID, InlineRowSaveStatus>>(new Map())
  const debounceTimers = new Map<TUUID, ReturnType<typeof setTimeout>>()
  const savedFlashTimers = new Map<TUUID, ReturnType<typeof setTimeout>>()

  function setStatus(itemId: TUUID, status: InlineRowSaveStatus) {
    const next = new Map(rowStatus.value)
    if (status === 'idle') {
      next.delete(itemId)
    } else {
      next.set(itemId, status)
    }
    rowStatus.value = next
  }

  function getStatus(itemId: TUUID): InlineRowSaveStatus {
    return rowStatus.value.get(itemId) ?? 'idle'
  }

  function hasDirtyChanges(itemId: TUUID): boolean {
    return dirtyChanges.value.has(itemId)
  }

  function clearDebounce(itemId: TUUID) {
    const timer = debounceTimers.get(itemId)
    if (timer) {
      clearTimeout(timer)
      debounceTimers.delete(itemId)
    }
  }

  function clearSavedFlash(itemId: TUUID) {
    const timer = savedFlashTimers.get(itemId)
    if (timer) {
      clearTimeout(timer)
      savedFlashTimers.delete(itemId)
    }
  }

  function scheduleSavedFlash(itemId: TUUID) {
    clearSavedFlash(itemId)
    setStatus(itemId, 'saved')
    const timer = setTimeout(() => {
      savedFlashTimers.delete(itemId)
      if (getStatus(itemId) === 'saved') {
        setStatus(itemId, 'idle')
      }
    }, SAVED_FLASH_MS)
    savedFlashTimers.set(itemId, timer)
  }

  function setDirty(itemId: TUUID, updates: IUpdateGearItemV2Dto) {
    const current = dirtyChanges.value.get(itemId) ?? {}
    const merged: IUpdateGearItemV2Dto = { ...current, ...updates }

    const next = new Map(dirtyChanges.value)
    if (hasMeaningfulChanges(merged)) {
      next.set(itemId, merged)
      dirtyChanges.value = next
      if (getStatus(itemId) !== 'saving') {
        setStatus(itemId, 'pending')
      }
      return true
    }

    next.delete(itemId)
    dirtyChanges.value = next
    if (getStatus(itemId) === 'pending') {
      setStatus(itemId, 'idle')
    }
    return false
  }

  function scheduleSave(item: IGearItemV2) {
    clearDebounce(item.id)
    const timer = setTimeout(() => {
      debounceTimers.delete(item.id)
      void saveRow(item)
    }, AUTO_SAVE_DEBOUNCE_MS)
    debounceTimers.set(item.id, timer)
  }

  /**
   * Merge cell updates into the row patch.
   * Schedules debounced save unless `immediate` (Enter / select discrete change).
   */
  function handleCellChange(
    item: IGearItemV2,
    updates: IUpdateGearItemV2Dto,
    options: { immediate?: boolean } = {},
  ) {
    const hasChanges = setDirty(item.id, updates)

    if (!hasChanges) {
      clearDebounce(item.id)
      return
    }

    if (options.immediate) {
      clearDebounce(item.id)
      void saveRow(item)
    } else {
      scheduleSave(item)
    }
  }

  async function saveRow(item: IGearItemV2): Promise<IGearItemV2 | null> {
    clearDebounce(item.id)
    const changes = dirtyChanges.value.get(item.id)
    if (!changes || !hasMeaningfulChanges(changes)) {
      return null
    }

    setStatus(item.id, 'saving')

    try {
      const updated = await updateItem(item.id, changes)
      const next = new Map(dirtyChanges.value)
      next.delete(item.id)
      dirtyChanges.value = next
      scheduleSavedFlash(item.id)
      callbacks.onSaved?.(updated)
      return updated
    } catch (error) {
      setStatus(item.id, 'error')
      callbacks.onError?.(item.id, error)
      return null
    }
  }

  function saveImmediately(item: IGearItemV2) {
    clearDebounce(item.id)
    return saveRow(item)
  }

  function retrySave(item: IGearItemV2) {
    return saveImmediately(item)
  }

  function discardDirty(itemId: TUUID) {
    clearDebounce(itemId)
    const next = new Map(dirtyChanges.value)
    next.delete(itemId)
    dirtyChanges.value = next
    if (getStatus(itemId) === 'pending' || getStatus(itemId) === 'error') {
      setStatus(itemId, 'idle')
    }
  }

  return {
    dirtyChanges,
    rowStatus,
    getStatus,
    hasDirtyChanges,
    handleCellChange,
    saveImmediately,
    retrySave,
    discardDirty,
  }
}
