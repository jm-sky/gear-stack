<script setup lang="ts">
import { Check, Copy } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const props = defineProps<{
  open: boolean
  markdown: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { t } = useI18n()
const copied = ref(false)

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(props.markdown)
    copied.value = true
    toast.success(t('gear.actions.exportToPromptSuccess'))
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (error) {
    toast.error(t('common.error'))
    console.error('Error copying to clipboard:', error)
  }
}

const handleOpenChange = (value: boolean) => {
  emit('update:open', value)
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="min-w-3xl max-w-6xl max-h-[90vh] flex flex-col">
      <DialogHeader>
        <DialogTitle>
          {{ t('gear.actions.exportToPrompt') }}
        </DialogTitle>
        <DialogDescription>
          {{ t('gear.actions.exportToPromptDescription', 'Skopiuj poniższą treść i wklej do ChatGPT lub innego AI') }}
        </DialogDescription>
      </DialogHeader>

      <div class="flex-1 overflow-auto">
        <pre class="whitespace-pre-wrap text-sm font-mono bg-muted p-4 rounded-md border overflow-x-auto">{{ markdown }}</pre>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="handleOpenChange(false)">
          {{ t('common.close') }}
        </Button>
        <Button @click="handleCopy">
          <Copy v-if="!copied" class="size-4" />
          <Check v-else class="size-4" />
          {{ copied ? t('common.copyToClipboard.copied') : t('common.copyToClipboard.copy') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

