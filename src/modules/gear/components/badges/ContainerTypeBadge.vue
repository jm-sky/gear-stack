<script setup lang="ts">
import { computed } from 'vue'
import { Badge } from '@/components/ui/badge'
import type { IGearContainer } from '../../types/gear.types'
import { useContainerTypeLabel } from '../../composables/useContainerTypeLabel'
import { COLOR_BORDER_CLASSES, COLOR_TEXT_CLASSES } from '../../utils/containerColors'
import ContainerIcon from '../ContainerIcon.vue'

const props = defineProps<{
  container: IGearContainer
}>()

const { typeLabel } = useContainerTypeLabel(computed(() => props.container.type))
</script>

<template>
  <Badge
    variant="outline"
    :class="[
      COLOR_TEXT_CLASSES[container.color ?? 'default'],
      COLOR_BORDER_CLASSES[container.color ?? 'default'],
    ]"
  >
    <ContainerIcon
      :color="container.color ?? undefined"
      :type="container.type ?? 'other'"
      :size="4"
      class="mr-0.5"
    />
    {{ typeLabel }}
  </Badge>
</template>
