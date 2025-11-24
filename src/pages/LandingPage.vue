<script setup lang="ts">
import { BackpackIcon, LogIn, Plus, UserPlus } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import AppFooter from '@/components/layout/AppFooter.vue'
import LandingPageContainerCard from '@/components/layout/LandingPageContainerCard.vue'
import TotalsStats from '@/components/layout/TotalsStats.vue'
import { Button } from '@/components/ui/button'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { AuthRoutePaths } from '@/modules/auth/config/routes'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { GearRouteName, GearRoutePath } from '@/modules/gear/routes'
import { hasLocalData } from '@/modules/gear/services/dataMigrationService'
import { generateSampleSet } from '@/modules/gear/services/sampleSetGenerator'
import { useGearStore } from '@/modules/gear/store/useGearStore'
import { READINESS_EXCELLENT_THRESHOLD } from '@/modules/gear/utils/constants'
import DarkModeToggle from '@/shared/components/DarkModeToggle.vue'
import { config } from '@/shared/config/config'
import LocaleToggle from '@/shared/i18n/components/LocaleToggle.vue'

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

// Get containers for stats
const localContainers = computed(() => {
  if (!hasLocalContainers.value) return []
  return gearStore.getAllContainers
})

// Calculate stats similar to HomePage
const containersCount = computed(() => localContainers.value.length)

const itemsCount = computed(() => {
  return localContainers.value.reduce((sum, c) => sum + c.items.length, 0)
})

const readyContainersCount = computed(() => {
  return localContainers.value.filter(c => {
    const ownedItems = c.items.filter(i => i.status === 'owned').length
    const totalItems = c.items.length
    if (totalItems === 0) return false
    return (ownedItems / totalItems) * 100 >= READINESS_EXCELLENT_THRESHOLD
  }).length
})

const handleGenerateSampleSet = () => {
  try {
    generateSampleSet(t)
    toast.success(t('gear.sampleSet.success'))
    router.push({ name: GearRouteName.Containers })
  } catch (error) {
    console.error('Error generating sample set:', error)
    toast.error(t('common.error'))
  }
}

// If backend is disabled, redirect to home (offline mode)
if (!config.backend.enabled) {
  router.replace({ name: 'home' })
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-linear-to-br from-background to-muted relative">
    <!-- Fixed controls in top right -->
    <nav class="fixed top-2 right-2 flex gap-2 rounded-lg p-2 bg-card/50 backdrop-blur-sm z-10">
      <LocaleToggle />
      <DarkModeToggle />
    </nav>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col items-center justify-center p-4">
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

        <!-- Local Containers Summary (shown when not logged in but has containers) -->
        <div v-if="hasLocalContainers" class="space-y-6 py-8">
          <div class="bg-card/50 backdrop-blur-sm rounded-lg border p-6 space-y-4">
            <div class="text-center space-y-2">
              <h2 class="text-2xl font-semibold">
                {{ t('landing.localData.title', 'Masz kontenery w przeglądarce') }}
              </h2>
              <p class="text-muted-foreground">
                {{ t('landing.localData.description', 'Zaloguj się lub zarejestruj, aby zsynchronizować swoje dane') }}
              </p>
            </div>

            <!-- Container Stats -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <LandingPageContainerCard
                :to="GearRoutePath.Containers"
                :label="t('gear.page.containers', 'Containers')"
                :containers-count="containersCount"
              />
              <LandingPageContainerCard
                :to="GearRoutePath.AllItems"
                :label="t('gear.page.items', 'Items')"
                :containers-count="itemsCount"
              />
              <LandingPageContainerCard
                :to="GearRoutePath.Containers"
                :label="t('gear.page.readyContainers', 'Ready Containers')"
                :containers-count="readyContainersCount"
              />
            </div>

            <!-- Login/Register CTA -->
            <div class="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
              <ButtonLink size="lg" class="w-full sm:w-auto" :to="AuthRoutePaths.login">
                <LogIn class="size-5" />
                {{ t('landing.login', 'Log In') }}
              </ButtonLink>
            </div>

            <div class="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
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
        </div>

        <!-- Features -->
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6 py-8">
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
        <div v-if="!hasLocalContainers" class="flex flex-col gap-4 md:gap-8 justify-center items-center pt-4">
          <div class="flex flex-col md:flex-row gap-4">
            <ButtonLink
              size="lg"
              class="w-full sm:w-auto"
              :to="GearRoutePath.ContainerNew"
            >
              <Plus class="size-5" />
              {{ t('gear.container.create.title', 'Add Container') }}
            </ButtonLink>
            <Button
              size="lg"
              variant="outline"
              class="flex-1"
              @click="handleGenerateSampleSet"
            >
              {{ t('gear.sampleSet.generateButton', 'Generate Sample Set') }}
            </Button>
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
        <p class="text-sm text-muted-foreground pt-8">
          {{ t('landing.footer', 'Start organizing your gear today') }}
        </p>
      </div>
    </main>

    <!-- Footer -->
    <AppFooter />
  </div>
</template>

