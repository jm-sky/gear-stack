<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { Settings } from 'lucide-vue-next'
import { useForm } from 'vee-validate'
import { watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useGearSettings } from '@/modules/gear/composables/useGearSettings'
import { SUPPORTED_CURRENCIES } from '@/modules/gear/utils/currencyFormatter'
import { config } from '@/shared/config/config'
import type { TGearWeightUnit } from '@/modules/gear/types/gear.types'

const { t } = useI18n()

const settingsSchema = z.object({
  preferredWeightUnit: z.enum(['g', 'kg', 'oz', 'lb']), // TODO: Extract to file for one source of truth
  defaultCurrency: z.string().optional(),
})

const { settings, updateSettings, defaultCurrency } = useGearSettings()

const { handleSubmit, setValues } = useForm({
  validationSchema: toTypedSchema(settingsSchema),
  initialValues: {
    preferredWeightUnit: config.defaults.preferredWeightUnit,
    defaultCurrency: defaultCurrency.value,
  },
})

watch(() => settings.value, (val) => {
  if (val) {
    setValues({
      preferredWeightUnit: val.preferredWeightUnit ?? config.defaults.preferredWeightUnit,
      defaultCurrency: defaultCurrency.value,
    })
  }
}, { immediate: true })


const onSubmit = handleSubmit(async (values) => {
  updateSettings({
    preferredWeightUnit: values.preferredWeightUnit as TGearWeightUnit,
    defaultCurrency: values.defaultCurrency,
  })
})
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex items-center gap-2">
        <Settings :size="20" />
        <CardTitle>{{ t('settings.preferences.title') }}</CardTitle>
      </div>
      <CardDescription>
        {{ t('settings.preferences.description') }}
      </CardDescription>
    </CardHeader>
    <CardContent>
      <form class="space-y-2" @submit="onSubmit">
        <div class="grid gap-6 md:grid-cols-2">
          <!-- Preferred Weight Unit -->
          <div class="space-y-3">
            <FormField v-slot="{ componentField }" name="preferredWeightUnit">
              <FormItem>
                <FormLabel required>
                  {{ t('settings.preferences.preferredWeightUnit.label') }}
                </FormLabel>
                <p class="text-sm text-muted-foreground">
                  {{ t('settings.preferences.preferredWeightUnit.subtitle') }}
                </p>
                <FormControl>
                  <Select v-bind="componentField">
                    <SelectTrigger>
                      <SelectValue :placeholder="t('settings.preferences.preferredWeightUnit.placeholder')" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="g">
                        {{ t('settings.preferences.preferredWeightUnit.options.g') }}
                      </SelectItem>
                      <SelectItem value="kg">
                        {{ t('settings.preferences.preferredWeightUnit.options.kg') }}
                      </SelectItem>
                      <SelectItem value="oz">
                        {{ t('settings.preferences.preferredWeightUnit.options.oz') }}
                      </SelectItem>
                      <SelectItem value="lb">
                        {{ t('settings.preferences.preferredWeightUnit.options.lb') }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
          </div>

          <!-- Default Currency -->
          <div class="space-y-3">
            <FormField v-slot="{ componentField }" name="defaultCurrency">
              <FormItem>
                <FormLabel>
                  {{ t('settings.preferences.defaultCurrency.label') }}
                </FormLabel>
                <p class="text-sm text-muted-foreground">
                  {{ t('settings.preferences.defaultCurrency.subtitle') }}
                </p>
                <FormControl>
                  <Select v-bind="componentField">
                    <SelectTrigger>
                      <SelectValue :placeholder="t('settings.preferences.defaultCurrency.placeholder')" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem
                        v-for="curr in SUPPORTED_CURRENCIES"
                        :key="curr.value"
                        :value="curr.value"
                      >
                        {{ curr.label }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
          </div>
        </div>

        <div class="flex justify-end">
          <Button type="submit">
            {{ t('settings.preferences.save') }}
          </Button>
        </div>
      </form>
    </CardContent>
  </Card>
</template>

