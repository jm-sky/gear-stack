<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useCategoryLabel } from '../../composables/useCategoryLabel'
import { useGearSettings } from '../../composables/useGearSettings'
import { DEFAULT_ITEM_CATEGORY } from '../../utils/constants'
import CategoryIcon from '../CategoryIcon.vue'
import type { IGearItemV2, IUpdateGearItemV2Dto, TGearItemCategory } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()
const { customCategories } = useGearSettings()
const { getCategoryLabel } = useCategoryLabel()

const props = defineProps<{
  item: IGearItemV2
}>()

const emit = defineEmits<{
  change: [updates: IUpdateGearItemV2Dto, options?: { immediate?: boolean }]
  navigate: [direction: 'next' | 'prev' | 'down']
}>()

const editedCategory = ref<TGearItemCategory>(props.item.category ?? DEFAULT_ITEM_CATEGORY)

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

function handleCategoryChange(newCategory: unknown) {
  if (newCategory === props.item.category) {
    emit('change', {})
    return
  }

  editedCategory.value = newCategory as TGearItemCategory
  emit('change', { category: newCategory as TGearItemCategory }, { immediate: true })
}

function handleTab(event: KeyboardEvent) {
  event.preventDefault()
  emit('navigate', event.shiftKey ? 'prev' : 'next')
}

watch(
  () => props.item.category,
  (newCategory) => {
    editedCategory.value = newCategory ?? DEFAULT_ITEM_CATEGORY
  },
)
</script>

<template>
  <div
    data-editable-cell
    data-field="category"
    :data-item-id="item.id"
  >
    <Select
      :model-value="editedCategory"
      @update:model-value="handleCategoryChange"
    >
      <SelectTrigger
        :aria-label="t('gear.item.category')"
        class="h-10 sm:h-[2.1rem]! min-w-24 sm:min-w-35 w-full border-transparent bg-transparent shadow-none focus:ring-1"
        @keydown.tab="handleTab"
      >
        <SelectValue>
          <div class="flex items-center gap-2">
            <CategoryIcon
              :category="editedCategory"
              :size="16"
            />
            <span>{{ getCategoryLabel(editedCategory) }}</span>
          </div>
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        <SelectItem
          v-for="category in defaultCategories"
          :key="category"
          :value="category"
        >
          <div class="flex items-center gap-2">
            <CategoryIcon
              :category="category"
              :size="16"
            />
            <span>{{ t(`gear.item.categories.${category}`) }}</span>
          </div>
        </SelectItem>

        <template v-if="customCategories.length > 0">
          <div class="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
            {{ t('settings.categories.title') }}
          </div>
          <SelectItem
            v-for="category in customCategories"
            :key="category.id"
            :value="category.value"
          >
            <div class="flex items-center gap-2">
              <CategoryIcon
                :category="category.value"
                :size="16"
              />
              <span>{{ getCategoryLabel(category.value) }}</span>
            </div>
          </SelectItem>
        </template>
      </SelectContent>
    </Select>
  </div>
</template>
