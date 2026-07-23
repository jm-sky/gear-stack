<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { IGearItemV2, TContainerColor } from '../../types/gear.types.v2'
import { GearRoutePath } from '../../routes'
import { useGearStoreV2 } from '../../store/useGearStoreV2'
import { calculateReadinessPercentageSyncV2 } from '../../utils/containerCalculationsV2'
import { COLOR_BORDER_CLASSES } from '../../utils/containerColors'
import { getContainerIcon } from '../../utils/containerIcons'
import ColorDot from '../ColorDot.vue'
import ContainerReadinessProgressBar from '../ContainerReadinessProgressBar.vue'

const { container } = defineProps<{
  container: IGearItemV2
}>()

const store = useGearStoreV2()

const readinessPercentage = computed<number>(() =>
  calculateReadinessPercentageSyncV2(container.id, store.getItemById, store.getChildrenOfItem)
)
const colorBorderClass = computed<string>(() =>
  COLOR_BORDER_CLASSES[(container.color as TContainerColor) ?? 'default']
)
const ContainerIcon = computed(() => getContainerIcon(container.containerType))
const detailPath = computed<string>(() => GearRoutePath.ContainerDetailById(container.id))

function handleDragStart(event: DragEvent): void {
  event.dataTransfer?.setData('text/plain', container.id)
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
  }
}
</script>

<template>
  <RouterLink
    :to="detailPath"
    class="block group"
    draggable="true"
    @dragstart="handleDragStart"
  >
    <div
      class="border-l-4 border rounded-lg bg-card p-3 transition-all duration-200 group-hover:shadow-md group-hover:bg-accent/30 cursor-grab active:cursor-grabbing"
      :class="colorBorderClass"
    >
      <div class="flex items-center gap-2 mb-2">
        <ColorDot :color="(container.color as TContainerColor)" :icon="ContainerIcon" :size="4" />
        <span class="font-medium text-sm truncate flex-1">{{ container.name }}</span>
        <span class="text-xs text-muted-foreground shrink-0">{{ readinessPercentage }}%</span>
      </div>
      <ContainerReadinessProgressBar :readiness-percentage="readinessPercentage" />
    </div>
  </RouterLink>
</template>
