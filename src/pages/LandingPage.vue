<script setup lang="ts">
import { BackpackIcon, LogIn, UserPlus } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import AppFooter from '@/components/layout/AppFooter.vue'
import { Button } from '@/components/ui/button'
import { AuthRouteNames } from '@/modules/auth/config/routes'
import DarkModeToggle from '@/shared/components/DarkModeToggle.vue'
import { config } from '@/shared/config/config'
import LocaleToggle from '@/shared/i18n/components/LocaleToggle.vue'

const router = useRouter()
const { t } = useI18n()

const handleLogin = () => {
  router.push({ name: AuthRouteNames.login })
}

const handleRegister = () => {
  router.push({ name: AuthRouteNames.register })
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

        <!-- Features -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 py-8">
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

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
          <Button size="lg" class="w-full sm:w-auto" @click="handleLogin">
            <LogIn class="size-5 mr-2" />
            {{ t('landing.login', 'Log In') }}
          </Button>
          <Button
            size="lg"
            variant="outline"
            class="w-full sm:w-auto"
            @click="handleRegister"
          >
            <UserPlus class="size-5 mr-2" />
            {{ t('landing.register', 'Sign Up') }}
          </Button>
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

