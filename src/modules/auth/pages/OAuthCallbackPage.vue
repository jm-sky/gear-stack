<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { authService } from '@/modules/auth/services/authService'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { useRecaptcha } from '@/shared/composables/useRecaptcha'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { getToken } = useRecaptcha()

const isProcessing = ref(false)
const error = ref<string | null>(null)
const provider = ref('')

onMounted(async () => {
  if (isProcessing.value) {
    return
  }

  isProcessing.value = true

  try {
    // Get OAuth parameters from URL
    const code = route.query.code as string
    const state = route.query.state as string
    const errorParam = route.query.error as string
    const providerParam = route.params.provider as string

    provider.value = providerParam

    // Handle OAuth error (user denied)
    if (errorParam) {
      error.value = 'OAuth authentication was cancelled or denied'
      setTimeout(() => {
        router.push(AuthRoutePaths.login)
      }, 2000)
      return
    }

    // Validate required parameters
    if (!providerParam || !code || !state) {
      error.value = 'Invalid OAuth parameters'
      setTimeout(() => {
        router.push(AuthRoutePaths.login)
      }, 2000)
      return
    }

    // Verify state parameter for CSRF protection
    const storedState = localStorage.getItem('oauth_state')
    if (!storedState || storedState !== state) {
      error.value = 'Invalid state parameter - possible CSRF attack'
      setTimeout(() => {
        router.push(AuthRoutePaths.login)
      }, 2000)
      return
    }

    // Clear stored state
    localStorage.removeItem('oauth_state')

    // Get reCAPTCHA token if enabled
    const recaptchaToken = await getToken('oauth_callback')

    // Call OAuth callback endpoint
    const response = await authService.oauthCallback(providerParam, {
      code,
      state,
      recaptchaToken,
    })

    // Handle response
    if ('requiresTwoFactor' in response) {
      // 2FA required - redirect to 2FA page
      toast.info('Two-factor authentication required')
      await router.push(AuthRoutePaths.twoFactorVerify)
      return
    }

    // Success - set auth data and redirect
    authStore.setToken(response.accessToken)
    authStore.setRefreshToken(response.refreshToken)
    authStore.setUser(response.user)
    toast.success('Successfully signed in with ' + providerParam)
    await router.push(AuthRoutePaths.dashboard)
  }
  catch (err: unknown) {
    console.error('OAuth callback error:', err)

    // Better error handling - extract message from API response
    let errorMessage = 'OAuth authentication failed'

    if (err && typeof err === 'object' && 'response' in err) {
      const axiosError = err as { response?: { data?: { detail?: string } } }
      if (axiosError.response?.data?.detail) {
        errorMessage = axiosError.response.data.detail
      }
    }
    else if (err instanceof Error) {
      errorMessage = err.message
    }

    error.value = errorMessage
    console.error('OAuth callback detailed error:', errorMessage)
    toast.error(errorMessage)

    setTimeout(() => {
      router.push(AuthRoutePaths.login)
    }, 3000)
  }
  finally {
    isProcessing.value = false
  }
})
</script>

<template>
  <div class="flex min-h-screen items-center justify-center px-4 py-12">
    <Card class="w-full max-w-md">
      <CardHeader>
        <CardTitle v-if="error" class="text-destructive">
          Authentication Failed
        </CardTitle>
        <CardTitle v-else class="flex items-center">
          <div class="mr-2 size-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          Signing you in...
        </CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription v-if="error">
          {{ error }}
        </CardDescription>
        <CardDescription v-else>
          Processing your {{ provider }} authentication. Please wait...
        </CardDescription>
      </CardContent>
    </Card>
  </div>
</template>
