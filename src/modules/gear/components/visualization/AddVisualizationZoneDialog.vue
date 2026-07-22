<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'
import type { IVisualizationCustomZone } from '../../types/gearSettings.types'
import { useGearSettings } from '../../composables/useGearSettings'
import { getZoneIcon, type TZoneIconKey, ZONE_ICON_KEYS } from '../../utils/visualizationZones'

const { zone } = defineProps<{
  zone?: IVisualizationCustomZone | null
}>()

const open = defineModel<boolean>('open', { required: true })

const { t } = useI18n()
const { addVisualizationZone, updateVisualizationZone } = useGearSettings()

const name = ref('')
const iconKey = ref<TZoneIconKey>('tent')

const isEditMode = computed<boolean>(() => zone != null)
const canSave = computed<boolean>(() => name.value.trim().length > 0)

watch(() => open.value, (isOpen) => {
  if (!isOpen) return
  name.value = zone?.name ?? ''
  iconKey.value = (zone?.iconKey as TZoneIconKey) ?? 'tent'
}, { immediate: true })

function handleSave(): void {
  if (!canSave.value) return

  const now = new Date().toISOString()

  if (isEditMode.value && zone) {
    updateVisualizationZone({ ...zone, name: name.value.trim(), iconKey: iconKey.value, updatedAt: now })
  } else {
    addVisualizationZone({
      id: crypto.randomUUID(),
      name: name.value.trim(),
      iconKey: iconKey.value,
      createdAt: now,
      updatedAt: now,
    })
  }

  open.value = false
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <DialogTitle>
          {{ isEditMode ? t('gear.visualization.zoneDialog.editTitle') : t('gear.visualization.zoneDialog.addTitle') }}
        </DialogTitle>
      </DialogHeader>

      <div class="space-y-4 py-2">
        <div class="space-y-2">
          <Label for="zoneName">
            {{ t('gear.visualization.zoneDialog.nameLabel') }}
          </Label>
          <Input
            id="zoneName"
            v-model="name"
            :placeholder="t('gear.visualization.zoneDialog.namePlaceholder')"
            @keyup.enter="handleSave"
          />
        </div>

        <div class="space-y-2">
          <Label>
            {{ t('gear.visualization.zoneDialog.iconLabel') }}
          </Label>
          <div class="grid grid-cols-6 gap-2">
            <button
              v-for="key in ZONE_ICON_KEYS"
              :key="key"
              type="button"
              :class="cn(
                'flex items-center justify-center rounded-md border p-2 transition-colors hover:bg-accent',
                iconKey === key ? 'border-primary bg-primary/10' : 'border-input',
              )"
              :aria-label="key"
              @click="iconKey = key"
            >
              <component :is="getZoneIcon(key)" class="size-5" />
            </button>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="open = false">
          {{ t('gear.actions.cancel') }}
        </Button>
        <Button :disabled="!canSave" @click="handleSave">
          {{ t('gear.actions.save') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
