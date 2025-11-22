<script setup lang="ts">
import { BackpackIcon, Package, ShoppingCart } from 'lucide-vue-next'
import { type Component, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AppFooter from '@/components/layout/AppFooter.vue'
import UserNav from '@/components/layout/UserNav.vue'
import HoverLink from '@/components/ui/hover-link/HoverLink.vue'
import LogoText from '@/components/ui/LogoText.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { AuthRouteNames, AuthRoutePaths } from '@/modules/auth/config/routes'
import { GearRoutePath } from '@/modules/gear/routes'
import { useUser } from '@/modules/user/composables/useUser'
import DarkModeToggle from '@/shared/components/DarkModeToggle.vue'
import LocaleToggle from '@/shared/i18n/components/LocaleToggle.vue'

const { t } = useI18n()
const router = useRouter()
const { profile } = useUser()
const { logout, user: authUser } = useAuth()

// Use auth user if backend is enabled, otherwise use profile from localStorage
const user = computed(() => authUser.value || profile.value)

interface Link {
  to: string
  label: string
  icon?: Component
}

// Navigation links - can be customized via props in the future
const navLinks = computed<Link[]>(() => [
  {
    to: GearRoutePath.Containers,
    label: t('gear.page.title', 'Gear'),
    icon: BackpackIcon,
  },
  {
    to: GearRoutePath.AllItems,
    label: t('gear.allItems.navTitle', 'All Items'),
    icon: Package,
  },
  {
    to: GearRoutePath.ShoppingPlanning,
    label: t('gear.shopping.navTitle', 'Shopping'),
    icon: ShoppingCart,
  },
])

const handleLogout = async () => {
  try {
    await logout()
    toast.success(t('auth.logout_success', 'Logged out successfully'))
    await router.push({ name: AuthRouteNames.login })
  } catch (error) {
    console.error('Logout error:', error)
    toast.error(t('auth.logout_error', 'Failed to logout'))
  }
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-muted bg-radial from-card to-slate-300 dark:to-slate-800 w-full max-w-full overflow-x-hidden">
    <!-- Top Bar -->
    <header class="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div class="mx-auto flex h-14 max-w-screen-2xl items-center px-4">
        <div class="mr-4 flex items-center gap-2 md:mr-6">
          <RouterLink :to="AuthRoutePaths.dashboard" class="flex items-center gap-2 hover:brightness-80 transition-all duration-300">
            <LogoText />
          </RouterLink>
          <nav v-if="navLinks.length > 0" class="hidden md:flex items-center gap-6 text-sm ml-6">
            <template v-for="link in navLinks" :key="link.to">
              <HoverLink :to="link.to">
                {{ link.label }}
              </HoverLink>
            </template>
          </nav>
        </div>

        <div class="flex flex-1 items-center justify-end space-x-2">
          <nav class="flex items-center space-x-2">
            <LocaleToggle />
            <DarkModeToggle />
            <UserNav
              :user-name="user?.name ?? t('user.guest')"
              :user-email="user?.email"
              :user-avatar="user?.avatar"
              :nav-links="navLinks"
              @logout="handleLogout"
            >
              <template #menu-items>
                <!-- Add menu items here if needed -->
              </template>
            </UserNav>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="w-full max-w-7xl mx-auto flex-1 py-6 px-2 sm:px-6 lg:px-8">
      <div class="rounded-xl bg-card p-4 sm:p-6 shadow-lg w-full max-w-full overflow-hidden">
        <slot />
      </div>
    </main>

    <!-- Footer -->
    <AppFooter />
  </div>
</template>
