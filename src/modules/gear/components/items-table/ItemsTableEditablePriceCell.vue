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

const editedPrice = ref<string>(props.item.price?.toString() ?? '')
const editedCurrency = ref<string>(resolveCurrency(props.item.currency))
const isFocused = ref(false)
const suppressBlurSave = ref(false)

function resolveCurrency(currency: string | null | undefined): string {
  if (currency && SUPPORTED_CURRENCIES.some((entry) => entry.value === currency)) {
    return currency
  }
  return defaultCurrency.value
}

/** type="number" + v-model can emit numbers — keep a string for trim/parse. */
function setEditedPrice(value: string | number | null | undefined) {
  editedPrice.value = value == null || value === '' ? '' : String(value)
}

function parseEditedPrice(): number | null {
  const raw = editedPrice.value.trim()
  if (raw === '') return null
  return parseFloat(raw)
}

const hasChanges = computed<boolean>(() => {
  const priceValue = parseEditedPrice()
  const originalPrice = props.item.price ?? null
  const originalCurrency = resolveCurrency(props.item.currency)

  return (
    priceValue !== originalPrice ||
    editedCurrency.value !== originalCurrency
  )
})

function emitChange(immediate = false) {
  const priceValue = parseEditedPrice()

  if (priceValue !== null && (isNaN(priceValue) || priceValue < 0)) {
    setEditedPrice(props.item.price?.toString() ?? '')
    editedCurrency.value = resolveCurrency(props.item.currency)
    emit('change', {})
    return
  }

  const originalPrice = props.item.price ?? null
  const originalCurrency = resolveCurrency(props.item.currency)

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
    setEditedPrice(props.item.price?.toString() ?? '')
    editedCurrency.value = resolveCurrency(props.item.currency)
    emit('change', {})
    ;(document.activeElement as HTMLElement | null)?.blur()
    queueMicrotask(() => {
      suppressBlurSave.value = false
    })
  }
}

function handleReset() {
  setEditedPrice(props.item.price?.toString() ?? '')
  editedCurrency.value = resolveCurrency(props.item.currency)
  emit('change', {})
}

function handleCurrencyChange(value: unknown) {
  if (typeof value !== 'string' || value === '') return
  if (value === editedCurrency.value) return
  editedCurrency.value = value
  emitChange(true)
}

watch(
  () => [props.item.price, props.item.currency] as const,
  ([newPrice, newCurrency]) => {
    if (!isFocused.value) {
      setEditedPrice(newPrice)
      editedCurrency.value = resolveCurrency(newCurrency)
    }
  },
)
</script>

<template>
  <div
    class="flex min-w-44 items-center gap-0"
    data-editable-cell
    data-field="price"
    :data-item-id="item.id"
  >
    <div class="relative shrink-0">
      <Input
        :id="`item-price-${item.id}`"
        :model-value="editedPrice"
        :name="`item-price-${item.id}`"
        type="number"
        min="0"
        step="0.01"
        inputmode="decimal"
        :aria-label="t('gear.item.price')"
        :placeholder="t('gear.item.price')"
        class="h-10 sm:h-[2.1rem]! w-20 sm:w-24 text-end rounded-r-none border-transparent bg-transparent px-2! py-1! shadow-none focus-visible:border-input focus-visible:bg-background focus-visible:ring-1"
        :class="{ 'pr-6!': hasChanges && isFocused }"
        @update:model-value="setEditedPrice"
        @focus="isFocused = true"
        @blur="handleBlur"
        @keydown="handleKeydown"
      />
      <button
        v-if="hasChanges && isFocused"
        type="button"
        class="absolute top-0 right-1 bottom-0 my-auto p-0"
        :aria-label="t('gear.actions.undo')"
        @mousedown.prevent
        @click.stop.prevent="handleReset"
      >
        <XIcon class="size-4" />
      </button>
    </div>
    <Select
      :model-value="editedCurrency"
      @update:model-value="handleCurrencyChange"
    >
      <SelectTrigger
        :aria-label="t('gear.item.currency')"
        class="h-10 sm:h-[2.1rem]! w-18 shrink-0 rounded-l-none border-transparent bg-transparent px-2 shadow-none focus:ring-1"
      >
        <SelectValue>
          {{ editedCurrency }}
        </SelectValue>
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
