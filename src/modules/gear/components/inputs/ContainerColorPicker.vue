<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { COLOR_DOT_CLASSES, CONTAINER_COLORS } from '../../utils/containerColors'

const { t } = useI18n()

const modelValue = defineModel<string>('value', { default: '' })
</script>

<template>
  <div class="grid grid-cols-5 sm:grid-cols-10 gap-2">
    <button
      v-for="color in CONTAINER_COLORS"
      :key="color"
      v-tooltip.bottom="t(`gear.container.colors.${color}`)"
      type="button"
      :class="[
        'cursor-pointer size-10 rounded-full border-2 transition-all',
        COLOR_DOT_CLASSES[color],
        value === color || (!value && color === 'default') ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : 'opacity-50 hover:opacity-75',
      ]"
      :aria-label="t(`gear.container.colors.${color}`)"
      @click="modelValue = color"
    />
  </div>
</template>
