<script setup lang="ts">
import { History, HourglassIcon, Settings, Trash2, X } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { ButtonLink } from '@/components/ui/button-link'
import DialogTitle from '@/components/ui/dialog/DialogTitle.vue'
import { useAiChat } from '../composables/useAiChat'
import { AiRoutePath } from '../routes'
import AiModelSelector from './AiModelSelector.vue'

const { t } = useI18n()
const { clearMessages } = useAiChat()

const showContextConfig = defineModel<boolean>('showContextConfig', { required: true })
const showHistorySidebar = defineModel<boolean>('showHistorySidebar', { required: true })

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <DialogTitle class="flex items-center justify-between gap-2 border-b p-4">
    <h2 class="text-lg font-semibold">
      {{ t('ai.chat.title') }}
    </h2>
    <div class="flex flex-col md:flex-row items-center gap-2 -my-1">
      <div class="hidden md:flex flex-row items-center gap-2">
        <AiModelSelector />
        <Button
          v-tooltip.bottom="t('ai.chat.showContextConfig')"
          :variant="showContextConfig ? 'default' : 'outline'"
          size="sm"
          @click="showContextConfig = !showContextConfig"
        >
          <Settings class="size-4" />
          {{ t('ai.chat.context') }}
        </Button>
        <Button
          v-tooltip.bottom="t('ai.chat.clearMessages')"
          variant="ghost"
          size="sm"
          @click="clearMessages"
        >
          <Trash2 class="size-4" />
        </Button>
        <Button
          v-tooltip.bottom="t('ai.chat.history.openHistory')"
          variant="ghost"
          size="sm"
          @click="showHistorySidebar = true"
        >
          <History class="size-4" />
        </Button>
        <ButtonLink
          v-tooltip.bottom="t('ai.history.title')"
          variant="ghost"
          size="sm"
          :to="AiRoutePath.History"
        >
          <HourglassIcon class="size-4" />
        </ButtonLink>
      </div>
      <Button
        v-tooltip.bottom="t('common.close')"
        variant="ghost"
        size="sm"
        @click="emit('close')"
      >
        <X class="size-4" />
      </Button>
    </div>
  </DialogTitle>
</template>
