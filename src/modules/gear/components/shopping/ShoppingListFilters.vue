<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { TGearItemCategory } from '../../types/gear.types'
import { useCategoryLabel } from '../../composables/useCategoryLabel'
import CategoryIcon from '../CategoryIcon.vue'

const { t } = useI18n()

const { allCategories, selectedCategories, budget, includeExpiringSoon, defaultCurrency } = defineProps<{
  allCategories: TGearItemCategory[]
  selectedCategories: TGearItemCategory[]
  budget: number | null
  includeExpiringSoon: boolean
  defaultCurrency: string
}>()

const emit = defineEmits<{
  'update:selectedCategories': [categories: TGearItemCategory[]]
  'update:budget': [budget: number | null]
  'update:includeExpiringSoon': [include: boolean]
}>()

const { getCategoryLabel } = useCategoryLabel()

// Category checkbox states - using reactive object for v-model compatibility
const categoryChecked = ref<Record<string, boolean>>({})

// Initialize categoryChecked from props
watch(
  () => allCategories,
  (categories) => {
    categories.forEach(category => {
      if (!(category in categoryChecked.value)) {
        categoryChecked.value[category] = selectedCategories.includes(category)
      }
    })
  },
  { immediate: true },
)

// Watch categoryChecked changes and emit
watch(
  categoryChecked,
  (checked) => {
    const newSelected: TGearItemCategory[] = []
    Object.entries(checked).forEach(([category, isChecked]) => {
      if (isChecked && allCategories.includes(category as TGearItemCategory)) {
        newSelected.push(category as TGearItemCategory)
      }
    })
    emit('update:selectedCategories', newSelected)
  },
  { deep: true },
)

// Watch selectedCategories changes from parent and sync to categoryChecked
watch(
  () => selectedCategories,
  (selected) => {
    allCategories.forEach(category => {
      categoryChecked.value[category] = selected.includes(category)
    })
  },
  { immediate: true },
)

const handleBudgetUpdate = (value: string | number) => {
  const stringValue = typeof value === 'number' ? value.toString() : value
  emit('update:budget', stringValue === '' ? null : Number(stringValue))
}

const handleClearBudget = () => {
  emit('update:budget', null)
}

const handleIncludeExpiringUpdate = (value: boolean | 'indeterminate') => {
  if (value === 'indeterminate') return
  emit('update:includeExpiringSoon', value)
}
</script>

<template>
  <div class="space-y-4 p-4 border rounded-lg bg-muted/50">
    <h3 class="font-semibold text-base">
      {{ t('gear.shopping.filters', 'Filters') }}
    </h3>

    <!-- Categories filter -->
    <div v-if="allCategories.length > 0" class="space-y-2">
      <p class="text-sm font-medium">
        {{ t('gear.shopping.filterByCategory', 'Filter by Category') }}:
      </p>
      <div class="flex flex-wrap gap-4">
        <div
          v-for="category in allCategories"
          :key="category"
          class="flex items-center gap-2"
        >
          <Checkbox
            :id="`category-${category}`"
            v-model="categoryChecked[category]"
          />
          <Label
            :for="`category-${category}`"
            class="text-sm cursor-pointer flex items-center gap-2"
          >
            <CategoryIcon :category="category" :size="14" />
            {{ getCategoryLabel(category) }}
          </Label>
        </div>
      </div>
    </div>

    <!-- Budget filter -->
    <div class="space-y-2">
      <Label
        for="shopping-budget-filter"
        class="text-sm"
      >
        {{ t('gear.shopping.filterByBudget', 'Filter by Budget') }}:
      </Label>
      <div class="flex items-center gap-2">
        <Input
          id="shopping-budget-filter"
          name="shopping-budget-filter"
          :model-value="budget?.toString() ?? ''"
          type="number"
          :placeholder="t('gear.shopping.budgetPlaceholder', 'Enter budget amount')"
          class="max-w-xs"
          min="0"
          step="0.01"
          @update:model-value="handleBudgetUpdate"
        />
        <span class="text-sm text-muted-foreground">{{ defaultCurrency }}</span>
        <Button
          v-if="budget !== null"
          variant="ghost"
          size="sm"
          @click="handleClearBudget"
        >
          {{ t('gear.shopping.clearBudget', 'Clear') }}
        </Button>
      </div>
    </div>

    <!-- Include expiring soon -->
    <div class="flex items-center gap-2">
      <Checkbox
        id="include-expiring"
        :model-value="includeExpiringSoon"
        @update:model-value="handleIncludeExpiringUpdate"
      />
      <Label
        for="include-expiring"
        class="text-sm cursor-pointer"
      >
        {{ t('gear.shopping.includeExpiringSoon', 'Include items expiring soon') }}
      </Label>
    </div>
  </div>
</template>
