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
    prompt: string,
    context?: { container_ids?: string[]; fields?: string[] },
    expectStructuredOutput = true,
  ): Promise<IAiChatResponse | null> => {
    if (!prompt.trim()) return null

    isLoading.value = true
    error.value = null

    // Add user message
    const userMessage: IAiChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: prompt,
      created_at: new Date().toISOString(),
    }
    messages.value.push(userMessage)

    try {
      const request: IAiChatRequest = {
        prompt,
        context,
        model: aiStore.settings?.selected_model,
        expect_structured_output: expectStructuredOutput,
      }

      const response = await aiApiService.chat(request)

      // Add assistant message
      const assistantMessage: IAiChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        tokens: response.tokens,
        cost: response.cost,
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

