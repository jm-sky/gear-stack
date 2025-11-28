<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useContainerTypeLabel } from '../composables/useContainerTypeLabel'
import { useGearSettings } from '../composables/useGearSettings'

const modelValue = defineModel<string>()

defineProps<{
  placeholder?: string
}>()

const { customContainerTypes } = useGearSettings()
const { getContainerTypeLabel } = useContainerTypeLabel()

const defaultContainerTypes = [
  'backpack',
  'bag',
  'pouch',
  'box',
  'cabinet',
  'vehicle',
  'shelf',
  'drawer',
  'case',
  'trunk',
  'other',
] as const
</script>

<template>
  <Select v-model="modelValue">
    <SelectTrigger>
      <SelectValue :placeholder="placeholder ?? $t('gear.container.type')" />
    </SelectTrigger>
    <SelectContent>
      <!-- Default Container Types -->
      <SelectItem
        v-for="containerType in defaultContainerTypes"
        :key="containerType"
        :value="containerType"
      >
        {{ $t(`gear.container.types.${containerType}`) }}
      </SelectItem>

      <!-- Custom Container Types -->
      <template v-if="customContainerTypes.length > 0">
        <div class="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
          {{ $t('settings.containerTypes.title') }}
        </div>
        <SelectItem
          v-for="containerType in customContainerTypes"
          :key="containerType.id"
          :value="containerType.value"
        >
          {{ getContainerTypeLabel(containerType.value) }}
        </SelectItem>
      </template>
    </SelectContent>
  </Select>
</template>
