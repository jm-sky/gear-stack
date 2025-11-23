<script setup lang="ts">
import { Package, User } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { apiClient } from '@/shared/services/apiClient'
import { useAuth } from '@/modules/auth/composables/useAuth'
import type { IGearContainer } from '../types/gear.types'
import ColorDot from '../components/ColorDot.vue'

const router = useRouter()
const { t } = useI18n()
const { isAuthenticated } = useAuth()

const containers = ref<IGearContainer[]>([])
const isLoading = ref(true)

onMounted(async () => {
  try {
    const response = await apiClient.get<IGearContainer[]>('/gear/public/containers')
    containers.value = response.data
  } catch (error) {
    console.error('Failed to load public containers:', error)
  } finally {
    isLoading.value = false
  }
})

const handleContainerClick = (containerId: string) => {
  router.push(`/gear/public/${containerId}`)
}

const handleAuthorClick = (e: MouseEvent, authorId?: string | null) => {
  e.stopPropagation()
  if (authorId && isAuthenticated.value) {
    router.push(`/users/${authorId}/public`)
  }
}
</script>

<template>
  <AuthenticatedLayout>
    <div class="space-y-6 w-full max-w-full">
      <!-- Header -->
      <div>
        <h1 class="text-3xl font-bold">
          {{ t('gear.publicContainers.title') }}
        </h1>
        <p class="text-muted-foreground mt-1">
          {{ t('gear.publicContainers.description') }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i" class="h-48 bg-muted rounded-lg animate-pulse" />
      </div>

      <!-- Containers Grid -->
      <div v-else-if="containers.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card
          v-for="container in containers"
          :key="container.id"
          class="gap-1 hover:shadow-lg hover:bg-current/5 hover:scale-102 hover:-translate-y-1 transition-all duration-300 cursor-pointer"
          @click="handleContainerClick(container.id)"
        >
          <CardHeader class="text-card-foreground">
            <div class="flex items-center gap-2">
              <ColorDot :color="container.color ?? undefined" />
              <Package class="size-5" />
              <CardTitle>{{ container.name }}</CardTitle>
            </div>
            <CardDescription v-if="container.description">
              {{ container.description }}
            </CardDescription>
          </CardHeader>

          <CardContent class="flex flex-col gap-3 px-6 pb-4 text-card-foreground">
            <div class="flex items-center gap-2 flex-wrap">
              <Badge variant="outline">
                {{ container.type }}
              </Badge>
              <Badge
                v-if="container.authorName"
                variant="secondary"
                :class="{ 'cursor-pointer hover:bg-secondary/80': container.authorId && isAuthenticated }"
                @click="handleAuthorClick($event, container.authorId)"
                v-tooltip.bottom="t('gear.publicContainers.by')"
                :aria-label="t('gear.publicContainers.by')"
              >
                <User class="size-3 mr-1" />
                <span v-if="!container.authorId || !isAuthenticated">{{ container.authorName }}</span>
              </Badge>
            </div>
            <div class="text-sm text-muted-foreground">
              {{ container.items.length }} {{ t('gear.container.itemsCount') }}
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Empty State -->
      <div v-else class="flex flex-col items-center justify-center py-12 text-center">
        <div class="rounded-full bg-muted p-6 mb-4">
          <Package class="size-12 text-muted-foreground" />
        </div>
        <h3 class="text-lg font-semibold mb-2">
          {{ t('gear.publicContainers.empty') }}
        </h3>
        <p class="text-muted-foreground max-w-md">
          {{ t('gear.publicContainers.emptyDescription') }}
        </p>
      </div>
    </div>
  </AuthenticatedLayout>
</template>
