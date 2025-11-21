<script setup lang="ts">
import { LogOut, User } from 'lucide-vue-next'
import { type Component, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import Avatar from '../ui/avatar/Avatar.vue'
import AvatarFallback from '../ui/avatar/AvatarFallback.vue'
import AvatarImage from '../ui/avatar/AvatarImage.vue'

export interface Link {
  to: string
  label: string
  icon?: Component
}

export interface UserNavProps {
  userName?: string
  userEmail?: string
  userAvatar?: string
  navLinks?: Link[]
}

const { t } = useI18n()
const router = useRouter()

const props = defineProps<UserNavProps>()

const emit = defineEmits<{
  logout: []
}>()

// Generate initials from name or email
const initials = computed(() => {
  if (props.userName) {
    return props.userName
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2)
  }
  if (props.userEmail) {
    return props.userEmail.substring(0, 2).toUpperCase()
  }
  return 'U'
})

const handleLogout = () => {
  emit('logout')
}

const navigateTo = (path: string) => {
  router.push(path)
}
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Avatar aria-label="User menu" class="cursor-pointer">
        <AvatarImage :src="userAvatar ?? ''" />
        <AvatarFallback class="bg-primary text-primary-foreground">
          {{ initials }}
        </AvatarFallback>
      </Avatar>
    </DropdownMenuTrigger>

    <DropdownMenuContent class="w-64" align="end">
      <!-- User info -->
      <DropdownMenuLabel>
        <div class="flex flex-col space-y-1">
          <p class="text-sm font-medium leading-none">
            {{ userName ?? 'N/A' }}
          </p>
          <p class="text-xs leading-none text-muted-foreground">
            {{ userEmail ?? '-' }}
          </p>
        </div>
      </DropdownMenuLabel>

      <DropdownMenuSeparator />

      <!-- Navigation Links (mobile only) -->
      <template v-if="navLinks && navLinks.length > 0">
        <div class="md:hidden">
          <DropdownMenuItem
            v-for="link in navLinks"
            :key="link.to"
            @click="navigateTo(link.to)"
          >
            <component :is="link.icon" v-if="link.icon" class="size-4 mr-2" />
            {{ link.label }}
          </DropdownMenuItem>
          <DropdownMenuSeparator />
        </div>
      </template>

      <!-- Profile/Settings slot -->
      <slot name="menu-items">
        <DropdownMenuItem @click="navigateTo('/profile')">
          <User class="size-4 mr-2" />
          {{ t('user.profile.title', 'Profile') }}
        </DropdownMenuItem>

        <DropdownMenuItem @click="navigateTo('/settings')">
          <User class="size-4 mr-2" />
          {{ t('settings.page.title', 'Settings') }}
        </DropdownMenuItem>
      </slot>

      <DropdownMenuSeparator />

      <!-- Logout -->
      <DropdownMenuItem @click="handleLogout">
        <LogOut class="size-4 mr-2" />
        {{ t('auth.logout', 'Logout') }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
