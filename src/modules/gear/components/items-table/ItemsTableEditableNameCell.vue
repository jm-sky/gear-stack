<script setup lang="ts">
import { Check, RefreshCcwIcon, XIcon } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useInlineItemEditing } from '../../composables/useInlineItemEditing'
import type { IGearItem } from '@/modules/gear/types/gear.types'

const { t } = useI18n()

const props = defineProps<{
  item: IGearItem
  isExpired?: boolean
  isExpiringSoon?: boolean
}>()

const emit = defineEmits<{
  update: [item: IGearItem]
}>()

// Use shared composable
const { isLoading, save } = useInlineItemEditing(props.item)

// In edit mode, always show input
const editedName = ref(props.item.name)
const isResetting = ref(false)

const textClass = computed<string>(() => {
  if (props.isExpired) return 'text-destructive font-semibold'
  if (props.isExpiringSoon) return 'text-yellow-600'
  return ''
})

// Handle blur - save immediately (unless reset is in progress)
async function handleBlur() {
  // Don't save if reset button was clicked
  if (isResetting.value) {
    return
  }

  if (editedName.value.trim() === '') {
    // Validation - name is required, reset to original
    editedName.value = props.item.name
    return
  }

  if (editedName.value.trim() !== props.item.name) {
    const updated = await save({ name: editedName.value.trim() })
    if (updated) {
      emit('update', updated)
    }
  }
}

// Save on Enter
async function handleEnter() {
  if (editedName.value.trim() === '') {
    // Validation - name is required
    editedName.value = props.item.name
    return
  }

  const updated = await save({ name: editedName.value.trim() })
  if (updated) {
    emit('update', updated)
  }
}

// Watch for external changes to item
watch(
  () => props.item.name,
  (newName) => {
    editedName.value = newName
  },
)

// Handle mousedown on reset button - prevent blur from saving
function handleResetMousedown() {
  isResetting.value = true
}

// Reset value and clear flag
function handleReset() {
  editedName.value = props.item.name
  // Clear flag after a small delay to ensure blur handler has finished
  setTimeout(() => {
    isResetting.value = false
  }, 0)
}
</script>

<template>
  <div class="flex items-center">
    <div class="relative flex-1 mr-1">
      <Input
        v-model="editedName"
        v-tooltip="isExpiringSoon ? t('gear.item.expiration.expiringSoon') : ''"
        :disabled="isLoading"
        class="pr-8 py-1! h-[2.1rem]!"
        :class="[textClass, isExpiringSoon ? 'border-yellow-600' : '']"
        @keyup.enter="handleEnter"
        @blur="handleBlur"
      />
      <!-- Reset button -->
      <button
        v-if="editedName && editedName !== props.item.name && !isLoading"
        type="button"
        class="absolute right-2 top-0 bottom-0 my-auto p-0"
        @mousedown.prevent="handleResetMousedown"
        @click.stop.prevent="handleReset"
      >
        <XIcon class="size-4" />
      </button>
    </div>
    <Button
      v-tooltip="isLoading ? t('gear.actions.saving') : t('gear.actions.save')"
      size="sm"
      variant="ghost"
      class="px-2!"
      :aria-label="t('gear.actions.save')"
      @click="handleEnter"
    >
      <Check v-if="!isLoading" class="size-4" />
      <RefreshCcwIcon v-if="isLoading" class="size-4 animate-spin" />
    </Button>
    <!-- Badges for expired/expiring items -->
    <Badge v-if="isExpired" variant="destructive" class="text-xs">
      {{ t('gear.item.expiration.expired') }}
    </Badge>
  </div>
</template>

