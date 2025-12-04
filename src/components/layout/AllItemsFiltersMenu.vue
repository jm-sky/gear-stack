<script setup lang="ts">
import { MoreVertical } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/button/Button.vue'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

const { t } = useI18n()

const hasImageFilter = defineModel<'all' | 'withImage' | 'withoutImage'>('hasImageFilter', {
  required: true,
})

function handleFilterChange(value: 'all' | 'withImage' | 'withoutImage') {
  hasImageFilter.value = value
}
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="outline" size="icon" class="shrink-0">
        <MoreVertical class="size-4" />
        <span class="sr-only">{{ t('gear.allItems.filters.menu', 'More filters') }}</span>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem
        :data-selected="hasImageFilter === 'withImage' ? '' : undefined"
        @click="handleFilterChange('withImage')"
      >
        {{ t('gear.allItems.filters.withImage', 'Only with image') }}
      </DropdownMenuItem>
      <DropdownMenuItem
        :data-selected="hasImageFilter === 'withoutImage' ? '' : undefined"
        @click="handleFilterChange('withoutImage')"
      >
        {{ t('gear.allItems.filters.withoutImage', 'Only without image') }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
