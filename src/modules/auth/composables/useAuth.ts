// modules/auth/composables/useAuth.ts
import { computed, ref } from 'vue'
import { authService } from '@/modules/auth/services/authService'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { useBackend } from '@/shared/composables/useBackend'
import type { IAuthService } from '@/modules/auth/types/auth.type'
import type {
  ChangePasswordData,
  ForgotPasswordData,
  LoginCredentials,
  LoginResponse,
  RegisterCredentials,
  ResetPasswordData,
  User,
} from '@/modules/auth/types/user.type'

/**
 * Simplified auth composable without TanStack Query
 * Uses Pinia store and authService directly
 */
export function useAuth(service?: IAuthService) {
  const authStore = useAuthStore()
  const { isBackendEnabled } = useBackend()
  const auth = service ?? authService

  // Loading states
  const isLoggingIn = ref(false)
  const isRegistering = ref(false)
  const isLoggingOut = ref(false)
  const isLoading = ref(false)
  const isVerifyingEmail = ref(false)
  const isResendingVerification = ref(false)

  // Computed values
  const user = computed<User | null>(() => authStore.user)
  const isAuthenticated = computed<boolean>(() => authStore.isAuthenticated)
  const isEmailVerified = computed<boolean>(() => user.value?.isEmailVerified ?? false)

  /**
   * Login user
   */
  async function login(credentials: LoginCredentials): Promise<LoginResponse> {
    if (!isBackendEnabled.value) {
      throw new Error('Backend is not enabled. Set VITE_ENABLE_BACKEND=true')
    }

    isLoggingIn.value = true
    try {
      const response = await auth.login(credentials)

      // Check if 2FA is required
      if ('requiresTwoFactor' in response && response.requiresTwoFactor) {
        // Store 2FA token and methods instead of access token
        authStore.setTwoFactorToken(
          response.twoFactorToken,
          response.methods,
          response.preferredMethod,
        )
        // Don't set access token - user needs to complete 2FA first
      } else if ('accessToken' in response) {
        // Normal login response - set access token and refresh token
        authStore.setToken(response.accessToken)
        authStore.setRefreshToken(response.refreshToken)
        // Set user from login response
        if (response.user) {
          authStore.setUser(response.user)
        }
      }

      return response
    } finally {
      isLoggingIn.value = false
    }
  }

  /**
   * Register user
   */
  async function register(credentials: RegisterCredentials) {
    if (!isBackendEnabled.value) {
      throw new Error('Backend is not enabled. Set VITE_ENABLE_BACKEND=true')
    }

    isRegistering.value = true
    try {
      return await auth.register(credentials)
    } finally {
      isRegistering.value = false
    }
  }

  /**
   * Logout user
   */
  async function logout() {
    if (!isBackendEnabled.value) {
      authStore.logout()
      return
    }

    isLoggingOut.value = true
    try {
      await auth.logout()
    } catch (error) {
      console.error('Logout error:', error)
      // Even if logout fails on server, clear local state
    } finally {
      authStore.logout()
      isLoggingOut.value = false
    }
  }

  /**
   * Fetch current user
   */
  async function fetchUser() {
    if (!isBackendEnabled.value) {
      return null
    }

    if (!authStore.token) {
      return null
    }

    isLoading.value = true
    try {
      const user = await auth.getCurrentUser()
      authStore.setUser(user)
      return user
    } catch (error) {
      console.error('Failed to fetch user:', error)
      // If fetch fails, clear auth state
      authStore.logout()
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Forgot password
   */
  async function forgotPassword(data: ForgotPasswordData) {
    if (!isBackendEnabled.value) {
      throw new Error('Backend is not enabled. Set VITE_ENABLE_BACKEND=true')
    }
    return await auth.forgotPassword(data)
  }

  /**
   * Reset password
   */
  async function resetPassword(data: ResetPasswordData) {
    if (!isBackendEnabled.value) {
      throw new Error('Backend is not enabled. Set VITE_ENABLE_BACKEND=true')
    }
    return await auth.resetPassword(data)
  }

  /**
   * Change password
   */
  async function changePassword(data: ChangePasswordData) {
    if (!isBackendEnabled.value) {
      throw new Error('Backend is not enabled. Set VITE_ENABLE_BACKEND=true')
    }
    return await auth.changePassword(data)
  }

  /**
   * Verify email
   */
  async function verifyEmail(token: string) {
    if (!isBackendEnabled.value) {
      throw new Error('Backend is not enabled. Set VITE_ENABLE_BACKEND=true')
    }
    isVerifyingEmail.value = true
    try {
      return await auth.verifyEmail(token)
    } finally {
      isVerifyingEmail.value = false
    }
  }

  /**
   * Resend verification email
   */
  async function resendVerification(email: string) {
    if (!isBackendEnabled.value) {
      throw new Error('Backend is not enabled. Set VITE_ENABLE_BACKEND=true')
    }
    isResendingVerification.value = true
    try {
      return await auth.resendVerification(email)
    } finally {
      isResendingVerification.value = false
    }
  }

  return {
    // Data
    user,
    isAuthenticated,
    isEmailVerified,
    isLoading: computed(() => isLoading.value),

    // Actions
    login,
    register,
    logout,
    fetchUser,
    forgotPassword,
    resetPassword,
    changePassword,
    verifyEmail,
    resendVerification,

    // Loading states (computed for template usage)
    isLoggingIn: computed(() => isLoggingIn.value),
    isRegistering: computed(() => isRegistering.value),
    isLoggingOut: computed(() => isLoggingOut.value),
    isVerifyingEmail: computed(() => isVerifyingEmail.value),
    isResendingVerification: computed(() => isResendingVerification.value),
  }
}

