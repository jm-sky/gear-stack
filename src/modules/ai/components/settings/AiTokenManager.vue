<script setup lang="ts">
import { Key, Trash2 } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAiStore } from '@/modules/ai/store/useAiStore'
import { useHandleError } from '@/shared/composables/useHandleError'

const { isAuthenticated = true } = defineProps<{
  isAuthenticated?: boolean
}>()

const { t } = useI18n()
const { handleError } = useHandleError()
const aiStore = useAiStore()

const apiToken = ref('')
const isSavingToken = ref(false)
const isRemovingToken = ref(false)

const hasOwnToken = computed(() => aiStore.hasOwnToken)

const handleSaveToken = async () => {
  if (!apiToken.value.trim()) {
    toast.error(t('gear.settings.ai.tokenRequired'))
    return
  }

  isSavingToken.value = true
  try {
    await aiStore.setApiToken(apiToken.value)
    apiToken.value = ''
    toast.success(t('gear.settings.ai.tokenSaved'))
  } catch (error: unknown) {
    handleError(error, { fallbackMessage: t('gear.settings.ai.tokenSaveError') })
  } finally {
    isSavingToken.value = false
  }
}

const handleRemoveToken = async () => {
  isRemovingToken.value = true
  try {
    await aiStore.removeApiToken()
    toast.success(t('gear.settings.ai.tokenRemoved'))
  } catch (error: unknown) {
    handleError(error, { fallbackMessage: t('gear.settings.ai.tokenRemoveError') })
  } finally {
    isRemovingToken.value = false
  }
}
</script>

<template>
  <div class="space-y-3">
    <div class="flex items-center gap-2">
      <Key :size="16" />
      <Label>
        {{ t('gear.settings.ai.apiToken.label') }}
      </Label>
    </div>
    <p class="text-sm text-muted-foreground">
      {{ t('gear.settings.ai.apiToken.subtitle') }}
    </p>

    <div v-if="hasOwnToken" class="space-y-3">
      <div class="rounded-md border bg-muted/50 p-3">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium">
              {{ t('gear.settings.ai.apiToken.configured') }}
            </p>
            <p class="text-xs text-muted-foreground">
              {{ t('gear.settings.ai.apiToken.encrypted') }}
            </p>
          </div>
          <Button
            variant="destructive"
            size="sm"
            :loading="isRemovingToken"
            :disabled="!isAuthenticated"
            @click="handleRemoveToken"
          >
            <Trash2 class="size-4" />
            {{ t('gear.settings.ai.apiToken.remove') }}
          </Button>
        </div>
      </div>
    </div>

    <div v-else class="space-y-3">
      <Input
        v-model="apiToken"
        type="password"
        :placeholder="t('gear.settings.ai.apiToken.placeholder')"
        :disabled="!isAuthenticated"
        class="font-mono text-sm"
      />
      <Button
        type="button"
        :loading="isSavingToken"
        :disabled="!isAuthenticated"
        @click="handleSaveToken"
      >
        {{ t('gear.settings.ai.apiToken.save') }}
      </Button>
    </div>
  </div>
</template>
