<!--
  AI Chat Window Component
  Main chat interface for AI interactions
-->
<script setup lang="ts">
import { Loader2 } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAiActions } from '../composables/useAiActions'
import { useAiChat } from '../composables/useAiChat'
import { useAiContext } from '../composables/useAiContext'
import { useAiStore } from '../store/useAiStore'
import AiChatInputSection from './AiChatInputSection.vue'
import AiChatMessage from './AiChatMessage.vue'
import AiChatTemplateMsgButton from './AiChatTemplateMsgButton.vue'
import AiChatWindowHeader from './AiChatWindowHeader.vue'
import AiContextConfig from './AiContextConfig.vue'

const { t } = useI18n()

const props = defineProps<{
  containerIds?: string[]
}>()

const aiStore = useAiStore()
const { messages, isLoading, lastPrompt, lastStructuredOutput, sendMessage, hasMessages } = useAiChat()
const { buildContextData } = useAiContext()
const { executeAction } = useAiActions()

const userMessage = ref('')
const showContextConfig = ref(false)
const includeContainerData = ref(true)

const emit = defineEmits<{
  close: []
}>()

onMounted(async () => {
  // Load settings and models on mount
  if (!aiStore.settings) {
    await aiStore.loadSettings()
  }
  if (aiStore.availableModels.length === 0) {
    await aiStore.loadModels()
  }
})

const handleSend = async (): Promise<void> => {
  if (!userMessage.value.trim() || isLoading.value) return

  // Build context with actual container data if enabled
  const context: Record<string, unknown> = includeContainerData.value && props.containerIds
    ? buildContextData(props.containerIds)
    : {}

  const response = await sendMessage(userMessage.value, context)
  userMessage.value = ''

  // Execute structured output action if present
  if (response?.structured_output) {
    const containerId = props.containerIds?.[0]
    await executeAction(response.structured_output, containerId)
  }
}

const onTemplatePrompt = (prompt: string) => {
  userMessage.value = prompt
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header with model selector -->
    <AiChatWindowHeader
      v-model:show-context-config="showContextConfig"
      @close="emit('close')"
    />

    <!-- Context config (collapsible) -->
    <AiContextConfig v-if="showContextConfig" />

    <!-- Messages -->
    <div class="relative flex-1 overflow-y-auto p-2 md:p-4 space-y-4">
      <div v-if="!hasMessages" class="absolute bottom-0 left-0 w-full text-xs z-10 flex flex-nowrap whitespace-nowrap gap-4 px-4 overflow-x-auto">
        <AiChatTemplateMsgButton variant="whatsUnnecessary" @prompt="onTemplatePrompt" />
        <AiChatTemplateMsgButton variant="whatsNeeded" @prompt="onTemplatePrompt" />
        <AiChatTemplateMsgButton variant="addRandomItem" @prompt="onTemplatePrompt" />
      </div>

      <div v-if="!hasMessages" class="flex items-center justify-center h-full text-muted-foreground">
        <p class="text-sm">
          {{ t('ai.chat.startConversation') }}
        </p>
      </div>

      <AiChatMessage
        v-for="(message, index) in messages"
        :key="message.id"
        :message
        :debug-prompt="message.role === 'assistant' && index === messages.length - 1 ? lastPrompt : null"
        :debug-structured-output="message.role === 'assistant' && index === messages.length - 1 ? lastStructuredOutput : null"
      />

      <div v-if="isLoading" class="flex items-center gap-2">
        <Loader2 class="size-4 animate-spin" />
        <span class="text-sm text-muted-foreground">{{ t('ai.chat.thinking') }}</span>
      </div>
    </div>

    <!-- Input -->
    <AiChatInputSection
      v-model:user-message="userMessage"
      :container-ids="props.containerIds"
      :is-loading="isLoading"
      :include-container-data="includeContainerData"
      @send="handleSend"
      @toggle-context-config="showContextConfig = !showContextConfig"
    />
  </div>
</template>

