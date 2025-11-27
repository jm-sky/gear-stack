<!--
  AI Chat Dialog Component
  Dialog wrapper for AI chat interface
-->
<script setup lang="ts">
import { Dialog, DialogContent } from '@/components/ui/dialog'
import AiChatWindow from './AiChatWindow.vue'

const props = defineProps<{
  open: boolean
  context?: {
    container_ids?: string[]
    fields?: string[]
  }
}>()

const emits = defineEmits<{
  'update:open': [value: boolean]
}>()

const handleOpenChange = (value: boolean): void => {
  emits('update:open', value)
}
</script>

<template>
  <Dialog :open="props.open" @update:open="handleOpenChange">
    <DialogContent
      class="sm:max-w-4xl h-[80vh] flex flex-col p-0"
      :show-close-button="false"
      aria-describedby="ai-chat-dialog-description"
    >
      <!-- installHook.js:1 Warning: Missing `Description` or `aria-describedby="undefined"` for DialogContent. -->
      <AiChatWindow @close="handleOpenChange(false)" />
    </DialogContent>
  </Dialog>
</template>

