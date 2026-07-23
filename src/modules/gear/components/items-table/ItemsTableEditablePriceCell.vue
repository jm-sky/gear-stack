<script setup lang="ts">
import { XIcon } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useGearSettings } from '../../composables/useGearSettings'
import { SUPPORTED_CURRENCIES } from '../../utils/currencyFormatter'
import type { IGearItemV2, IUpdateGearItemV2Dto } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()
const { defaultCurrency } = useGearSettings()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto, options?: { immediate?: boolean }]
  navigate: [direction: 'next' | 'prev' | 'down']
}>()

const editedPrice = ref(props.item.price?.toString() ?? '')
const editedCurrency = ref<string>(props.item.currency ?? defaultCurrency.value)
const isFocused = ref(false)
const suppressBlurSave = ref(false)

const hasChanges = computed<boolean>(() => {
  const priceValue = editedPrice.value.trim() === '' ? null : parseFloat(editedPrice.value)
  const originalPrice = props.item.price ?? null
  const originalCurrency = props.item.currency ?? defaultCurrency.value

  return (
    priceValue !== originalPrice ||
    editedCurrency.value !== originalCurrency
  )
})

function emitChange(immediate = false) {
  const priceValue = editedPrice.value.trim() === '' ? null : parseFloat(editedPrice.value)

  if (priceValue !== null && (isNaN(priceValue) || priceValue < 0)) {
    editedPrice.value = props.item.price?.toString() ?? ''
    editedCurrency.value = props.item.currency ?? defaultCurrency.value
    emit('change', {})
    return
  }

  const originalPrice = props.item.price ?? null
  const originalCurrency = props.item.currency ?? defaultCurrency.value

  if (priceValue !== originalPrice || editedCurrency.value !== originalCurrency) {
    emit('change', {
      price: priceValue,
      currency: editedCurrency.value,
    }, { immediate })
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
    editedPrice.value = props.item.price?.toString() ?? ''
    editedCurrency.value = props.item.currency ?? defaultCurrency.value
    emit('change', {})
    ;(document.activeElement as HTMLElement | null)?.blur()
    queueMicrotask(() => {
      suppressBlurSave.value = false
    })
  }
}

function handleReset() {
  editedPrice.value = props.item.price?.toString() ?? ''
  editedCurrency.value = props.item.currency ?? defaultCurrency.value
  emit('change', {})
}

function handleCurrencyChange() {
  emitChange(true)
}

watch(
  () => [props.item.price, props.item.currency],
  ([newPrice, newCurrency]) => {
    if (!isFocused.value) {
      editedPrice.value = newPrice?.toString() ?? ''
      editedCurrency.value = (newCurrency ?? defaultCurrency.value) as string
    }
  },
)
</script>

<template>
  <div
    class="flex items-center gap-1"
    data-editable-cell
    data-field="price"
    :data-item-id="item.id"
  >
    <div class="relative flex-1">
      <Input
        :id="`item-price-${item.id}`"
        v-model="editedPrice"
        :name="`item-price-${item.id}`"
        type="number"
        min="0"
        step="0.01"
        :aria-label="t('gear.item.price')"
        :placeholder="t('gear.item.price')"
        class="h-[2.1rem]! border-transparent bg-transparent py-1! pr-8 shadow-none focus-visible:border-input focus-visible:bg-background focus-visible:ring-1"
        @focus="isFocused = true"
        @blur="handleBlur"
        @keydown="handleKeydown"
      />
      <button
        v-if="hasChanges && isFocused"
        type="button"
        class="absolute top-0 right-2 bottom-0 my-auto p-0"
        :aria-label="t('gear.actions.undo')"
        @mousedown.prevent
        @click.stop.prevent="handleReset"
      >
        <XIcon class="size-4" />
      </button>
    </div>
    <Select
      v-model="editedCurrency"
      @update:model-value="handleCurrencyChange"
    >
      <SelectTrigger
        :aria-label="t('gear.item.currency')"
        class="h-[2.1rem]! w-[100px] border-transparent bg-transparent shadow-none focus:ring-1"
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem
          v-for="curr in SUPPORTED_CURRENCIES"
          :key="curr.value"
          :value="curr.value"
        >
          {{ curr.label }}
        </SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>
