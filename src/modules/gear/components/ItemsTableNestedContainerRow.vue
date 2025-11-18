<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { TableCell, TableRow } from '@/components/ui/table'
import type { IGearContainer, IGearItem, TContainerColor } from '../types/gear.types'
import { getStatusVariant } from '../utils/badgeVariants'
import { COLOR_BORDER_CLASSES } from '../utils/containerColors'
import { formatWeight } from '../utils/formatWeight'
import CategoryIcon from './CategoryIcon.vue'

const { t } = useI18n()

const props = defineProps<{
  nestedItems: IGearItem[]
  columnsLength: number
  container?: IGearContainer
}>()

// Get container color with fallback to 'default'
const containerColor = computed<TContainerColor>(() => {
  return props.container?.color ?? 'default'
})

// Get border color class
const borderColorClass = computed(() => {
  return COLOR_BORDER_CLASSES[containerColor.value]
})
</script>

<template>
  <TableRow class="bg-muted/30 shadow-inner">
    <TableCell :colspan="columnsLength" class="p-0">
      <div class="flex flex-col border-l-2" :class="borderColorClass">
        <div class="pl-8 pr-4 py-3 text-sm font-medium text-muted-foreground border-b">
          {{ t('gear.item.containerContents') }} ({{ nestedItems.length }})
        </div>

        <div v-if="nestedItems.length === 0" class="pl-8 pr-4 py-3 text-sm text-muted-foreground italic">
          {{ t('gear.item.emptyContainer') }}
        </div>
        <template v-else>
          <div
            v-for="nestedItem in nestedItems"
            :key="nestedItem.id"
            class="pl-8 pr-4 py-3 flex items-center gap-4 text-sm border-b rounded hover:bg-muted/50"
          >
            <div class="flex items-center gap-2 min-w-[200px]">
              <CategoryIcon :category="nestedItem.category" :size="14" class="text-muted-foreground" />
              <span>{{ nestedItem.name }}</span>
            </div>
            <div class="text-muted-foreground min-w-[60px]">
              {{ nestedItem.quantity }}x
            </div>
            <div class="text-muted-foreground min-w-[80px]">
              {{ formatWeight(nestedItem.weight * nestedItem.quantity, nestedItem.weightUnit ?? 'g') }}
            </div>
            <Badge :variant="getStatusVariant(nestedItem.status)" class="text-xs">
              {{ t(`gear.item.statuses.${nestedItem.status}`) }}
            </Badge>
          </div>
        </template>
      </div>
    </TableCell>
  </TableRow>
</template>
