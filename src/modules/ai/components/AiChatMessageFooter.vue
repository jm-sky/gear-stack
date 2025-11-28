<!--
  AI Chat Message Component
  Displays a single chat message with markdown support
-->
<script setup lang="ts">
import { CheckIcon, XIcon } from 'lucide-vue-next'
import { computed, ref, } from 'vue'
import Button from '@/components/ui/button/Button.vue'
import { usePermissions } from '@/shared/composables/usePermissions'
import type { IAiChatMessage, IAiStructuredOutput } from '../types'
import AiCostDisplay from './AiCostDisplay.vue'

const { isAdmin } = usePermissions()

const { message, debugPrompt } = defineProps<{
  message: IAiChatMessage
  debugPrompt?: string | null
  debugStructuredOutput?: IAiStructuredOutput | null
}>()

const debugPromptMessage = ref(false)
const debugStructuredOutputMessage = ref(false)

const shouldShowCost = computed<boolean>(() => {
  return message.role === 'assistant' && message.tokens !== undefined && message.cost !== undefined
})

const shouldShowDebug = computed<boolean>(() => {
  return message.role === 'assistant' && isAdmin.value && debugPrompt !== null && debugPrompt !== undefined
})
</script>

<template>
  <div v-if="shouldShowDebug || shouldShowCost" class="w-full flex flex-col sm:flex-row items-center justify-between gap-2 mt-3 border-t pt-2">
    <AiCostDisplay
      v-if="shouldShowCost"
      :tokens="message.tokens"
      :cost="message.cost"
    />
    <div v-if="shouldShowDebug" class="flex flex-row gap-2">
      <Button
        :variant="debugPromptMessage ? 'default' : 'outline'"
        size="xs"
        @click="debugPromptMessage = !debugPromptMessage"
      >
        <CheckIcon v-if="debugPromptMessage" class="size-3" />
        <XIcon v-if="!debugPromptMessage" class="size-3" />
        Prompt
      </Button>
      <Button
        :variant="debugStructuredOutputMessage ? 'default' : 'outline'"
        size="xs"
        @click="debugStructuredOutputMessage = !debugStructuredOutputMessage"
      >
        <CheckIcon v-if="debugStructuredOutputMessage" class="size-3" />
        <XIcon v-if="!debugStructuredOutputMessage" class="size-3" />
        Output
      </Button>
    </div>
  </div>
</template>
