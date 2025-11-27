/**
 * AI Chat Composable
 * Handles chat interactions with AI
 */

import { computed, ref } from 'vue'
import type { IAiChatMessage, IAiChatRequest, IAiChatResponse } from '../types'
import { aiApiService } from '../services/aiApiService'
import { useAiStore } from '../store/useAiStore'

export function useAiChat() {
  const aiStore = useAiStore()
  const messages = ref<IAiChatMessage[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const sendMessage = async (
    message: string,
    context?: Record<string, unknown>,
  ): Promise<IAiChatResponse | null> => {
    if (!message.trim()) return null

    isLoading.value = true
    error.value = null

    // Add user message
    const userMessage: IAiChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    }
    messages.value.push(userMessage)

    try {
      const request: IAiChatRequest = {
        message,
        context,
        model: aiStore.settings?.selected_model,
      }

      const response = await aiApiService.chat(request)

      // Add assistant message
      const assistantMessage: IAiChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        tokens: {
          input: response.tokens.prompt,
          output: response.tokens.completion,
          total: response.tokens.total,
        },
        cost: response.cost !== null
          ? {
              input: 0,
              output: 0,
              total: response.cost,
            }
          : undefined,
        created_at: new Date().toISOString(),
      }
      messages.value.push(assistantMessage)

      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message'
      error.value = errorMessage

      // Add error message
      const errorMsg: IAiChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Error: ${errorMessage}`,
        created_at: new Date().toISOString(),
      }
      messages.value.push(errorMsg)

      return null
    } finally {
      isLoading.value = false
    }
  }

  const clearMessages = (): void => {
    messages.value = []
    error.value = null
  }

  const hasMessages = computed<boolean>(() => messages.value.length > 0)

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    hasMessages,
  }
}

