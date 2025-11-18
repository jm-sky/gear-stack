<script setup lang="ts">
import { useFocus } from '@vueuse/core'
import { nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useSettings } from '@/modules/settings/composables/useSettings'
import type { IGearContainer } from '../types/gear.types'
import { COLOR_DOT_CLASSES, CONTAINER_COLORS } from '../utils/containerColors'

defineProps<{
  container?: IGearContainer
  loading?: boolean
}>()

const emit = defineEmits<{
  cancel: []
}>()

const { t } = useI18n()
const { customContainerTypes } = useSettings()

// Auto-focus na pierwszym polu
const nameInputRef = ref<HTMLInputElement | undefined>(undefined)
nextTick(() => {
  useFocus(nameInputRef)
})

// Get container type label helper
const getContainerTypeLabel = (typeKey: string): string => {
  // Check if it's a custom container type
  const customType = customContainerTypes.value.find(t => t.key === typeKey)
  if (customType) {
    return customType.label
  }
  
  // Default types
  return t(`gear.container.types.${typeKey}`)
}

// Cancel handler
const handleCancel = () => {
  emit('cancel')
}
</script>

<template>
  <div class="space-y-6">
    <!-- Name -->
    <FormField v-slot="{ componentField }" name="name">
      <FormItem>
        <FormLabel :label="$t('gear.container.name')" required />
        <Input
          ref="nameInputRef"
          v-bind="componentField"
          :placeholder="$t('gear.container.name')"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Description -->
    <FormField v-slot="{ componentField }" name="description">
      <FormItem>
        <FormLabel :label="$t('gear.container.description')" />
        <textarea
          v-bind="componentField"
          :placeholder="$t('gear.container.description')"
          rows="3"
          class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Type -->
    <FormField v-slot="{ value, handleChange }" name="type">
      <FormItem>
        <FormLabel :label="$t('gear.container.type')" required />
        <Select :model-value="value" @update:model-value="handleChange">
          <SelectTrigger>
            <SelectValue :placeholder="$t('gear.container.type')" />
          </SelectTrigger>
          <SelectContent>
            <!-- Default Container Types -->
            <SelectItem value="backpack">
              {{ $t('gear.container.types.backpack') }}
            </SelectItem>
            <SelectItem value="bag">
              {{ $t('gear.container.types.bag') }}
            </SelectItem>
            <SelectItem value="pouch">
              {{ $t('gear.container.types.pouch') }}
            </SelectItem>
            <SelectItem value="box">
              {{ $t('gear.container.types.box') }}
            </SelectItem>
            <SelectItem value="cabinet">
              {{ $t('gear.container.types.cabinet') }}
            </SelectItem>
            <SelectItem value="vehicle">
              {{ $t('gear.container.types.vehicle') }}
            </SelectItem>
            <SelectItem value="shelf">
              {{ $t('gear.container.types.shelf') }}
            </SelectItem>
            <SelectItem value="drawer">
              {{ $t('gear.container.types.drawer') }}
            </SelectItem>
            <SelectItem value="case">
              {{ $t('gear.container.types.case') }}
            </SelectItem>
            <SelectItem value="trunk">
              {{ $t('gear.container.types.trunk') }}
            </SelectItem>
            <SelectItem value="other">
              {{ $t('gear.container.types.other') }}
            </SelectItem>
            
            <!-- Custom Container Types -->
            <template v-if="customContainerTypes.length > 0">
              <div class="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                {{ $t('settings.containerTypes.title') }}
              </div>
              <SelectItem
                v-for="containerType in customContainerTypes"
                :key="containerType.id"
                :value="containerType.key"
              >
                {{ getContainerTypeLabel(containerType.key) }}
              </SelectItem>
            </template>
          </SelectContent>
        </Select>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Color -->
    <FormField v-slot="{ value, handleChange }" name="color">
      <FormItem>
        <FormLabel :label="$t('gear.container.color')" />
        <div class="flex gap-2 flex-wrap">
          <button
            v-for="color in CONTAINER_COLORS"
            :key="color"
            type="button"
            :class="[
              'w-10 h-10 rounded-full border-2 transition-all',
              COLOR_DOT_CLASSES[color],
              value === color || (!value && color === 'default') ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : 'opacity-50 hover:opacity-75',
            ]"
            :aria-label="color"
            :title="$t(`gear.container.colors.${color}`)"
            @click="handleChange(color)"
          />
        </div>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Actions -->
    <div class="flex flex-col sm:flex-row justify-end gap-3">
      <Button type="button" variant="outline" @click="handleCancel">
        {{ $t('gear.actions.cancel') }}
      </Button>
      <Button type="submit" :loading>
        {{ $t('gear.actions.save') }}
      </Button>
    </div>
  </div>
</template>

