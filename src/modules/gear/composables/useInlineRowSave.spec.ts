import { beforeEach, describe, expect, it, vi } from 'vitest'

const updateItem = vi.fn()

vi.mock('./useGearMutations', () => ({
  useGearMutations: () => ({
    updateItem,
  }),
}))

const { useInlineRowSave } = await import('./useInlineRowSave')
import type { IGearItemV2 } from '../types/gear.types.v2'

function makeItem(overrides: Partial<IGearItemV2> = {}): IGearItemV2 {
  return {
    id: 'item-1',
    name: 'Knife',
    quantity: 1,
    weight: 100,
    weightUnit: 'g',
    ...overrides,
  } as IGearItemV2
}

describe('useInlineRowSave', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    updateItem.mockReset()
    updateItem.mockResolvedValue(makeItem({ name: 'Updated' }))
  })

  it('debounces multiple cell edits into one save', async () => {
    const onSaved = vi.fn()
    const { handleCellChange, getStatus } = useInlineRowSave({ onSaved })
    const item = makeItem()

    handleCellChange(item, { name: 'Axe' })
    handleCellChange(item, { quantity: 2 })
    expect(getStatus(item.id)).toBe('pending')
    expect(updateItem).not.toHaveBeenCalled()

    await vi.advanceTimersByTimeAsync(450)

    expect(updateItem).toHaveBeenCalledTimes(1)
    expect(updateItem).toHaveBeenCalledWith('item-1', { name: 'Axe', quantity: 2 })
    expect(onSaved).toHaveBeenCalled()
    expect(getStatus(item.id)).toBe('saved')
  })

  it('saves immediately when requested', async () => {
    const { handleCellChange } = useInlineRowSave()
    const item = makeItem()

    handleCellChange(item, { name: 'Axe' }, { immediate: true })
    await Promise.resolve()

    expect(updateItem).toHaveBeenCalledTimes(1)
  })

  it('sets error status when save fails', async () => {
    updateItem.mockRejectedValueOnce(new Error('network'))
    const onError = vi.fn()
    const { handleCellChange, getStatus } = useInlineRowSave({ onError })
    const item = makeItem()

    handleCellChange(item, { name: 'Axe' }, { immediate: true })
    await vi.waitFor(() => {
      expect(getStatus(item.id)).toBe('error')
    })
    expect(onError).toHaveBeenCalled()
  })
})
