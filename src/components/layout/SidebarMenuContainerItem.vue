<script setup lang="ts">
import { BackpackIcon } from 'lucide-vue-next'
import { RouterLink, useRoute } from 'vue-router'
import {
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'
import { GearRoutePath } from '@/modules/gear/routes'
import { COLOR_TEXT_CLASSES } from '@/modules/gear/utils/containerColors'
import type { IGearContainer } from '@/modules/gear/types/gear.types'

defineProps<{
  container: IGearContainer
}>()

const route = useRoute()

// Sprawdzanie czy kontener jest aktywny
const isActive = (containerId: string): boolean => {
  return route.params.id === containerId || route.params.containerId === containerId
}
</script>

<template>
  <SidebarMenuItem>
    <SidebarMenuButton :is-active="isActive(container.id)" as-child>
      <RouterLink :to="GearRoutePath.ContainerDetailById(container.id)">
        <BackpackIcon :class="COLOR_TEXT_CLASSES[container.color ?? 'default']" />
        <span>{{ container.name }}</span>
      </RouterLink>
    </SidebarMenuButton>
  </SidebarMenuItem>
</template>

