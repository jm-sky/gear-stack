<script setup lang="ts">
import { Bot } from 'lucide-vue-next'
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Separator from '@/components/ui/separator/Separator.vue'
import AiModelSelector from '@/modules/ai/components/settings/AiModelSelector.vue'
import AiTokenManager from '@/modules/ai/components/settings/AiTokenManager.vue'
import AiUsageDisplay from '@/modules/ai/components/settings/AiUsageDisplay.vue'
import { useAiModels } from '@/modules/ai/composables/useAiModels'
import { useAiStore } from '@/modules/ai/store/useAiStore'
import { useUser } from '@/modules/user/composables/useUser'
import { useUserStore } from '@/modules/user/store/useUserStore'
import { usePermissions } from '@/shared/composables/usePermissions'

const { t } = useI18n()
const { isAuthenticated } = usePermissions()

const aiStore = useAiStore()
const userStore = useUserStore()
const { models, loadModels } = useAiModels()
const { loadProfile } = useUser()

onMounted(async () => {
  await aiStore.loadSettings()
  if (models.value.length === 0) {
    await loadModels()
  }
  // Load user profile to get features if not already loaded
  if (!userStore.user?.features) {
    try {
      await loadProfile()
    } catch (error) {
      // Silently fail if user profile can't be loaded
      console.warn('Failed to load user profile for features:', error)
    }
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
      <div :class="{ 'opacity-50 pointer-events-none': !isAuthenticated }">
        <!-- AI Model Selector -->
        <AiModelSelector :is-authenticated />

        <Separator />

        <!-- API Token Manager -->
        <AiTokenManager :is-authenticated />

        <Separator />

        <!-- Usage Display -->
        <AiUsageDisplay />
      </div>
    </CardContent>
  </Card>
</template>

