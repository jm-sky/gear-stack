import {
  EDITABLE_CELL_FIELD_ORDER,
  type EditableCellField,
} from '../types/inlineEditing.types'
import type { TUUID } from '@/shared/types/base.type'

function cellSelector(itemId: TUUID, field: EditableCellField): string {
  return `[data-editable-cell][data-item-id="${itemId}"][data-field="${field}"]`
}

function focusableInside(root: Element): HTMLElement | null {
  const candidate = root.querySelector<HTMLElement>(
    'input:not([disabled]), textarea:not([disabled]), button[data-slot="select-trigger"]:not([disabled]), [role="combobox"]:not([disabled])',
  )
  return candidate ?? (root as HTMLElement)
}

function focusCell(itemId: TUUID, field: EditableCellField): boolean {
  const root = document.querySelector(cellSelector(itemId, field))
  if (!root) return false
  const target = focusableInside(root)
  if (!target) return false
  target.focus()
  if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) {
    target.select?.()
  }
  return true
}

function findNextAvailableField(
  itemId: TUUID,
  startIndex: number,
  direction: 1 | -1,
): EditableCellField | null {
  let index = startIndex
  for (let step = 0; step < EDITABLE_CELL_FIELD_ORDER.length; step++) {
    index += direction
    if (index < 0 || index >= EDITABLE_CELL_FIELD_ORDER.length) {
      return null
    }
    const field = EDITABLE_CELL_FIELD_ORDER[index]
    if (document.querySelector(cellSelector(itemId, field))) {
      return field
    }
  }
  return null
}

/**
 * Keyboard navigation between inline-editable cells (Excel-like Tab / Enter).
 */
export function useItemsTableCellNavigation() {
  function focusNextCell(itemId: TUUID, field: EditableCellField, itemIds: TUUID[]): boolean {
    const currentIndex = EDITABLE_CELL_FIELD_ORDER.indexOf(field)
    const nextField = findNextAvailableField(itemId, currentIndex, 1)
    if (nextField) {
      return focusCell(itemId, nextField)
    }

    const rowIndex = itemIds.indexOf(itemId)
    if (rowIndex < 0 || rowIndex >= itemIds.length - 1) return false
    const nextItemId = itemIds[rowIndex + 1]
    for (const candidate of EDITABLE_CELL_FIELD_ORDER) {
      if (focusCell(nextItemId, candidate)) return true
    }
    return false
  }

  function focusPrevCell(itemId: TUUID, field: EditableCellField, itemIds: TUUID[]): boolean {
    const currentIndex = EDITABLE_CELL_FIELD_ORDER.indexOf(field)
    const prevField = findNextAvailableField(itemId, currentIndex, -1)
    if (prevField) {
      return focusCell(itemId, prevField)
    }

    const rowIndex = itemIds.indexOf(itemId)
    if (rowIndex <= 0) return false
    const prevItemId = itemIds[rowIndex - 1]
    for (let i = EDITABLE_CELL_FIELD_ORDER.length - 1; i >= 0; i--) {
      if (focusCell(prevItemId, EDITABLE_CELL_FIELD_ORDER[i])) return true
    }
    return false
  }

  function focusDownCell(itemId: TUUID, field: EditableCellField, itemIds: TUUID[]): boolean {
    const rowIndex = itemIds.indexOf(itemId)
    if (rowIndex < 0 || rowIndex >= itemIds.length - 1) return false
    return focusCell(itemIds[rowIndex + 1], field)
  }

  return {
    focusCell,
    focusNextCell,
    focusPrevCell,
    focusDownCell,
  }
}
