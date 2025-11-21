<script setup lang="ts">
import { BackpackIcon, FileInput, Plus } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useGear } from '@/modules/gear/composables/useGear'
import { gearContainerService } from '@/modules/gear/services/gearContainerService'
import { generateSampleSet } from '@/modules/gear/services/sampleSetGenerator'
import { READINESS_EXCELLENT_THRESHOLD } from '@/modules/gear/utils/constants'
import { config } from '@/shared/config/config'

const router = useRouter()
const { t } = useI18n()
const { containers } = useGear()

// Load containers from API on mount (when backend is enabled)
onMounted(async () => {
  if (config.backend.enabled) {
    try {
      await gearContainerService().getContainers()
    } catch (error) {
      console.error('Failed to load containers from API:', error)
      // Fallback to localStorage is handled by store initialization
    }
  }
})

const handleGoToGear = () => {
  router.push('/gear')
}

const handleCreateContainer = () => {
  router.push('/gear/new')
}

const handleImport = () => {
  router.push('/gear?import=true')
}

const handleGenerateSampleSet = () => {
  try {
    generateSampleSet(t)
    toast.success(t('gear.sampleSet.success'))
  } catch (error) {
    console.error('Error generating sample set:', error)
    toast.error(t('common.error'))
  }
}

const readyContainersCount = computed(() => {
  return containers.value.filter(c => {
    const ownedItems = c.items.filter(i => i.status === 'owned').length
    const totalItems = c.items.length
    return ownedItems / totalItems * 100 >= READINESS_EXCELLENT_THRESHOLD
  }).length
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-8">
      <!-- Header -->
      <div class="text-center space-y-4">
        <div class="flex justify-center">
          <div class="rounded-full bg-primary/10 p-6">
            <BackpackIcon class="size-16 text-primary" />
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
            {{ readyContainersCount }}
          </div>
          <div class="text-muted-foreground">
            {{ t('gear.page.readyContainers', 'Ready Containers') }}
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex flex-col items-center gap-4">
        <div v-if="containers.length > 0" class="flex flex-col sm:flex-row gap-4">
          <Button size="lg" @click="handleGoToGear">
            <BackpackIcon class="size-5" />
            {{ t('gear.page.viewContainers', 'View Containers') }}
          </Button>
          <Button size="lg" variant="outline" @click="handleCreateContainer">
            <Plus class="size-5" />
            {{ t('gear.container.create.title', 'Create Container') }}
          </Button>
        </div>

        <!-- Empty State -->
        <div v-if="containers.length === 0" class="text-center py-12 max-w-md">
          <p class="text-muted-foreground mb-6">
            {{ t('gear.page.emptyDescription', 'Get started by creating your first gear container.') }}
          </p>
          <div class="flex flex-col gap-4 items-center justify-center">
            <Button size="lg" @click="handleCreateContainer">
              <Plus class="size-5" />
              {{ t('gear.container.create.title', 'Create Container') }}
            </Button>
            <div class="flex items-center gap-2 text-muted-foreground">
              <span>{{ t('common.or', 'or') }}</span>
            </div>
            <div class="flex flex-col md:flex-row gap-2 items-center justify-center">
              <Button size="lg" variant="outline" @click="handleImport">
                <FileInput class="size-5" />
                {{ t('gear.import.fromMarkdown', 'Import from Markdown') }}
              </Button>
              <Button size="lg" variant="outline" @click="handleGenerateSampleSet">
                {{ t('gear.sampleSet.generateButton', 'Generate Sample Set') }}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
