<script setup lang="ts">
import { Box, ChevronRight } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import { Button } from '@/components/ui/button'
import { COLOR_TEXT_CLASSES } from '@/modules/gear/utils/containerColors'
import ItemsTableMoveButtons from './ItemsTableMoveButtons.vue'
import type { IGearContainer, IGearItem } from '@/modules/gear/types/gear.types'

const { t } = useI18n()

const {
  item,
  publicMode,
  isExpired,
  isExpiringSoon,
  isNestedContainer,
  isRowExpanded,
  canMoveUp,
  canMoveDown,
  nestedContainer,
} = defineProps<{
  item: IGearItem
  publicMode: boolean
  isExpired: boolean
  isExpiringSoon: boolean
  isNestedContainer: boolean
  isRowExpanded: boolean
  canMoveUp: boolean
  canMoveDown: boolean
  nestedContainer?: IGearContainer
}>()

const emit = defineEmits<{
  moveUp: []
  moveDown: []
  navigate: []
  navigateToNestedContainer: []
  toggleExpand: []
}>()

const textClass = computed<string>(() => {
  if (isExpired) return 'text-destructive font-semibold'
  if (isExpiringSoon) return 'text-yellow-600'
  return ''
})

const containerColor = computed<string>(() => {
  return COLOR_TEXT_CLASSES[nestedContainer?.color ?? 'default']
})
</script>

<template>
  <div class="flex items-center gap-2" :class="textClass">
    <!-- Move up/down buttons (only in non-public mode) -->
    <ItemsTableMoveButtons
      v-if="!publicMode"
      :can-move-up
      :can-move-down
      @move-up="emit('moveUp')"
      @move-down="emit('moveDown')"
    />

    <!-- Expand/Collapse button for nested containers -->
    <Button
      v-if="isNestedContainer"
      variant="ghost"
      size="sm"
      class="size-6 p-0 shrink-0"
      @click.stop="emit('toggleExpand')"
    >
      <ChevronRight
        :size="16"
        class="text-muted-foreground transition-transform"
        :class="{ 'rotate-90': isRowExpanded }"
      />
    </Button>

    <!-- Nested container display -->
    <template v-if="isNestedContainer">
      <Box :size="16" class="text-muted-foreground shrink-0" :class="containerColor" />
      <span
        class="font-semibold cursor-pointer text-foreground/80 hover:text-primary transition-colors"
        @click="emit('navigateToNestedContainer')"
      >
        {{ item.name }}
      </span>
    </template>

    <!-- Regular item display -->
    <span
      v-else
      class="cursor-pointer hover:text-primary transition-colors"
      @click="emit('navigate')"
    >
      {{ item.name }}
    </span>

    <!-- Badges -->
    <Badge v-if="isNestedContainer" variant="outline" class="text-xs">
      {{ t('gear.item.nestedContainer') }}
    </Badge>
    <Badge v-if="isExpired" variant="destructive" class="text-xs">
      {{ t('gear.item.expiration.expired') }}
    </Badge>
    <Badge v-if="isExpiringSoon" variant="outline" class="text-xs text-yellow-600 border-yellow-600">
      {{ t('gear.item.expiration.expiringSoon') }}
    </Badge>
  </div>
</template>
