<script setup lang="ts">
import { LogIn, LogOut, Shield, User, UserPlus } from 'lucide-vue-next'
import { type Component, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import { useAdmin } from '@/modules/admin/composables/useAdmin'
import { AdminRoutePaths } from '@/modules/admin/routes'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { SettingsRoutePaths } from '@/modules/settings/routes'
import { UserRoutePaths } from '@/modules/user/routes'
import Avatar from '../ui/avatar/Avatar.vue'
import AvatarFallback from '../ui/avatar/AvatarFallback.vue'
import AvatarImage from '../ui/avatar/AvatarImage.vue'
import DropdownMenuItemLink from '../ui/dropdown-menu/DropdownMenuItemLink.vue'

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
const { isAuthenticated } = useAuth()
const { isAdmin } = useAdmin()

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
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Avatar
        aria-label="User menu"
        :class="cn('cursor-pointer hover:brightness-95 transition-all duration-300', !isAuthenticated && 'ring-2 ring-muted-foreground/30', isAdmin && 'ring-2 ring-primary ring-offset-2 ring-offset-background')"
      >
        <AvatarImage :src="userAvatar ?? ''" />
        <AvatarFallback :class="isAuthenticated ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'">
          <User v-if="!isAuthenticated" class="size-4" />
          <template v-else>
            {{ initials }}
          </template>
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
          <DropdownMenuItemLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
          >
            <component :is="link.icon" v-if="link.icon" class="size-4 mr-2" />
            {{ link.label }}
          </DropdownMenuItemLink>
          <DropdownMenuSeparator />
        </div>
      </template>

      <!-- Profile/Settings slot -->
      <slot name="menu-items">
        <DropdownMenuItemLink :to="UserRoutePaths.profile">
          <User class="size-4 mr-2" />
          {{ t('user.profile.title', 'Profile') }}
        </DropdownMenuItemLink>

        <DropdownMenuItemLink :to="SettingsRoutePaths.settings">
          <User class="size-4 mr-2" />
          {{ t('settings.page.title', 'Settings') }}
        </DropdownMenuItemLink>

        <DropdownMenuItemLink v-if="isAdmin" :to="AdminRoutePaths.dashboard">
          <Shield class="size-4 mr-2" />
          {{ t('admin.dashboard.title', 'Admin Dashboard') }}
        </DropdownMenuItemLink>
      </slot>

      <DropdownMenuSeparator />

      <!-- Logout -->
      <DropdownMenuItem v-if="isAuthenticated" @click="handleLogout">
        <LogOut class="size-4 mr-2" />
        {{ t('auth.logout', 'Logout') }}
      </DropdownMenuItem>
      <template v-else>
        <DropdownMenuItemLink :to="AuthRoutePaths.login">
          <LogIn class="size-4 mr-2" />
          {{ t('auth.login', 'Login') }}
        </DropdownMenuItemLink>
        <DropdownMenuItemLink :to="AuthRoutePaths.register">
          <UserPlus class="size-4 mr-2" />
          {{ t('auth.register', 'Register') }}
        </DropdownMenuItemLink>
      </template>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
