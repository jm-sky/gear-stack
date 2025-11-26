<script setup lang="ts">
import { BackpackIcon, LogIn, Plus, UserPlus } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import LocalContainersStats from '@/components/layout/LocalContainersStats.vue'
import TotalsStats from '@/components/layout/TotalsStats.vue'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import LandingLayout from '@/layouts/LandingLayout.vue'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import GenerateExampleGearButton from '@/modules/gear/components/GenerateExampleGearButton.vue'
import { GearRoutePath } from '@/modules/gear/routes'
import { hasLocalData } from '@/modules/gear/services/dataMigrationService'
import { useGearStore } from '@/modules/gear/store/useGearStore'
import { config } from '@/shared/config/config'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const gearStore = useGearStore()

// Check if user is not logged in but has containers in localStorage
const hasLocalContainers = computed(() => {
  if (authStore.isAuthenticated) return false
  return hasLocalData()
})

// Load containers from localStorage if not authenticated
onMounted(() => {
  if (!authStore.isAuthenticated) {
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
      <div v-if="!hasLocalContainers" class="flex flex-col gap-4 md:gap-8 justify-center items-center">
        <div class="flex flex-col md:flex-row gap-4">
          <ButtonLink
            size="lg"
            class="w-full sm:w-auto"
            :to="GearRoutePath.ContainerNew"
          >
            <Plus class="size-5" />
            {{ t('gear.container.create.title', 'Add Container') }}
          </ButtonLink>
          <GenerateExampleGearButton class="flex-1" />
        </div>
        <div class="flex flex-col md:flex-row gap-4">
          <ButtonLink
            size="lg"
            variant="outline"
            class="w-full sm:w-auto"
            :to="AuthRoutePaths.login"
          >
            <LogIn class="size-5" />
            {{ t('landing.login', 'Log In') }}
          </ButtonLink>
          <ButtonLink
            size="lg"
            variant="outline"
            class="w-full sm:w-auto"
            :to="AuthRoutePaths.register"
          >
            <UserPlus class="size-5" />
            {{ t('landing.register', 'Sign Up') }}
          </ButtonLink>
        </div>
      </div>

      <!-- Footer text -->
      <p class="text-sm text-muted-foreground py-8">
        {{ t('landing.footer', 'Start organizing your gear today') }}
      </p>
    </div>
  </LandingLayout>
</template>

