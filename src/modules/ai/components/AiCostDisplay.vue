<!--
  AI Cost Display Component
  Displays token usage and cost information
-->
<script setup lang="ts">
import type { IAiCost, IAiTokenUsage } from '../types'

const props = defineProps<{
  tokens?: IAiTokenUsage
  cost?: IAiCost
  class?: string
}>()
</script>

<template>
  <div v-if="tokens || cost" :class="props.class" class="flex flex-col gap-1 text-xs text-muted-foreground">
    <div v-if="tokens" class="flex items-center gap-2">
      <span>Tokens:</span>
      <span class="font-mono">{{ tokens.total.toLocaleString() }}</span>
      <span class="text-muted-foreground/70">
        ({{ tokens.input.toLocaleString() }} in / {{ tokens.output.toLocaleString() }} out)
      </span>
    </div>
    <div v-if="cost" class="flex items-center gap-2">
      <span>Cost:</span>
      <span class="font-mono">${{ cost.total.toFixed(6) }}</span>
      <span class="text-muted-foreground/70">
        (${{ cost.input.toFixed(6) }} in / ${{ cost.output.toFixed(6) }} out)
      </span>
    </div>
  </div>
</template>

