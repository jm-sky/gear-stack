<script setup lang="ts">
import {
  AlertCircle,
  CheckCircle2,
  Edit,
  Eye,
  MoreHorizontal,
  Scan,
  ShoppingCart,
  Trash2,
} from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import DropdownMenuSeparator from '@/components/ui/dropdown-menu/DropdownMenuSeparator.vue'
import type { IGearItem, TGearItemStatus } from '../types/gear.types'

const { t } = useI18n()

const props = defineProps<{
  row: IGearItem
}>()

const emit = defineEmits<{
  edit: [item: IGearItem]
  delete: [item: IGearItem]
  statusChange: [status: TGearItemStatus]
  viewContainer: [item: IGearItem]
  recognizeParameters: [item: IGearItem]
}>()

// Check if item is a nested container
const isNestedContainer = computed(() => {
  return !!props.row.containerId
})
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button
        v-tooltip.bottom="t('gear.actions.moreActions')"
        variant="ghost"
        class="size-8 p-0"
        :aria-label="t('gear.actions.moreActions')"
      >
        <MoreHorizontal class="size-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <!-- For nested containers: show "View Container" first -->
      <template v-if="isNestedContainer">
        <DropdownMenuItem @click="emit('viewContainer', row)">
          <Eye class="size-4 mr-2" />
          {{ t('gear.item.viewContainer') }}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          class="text-destructive hover:text-destructive! hover:bg-destructive/4!"
          @click="emit('delete', row)"
        >
          <Trash2 class="size-4 mr-2" />
          {{ t('gear.actions.delete') }}
        </DropdownMenuItem>
      </template>
      <!-- For regular items: standard actions -->
      <template v-else>
        <DropdownMenuItem @click="emit('edit', row)">
          <Edit class="size-4 mr-2" />
          {{ t('gear.actions.edit') }}
        </DropdownMenuItem>
        <DropdownMenuItem @click="emit('recognizeParameters', row)">
          <Scan class="size-4 mr-2" />
          {{ t('gear.actions.recognizeParameters') }}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          v-if="row.status !== 'owned'"
          @click="emit('statusChange', 'owned')"
        >
          <CheckCircle2 class="size-4 mr-2" />
          {{ t('gear.item.statuses.owned') }}
        </DropdownMenuItem>
        <DropdownMenuItem
          v-if="row.status !== 'missing'"
          @click="emit('statusChange', 'missing')"
        >
          <AlertCircle class="size-4 mr-2" />
          {{ t('gear.item.statuses.missing') }}
        </DropdownMenuItem>
        <DropdownMenuItem
          v-if="row.status !== 'toBuy'"
          @click="emit('statusChange', 'toBuy')"
        >
          <ShoppingCart class="size-4 mr-2" />
          {{ t('gear.item.statuses.toBuy') }}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          class="text-destructive hover:text-destructive! hover:bg-destructive/4!"
          @click="emit('delete', row)"
        >
          <Trash2 class="size-4 mr-2" />
          {{ t('gear.actions.delete') }}
        </DropdownMenuItem>
      </template>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
