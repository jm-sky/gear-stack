<script setup lang="ts">
import { AlertCircle, Check, Loader2 } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import type { InlineRowSaveStatus } from '@/modules/gear/types/inlineEditing.types'

const { t } = useI18n()

const props = defineProps<{
  status: InlineRowSaveStatus
}>()

const emit = defineEmits<{
  retry: []
}>()

const tooltip = computed<string>(() => {
  switch (props.status) {
    case 'pending':
      return t('gear.actions.pendingSave')
    case 'saving':
      return t('gear.actions.saving')
    case 'saved':
      return t('gear.actions.saved')
    case 'error':
      return t('gear.actions.saveError')
    default:
      return ''
  }
})
</script>

<template>
  <div
    class="flex size-8 shrink-0 items-center justify-center"
    :aria-label="tooltip || undefined"
    :aria-hidden="status === 'idle'"
  >
    <template v-if="status !== 'idle'">
      <span
        v-if="status === 'pending'"
        v-tooltip="tooltip"
        class="size-2.5 animate-pulse rounded-full bg-amber-500"
      />
      <Loader2
        v-else-if="status === 'saving'"
        v-tooltip="tooltip"
        class="size-4 animate-spin text-muted-foreground"
      />
      <Check
        v-else-if="status === 'saved'"
        v-tooltip="tooltip"
        class="size-4 text-emerald-600"
      />
      <Button
        v-else-if="status === 'error'"
        v-tooltip="tooltip"
        size="sm"
        variant="ghost"
        class="size-8 p-0 text-destructive"
        :aria-label="t('gear.actions.retrySave')"
        @click="emit('retry')"
      >
        <AlertCircle class="size-4" />
      </Button>
    </template>
  </div>
</template>
