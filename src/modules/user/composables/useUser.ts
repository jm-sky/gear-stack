import { computed, ref } from 'vue'
import type { IUpdateUserDto, IUser } from '../types/user.types'
import { userService } from '../services/userService'
import { useUserStore } from '../store/useUserStore'

/**
 * Composable for user profile management
 * Uses hybrid service (API when authenticated, localStorage otherwise)
 * Automatically syncs with UserStore
 */
export function useUser() {
  const store = useUserStore()
  const isLoading = ref(false)

  // Use store as source of truth, but sync with service
  const profile = computed(() => store.getProfile)

  /**
   * Load user data from service (API or localStorage)
   * This will sync with store automatically
   */
  const loadProfile = async (): Promise<void> => {
    isLoading.value = true
    try {
      const user = await userService.getUser()
      store.setUser(user)
    } catch (error) {
      console.error('Failed to load user profile:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update user profile
   * Uses hybrid service (API when authenticated, localStorage otherwise)
   */
  const updateProfile = async (data: IUpdateUserDto): Promise<IUser> => {
    isLoading.value = true
    try {
      const updated = await userService.updateUser(data)
      store.setUser(updated)
      return updated
    } catch (error) {
      console.error('Failed to update user profile:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  return {
    profile,
    isLoading: computed(() => isLoading.value),
    loadProfile,
    updateProfile,
  }
}

