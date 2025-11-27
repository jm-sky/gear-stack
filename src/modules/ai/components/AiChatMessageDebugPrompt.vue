<script setup lang="ts">
import { ChevronDown, ChevronUp } from 'lucide-vue-next'
import { computed } from 'vue'
import { Button } from '@/components/ui/button'
import { useAdmin } from '@/modules/admin/composables/useAdmin'
import type { IAiChatMessage } from '../types'

const { isAdmin } = useAdmin()

const showDebug = defineModel<boolean>('showDebug', { default: false })

const { message, debugPrompt } = defineProps<{
  message: IAiChatMessage
  debugPrompt?: string | null
}>()

const shouldShowDebug = computed<boolean>(() => {
  return message.role === 'assistant' && isAdmin.value && debugPrompt !== null && debugPrompt !== undefined
})
</script>

<template>
  <div v-if="shouldShowDebug" class="mt-3 border-t pt-2">
    <Button
      variant="ghost"
      size="sm"
      class="text-xs h-auto py-1"
      @click="showDebug = !showDebug"
    >
      Debug: Full Prompt
      <ChevronDown v-if="!showDebug" class="size-3" />
      <ChevronUp v-if="showDebug" class="size-3" />
    </Button>

    <div v-if="showDebug" class="border mt-2 px-2 py-1 bg-foreground/5 rounded text-xs font-mono whitespace-pre-wrap overflow-x-auto">
      {{ debugPrompt }}
    </div>
  </div>
</template>
