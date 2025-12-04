import { computed } from 'vue'
import { useAiStore } from '@/modules/ai/store/useAiStore'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { useUserStore } from '@/modules/user/store/useUserStore'
import { usePermissions } from '@/shared/composables/usePermissions'
import { config } from '@/shared/config/config'

export const useAi = () => {
  const isEnabled = computed(() => config.features.ai.enabled)
  const { isAuthenticated } = useAuth()
  const { isPremium, isAdmin, isOwner } = usePermissions()
  const aiStore = useAiStore()
  const userStore = useUserStore()

  const canUseAi = computed<boolean>(() => {
    if (!isEnabled.value || !isAuthenticated.value) {
      return false
    }

    // Premium, Admin, or Owner can always use AI
    if (isPremium.value || isAdmin.value || isOwner.value) {
      return true
    }

    // Regular user can only use AI if they have their own token
    const hasOwnToken = aiStore.hasOwnToken
    const userFeatures = userStore.user?.features
    // Check from features (limit === null means unlimited = own token)
    const hasOwnTokenFromFeatures = userFeatures?.ai?.limit === null

    return hasOwnToken || hasOwnTokenFromFeatures
  })

  return {
    canUseAi,
  }
}
