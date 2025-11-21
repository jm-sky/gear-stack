import { ref } from 'vue'
import { config } from '@/shared/config/config'
import { executeRecaptcha } from '@/shared/utils/recaptcha'

export function useRecaptcha() {
  const isReady = ref(false)
  const isExecuting = ref(false)
  const error = ref<string | null>(null)

  /**
   * Get reCAPTCHA token for action
   */
  const getToken = async (action: string): Promise<string | null> => {
    if (!config.recaptcha.enabled) {
      return null
    }

    isExecuting.value = true
    error.value = null

    try {
      const token = await executeRecaptcha(action)
      isReady.value = true
      return token
    }
    catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to get token'
      return null
    }
    finally {
      isExecuting.value = false
    }
  }

  return {
    error,
    getToken,
    isEnabled: config.recaptcha.enabled,
    isExecuting,
    isReady,
  }
}
