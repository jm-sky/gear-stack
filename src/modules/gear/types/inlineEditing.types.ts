export type InlineRowSaveStatus = 'idle' | 'pending' | 'saving' | 'saved' | 'error'

export type EditableCellField =
  | 'name'
  | 'category'
  | 'quantity'
  | 'weight'
  | 'priority'
  | 'status'
  | 'price'

/** Tab order through editable cells in a row (matches typical column layout). */
export const EDITABLE_CELL_FIELD_ORDER: EditableCellField[] = [
  'name',
  'category',
  'quantity',
  'weight',
  'priority',
  'status',
  'price',
]
