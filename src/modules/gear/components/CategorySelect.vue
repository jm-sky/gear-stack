<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useGearSettings } from '../composables/useGearSettings'
import CategoryIcon from './CategoryIcon.vue'

const modelValue = defineModel<string>()

defineProps<{
  placeholder?: string
}>()

const { t } = useI18n()
const { customCategories } = useGearSettings()

const getCategoryLabel = (categoryValue: string): string => {
  const customCategory = customCategories.value.find(c => c.value === categoryValue)
  if (customCategory) {
    return customCategory.value
  }
  return t(`gear.item.categories.${categoryValue}`)
}

const defaultCategories = [
  'blades',
  'fire',
  'light',
  'tools',
  'firstAid',
  'water',
  'food',
  'shelter',
  'navigation',
  'communication',
  'clothing',
  'hygiene',
  'other',
] as const
</script>

<template>
  <Select v-model="modelValue">
    <SelectTrigger class="min-w-36">
      <SelectValue :placeholder="placeholder ?? $t('gear.item.category')" />
    </SelectTrigger>
    <SelectContent>
      <!-- Default Categories - ordered by most commonly used -->
      <SelectItem
        v-for="category in defaultCategories"
        :key="category"
        :value="category"
      >
        <div class="flex items-center gap-2">
          <CategoryIcon :category="category" :size="16" />
          <span>{{ $t(`gear.item.categories.${category}`) }}</span>
        </div>
      </SelectItem>

      <!-- Custom Categories -->
      <template v-if="customCategories.length > 0">
        <div class="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
          {{ $t('settings.categories.title') }}
        </div>
        <SelectItem
          v-for="category in customCategories"
          :key="category.id"
          :value="category.value"
        >
          <div class="flex items-center gap-2">
            <CategoryIcon :category="category.value" :size="16" />
            <span>{{ getCategoryLabel(category.value) }}</span>
          </div>
        </SelectItem>
      </template>
    </SelectContent>
  </Select>
</template>
