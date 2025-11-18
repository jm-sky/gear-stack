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
import type { IGearItem } from '../types/gear.types'

defineProps<{
  item?: IGearItem
  loading?: boolean
}>()

const emit = defineEmits<{
  cancel: []
}>()

const { t } = useI18n()
const { customCategories } = useSettings()

// Auto-focus na pierwszym polu
const nameInputRef = ref<HTMLInputElement | undefined>(undefined)
nextTick(() => {
  useFocus(nameInputRef)
})

// Get category label helper
const getCategoryLabel = (categoryKey: string): string => {
  // Check if it's a custom category
  const customCategory = customCategories.value.find(c => c.key === categoryKey)
  if (customCategory) {
    return customCategory.label
  }

  // Default categories
  return t(`gear.item.categories.${categoryKey}`)
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
        <FormLabel :label="$t('gear.item.name')" required />
        <Input
          ref="nameInputRef"
          v-bind="componentField"
          :placeholder="$t('gear.item.name')"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Category -->
    <FormField v-slot="{ value, handleChange }" name="category">
      <FormItem>
        <FormLabel :label="$t('gear.item.category')" required />
        <Select :model-value="value" @update:model-value="handleChange">
          <SelectTrigger>
            <SelectValue :placeholder="$t('gear.item.category')" />
          </SelectTrigger>
          <SelectContent>
            <!-- Default Categories -->
            <SelectItem value="water">
              {{ $t('gear.item.categories.water') }}
            </SelectItem>
            <SelectItem value="food">
              {{ $t('gear.item.categories.food') }}
            </SelectItem>
            <SelectItem value="shelter">
              {{ $t('gear.item.categories.shelter') }}
            </SelectItem>
            <SelectItem value="fire">
              {{ $t('gear.item.categories.fire') }}
            </SelectItem>
            <SelectItem value="firstAid">
              {{ $t('gear.item.categories.firstAid') }}
            </SelectItem>
            <SelectItem value="tools">
              {{ $t('gear.item.categories.tools') }}
            </SelectItem>
            <SelectItem value="navigation">
              {{ $t('gear.item.categories.navigation') }}
            </SelectItem>
            <SelectItem value="communication">
              {{ $t('gear.item.categories.communication') }}
            </SelectItem>
            <SelectItem value="clothing">
              {{ $t('gear.item.categories.clothing') }}
            </SelectItem>
            <SelectItem value="hygiene">
              {{ $t('gear.item.categories.hygiene') }}
            </SelectItem>
            <SelectItem value="other">
              {{ $t('gear.item.categories.other') }}
            </SelectItem>

            <!-- Custom Categories -->
            <template v-if="customCategories.length > 0">
              <div class="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                {{ $t('settings.categories.title') }}
              </div>
              <SelectItem
                v-for="category in customCategories"
                :key="category.id"
                :value="category.key"
              >
                {{ getCategoryLabel(category.key) }}
              </SelectItem>
            </template>
          </SelectContent>
        </Select>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Quantity and Weight -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <FormField v-slot="{ componentField }" name="quantity">
        <FormItem>
          <FormLabel :label="$t('gear.item.quantity')" required />
          <Input
            v-bind="componentField"
            type="number"
            :placeholder="$t('gear.item.quantity')"
            min="1"
          />
          <FormMessage />
        </FormItem>
      </FormField>

      <div class="grid grid-cols-[1fr_80px] sm:grid-cols-[1fr_auto] gap-2">
        <FormField v-slot="{ componentField }" name="weight">
          <FormItem>
            <FormLabel :label="$t('gear.item.weight')" required />
            <Input
              v-bind="componentField"
              type="number"
              :placeholder="$t('gear.item.weight')"
              min="0"
              step="0.01"
            />
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ value, handleChange }" name="weightUnit">
          <FormItem>
            <FormLabel :label="$t('gear.item.weightUnit')" />
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
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        </FormField>
      </div>
    </div>

    <!-- Priority and Status -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <FormField v-slot="{ value, handleChange }" name="priority">
        <FormItem>
          <FormLabel :label="$t('gear.item.priority')" required />
          <Select :model-value="value" @update:model-value="handleChange">
            <SelectTrigger>
              <SelectValue :placeholder="$t('gear.item.priority')" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="critical">
                {{ $t('gear.item.priorities.critical') }}
              </SelectItem>
              <SelectItem value="high">
                {{ $t('gear.item.priorities.high') }}
              </SelectItem>
              <SelectItem value="medium">
                {{ $t('gear.item.priorities.medium') }}
              </SelectItem>
              <SelectItem value="low">
                {{ $t('gear.item.priorities.low') }}
              </SelectItem>
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      </FormField>

      <FormField v-slot="{ value, handleChange }" name="status">
        <FormItem>
          <FormLabel :label="$t('gear.item.status')" required />
          <Select :model-value="value" @update:model-value="handleChange">
            <SelectTrigger>
              <SelectValue :placeholder="$t('gear.item.status')" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="owned">
                {{ $t('gear.item.statuses.owned') }}
              </SelectItem>
              <SelectItem value="missing">
                {{ $t('gear.item.statuses.missing') }}
              </SelectItem>
              <SelectItem value="toBuy">
                {{ $t('gear.item.statuses.toBuy') }}
              </SelectItem>
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      </FormField>
    </div>

    <!-- Expiration Date -->
    <FormField v-slot="{ componentField }" name="expirationDate">
      <FormItem>
        <FormLabel :label="$t('gear.item.expirationDate')" />
        <Input
          v-bind="componentField"
          type="date"
          :placeholder="$t('gear.item.expirationDate')"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Notes -->
    <FormField v-slot="{ componentField }" name="notes">
      <FormItem>
        <FormLabel :label="$t('gear.item.notes')" />
        <textarea
          v-bind="componentField"
          :placeholder="$t('gear.item.notes')"
          rows="3"
          class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        />
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

