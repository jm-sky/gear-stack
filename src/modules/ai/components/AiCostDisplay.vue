<!--
  AI Cost Display Component
  Displays token usage and cost information
-->
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { IAiCost, IAiTokenUsage } from '../types'

const { t } = useI18n()

const props = defineProps<{
  tokens?: IAiTokenUsage
  cost?: IAiCost
  class?: string
}>()
</script>

<template>
  <div v-if="tokens || cost" :class="props.class" class="flex flex-col gap-1 text-xs text-muted-foreground">
    <div v-if="tokens" class="flex items-center gap-2">
      <span>{{ t('ai.cost.tokens') }}</span>
      <span>{{ tokens.total.toLocaleString() }}</span>
      <span class="text-muted-foreground/70">
        ({{ tokens.input.toLocaleString() }} {{ t('ai.cost.in') }} / {{ tokens.output.toLocaleString() }} {{ t('ai.cost.out') }})
      </span>
    </div>
    <div v-if="cost" class="flex items-center gap-2">
      <span>{{ t('ai.cost.cost') }}</span>
      <span>${{ cost.total.toFixed(6) }}</span>
      <span class="text-muted-foreground/70">
        (${{ cost.input.toFixed(6) }} {{ t('ai.cost.in') }} / ${{ cost.output.toFixed(6) }} {{ t('ai.cost.out') }})
      </span>
    </div>
  </div>
</template>

