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
import type { IGearItem, IUpdateItemDto, TGearItemStatus } from '@/modules/gear/types/gear.types'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItem
}>()

const emit = defineEmits<{
  change: [updates: IUpdateItemDto]
}>()

// In edit mode, always show select
const editedStatus = ref<TGearItemStatus>(props.item.status)

const statuses: TGearItemStatus[] = ['owned', 'missing', 'toBuy']

// Handle status change
function handleStatusChange(newStatus: unknown) {
  if (newStatus === props.item.status) {
    emit('change', {})
    return
  }

  emit('change', { status: newStatus as TGearItemStatus })
}

// Watch for external changes to item
watch(
  () => props.item.status,
  (newStatus) => {
    editedStatus.value = newStatus
  },
)
</script>

<template>
  <Select
    :model-value="editedStatus"
    @update:model-value="handleStatusChange"
  >
    <SelectTrigger class="h-[2.1rem]! min-w-[120px]">
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
</template>

