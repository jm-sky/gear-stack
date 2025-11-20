<script setup lang="ts">
import { useFocus } from '@vueuse/core'
import { nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import ComboBox from '@/components/ui/combo-box/ComboBox.vue'
import { FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { IGearContainer } from '../types/gear.types'
import { useGearSettings } from '../composables/useGearSettings'
import { COLOR_DOT_CLASSES, CONTAINER_COLORS } from '../utils/containerColors'
import { getBrandOptions } from '../utils/suggestedValues'

defineProps<{
  container?: IGearContainer
  loading?: boolean
}>()

const emit = defineEmits<{
  cancel: []
  nameBlur: []
}>()

const { t } = useI18n()
const { customContainerTypes } = useGearSettings()

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
          @blur="emit('nameBlur')"
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

    <!-- Extended Fields Section -->
    <div class="border-t pt-6 space-y-6">
      <h3 class="text-lg font-semibold text-muted-foreground">
        {{ $t('gear.container.extendedFields') }}
      </h3>

      <!-- Brand and Price -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField v-slot="{ value, handleChange }" name="brand">
          <FormItem>
            <FormLabel :label="$t('gear.container.brand')" />
            <ComboBox
              :value="value"
              :options="getBrandOptions()"
              :placeholder="$t('gear.container.brand')"
              :creatable="true"
              :create-label="$t('gear.comboBox.add')"
              class="w-full"
              @update:value="handleChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="price">
          <FormItem>
            <FormLabel :label="$t('gear.container.price')" />
            <Input
              v-bind="componentField"
              type="number"
              :placeholder="$t('gear.container.price')"
              min="0"
              step="0.01"
            />
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

      <!-- Weight and Weight Unit -->
      <div class="grid grid-cols-[1fr_80px] sm:grid-cols-[1fr_auto] gap-2">
        <FormField v-slot="{ componentField }" name="weight">
          <FormItem>
            <FormLabel :label="$t('gear.container.weight')" />
            <Input
              v-bind="componentField"
              type="number"
              :placeholder="$t('gear.container.weight')"
              min="0"
              step="0.01"
            />
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ value, handleChange }" name="weightUnit">
          <FormItem>
            <FormLabel :label="$t('gear.container.weightUnit')" />
            <Select :model-value="value" @update:model-value="handleChange">
              <SelectTrigger class="w-[80px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="g">
                  {{ $t('gear.item.weightUnits.g') }}
                </SelectItem>
                <SelectItem value="kg">
                  {{ $t('gear.item.weightUnits.kg') }}
                </SelectItem>
                <SelectItem value="oz">
                  {{ $t('gear.item.weightUnits.oz') }}
                </SelectItem>
                <SelectItem value="lb">
                  {{ $t('gear.item.weightUnits.lb') }}
                </SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

      <!-- URL -->
      <FormField v-slot="{ componentField }" name="url">
        <FormItem>
          <FormLabel :label="$t('gear.container.url')" />
          <Input
            v-bind="componentField"
            type="url"
            :placeholder="$t('gear.container.url')"
          />
          <FormMessage />
        </FormItem>
      </FormField>
    </div>

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

