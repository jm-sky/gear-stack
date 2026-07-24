<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Input } from '@/components/ui/input'
import TableCell from '@/components/ui/table/TableCell.vue'
import TableRow from '@/components/ui/table/TableRow.vue'
import { useGearMutations } from '../../composables/useGearMutations'
import {
  DEFAULT_ITEM_CATEGORY,
  DEFAULT_ITEM_PRIORITY,
  DEFAULT_ITEM_QUANTITY,
  DEFAULT_ITEM_STATUS,
  DEFAULT_ITEM_WEIGHT,
} from '../../utils/constants'
import type { IGearItemV2 } from '@/modules/gear/types/gear.types.v2'
import type { TUUID } from '@/shared/types/base.type'

const { t } = useI18n()
const { createItem } = useGearMutations()

const props = defineProps<{
  containerId: TUUID
  columnCount: number
}>()

const emit = defineEmits<{
  created: [item: IGearItemV2]
}>()

const draftName = ref<string>('')
const isCreating = ref<boolean>(false)
const suppressBlurCommit = ref<boolean>(false)
const nameInputRef = ref<HTMLInputElement | null>(null)

async function commitDraft() {
  const name = draftName.value.trim()
  if (!name || isCreating.value) return

  isCreating.value = true
  try {
    const created = await createItem({
      itemType: 'item',
      parentItemId: props.containerId,
      name,
      category: DEFAULT_ITEM_CATEGORY,
      quantity: DEFAULT_ITEM_QUANTITY,
      weight: DEFAULT_ITEM_WEIGHT,
      weightUnit: 'g',
      status: DEFAULT_ITEM_STATUS,
      priority: DEFAULT_ITEM_PRIORITY,
    })
    draftName.value = ''
    emit('created', created)
    await nextTick()
    nameInputRef.value?.focus()
  } catch (error) {
    console.error('Failed to create item from quick add:', error)
    toast.error(t('gear.actions.saveError'))
  } finally {
    isCreating.value = false
  }
}

function handleBlur() {
  if (suppressBlurCommit.value) return
  void commitDraft()
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter') {
    event.preventDefault()
    suppressBlurCommit.value = true
    void commitDraft().finally(() => {
      queueMicrotask(() => {
        suppressBlurCommit.value = false
      })
    })
    return
  }

  if (event.key === 'Escape') {
    event.preventDefault()
    suppressBlurCommit.value = true
    draftName.value = ''
    nameInputRef.value?.blur()
    queueMicrotask(() => {
      suppressBlurCommit.value = false
    })
  }
}

function setInputRef(el: unknown) {
  const root = el as { $el?: HTMLElement } | HTMLElement | null
  if (!root) {
    nameInputRef.value = null
    return
  }
  if (root instanceof HTMLElement) {
    nameInputRef.value = root instanceof HTMLInputElement
      ? root
      : root.querySelector('input')
    return
  }
  const elNode = root.$el
  nameInputRef.value = elNode instanceof HTMLInputElement
    ? elNode
    : elNode?.querySelector?.('input') ?? null
}
</script>

<template>
  <TableRow class="border-dashed bg-muted/20 hover:bg-muted/30">
    <TableCell :colspan="columnCount">
      <div class="flex min-w-48 max-w-md items-center gap-2 py-0.5">
        <Input
          :ref="setInputRef"
          v-model="draftName"
          :disabled="isCreating"
          :placeholder="t('gear.itemsTable.quickAddPlaceholder')"
          :aria-label="t('gear.itemsTable.quickAddPlaceholder')"
          class="h-10 sm:h-[2.1rem]! border-transparent bg-transparent py-1! shadow-none placeholder:text-muted-foreground/70 focus-visible:border-input focus-visible:bg-background focus-visible:ring-1"
          data-editable-cell
          data-field="name"
          data-item-id="__quick-add__"
          @keydown="handleKeydown"
          @blur="handleBlur"
        />
        <span
          v-if="isCreating"
          class="shrink-0 text-xs text-muted-foreground"
        >
          {{ t('gear.actions.saving') }}
        </span>
      </div>
    </TableCell>
  </TableRow>
</template>
