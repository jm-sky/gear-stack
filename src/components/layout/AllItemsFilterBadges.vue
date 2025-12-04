<script setup lang="ts">
import { computed } from 'vue'
import { X } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Badge from '@/components/ui/badge/Badge.vue'
import Button from '@/components/ui/button/Button.vue'

const { t } = useI18n()

const props = defineProps<{
  hasImageFilter: 'all' | 'withImage' | 'withoutImage'
}>()

const emit = defineEmits<{
  'remove-filter': [filter: 'withImage' | 'withoutImage']
}>()

const activeFilters = computed<Array<{ key: 'withImage' | 'withoutImage', label: string }>>(() => {
  const filters: Array<{ key: 'withImage' | 'withoutImage', label: string }> = []
  if (props.hasImageFilter === 'withImage') {
    filters.push({
      key: 'withImage',
      label: t('gear.allItems.filters.withImage', 'Only with image'),
    })
  }
  if (props.hasImageFilter === 'withoutImage') {
    filters.push({
      key: 'withoutImage',
      label: t('gear.allItems.filters.withoutImage', 'Only without image'),
    })
  }
  return filters
})

function removeFilter(filterKey: 'withImage' | 'withoutImage') {
  emit('remove-filter', filterKey)
}
</script>

<template>
  <div v-if="activeFilters.length > 0" class="flex flex-wrap items-center gap-2">
    <Badge
      v-for="filter in activeFilters"
      :key="filter.key"
      variant="secondary"
      class="flex items-center gap-1.5 pr-1"
    >
      <span>{{ filter.label }}</span>
      <Button
        variant="ghost"
        size="icon"
        class="size-4 h-auto w-auto p-0 hover:bg-transparent"
        @click="removeFilter(filter.key)"
      >
        <X class="size-3" />
        <span class="sr-only">{{ t('gear.allItems.filters.removeFilter', 'Remove filter') }}</span>
      </Button>
    </Badge>
  </div>
</template>
