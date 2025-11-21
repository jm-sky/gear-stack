<script setup lang="ts">
import ComboBox from '@/components/ui/combo-box/ComboBox.vue'
import { getColorOptions } from '../utils/suggestedValues'

const modelValue = defineModel<string>('value', { default: '' })
</script>

<template>
  <ComboBox
    v-model:value="modelValue"
    :options="getColorOptions()"
    :placeholder="''"
    :creatable="true"
    :create-label="$t('gear.comboBox.add')"
    class="w-full"
  >
    <template #option-content="{ option }">
      <div class="flex items-center gap-2">
        <div class="w-4 h-4 rounded-full" :style="{ backgroundColor: option.data as string }" />
        <span>{{ option.label }}</span>
      </div>
    </template>
  </ComboBox>
</template>
