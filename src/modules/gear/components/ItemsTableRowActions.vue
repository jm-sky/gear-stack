<script setup lang="ts">
import { MoreHorizontal } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import DropdownMenuSeparator from '@/components/ui/dropdown-menu/DropdownMenuSeparator.vue'
import type { IGearItem, TGearItemStatus } from '../types/gear.types'

const { t } = useI18n()

const emit = defineEmits<{
  edit: [item: IGearItem]
  delete: [item: IGearItem]
  statusChange: [status: TGearItemStatus]
}>()

defineProps<{
  row: IGearItem
}>()
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" class="size-8 p-0">
        <MoreHorizontal class="size-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem @click="emit('edit', row)">
        {{ t('gear.actions.edit') }}
      </DropdownMenuItem>
      <DropdownMenuSeparator />
      <DropdownMenuItem
        v-if="row.status !== 'owned'"
        @click="emit('statusChange', 'owned')"
      >
        {{ t('gear.item.statuses.owned') }}
      </DropdownMenuItem>
      <DropdownMenuItem
        v-if="row.status !== 'missing'"
        @click="emit('statusChange', 'missing')"
      >
        {{ t('gear.item.statuses.missing') }}
      </DropdownMenuItem>
      <DropdownMenuItem
        v-if="row.status !== 'toBuy'"
        @click="emit('statusChange', 'toBuy')"
      >
        {{ t('gear.item.statuses.toBuy') }}
      </DropdownMenuItem>
      <DropdownMenuSeparator />
      <DropdownMenuItem
        class="text-destructive hover:text-destructive! hover:bg-destructive/4!"
        @click="emit('delete', row)"
      >
        {{ t('gear.actions.delete') }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
