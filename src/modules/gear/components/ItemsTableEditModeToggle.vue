<script setup lang="ts">
import { Pencil } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import Label from '@/components/ui/label/Label.vue'
import Switch from '@/components/ui/switch/Switch.vue'
import { config } from '@/shared/config/config'
import { useItemsTableEditMode } from '../composables/useItemsTableEditMode'

const { t } = useI18n()
const { editMode } = useItemsTableEditMode()
</script>

<template>
  <div
    v-if="config.features.inlineEditing.enabled"
    v-tooltip.bottom="editMode ? t('gear.actions.disableInlineEditing') : t('gear.actions.enableInlineEditing')"
    class="flex shrink-0 items-center gap-2 px-1"
  >
    <Pencil
      class="size-4 text-muted-foreground sm:hidden"
      aria-hidden="true"
    />
    <Label
      for="items-table-edit-mode"
      class="hidden cursor-pointer text-sm sm:inline"
    >
      {{ editMode ? t('gear.actions.disableInlineEditing') : t('gear.actions.enableInlineEditing') }}
    </Label>
    <Switch
      id="items-table-edit-mode"
      v-model="editMode"
      :aria-label="editMode ? t('gear.actions.disableInlineEditing') : t('gear.actions.enableInlineEditing')"
    />
  </div>
</template>
