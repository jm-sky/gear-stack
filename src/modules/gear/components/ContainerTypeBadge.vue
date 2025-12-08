<script setup lang="ts">
import { computed } from 'vue'
import { Badge } from '@/components/ui/badge'
import type { IGearContainer } from '../types/gear.types'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { COLOR_BORDER_CLASSES } from '../utils/containerColors'
import { getContainerIcon } from '../utils/containerIcons'
import ColorDot from './ColorDot.vue'

const props = defineProps<{
  container: IGearContainer
}>()

const { typeLabel } = useContainerTypeLabel(computed(() => props.container.type))
const ContainerIcon = computed(() => getContainerIcon(props.container.type))
</script>

<template>
  <Badge variant="outline" :class="COLOR_BORDER_CLASSES[container.color ?? 'default']">
    <ColorDot
      :color="container.color ?? undefined"
      :icon="ContainerIcon"
      :size="4"
      class="mr-0.5"
    />
    {{ typeLabel }}
  </Badge>
</template>
