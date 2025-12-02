<script setup lang="ts">
import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'vue'

const props = defineProps<{
  class?: HTMLAttributes['class']
  ariaLabel?: string
  ariaLabelledby?: string
}>()
</script>

<template>
  <div data-slot="table-container" class="relative w-full overflow-x-auto overflow-y-visible">
    <table
      data-slot="table"
      :class="cn('w-full caption-bottom text-sm min-w-lg', props.class)"
      :aria-label
      :aria-labelledby
    >
      <slot />
    </table>
  </div>
</template>
