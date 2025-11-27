import { computed } from 'vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { config } from '@/shared/config/config'

export const useAi = () => {
  const isEnabled = computed(() => config.features.ai.enabled)
  const { user, isAuthenticated } = useAuth()

  const canUseAi = computed<boolean>(() => (isEnabled.value && isAuthenticated.value && user.value?.isAdmin) ?? false)

  return {
    canUseAi,
  }
}
