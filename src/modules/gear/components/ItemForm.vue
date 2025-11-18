<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useFocus } from '@vueuse/core'
import { useForm } from 'vee-validate'
import { nextTick, ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Form, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { ICreateItemDto, IGearItem, IUpdateItemDto } from '../types/gear.types'
import { getDefaultItemValues } from '../utils/defaultValues'
import { type ItemFormData, itemSchema } from '../utils/validation'
import CategoryIcon from './CategoryIcon.vue'

const props = defineProps<{
  item?: IGearItem
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [data: ICreateItemDto | IUpdateItemDto]
  cancel: []
}>()

const getInitialValues = (): ItemFormData => {
  if (props.item) {
    return {
      name: props.item.name,
      category: props.item.category,
      quantity: props.item.quantity,
      weight: props.item.weight,
      weightUnit: props.item.weightUnit,
      notes: props.item.notes ?? '',
      expirationDate: props.item.expirationDate ?? '',
      priority: props.item.priority,
      status: props.item.status,
    }
  }
  return {
    ...getDefaultItemValues(),
  }
}

// Form validation
const form = useForm({
  validationSchema: toTypedSchema(itemSchema),
  initialValues: getInitialValues(),
})

const nameInputRef = ref<HTMLInputElement | undefined>(undefined)
nextTick(() => {
  useFocus(nameInputRef)
})

const handleSubmit = form.handleSubmit((values) => {
  emit('submit', values as ICreateItemDto | IUpdateItemDto)
})

const handleCancel = () => {
  emit('cancel')
}
</script>

<template>
  <Form :handle-submit="handleSubmit">
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
            <SelectTrigger class="min-w-36">
              <SelectValue :placeholder="$t('gear.item.category')" />
            </SelectTrigger>
            <SelectContent>
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
              <SelectItem value="other">
                <div class="flex items-center gap-2">
                  <CategoryIcon category="other" :size="16" />
                  <span>{{ $t('gear.item.categories.other') }}</span>
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      </FormField>

      <!-- Quantity and Weight -->
      <div class="grid grid-cols-2 gap-4">
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
      </div>

      <!-- Priority and Status -->
      <div class="grid grid-cols-2 gap-4">
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
      <div class="flex justify-end gap-3">
        <Button type="button" variant="outline" @click="handleCancel">
          {{ $t('gear.actions.cancel') }}
        </Button>
        <Button type="submit" :loading="loading">
          {{ $t('gear.actions.save') }}
        </Button>
      </div>
    </div>
  </Form>
</template>

