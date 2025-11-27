<script setup lang="ts">
import { BackpackIcon, CheckIcon, SendIcon, XIcon } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'

const { t } = useI18n()

defineProps<{
  containerIds?: string[]
  isLoading?: boolean
}>()

const userMessage = defineModel<string>('userMessage', { required: true })
const includeContainerData = defineModel<boolean>('includeContainerData', { required: true })

const emit = defineEmits<{
  send: [message: string]
}>()

const handleSend = (): void => {
  emit('send', userMessage.value)
}

const handleKeyDown = (event: KeyboardEvent): void => {
  if (event.ctrlKey && event.key === 'Enter') {
    event.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="border-t p-4">
    <!-- ChatGPT like input section -->
    <div class="border rounded-3xl bg-foreground/5 px-2 py-2">
      <div class="flex flex-col gap-1">
        <textarea
          v-model="userMessage"
          class="text-sm w-full resize-none px-2 py-3 rounded-lg focus-visible:outline-none focus-visible:ring-0"
          rows="1"
          :placeholder="t('ai.chat.placeholder')"
          @keydown="handleKeyDown"
        />
        <div class="flex flex-row items-center justify-between gap-2">
          <div class="flex flex-row gap-2 items-center">
            <!-- Actions -->
            <!-- Context toggle (only show when containerIds are provided) -->
            <Button
              v-tooltip="t('ai.chat.includeContainerData.tooltip')"
              :variant="includeContainerData ? 'default' : 'outline'"
              size="sm"
              class="group rounded-full"
              @click="includeContainerData = !includeContainerData"
            >
              <BackpackIcon class="size-4 group-hover:hidden" />
              <XIcon v-if="includeContainerData" class="size-4 hidden group-hover:block" />
              <CheckIcon v-else class="size-4 hidden group-hover:block" />
              {{ t('ai.chat.includeContainerData.label') }}
            </Button>
          </div>
          <div class="flex flex-row gap-2 items-center justify-end">
            <Button
              :disabled="!userMessage.trim() || isLoading"
              size="icon"
              class="rounded-full"
              @click="handleSend"
            >
              <SendIcon class="size-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <p class="text-xs text-muted-foreground mt-2">
      {{ t('ai.chat.sendHint') }}
    </p>
  </div>
</template>
