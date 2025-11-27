<!--
  AI Chat Message Component
  Displays a single chat message with markdown support
-->
<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import { computed, } from 'vue'
import type { IAiChatMessage } from '../types'
import AiChatMessageDebugPrompt from './AiChatMessageDebugPrompt.vue'
import AiCostDisplay from './AiCostDisplay.vue'

const { message, debugPrompt } = defineProps<{
  message: IAiChatMessage
  debugPrompt?: string | null
}>()

const md = new MarkdownIt({
  html: false, // Disable HTML tags for security
  linkify: true, // Auto-convert URLs to links
  typographer: true, // Enable smart quotes and other typographic replacements
  breaks: true, // Convert line breaks to <br>
})

const renderedContent = computed<string>(() => {
  return md.render(message.content)
})

const messageClasses = computed<string>(() => {
  return message.role === 'user'
    ? 'bg-primary text-primary-foreground ml-auto max-w-[80%]'
    : 'bg-muted max-w-[80%]'
})
</script>

<template>
  <div :class="['p-3 rounded-lg', messageClasses]">
    <!-- eslint-disable-next-line vue/no-v-html -->
    <div class="prose prose-sm dark:prose-invert max-w-none" v-html="renderedContent" />

    <AiChatMessageDebugPrompt
      :message="message"
      :debug-prompt="debugPrompt"
    />

    <AiCostDisplay
      v-if="message.role === 'assistant' && (message.tokens || message.cost)"
      :tokens="message.tokens"
      :cost="message.cost"
      class="mt-3 border-t pt-2"
    />
  </div>
</template>

<style scoped>
/* Override prose styles for better integration with our theme */
.prose :deep(p) {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.prose :deep(p:first-child) {
  margin-top: 0;
}

.prose :deep(p:last-child) {
  margin-bottom: 0;
}

.prose :deep(ul),
.prose :deep(ol) {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.prose :deep(code) {
  background-color: hsl(var(--muted));
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
}

.prose :deep(pre) {
  background-color: hsl(var(--muted));
  padding: 0.75rem;
  border-radius: 0.375rem;
  overflow-x: auto;
}

.prose :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.prose :deep(a) {
  color: hsl(var(--primary));
  text-decoration: underline;
}

.prose :deep(a:hover) {
  opacity: 0.8;
}

.prose :deep(blockquote) {
  border-left: 3px solid hsl(var(--primary));
  padding-left: 1rem;
  font-style: italic;
  opacity: 0.9;
}

.prose :deep(h1),
.prose :deep(h2),
.prose :deep(h3),
.prose :deep(h4),
.prose :deep(h5),
.prose :deep(h6) {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.prose :deep(h1:first-child),
.prose :deep(h2:first-child),
.prose :deep(h3:first-child),
.prose :deep(h4:first-child),
.prose :deep(h5:first-child),
.prose :deep(h6:first-child) {
  margin-top: 0;
}

.prose :deep(ul) {
  list-style-type: disc;
  margin-left: 1rem;
}

.prose :deep(ol) {
  list-style-type: decimal;
  margin-left: 1rem;
}

.prose :deep(li) {
  margin-bottom: 0.25rem;
}
</style>
