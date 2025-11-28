<!--
  AI Context Configuration Component
  Allows user to configure which fields to send to AI
-->
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { usePermissions } from '@/shared/composables/usePermissions'
import { useAiContext } from '../composables/useAiContext'
import AiPremiumFeatureAlert from './AiPremiumFeatureAlert.vue'

const { t } = useI18n()

const { canUsePremiumFeatures } = usePermissions()
const { selectedFields, availableFields, toggleField } = useAiContext()

const isFieldSelected = (field: string): boolean => {
  return selectedFields.value.includes(field)
}

const handleFieldToggle = (field: string): void => {
  toggleField(field)
}
</script>

<template>
  <div class="border-t p-4 space-y-3">
    <AiPremiumFeatureAlert v-if="!canUsePremiumFeatures" />

    <div class="space-y-2" :class="{ 'opacity-50 pointer-events-none': !canUsePremiumFeatures }">
      <Label class="text-sm font-medium">{{ t('ai.context.fields') }}</Label>
      <p class="text-xs text-muted-foreground">
        {{ t('ai.context.description') }}
      </p>
      <div class="grid grid-cols-2 gap-2 mt-2">
        <div
          v-for="field in availableFields"
          :key="field"
          class="flex items-center space-x-2"
        >
          <Checkbox
            :id="`field-${field}`"
            :model-value="isFieldSelected(field)"
            @update:model-value="handleFieldToggle(field)"
          />
          <Label
            :for="`field-${field}`"
            class="text-sm font-normal cursor-pointer capitalize"
          >
            {{ field }}
          </Label>
        </div>
      </div>
    </div>
  </div>
</template>

