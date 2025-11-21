<script setup lang="ts">
import { computed } from 'vue'
import type { TGearItemCategory } from '../types/gear.types'
import { getCategoryIcon } from '../utils/categoryIcons'

const props = withDefaults(defineProps<{
  category: TGearItemCategory
  size?: number
  class?: string
}>(), {
  size: 16,
})

const IconComponent = computed(() => getCategoryIcon(props.category))
</script>

<template>
  <component
    :is="IconComponent"
    :size="size"
    :class="props.class"
  />
</template>

