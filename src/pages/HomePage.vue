<script setup lang="ts">
import { BackpackIcon, Plus } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useGear } from '@/modules/gear/composables/useGear'

const router = useRouter()
const { t } = useI18n()
const { containers } = useGear()

const handleGoToGear = () => {
  router.push('/gear')
}

const handleCreateContainer = () => {
  router.push('/gear/new')
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-8">
      <!-- Header -->
      <div class="text-center space-y-4">
        <div class="flex justify-center">
          <div class="rounded-full bg-primary/10 p-6">
            <BackpackIcon class="h-16 w-16 text-primary" />
          </div>
        </div>
        <h1 class="text-4xl font-bold">
          {{ t('gear.page.title', 'Gear Stack') }}
        </h1>
        <p class="text-muted-foreground text-lg max-w-2xl mx-auto">
          {{ t('gear.page.subtitle', 'Organize and manage your gear collections') }}
        </p>
      </div>

      <!-- Quick Stats -->
      <div v-if="containers.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-card rounded-lg border p-6 text-center">
          <div class="text-3xl font-bold text-primary mb-2">
            {{ containers.length }}
          </div>
          <div class="text-muted-foreground">
            {{ t('gear.page.containers', 'Containers') }}
          </div>
        </div>
        <div class="bg-card rounded-lg border p-6 text-center">
          <div class="text-3xl font-bold text-primary mb-2">
            {{ containers.reduce((sum, c) => sum + c.items.length, 0) }}
          </div>
          <div class="text-muted-foreground">
            {{ t('gear.page.items', 'Items') }}
          </div>
        </div>
        <div class="bg-card rounded-lg border p-6 text-center">
          <div class="text-3xl font-bold text-primary mb-2">
            {{ containers.filter(c => c.items.some(i => i.status === 'owned')).length }}
          </div>
          <div class="text-muted-foreground">
            {{ t('gear.page.readyContainers', 'Ready Containers') }}
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex flex-col items-center gap-4">
        <div class="flex flex-col sm:flex-row gap-4">
          <Button size="lg" @click="handleGoToGear">
            <BackpackIcon class="size-5" />
            {{ t('gear.page.viewContainers', 'View Containers') }}
          </Button>
          <Button size="lg" variant="outline" @click="handleCreateContainer">
            <Plus class="size-5" />
            {{ t('gear.container.create', 'Create Container') }}
          </Button>
        </div>

        <!-- Empty State -->
        <div v-if="containers.length === 0" class="text-center py-12 max-w-md">
          <p class="text-muted-foreground mb-6">
            {{ t('gear.page.emptyDescription', 'Get started by creating your first gear container.') }}
          </p>
          <Button size="lg" @click="handleCreateContainer">
            <Plus class="size-5" />
            {{ t('gear.container.create', 'Create Container') }}
          </Button>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
