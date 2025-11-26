<!--
  AI Context Configuration Component
  Allows user to configure which fields to send to AI
-->
<script setup lang="ts">
import { computed } from 'vue'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { useAiContext } from '../composables/useAiContext'

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
    <div class="space-y-2">
      <Label class="text-sm font-medium">Context Fields</Label>
      <p class="text-xs text-muted-foreground">
        Select which fields to include when sending data to AI
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

