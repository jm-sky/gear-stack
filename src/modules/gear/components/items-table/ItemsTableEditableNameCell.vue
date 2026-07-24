<script setup lang="ts">
import { UndoIcon } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { Input } from '@/components/ui/input'
import ItemsTableMoveButtons from './ItemsTableMoveButtons.vue'
import type { IGearItemV2, IUpdateGearItemV2Dto } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItemV2
  isExpired?: boolean
  isExpiringSoon?: boolean
  isSaving?: boolean
  canMoveUp?: boolean
  canMoveDown?: boolean
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto, options?: { immediate?: boolean }]
  moveUp: []
  moveDown: []
  navigate: [direction: 'next' | 'prev' | 'down']
}>()

const editedName = ref(props.item.name)
const isFocused = ref(false)
const suppressBlurSave = ref(false)

const textClass = computed<string>(() => {
  if (props.isExpired) return 'text-destructive font-semibold'
  if (props.isExpiringSoon) return 'text-yellow-600'
  return ''
})

const hasLocalChanges = computed<boolean>(() => {
  return editedName.value.trim() !== props.item.name
})

function emitChange(immediate = false) {
  if (editedName.value.trim() === '') {
    editedName.value = props.item.name
    emit('change', {})
    return
  }

  if (editedName.value.trim() !== props.item.name) {
    emit('change', { name: editedName.value.trim() }, { immediate })
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
    editedName.value = props.item.name
    emit('change', {})
    ;(document.activeElement as HTMLElement | null)?.blur()
    queueMicrotask(() => {
      suppressBlurSave.value = false
    })
  }
}

function handleReset() {
  editedName.value = props.item.name
  emit('change', {})
}

watch(
  () => props.item.name,
  (newName) => {
    if (!isFocused.value) {
      editedName.value = newName
    }
  },
)
</script>

<template>
  <div
    class="group flex min-w-32 sm:min-w-48 items-center gap-1"
    data-editable-cell
    data-field="name"
    :data-item-id="item.id"
  >
    <ItemsTableMoveButtons
      v-if="canMoveUp !== undefined && canMoveDown !== undefined"
      :can-move-up="canMoveUp"
      :can-move-down="canMoveDown"
      @move-up="emit('moveUp')"
      @move-down="emit('moveDown')"
    />
    <div class="relative flex-1">
      <Input
        :id="`item-name-${item.id}`"
        v-model="editedName"
        v-tooltip="isExpiringSoon ? t('gear.item.expiration.expiringSoon') : ''"
        :name="`item-name-${item.id}`"
        :aria-label="t('gear.item.name')"
        class="h-10 sm:h-[2.1rem]! rounded-l-none border-transparent bg-transparent py-1! pl-2 shadow-none focus-visible:border-input focus-visible:bg-background focus-visible:ring-1"
        :class="[textClass, isExpiringSoon ? 'border border-yellow-600' : '']"
        :disabled="isSaving"
        @focus="isFocused = true"
        @blur="handleBlur"
        @keydown="handleKeydown"
      />
      <button
        v-if="hasLocalChanges && isFocused"
        v-tooltip.bottom="t('gear.actions.undo')"
        type="button"
        :aria-label="t('gear.actions.undo')"
        class="absolute top-0 right-2 bottom-0 my-auto p-0"
        @mousedown.prevent
        @click.stop.prevent="handleReset"
      >
        <UndoIcon class="size-4" />
      </button>
    </div>
    <Badge
      v-if="isExpired"
      variant="destructive"
      class="text-xs"
    >
      {{ t('gear.item.expiration.expired') }}
    </Badge>
  </div>
</template>
