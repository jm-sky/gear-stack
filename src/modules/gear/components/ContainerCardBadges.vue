<script setup lang="ts">
import { Box } from 'lucide-vue-next'
import { computed } from 'vue'
import { Badge } from '@/components/ui/badge'
import ButtonLink from '@/components/ui/button-link/ButtonLink.vue'
import { useAuth } from '@/modules/auth/composables/useAuth'
import type { IGearContainer } from '../types/gear.types'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { GearRoutePath } from '../routes'
import { useGearStore } from '../store/useGearStore'
import PublicContainerAuthorBadge from './PublicContainerAuthorBadge.vue'

const props = defineProps<{
  container: IGearContainer
  withAuthor?: boolean
}>()

const store = useGearStore()
const { isAuthenticated } = useAuth()
const { typeLabel } = useContainerTypeLabel(computed(() => props.container.type))

// Find all containers that contain this container as an item
const parentContainers = computed<IGearContainer[]>(() => {
  const parents: IGearContainer[] = []
  const containerId = props.container.id

  // Add direct parent if exists
  if (props.container.parentContainerId) {
    const directParent = store.getContainerById(props.container.parentContainerId)
    if (directParent) {
      parents.push(directParent)
    }
  }

  // Find all containers that have this container as an item
  for (const container of store.getAllContainers) {
    if (container.id === containerId) continue // Skip self
    if (container.items.some(item => item.containerId === containerId)) {
      // Avoid duplicates
      if (!parents.some(p => p.id === container.id)) {
        parents.push(container)
      }
    }
  }

  return parents
})

// Get first parent container
const firstParentContainer = computed<IGearContainer | undefined>(() => {
  return parentContainers.value[0]
})

// Get count of additional parents (beyond the first one)
const additionalParentsCount = computed<number>(() => {
  return Math.max(0, parentContainers.value.length - 1)
})
</script>

<template>
  <div class="flex items-center justify-between gap-2 flex-wrap">
    <div class="flex items-center gap-2">
      <Badge class="h-5" variant="outline">
        {{ typeLabel }}
      </Badge>
      <template v-if="withAuthor">
        <PublicContainerAuthorBadge
          v-if="container.authorName"
          :author-name="container.authorName"
          :author-id="container.authorId"
          :as-link="isAuthenticated"
        />
      </template>
    </div>
    <div v-if="firstParentContainer" class="flex items-center gap-1">
      <ButtonLink
        :to="GearRoutePath.ContainerDetailById(firstParentContainer.id)"
        variant="outline"
        size="sm"
        class="h-5 px-2! text-xs text-muted-foreground"
        @click.stop
      >
        <Box class="size-3" />
        {{ firstParentContainer.name }}
      </ButtonLink>
      <Badge
        v-if="additionalParentsCount > 0"
        variant="secondary"
        class="h-5 text-xs px-1.5"
      >
        +{{ additionalParentsCount }}
      </Badge>
    </div>
  </div>
</template>

