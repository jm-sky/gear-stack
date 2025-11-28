<script setup lang="ts">
import { Bot, Key, Trash2 } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import Separator from '@/components/ui/separator/Separator.vue'
import AiPremiumFeatureAlert from '@/modules/ai/components/AiPremiumFeatureAlert.vue'
import { useAiModels } from '@/modules/ai/composables/useAiModels'
import { useAiStore } from '@/modules/ai/store/useAiStore'
import { useHandleError } from '@/shared/composables/useHandleError'
import { usePermissions } from '@/shared/composables/usePermissions'

const { t } = useI18n()
const { handleError } = useHandleError()
const { canUsePremiumFeatures } = usePermissions()

const aiStore = useAiStore()
const { models, selectedModel, loadModels, selectModel } = useAiModels()

const apiToken = ref('')
const isSavingToken = ref(false)
const isRemovingToken = ref(false)

const monthlyUsage = computed(() => aiStore.monthlyUsage)
const hasOwnToken = computed(() => aiStore.hasOwnToken)

const selectedModelId = computed({
  get: () => selectedModel.value?.id ?? '',
  set: async (value: string) => {
    if (value) {
      await selectModel(value)
      toast.success(t('gear.settings.ai.modelUpdated'))
    }
  },
})

const progressPercentage = computed(() => {
  if (!monthlyUsage.value.tokenLimit) return 0
  return Math.min((monthlyUsage.value.tokens / monthlyUsage.value.tokenLimit) * 100, 100)
})

const costProgressPercentage = computed(() => {
  if (!monthlyUsage.value.costLimit) return 0
  return Math.min((monthlyUsage.value.cost / monthlyUsage.value.costLimit) * 100, 100)
})

const progressColor = computed(() => {
  const percentage = progressPercentage.value
  if (percentage >= 90) return 'bg-red-500'
  if (percentage >= 70) return 'bg-yellow-500'
  return 'bg-green-500'
})

const costProgressColor = computed(() => {
  const percentage = costProgressPercentage.value
  if (percentage >= 90) return 'bg-red-500'
  if (percentage >= 70) return 'bg-yellow-500'
  return 'bg-green-500'
})

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

onMounted(async () => {
  await aiStore.loadSettings()
  if (models.value.length === 0) {
    await loadModels()
  }
})
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex items-center gap-2">
        <Bot :size="20" />
        <CardTitle>{{ t('gear.settings.ai.title') }}</CardTitle>
      </div>
      <CardDescription>
        {{ t('gear.settings.ai.description') }}
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-6">
      <AiPremiumFeatureAlert v-if="!canUsePremiumFeatures" />

      <!-- Default Model -->
      <div class="space-y-3">
        <Label>
          {{ t('gear.settings.ai.defaultModel.label') }}
          <span class="text-destructive">*</span>
        </Label>
        <p class="text-sm text-muted-foreground">
          {{ t('gear.settings.ai.defaultModel.subtitle') }}
        </p>
        <Select v-model="selectedModelId">
          <SelectTrigger>
            <SelectValue :placeholder="t('gear.settings.ai.defaultModel.placeholder')">
              <span v-if="selectedModel" class="flex items-center gap-2">
                <span class="font-medium">{{ selectedModel.name }}</span>
                <span class="text-xs text-muted-foreground uppercase">{{ selectedModel.provider }}</span>
              </span>
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            <SelectItem
              v-for="model in models"
              :key="model.id"
              :value="model.id"
            >
              <div class="flex flex-col gap-0.5">
                <span class="font-medium">{{ model.name }}</span>
                <span class="text-xs text-muted-foreground">{{ model.provider }}</span>
              </div>
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Separator />

      <!-- API Token -->
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
            class="font-mono text-sm"
          />
          <Button
            type="button"
            :loading="isSavingToken"
            @click="handleSaveToken"
          >
            {{ t('gear.settings.ai.apiToken.save') }}
          </Button>
        </div>
      </div>

      <Separator />

      <!-- Usage Limits & Progress -->
      <div class="space-y-4">
        <div>
          <Label>
            {{ t('gear.settings.ai.usage.label') }}
          </Label>
          <p class="text-sm text-muted-foreground">
            {{ t('gear.settings.ai.usage.subtitle') }}
          </p>
        </div>

        <!-- Token Usage -->
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-muted-foreground">{{ t('gear.settings.ai.usage.tokens') }}</span>
            <span class="font-medium">
              {{ monthlyUsage.tokens.toLocaleString() }}
              <span v-if="monthlyUsage.tokenLimit">
                / {{ monthlyUsage.tokenLimit.toLocaleString() }}
              </span>
              <span v-else class="text-muted-foreground">
                ({{ t('gear.settings.ai.usage.unlimited') }})
              </span>
            </span>
          </div>
          <div v-if="monthlyUsage.tokenLimit" class="h-2 w-full overflow-hidden rounded-full bg-muted">
            <div
              :class="progressColor"
              class="h-full transition-all duration-300"
              :style="{ width: `${progressPercentage}%` }"
            />
          </div>
          <div v-else class="h-2 w-full rounded-full bg-green-500/20" />
        </div>

        <!-- Cost Usage -->
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-muted-foreground">{{ t('gear.settings.ai.usage.cost') }}</span>
            <span class="font-medium">
              ${{ monthlyUsage.cost.toFixed(4) }}
              <span v-if="monthlyUsage.costLimit">
                / ${{ monthlyUsage.costLimit.toFixed(4) }}
              </span>
              <span v-else class="text-muted-foreground">
                ({{ t('gear.settings.ai.usage.unlimited') }})
              </span>
            </span>
          </div>
          <div v-if="monthlyUsage.costLimit" class="h-2 w-full overflow-hidden rounded-full bg-muted">
            <div
              :class="costProgressColor"
              class="h-full transition-all duration-300"
              :style="{ width: `${costProgressPercentage}%` }"
            />
          </div>
          <div v-else class="h-2 w-full rounded-full bg-green-500/20" />
        </div>

        <p v-if="hasOwnToken" class="text-xs text-muted-foreground">
          {{ t('gear.settings.ai.usage.ownTokenNote') }}
        </p>
        <p v-else class="text-xs text-muted-foreground">
          {{ t('gear.settings.ai.usage.systemTokenNote') }}
        </p>
      </div>
    </CardContent>
  </Card>
</template>

