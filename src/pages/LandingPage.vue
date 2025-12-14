<script setup lang="ts">
import { BackpackIcon } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'
import LocalContainersStats from '@/components/layout/LocalContainersStats.vue'
import TotalsStats from '@/components/layout/TotalsStats.vue'
import WelcomeQuickActions from '@/components/layout/WelcomeQuickActions.vue'
import LandingLayout from '@/layouts/LandingLayout.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import { GearRouteName } from '@/modules/gear/routes'
import { hasLocalData } from '@/modules/gear/services/dataMigrationService'
import { useGearStore } from '@/modules/gear/store/useGearStore'
import { PublicRouteNames } from '@/router/publicRoutes'
import { config } from '@/shared/config/config'

const { t } = useI18n()
const router = useRouter()
const { isAuthenticated, user } = useAuth()
const gearStore = useGearStore()

// Check if user is not logged in but has containers in localStorage
const hasLocalContainers = computed(() => {
  if (isAuthenticated.value) return false
  return hasLocalData()
})

// Load containers from localStorage if not authenticated
onMounted(() => {
  if (!isAuthenticated.value) {
    gearStore.loadFromStorage()
  }
})

// If backend is disabled, redirect to home (offline mode)
if (!config.backend.enabled) {
  router.replace({ name: 'home' })
}
</script>

<template>
  <LandingLayout>
    <div class="max-w-2xl w-full space-y-8 text-center">
      <!-- Logo/Icon -->
      <div class="flex justify-center">
        <div class="rounded-full bg-primary/10 p-8">
          <BackpackIcon class="size-20 text-primary" />
        </div>
      </div>

      <!-- Heading -->
      <div class="space-y-4">
        <p v-if="isAuthenticated && user" class="text-2xl font-semibold text-muted-foreground">
          {{ t('landing.welcomeBack', { name: user.name }) }}
        </p>
        <h1 class="text-5xl font-bold tracking-tight">
          {{ t('landing.title', 'Gear Stack') }}
        </h1>
        <p class="text-xl text-muted-foreground max-w-lg mx-auto">
          {{ t('landing.subtitle', 'Organize and manage your survival gear and bug-out bag equipment') }}
        </p>
      </div>
    </div>

    <!-- Stats Widgets (wider container) -->
    <div class="max-w-4xl w-full px-4">
      <TotalsStats />
    </div>

    <div class="max-w-2xl w-full space-y-8 text-center">
      <LocalContainersStats v-if="hasLocalContainers" />

      <!-- Features -->
      <div v-else class="grid grid-cols-1 md:grid-cols-3 py-4 gap-6">
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">
            {{ t('landing.feature1.title', 'Organize') }}
          </h3>
          <p class="text-sm text-muted-foreground">
            {{ t('landing.feature1.description', 'Keep track of all your gear in organized containers') }}
          </p>
        </div>
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">
            {{ t('landing.feature2.title', 'Track') }}
          </h3>
          <p class="text-sm text-muted-foreground">
            {{ t('landing.feature2.description', 'Monitor weight, readiness, and expiration dates') }}
          </p>
        </div>
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">
            {{ t('landing.feature3.title', 'Prepare') }}
          </h3>
          <p class="text-sm text-muted-foreground">
            {{ t('landing.feature3.description', 'Be ready for any situation with a well-prepared gear stack') }}
          </p>
        </div>
      </div>

      <!-- CTA Buttons (shown when no local containers) -->
      <WelcomeQuickActions class="max-w-md mx-auto" />

      <!-- Info Links -->
      <div v-if="isAuthenticated" class="flex flex-wrap justify-center gap-4 text-sm">
        <RouterLink :to="{ name: GearRouteName.Containers }" class="text-muted-foreground hover:text-primary transition-colors">
          {{ t('gear.page.viewContainers', 'View Containers') }}
        </RouterLink>
        <RouterLink :to="{ name: PublicRouteNames.about }" class="text-muted-foreground hover:text-primary transition-colors">
          {{ t('common.pages.about', 'About') }}
        </RouterLink>
      </div>

      <!-- Footer text -->
      <p class="text-sm text-muted-foreground py-8">
        {{ t('landing.footer', 'Start organizing your gear today') }}
      </p>
    </div>
  </LandingLayout>
</template>

