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
import { DEFAULT_ITEM_STATUS } from '../../utils/constants'
import type { IGearItemV2, IUpdateGearItemV2Dto, TGearItemStatus } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto, options?: { immediate?: boolean }]
  navigate: [direction: 'next' | 'prev' | 'down']
}>()

const editedStatus = ref<TGearItemStatus>(props.item.status ?? DEFAULT_ITEM_STATUS)

const statuses: TGearItemStatus[] = ['owned', 'missing', 'toBuy']

function handleStatusChange(newStatus: unknown) {
  if (newStatus === props.item.status) {
    emit('change', {})
    return
  }

  editedStatus.value = newStatus as TGearItemStatus
  emit('change', { status: newStatus as TGearItemStatus }, { immediate: true })
}

function handleTab(event: KeyboardEvent) {
  event.preventDefault()
  emit('navigate', event.shiftKey ? 'prev' : 'next')
}

watch(
  () => props.item.status,
  (newStatus) => {
    editedStatus.value = newStatus ?? DEFAULT_ITEM_STATUS
  },
)
</script>

<template>
  <div
    data-editable-cell
    data-field="status"
    :data-item-id="item.id"
  >
    <Select
      :model-value="editedStatus"
      @update:model-value="handleStatusChange"
    >
      <SelectTrigger
        :aria-label="t('gear.item.status')"
        class="h-10 sm:h-[2.1rem]! min-w-[110px] sm:min-w-[120px] border-transparent bg-transparent shadow-none focus:ring-1"
        @keydown.tab="handleTab"
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem
          v-for="status in statuses"
          :key="status"
          :value="status"
        >
          {{ t(`gear.item.statuses.${status}`) }}
        </SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>
