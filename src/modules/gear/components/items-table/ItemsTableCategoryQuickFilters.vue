<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import type { TGearItemCategory } from '../../types/gear.types'
import { useCategoryLabel } from '../../composables/useCategoryLabel'
import CategoryIcon from '../CategoryIcon.vue'

const { t } = useI18n()
const { getCategoryLabel } = useCategoryLabel()

const { categories } = defineProps<{
  categories: TGearItemCategory[]
}>()

const selectedCategories = defineModel<TGearItemCategory[]>({ default: () => [] })

function isSelected(category: TGearItemCategory): boolean {
  return selectedCategories.value.includes(category)
}

function toggleCategory(category: TGearItemCategory): void {
  if (isSelected(category)) {
    selectedCategories.value = selectedCategories.value.filter(c => c !== category)
  } else {
    selectedCategories.value = [...selectedCategories.value, category]
  }
}
</script>

<template>
  <div
    v-if="categories.length > 0"
    class="hidden lg:inline-flex flex-wrap items-center gap-1"
    role="group"
    :aria-label="t('gear.filters.categoryQuickFilters')"
  >
    <Button
      v-for="category in categories"
      :key="category"
      v-tooltip.bottom="getCategoryLabel(category)"
      type="button"
      variant="ghost"
      size="icon"
      class="size-8"
      :class="isSelected(category) ? 'bg-accent text-accent-foreground ring-1 ring-ring' : 'text-muted-foreground'"
      :aria-pressed="isSelected(category)"
      :aria-label="t('gear.filters.filterByCategory', { category: getCategoryLabel(category) })"
      @click="toggleCategory(category)"
    >
      <CategoryIcon
        :category="category"
        :size="16"
      />
    </Button>
  </div>
</template>
