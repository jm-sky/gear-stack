<script setup lang="ts">
import type { TContainerColor } from '../types/gear.types'
import { COLOR_DOT_CLASSES } from '../utils/containerColors'

defineProps<{
  color?: TContainerColor
}>()
</script>

<template>
  <div
    :class="[
      'size-3 rounded-full shrink-0',
      COLOR_DOT_CLASSES[color ?? 'default']
    ]"
  />
</template>
