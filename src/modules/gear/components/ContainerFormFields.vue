<script setup lang="ts">
import { useFocus } from '@vueuse/core'
import { nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
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
import WeightInputWithUnitPicker from '@/components/ui/weight-input/WeightInputWithUnitPicker.vue'
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
  recognizeParameters: []
}>()

const { t } = useI18n()
const { customContainerTypes, customBrands } = useGearSettings()

// Auto-focus na pierwszym polu
const nameInputRef = ref<HTMLInputElement | undefined>(undefined)
nextTick(() => {
  useFocus(nameInputRef)
})

// Get container type label helper
const getContainerTypeLabel = (typeValue: string): string => {
  // Check if it's a custom container type
  const customType = customContainerTypes.value.find(t => t.value === typeValue)
  if (customType) {
    return customType.value
  }

  // Default types
  return t(`gear.container.types.${typeValue}`)
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
                :value="containerType.value"
              >
                {{ getContainerTypeLabel(containerType.value) }}
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
        <div class="grid grid-cols-5 sm:grid-cols-10 gap-2">
          <button
            v-for="color in CONTAINER_COLORS"
            :key="color"
            type="button"
            :class="[
              'size-10 rounded-full border-2 transition-all',
              COLOR_DOT_CLASSES[color],
              value === color || (!value && color === 'default') ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : 'opacity-50 hover:opacity-75',
            ]"
            :aria-label="$t(`gear.container.colors.${color}`)"
            :title="$t(`gear.container.colors.${color}`)"
            @click="handleChange(color)"
          />
        </div>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Hide When Nested -->
    <FormField v-slot="{ componentField, handleChange }" name="hideWhenNested">
      <FormItem v-slot="{ id }" class="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
        <Checkbox
          :id="id"
          :model-value="componentField.modelValue"
          @update:model-value="handleChange"
        />
        <div class="flex-1 space-y-1">
          <FormLabel :label="$t('gear.container.hideWhenNested')" class="cursor-pointer" />
          <p class="text-sm text-muted-foreground">
            {{ $t('gear.container.hideWhenNestedDescription') }}
          </p>
        </div>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Is Public -->
    <FormField v-slot="{ componentField, handleChange }" name="isPublic">
      <FormItem v-slot="{ id }" class="flex flex-row items-start space-x-3 space-y-0 rounded-md border border-blue-200 bg-blue-50 dark:bg-blue-950/20 dark:border-blue-800 p-4">
        <Checkbox
          :id="id"
          :model-value="componentField.modelValue"
          @update:model-value="handleChange"
        />
        <div class="flex-1 space-y-1">
          <FormLabel :label="$t('gear.container.isPublic')" class="cursor-pointer" />
          <p class="text-sm text-muted-foreground">
            {{ $t('gear.container.isPublicDescription') }}
          </p>
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
              :options="getBrandOptions(customBrands)"
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
      <FormField v-slot="{ value: weightValue, handleChange: handleWeightChange }" name="weight">
        <FormField v-slot="{ value: unitValue, handleChange: handleUnitChange }" name="weightUnit">
          <FormItem>
            <FormLabel :label="$t('gear.container.weight')" />
            <WeightInputWithUnitPicker
              :model-value="weightValue"
              :unit="unitValue || 'g'"
              :placeholder="$t('gear.container.weight')"
              @update:model-value="handleWeightChange"
              @update:unit="handleUnitChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>
      </FormField>

      <!-- Max Weight and Max Weight Unit -->
      <FormField v-slot="{ value: maxWeightValue, handleChange: handleMaxWeightChange }" name="maxWeight">
        <FormField v-slot="{ value: maxUnitValue, handleChange: handleMaxUnitChange }" name="maxWeightUnit">
          <FormItem>
            <FormLabel :label="$t('gear.container.maxWeight')" />
            <WeightInputWithUnitPicker
              :model-value="maxWeightValue"
              :unit="maxUnitValue || 'g'"
              :placeholder="$t('gear.container.maxWeight')"
              @update:model-value="handleMaxWeightChange"
              @update:unit="handleMaxUnitChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>
      </FormField>

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
    <Button
      type="button"
      variant="outline"
      @click="$emit('recognizeParameters')"
    >
      {{ $t('gear.actions.recognizeParameters') }}
    </Button>
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

