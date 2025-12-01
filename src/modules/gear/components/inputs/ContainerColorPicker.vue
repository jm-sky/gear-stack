<script setup lang="ts">
import { Search } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Input from '@/components/ui/input/Input.vue'
import type { TContainerColor } from '../../types/gear.types'
import { COLOR_DOT_CLASSES, COLOR_TEXT_CLASSES, CONTAINER_COLORS } from '../../utils/containerColors'

const { t } = useI18n()

const modelValue = defineModel<string>('value', { default: '' })

const searchQuery = ref<string>('')

// Filter colors based on search query (searches in translated names)
const filteredColors = computed<TContainerColor[]>(() => {
  if (!searchQuery.value.trim()) {
    return CONTAINER_COLORS
  }

  const query = searchQuery.value.toLowerCase().trim()
  return CONTAINER_COLORS.filter((color) => {
    const translatedName = t(`gear.container.colors.${color}`).toLowerCase()
    return translatedName.includes(query)
  })
})
</script>

<template>
  <div class="space-y-3">
    <!-- Search Input -->
    <div class="relative">
      <Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        v-model="searchQuery"
        :placeholder="t('gear.container.colorSearchPlaceholder')"
        class="pl-9"
      />
    </div>

    <!-- Color Grid -->
    <div
      v-if="filteredColors.length > 0"
      class="grid grid-cols-4 sm:grid-cols-6 gap-2"
    >
      <button
        v-for="color in filteredColors"
        :key="color"
        v-tooltip.bottom="t(`gear.container.colors.${color}`)"
        type="button"
        class="flex flex-col items-center gap-1 cursor-pointer hover:opacity-80"
        :aria-label="t(`gear.container.colors.${color}`)"
        @click="modelValue = color"
      >
        <div
          :class="[
            'size-10 rounded-full border-2 transition-all',
            COLOR_DOT_CLASSES[color],
            COLOR_TEXT_CLASSES[color],
            modelValue === color || (!modelValue && color === 'default') ? 'ring-2 ring-offset-2 ring-current scale-110' : '',
          ]"
        />
        <span class="text-xs text-muted-foreground text-center">
          {{ t(`gear.container.colors.${color}`) }}
        </span>
      </button>
    </div>

    <!-- No results message -->
    <div v-else class="text-sm text-muted-foreground text-center py-4">
      {{ t('gear.container.colorSearchNoResults') }}
    </div>
  </div>
</template>
