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
import { useSettings } from '@/modules/settings/composables/useSettings'
import type { IGearItem } from '../types/gear.types'
import { getBrandOptions } from '../utils/suggestedValues'
import CategoryIcon from './CategoryIcon.vue'
import ColorAutocomplete from './ColorAutocomplete.vue'

defineProps<{
  item?: IGearItem
  loading?: boolean
}>()

const emit = defineEmits<{
  cancel: []
  nameBlur: []
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
          @blur="emit('nameBlur')"
        />
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Category -->
    <FormField v-slot="{ value, handleChange }" name="category">
      <FormItem>
        <FormLabel :label="$t('gear.item.category')" required />
        <Select :model-value="value" @update:model-value="handleChange">
          <SelectTrigger class="min-w-36">
            <SelectValue :placeholder="$t('gear.item.category')" />
          </SelectTrigger>
          <SelectContent>
            <!-- Default Categories -->
            <SelectItem value="water">
              <div class="flex items-center gap-2">
                <CategoryIcon category="water" :size="16" />
                <span>{{ $t('gear.item.categories.water') }}</span>
              </div>
            </SelectItem>
            <SelectItem value="food">
              <div class="flex items-center gap-2">
                <CategoryIcon category="food" :size="16" />
                <span>{{ $t('gear.item.categories.food') }}</span>
              </div>
            </SelectItem>
            <SelectItem value="shelter">
              <div class="flex items-center gap-2">
                <CategoryIcon category="shelter" :size="16" />
                <span>{{ $t('gear.item.categories.shelter') }}</span>
              </div>
            </SelectItem>
            <SelectItem value="fire">
              <div class="flex items-center gap-2">
                <CategoryIcon category="fire" :size="16" />
                <span>{{ $t('gear.item.categories.fire') }}</span>
              </div>
            </SelectItem>
            <SelectItem value="firstAid">
              <div class="flex items-center gap-2">
                <CategoryIcon category="firstAid" :size="16" />
                <span>{{ $t('gear.item.categories.firstAid') }}</span>
              </div>
            </SelectItem>
            <SelectItem value="tools">
              <div class="flex items-center gap-2">
                <CategoryIcon category="tools" :size="16" />
                <span>{{ $t('gear.item.categories.tools') }}</span>
              </div>
            </SelectItem>
            <SelectItem value="navigation">
              <div class="flex items-center gap-2">
                <CategoryIcon category="navigation" :size="16" />
                <span>{{ $t('gear.item.categories.navigation') }}</span>
              </div>
            </SelectItem>
            <SelectItem value="communication">
              <div class="flex items-center gap-2">
                <CategoryIcon category="communication" :size="16" />
                <span>{{ $t('gear.item.categories.communication') }}</span>
              </div>
            </SelectItem>
            <SelectItem value="clothing">
              <div class="flex items-center gap-2">
                <CategoryIcon category="clothing" :size="16" />
                <span>{{ $t('gear.item.categories.clothing') }}</span>
              </div>
            </SelectItem>
            <SelectItem value="hygiene">
              <div class="flex items-center gap-2">
                <CategoryIcon category="hygiene" :size="16" />
                <span>{{ $t('gear.item.categories.hygiene') }}</span>
              </div>
            </SelectItem>
            <SelectItem value="light">
              <div class="flex items-center gap-2">
                <CategoryIcon category="light" :size="16" />
                <span>{{ $t('gear.item.categories.light') }}</span>
              </div>
            </SelectItem>
            <SelectItem value="other">
              <div class="flex items-center gap-2">
                <CategoryIcon category="other" :size="16" />
                <span>{{ $t('gear.item.categories.other') }}</span>
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
                :value="category.key"
              >
                <div class="flex items-center gap-2">
                  <CategoryIcon :category="category.key" :size="16" />
                  <span>{{ getCategoryLabel(category.key) }}</span>
                </div>
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
            <SelectTrigger class="min-w-36">
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
            <SelectTrigger class="min-w-36">
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

    <!-- Extended Fields Section -->
    <div class="border-t pt-6 space-y-6">
      <h3 class="text-lg font-semibold text-muted-foreground">
        {{ $t('gear.item.extendedFields') }}
      </h3>

      <!-- Price and Brand -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField v-slot="{ componentField }" name="price">
          <FormItem>
            <FormLabel :label="$t('gear.item.price')" />
            <Input
              v-bind="componentField"
              type="number"
              :placeholder="$t('gear.item.price')"
              min="0"
              step="0.01"
            />
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ value, handleChange }" name="brand">
          <FormItem>
            <FormLabel :label="$t('gear.item.brand')" />
            <ComboBox
              :value="value"
              :options="getBrandOptions()"
              :placeholder="''"
              :creatable="true"
              :create-label="$t('gear.comboBox.add')"
              class="w-full"
              @update:value="handleChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

      <!-- URL -->
      <FormField v-slot="{ componentField }" name="url">
        <FormItem>
          <FormLabel :label="$t('gear.item.url')" />
          <Input
            v-bind="componentField"
            type="url"
            :placeholder="$t('gear.item.url')"
          />
          <FormMessage />
        </FormItem>
      </FormField>

      <!-- Color and Quality -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField v-slot="{ value, handleChange }" name="color">
          <FormItem>
            <FormLabel :label="$t('gear.item.color')" />
            <ColorAutocomplete
              :value="value"
              class="w-full"
              @update:value="handleChange"
            />
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ value, handleChange }" name="quality">
          <FormItem>
            <FormLabel :label="$t('gear.item.quality')" />
            <Select :model-value="value" @update:model-value="handleChange">
              <SelectTrigger class="w-full min-w-36">
                <SelectValue :placeholder="$t('gear.item.quality')" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">
                  {{ $t('gear.item.qualities.low') }}
                </SelectItem>
                <SelectItem value="medium">
                  {{ $t('gear.item.qualities.medium') }}
                </SelectItem>
                <SelectItem value="high">
                  {{ $t('gear.item.qualities.high') }}
                </SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        </FormField>
      </div>
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

