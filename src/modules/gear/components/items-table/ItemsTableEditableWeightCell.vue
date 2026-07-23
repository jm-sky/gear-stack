<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { DEFAULT_ITEM_WEIGHT } from '../../utils/constants'
import { WEIGHT_UNITS } from '../../utils/weightUnits'
import type { IGearItemV2, IUpdateGearItemV2Dto, TGearWeightUnit } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto, options?: { immediate?: boolean }]
  navigate: [direction: 'next' | 'prev' | 'down']
}>()

const editedWeight = ref((props.item.weight ?? DEFAULT_ITEM_WEIGHT).toString())
const editedWeightUnit = ref<TGearWeightUnit>(props.item.weightUnit ?? 'g')
const isFocused = ref(false)
const suppressBlurSave = ref(false)

function emitChange(immediate = false) {
  const weightValue = parseFloat(editedWeight.value)

  if (isNaN(weightValue) || weightValue < 0) {
    editedWeight.value = (props.item.weight ?? DEFAULT_ITEM_WEIGHT).toString()
    editedWeightUnit.value = props.item.weightUnit ?? 'g'
    emit('change', {})
    return
  }

  if (weightValue !== props.item.weight || editedWeightUnit.value !== (props.item.weightUnit ?? 'g')) {
    emit('change', {
      weight: weightValue,
      weightUnit: editedWeightUnit.value,
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
    editedWeight.value = (props.item.weight ?? DEFAULT_ITEM_WEIGHT).toString()
    editedWeightUnit.value = props.item.weightUnit ?? 'g'
    emit('change', {})
    ;(document.activeElement as HTMLElement | null)?.blur()
    queueMicrotask(() => {
      suppressBlurSave.value = false
    })
  }
}

function handleUnitChange() {
  emitChange(true)
}

watch(
  () => [props.item.weight, props.item.weightUnit],
  ([newWeight, newUnit]) => {
    if (!isFocused.value) {
      editedWeight.value = newWeight?.toString() ?? ''
      editedWeightUnit.value = (newUnit ?? 'g') as TGearWeightUnit
    }
  },
)
</script>

<template>
  <div
    class="flex items-center gap-1"
    data-editable-cell
    data-field="weight"
    :data-item-id="item.id"
  >
    <Input
      :id="`item-weight-${item.id}`"
      v-model="editedWeight"
      :name="`item-weight-${item.id}`"
      type="number"
      min="0"
      step="0.01"
      :aria-label="t('gear.item.weight')"
      class="h-[2.1rem]! text-end rounded-r-none w-20 border-transparent bg-transparent py-1! shadow-none focus-visible:border-input focus-visible:bg-background focus-visible:ring-1"
      @focus="isFocused = true"
      @blur="handleBlur"
      @keydown="handleKeydown"
    />
    <Select
      v-model="editedWeightUnit"
      @update:model-value="handleUnitChange"
    >
      <SelectTrigger
        :aria-label="t('gear.item.weightUnit')"
        class="h-[2.1rem]! rounded-l-none w-17.5 border-transparent bg-transparent shadow-none focus:ring-1"
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem
          v-for="unit in WEIGHT_UNITS"
          :key="unit"
          :value="unit"
        >
          {{ t(`gear.item.weightUnits.${unit}`) }}
        </SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>
