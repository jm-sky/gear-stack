<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { TableCell, TableRow } from '@/components/ui/table'
import { useCoreSettings } from '@/modules/settings/composables/useCoreSettings'
import type { IGearContainer, IGearItem, TContainerColor } from '../types/gear.types'
import { getPriorityVariant, getStatusVariant } from '../utils/badgeVariants'
import { COLOR_BORDER_CLASSES } from '../utils/containerColors'
import { formatWeightWithPreferredUnit } from '../utils/formatWeight'
import CategoryIcon from './CategoryIcon.vue'

const { t } = useI18n()
const { settings: coreSettings } = useCoreSettings()
const settings = computed(() => ({ preferredWeightUnit: coreSettings.value.preferredWeightUnit }))

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
            <div class="flex items-center gap-2 min-w-0 md:min-w-92">
              <CategoryIcon :category="nestedItem.category" :size="14" class="text-muted-foreground" />
              <span>{{ nestedItem.name }}</span>
            </div>
            <div class="text-muted-foreground min-w-0 md:min-w-18">
              {{ nestedItem.quantity }}
            </div>
            <div class="text-muted-foreground text-end px-4 min-w-0 md:min-w-[80px]">
              {{ formatWeightWithPreferredUnit(nestedItem.weight * nestedItem.quantity, nestedItem.weightUnit ?? 'g', settings.preferredWeightUnit) }}
            </div>
            <div class="min-w-0 md:min-w-26">
              <Badge :variant="getPriorityVariant(nestedItem.priority)">
                {{ t(`gear.item.priorities.${nestedItem.priority}`) }}
              </Badge>
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
