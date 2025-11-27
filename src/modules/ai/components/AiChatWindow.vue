<!--
  AI Chat Window Component
  Main chat interface for AI interactions
-->
<script setup lang="ts">
import { Loader2, Send, Settings, Trash2, X } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import DialogTitle from '@/components/ui/dialog/DialogTitle.vue'
import { Textarea } from '@/components/ui/textarea'
import { useAiChat } from '../composables/useAiChat'
import { useAiContext } from '../composables/useAiContext'
import { useAiStore } from '../store/useAiStore'
import AiChatMessage from './AiChatMessage.vue'
import AiChatTemplateMsgButton from './AiChatTemplateMsgButton.vue'
import AiContextConfig from './AiContextConfig.vue'
import AiModelSelector from './AiModelSelector.vue'

const { t } = useI18n()

const props = defineProps<{
  containerIds?: string[]
}>()

const aiStore = useAiStore()
const { messages, isLoading, lastPrompt, sendMessage, clearMessages, hasMessages } = useAiChat()
const { buildContextData } = useAiContext()

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

  await sendMessage(userMessage.value, context)
  userMessage.value = ''
}

const handleKeyDown = (event: KeyboardEvent): void => {
  if (event.ctrlKey && event.key === 'Enter') {
    event.preventDefault()
    handleSend()
  }
}

const onTemplatePrompt = (prompt: string) => {
  userMessage.value = prompt
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header with model selector -->
    <DialogTitle class="flex items-center justify-between border-b p-4">
      <h2 class="text-lg font-semibold">
        {{ t('ai.chat.title') }}
      </h2>
      <div class="flex items-center gap-2 -my-1">
        <AiModelSelector />
        <Button
          :variant="showContextConfig ? 'default' : 'outline'"
          size="sm"
          @click="showContextConfig = !showContextConfig"
        >
          <Settings class="size-4" />
          {{ t('ai.chat.context') }}
        </Button>
        <Button variant="ghost" size="sm" @click="clearMessages">
          <Trash2 class="size-4" />
        </Button>
        <Button variant="ghost" size="sm" @click="emit('close')">
          <X class="size-4" />
        </Button>
      </div>
    </DialogTitle>

    <!-- Context config (collapsible) -->
    <AiContextConfig v-if="showContextConfig" />

    <!-- Messages -->
    <div class="relative flex-1 overflow-y-auto p-4 space-y-4">
      <div v-if="!hasMessages" class="absolute bottom-0 left-0 w-full text-sm z-10 flex gap-4 px-4">
        <AiChatTemplateMsgButton variant="whatsUnnecessary" @prompt="onTemplatePrompt" />
        <AiChatTemplateMsgButton variant="whatsNeeded" @prompt="onTemplatePrompt" />
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
      />

      <div v-if="isLoading" class="flex items-center gap-2">
        <Loader2 class="size-4 animate-spin" />
        <span class="text-sm text-muted-foreground">{{ t('ai.chat.thinking') }}</span>
      </div>
    </div>

    <!-- Input -->
    <div class="border-t p-4">
      <!-- Context toggle (only show when containerIds are provided) -->
      <div v-if="props.containerIds && props.containerIds.length > 0" class="flex items-center gap-2 mb-3">
        <Checkbox :id="'include-container-data'" v-model="includeContainerData" />
        <Label
          :for="'include-container-data'"
          class="text-sm font-normal cursor-pointer"
        >
          {{ t('ai.chat.includeContainerData') }}
        </Label>
      </div>

      <div class="flex gap-2">
        <Textarea
          v-model="userMessage"
          :placeholder="t('ai.chat.placeholder')"
          :rows="3"
          @keydown="handleKeyDown"
        />
        <Button
          :disabled="!userMessage.trim() || isLoading"
          @click="handleSend"
        >
          <Send class="size-4" />
        </Button>
      </div>
      <p class="text-xs text-muted-foreground mt-2">
        {{ t('ai.chat.sendHint') }}
      </p>
    </div>
  </div>
</template>

