<script setup lang="ts">
import { ChevronDown, ChevronUp } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

const { canMoveUp, canMoveDown } = defineProps<{
  canMoveUp: boolean
  canMoveDown: boolean
}>()

const emit = defineEmits<{
  moveUp: []
  moveDown: []
}>()
</script>

<template>
  <div class="flex flex-col gap-0.5 shrink-0">
    <Button
      variant="ghost"
      size="sm"
      class="size-5 p-0 h-4"
      :disabled="!canMoveUp"
      @click.stop="emit('moveUp')"
    >
      <ChevronUp :size="12" class="text-muted-foreground" />
    </Button>
    <Button
      variant="ghost"
      size="sm"
      class="size-5 p-0 h-4"
      :disabled="!canMoveDown"
      @click.stop="emit('moveDown')"
    >
      <ChevronDown :size="12" class="text-muted-foreground" />
    </Button>
  </div>
</template>
