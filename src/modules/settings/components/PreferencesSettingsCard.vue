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
import { useDarkMode } from '@/shared/composables/useDarkMode'
import { type SupportedLocale, useLocale } from '@/shared/i18n'
import { useSettings } from '../composables/useSettings'
import type { TGearWeightUnit } from '@/modules/gear/types/gear.types'

const { t } = useI18n()
const { currentLocale } = useLocale()
const { isDark, toggle: toggleDarkMode } = useDarkMode()
const { settings, updateSettings } = useSettings()

const settingsSchema = z.object({
  darkMode: z.enum(['light', 'dark']),
  locale: z.enum(['en', 'pl']),
  preferredWeightUnit: z.enum(['g', 'kg']),
})

const getThemeValue = (darkMode: boolean | undefined) => {
  return darkMode ? 'dark' : 'light'
}

const { handleSubmit, setValues } = useForm({
  validationSchema: toTypedSchema(settingsSchema),
  initialValues: {
    darkMode: getThemeValue(settings.value.darkMode),
    locale: settings.value.locale ?? currentLocale.value,
    preferredWeightUnit: settings.value.preferredWeightUnit ?? 'g',
  },
})

watch(() => settings.value, (val) => {
  if (val) {
    setValues({ 
      darkMode: getThemeValue(val.darkMode), 
      locale: val.locale,
      preferredWeightUnit: val.preferredWeightUnit ?? 'g',
    })
  }
}, { immediate: true })

watch(() => currentLocale.value, (val: SupportedLocale) => {
  setValues({ locale: val })
}, { immediate: true })

watch(() => isDark.value, (val: boolean) => {
  setValues({ darkMode: getThemeValue(val) })
}, { immediate: true })

const onSubmit = handleSubmit(async (values) => {
  updateSettings({
    darkMode: values.darkMode === 'dark',
    locale: values.locale,
    preferredWeightUnit: values.preferredWeightUnit as TGearWeightUnit,
  })
  
  // Sync with composables
  if (isDark.value !== (values.darkMode === 'dark')) {
    toggleDarkMode()
  }
  const { setLocale } = useLocale()
  setLocale(values.locale)
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
      <form class="space-y-6" @submit="onSubmit">
        <div class="grid gap-6 md:grid-cols-2">
          <!-- Theme -->
          <div class="space-y-3">
            <FormField v-slot="{ componentField }" name="darkMode">
              <FormItem>
                <FormLabel required>
                  {{ t('settings.preferences.theme.label') }}
                </FormLabel>
                <p class="text-sm text-muted-foreground">
                  {{ t('settings.preferences.theme.subtitle') }}
                </p>
                <FormControl>
                  <Select v-bind="componentField">
                    <SelectTrigger>
                      <SelectValue :placeholder="t('settings.preferences.theme.placeholder')" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">
                        {{ t('settings.preferences.theme.options.light') }}
                      </SelectItem>
                      <SelectItem value="dark">
                        {{ t('settings.preferences.theme.options.dark') }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
          </div>

          <!-- Locale -->
          <div class="space-y-3">
            <FormField v-slot="{ componentField }" name="locale">
              <FormItem>
                <FormLabel required>
                  {{ t('settings.preferences.locale.label') }}
                </FormLabel>
                <p class="text-sm text-muted-foreground">
                  {{ t('settings.preferences.locale.subtitle') }}
                </p>
                <FormControl>
                  <Select v-bind="componentField">
                    <SelectTrigger>
                      <SelectValue :placeholder="t('settings.preferences.locale.placeholder')" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">
                        {{ t('settings.preferences.locale.options.en') }}
                      </SelectItem>
                      <SelectItem value="pl">
                        {{ t('settings.preferences.locale.options.pl') }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
          </div>

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

