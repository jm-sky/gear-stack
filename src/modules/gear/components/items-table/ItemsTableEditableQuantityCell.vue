<script setup lang="ts">
import { UndoIcon } from 'lucide-vue-next'
import { ref, watch } from 'vue'
import { Input } from '@/components/ui/input'
import type { IGearItem, IUpdateItemDto } from '@/modules/gear/types/gear.types'

const props = defineProps<{
  item: IGearItem
}>()

const emit = defineEmits<{
  change: [updates: IUpdateItemDto]
}>()

// In edit mode, always show input
const editedQuantity = ref(props.item.quantity.toString())

// Handle change - emit updates to parent
function handleChange() {
  const quantityValue = parseInt(editedQuantity.value, 10)

  // Validation - quantity must be >= 1
  if (isNaN(quantityValue) || quantityValue < 1) {
    editedQuantity.value = props.item.quantity.toString()
    emit('change', {})
    return
  }

  if (quantityValue !== props.item.quantity) {
    emit('change', { quantity: quantityValue })
  } else {
    emit('change', {})
  }
}

// Handle Enter - same as blur
function handleEnter() {
  handleChange()
}

// Watch for external changes to item
watch(
  () => props.item.quantity,
  (newQuantity) => {
    editedQuantity.value = newQuantity.toString()
  },
)

// Reset value
function handleReset() {
  editedQuantity.value = props.item.quantity.toString()
  emit('change', {})
}
</script>

<template>
  <div class="relative w-20">
    <Input
      v-model="editedQuantity"
      type="number"
      min="1"
      step="1"
      class="py-1! h-[2.1rem]! border-0"
      @keyup.enter="handleEnter"
      @blur="handleChange"
    />
    <!-- Reset button -->
    <button
      v-if="editedQuantity && parseInt(editedQuantity, 10) !== props.item.quantity"
      type="button"
      class="absolute right-8 top-0 bottom-0 my-auto p-0"
      @click.stop.prevent="handleReset"
    >
      <UndoIcon class="size-4" />
    </button>
  </div>
</template>

