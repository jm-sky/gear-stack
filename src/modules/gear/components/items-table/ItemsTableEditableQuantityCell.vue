<script setup lang="ts">
import { UndoIcon } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Input } from '@/components/ui/input'
import { DEFAULT_ITEM_QUANTITY } from '../../utils/constants'
import type { IGearItemV2, IUpdateGearItemV2Dto } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto, options?: { immediate?: boolean }]
  navigate: [direction: 'next' | 'prev' | 'down']
}>()

const editedQuantity = ref((props.item.quantity ?? DEFAULT_ITEM_QUANTITY).toString())
const isFocused = ref(false)
const suppressBlurSave = ref(false)

const hasLocalChanges = computed<boolean>(() => {
  const quantityValue = parseInt(editedQuantity.value, 10)
  return !isNaN(quantityValue) && quantityValue !== (props.item.quantity ?? DEFAULT_ITEM_QUANTITY)
})

function emitChange(immediate = false) {
  const quantityValue = parseInt(editedQuantity.value, 10)

  if (isNaN(quantityValue) || quantityValue < 1) {
    editedQuantity.value = (props.item.quantity ?? DEFAULT_ITEM_QUANTITY).toString()
    emit('change', {})
    return
  }

  if (quantityValue !== props.item.quantity) {
    emit('change', { quantity: quantityValue }, { immediate })
  } else {
    emit('change', {})
  }
}

function handleBlur() {
  isFocused.value = false
  if (suppressBlurSave.value) return
  emitChange(false)
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter') {
    event.preventDefault()
    suppressBlurSave.value = true
    emitChange(true)
    emit('navigate', 'down')
    queueMicrotask(() => {
      suppressBlurSave.value = false
    })
    return
  }

  if (event.key === 'Tab') {
    event.preventDefault()
    suppressBlurSave.value = true
    emitChange(false)
    emit('navigate', event.shiftKey ? 'prev' : 'next')
    queueMicrotask(() => {
      suppressBlurSave.value = false
    })
    return
  }

  if (event.key === 'Escape') {
    event.preventDefault()
    suppressBlurSave.value = true
    editedQuantity.value = (props.item.quantity ?? DEFAULT_ITEM_QUANTITY).toString()
    emit('change', {})
    ;(document.activeElement as HTMLElement | null)?.blur()
    queueMicrotask(() => {
      suppressBlurSave.value = false
    })
  }
}

function handleReset() {
  editedQuantity.value = (props.item.quantity ?? DEFAULT_ITEM_QUANTITY).toString()
  emit('change', {})
}

watch(
  () => props.item.quantity,
  (newQuantity) => {
    if (!isFocused.value) {
      editedQuantity.value = (newQuantity ?? DEFAULT_ITEM_QUANTITY).toString()
    }
  },
)
</script>

<template>
  <div
    class="relative w-20"
    data-editable-cell
    data-field="quantity"
    :data-item-id="item.id"
  >
    <Input
      :id="`item-quantity-${item.id}`"
      v-model="editedQuantity"
      :name="`item-quantity-${item.id}`"
      type="number"
      min="1"
      step="1"
      :aria-label="t('gear.item.quantity')"
      class="h-[2.1rem]! border-transparent bg-transparent py-1! shadow-none focus-visible:border-input focus-visible:bg-background focus-visible:ring-1"
      @focus="isFocused = true"
      @blur="handleBlur"
      @keydown="handleKeydown"
    />
    <button
      v-if="hasLocalChanges && isFocused"
      type="button"
      class="absolute top-0 right-8 bottom-0 my-auto p-0"
      :aria-label="t('gear.actions.undo')"
      @mousedown.prevent
      @click.stop.prevent="handleReset"
    >
      <UndoIcon class="size-4" />
    </button>
  </div>
</template>
