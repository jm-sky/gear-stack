import { computed } from 'vue'
import type { IUpdateUserDto } from '../types/user.types'
import { useUserStore } from '../store/useUserStore'

export function useUser() {
  const store = useUserStore()

  const profile = computed(() => store.getProfile)

  const updateProfile = (data: IUpdateUserDto): void => {
    store.updateUser(data)
  }

  return {
    profile,
    updateProfile,
  }
}

