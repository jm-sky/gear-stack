import { computed } from 'vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { usePermissions } from '@/shared/composables/usePermissions'
import { config } from '@/shared/config/config'

export const useAi = () => {
  const isEnabled = computed(() => config.features.ai.enabled)
  const { isAuthenticated } = useAuth()
  const { canUsePremiumFeatures } = usePermissions()

  const canUseAi = computed<boolean>(() => (isEnabled.value && isAuthenticated.value && canUsePremiumFeatures.value) ?? false)

  return {
    canUseAi,
  }
}
