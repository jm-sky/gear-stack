<script setup lang="ts">
import { BackpackIcon } from 'lucide-vue-next'
import { type Component, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import UserNav from '@/components/layout/UserNav.vue'
import HoverLink from '@/components/ui/hover-link/HoverLink.vue'
import LogoText from '@/components/ui/LogoText.vue'
import { GearRoutePath } from '@/modules/gear/routes'
import { useUser } from '@/modules/user/composables/useUser'
import DarkModeToggle from '@/shared/components/DarkModeToggle.vue'
import LocaleToggle from '@/shared/i18n/components/LocaleToggle.vue'

const { t } = useI18n()
const { profile } = useUser()

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
  }
])

const handleLogout = () => {
  // Handle logout if needed (for future use)
}
</script>

<template>
  <div class="min-h-screen bg-muted bg-radial from-card to-slate-300 dark:to-slate-800">
    <!-- Top Bar -->
    <header class="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div class="mx-auto flex h-14 max-w-screen-2xl items-center px-4">
        <div class="mr-4 flex items-center gap-2 md:mr-6">
          <RouterLink to="/" class="flex items-center gap-2 hover:brightness-80 transition-all duration-300">
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
              :user-name="profile?.name ?? 'User'"
              :user-email="profile?.email ?? 'user@example.com'"
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
    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <div class="rounded-xl bg-card p-6 shadow-lg">
        <slot />
      </div>
    </main>
  </div>
</template>
