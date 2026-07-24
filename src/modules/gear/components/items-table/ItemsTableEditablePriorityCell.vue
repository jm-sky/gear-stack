<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { DEFAULT_ITEM_PRIORITY } from '../../utils/constants'
import type { IGearItemV2, IUpdateGearItemV2Dto, TGearItemPriority } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto, options?: { immediate?: boolean }]
  navigate: [direction: 'next' | 'prev' | 'down']
}>()

const editedPriority = ref<TGearItemPriority>(props.item.priority ?? DEFAULT_ITEM_PRIORITY)

const priorities: TGearItemPriority[] = ['critical', 'high', 'medium', 'low']

function handlePriorityChange(newPriority: unknown) {
  if (newPriority === props.item.priority) {
    emit('change', {})
    return
  }

  editedPriority.value = newPriority as TGearItemPriority
  emit('change', { priority: newPriority as TGearItemPriority }, { immediate: true })
}

function handleTab(event: KeyboardEvent) {
  event.preventDefault()
  emit('navigate', event.shiftKey ? 'prev' : 'next')
}

watch(
  () => props.item.priority,
  (newPriority) => {
    editedPriority.value = newPriority ?? DEFAULT_ITEM_PRIORITY
  },
)
</script>

<template>
  <div
    data-editable-cell
    data-field="priority"
    :data-item-id="item.id"
  >
    <Select
      :model-value="editedPriority"
      @update:model-value="handlePriorityChange"
    >
      <SelectTrigger
        :aria-label="t('gear.item.priority')"
        class="h-10 sm:h-[2.1rem]! min-w-[110px] sm:min-w-[120px] border-transparent bg-transparent shadow-none focus:ring-1"
        @keydown.tab="handleTab"
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem
          v-for="priority in priorities"
          :key="priority"
          :value="priority"
        >
          {{ t(`gear.item.priorities.${priority}`) }}
        </SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>
