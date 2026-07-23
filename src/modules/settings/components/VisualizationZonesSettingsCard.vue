<script setup lang="ts">
import { Edit, InfoIcon, Plus, Trash2 } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AddVisualizationZoneDialog from '@/modules/gear/components/visualization/AddVisualizationZoneDialog.vue'
import { useGearSettings } from '@/modules/gear/composables/useGearSettings'
import { GearRoutePath } from '@/modules/gear/routes'
import { getZoneIcon } from '@/modules/gear/utils/visualizationZones'
import type { IVisualizationCustomZone } from '@/modules/gear/types/gearSettings.types'

const { t } = useI18n()
const { visualizationCustomZones, removeVisualizationZone } = useGearSettings()

const isDialogOpen = ref<boolean>(false)
const editingZone = ref<IVisualizationCustomZone | null>(null)

const handleAdd = (): void => {
  editingZone.value = null
  isDialogOpen.value = true
}

const handleEdit = (zone: IVisualizationCustomZone): void => {
  editingZone.value = zone
  isDialogOpen.value = true
}

const handleDelete = async (id: string): Promise<void> => {
  if (confirm(t('gear.visualization.confirmDeleteZone'))) {
    removeVisualizationZone(id)
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div class="space-y-1.5">
          <CardTitle>{{ t('settings.visualizationZones.title') }}</CardTitle>
          <CardDescription>
            {{ t('settings.visualizationZones.description') }}
          </CardDescription>
        </div>
        <Button
          variant="link"
          class="h-auto p-0 sm:shrink-0"
          as-child
        >
          <RouterLink :to="GearRoutePath.Visualization">
            {{ t('settings.visualizationZones.openVisualization') }}
          </RouterLink>
        </Button>
      </div>
    </CardHeader>
    <CardContent class="space-y-4">
      <Button
        type="button"
        @click="handleAdd"
      >
        <Plus class="size-4" />
        {{ t('settings.visualizationZones.add') }}
      </Button>

      <div
        v-if="visualizationCustomZones.length > 0"
        class="space-y-2"
      >
        <div
          v-for="zone in visualizationCustomZones"
          :key="zone.id"
          class="flex flex-col sm:flex-row sm:items-center justify-between p-3 border rounded-lg gap-3"
        >
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <component
              :is="getZoneIcon(zone.iconKey)"
              class="size-5 shrink-0 text-muted-foreground"
            />
            <div class="text-sm truncate">
              {{ zone.name }}
            </div>
          </div>
          <div class="flex gap-2 sm:shrink-0">
            <Button
              size="sm"
              variant="outline"
              @click="handleEdit(zone)"
            >
              <Edit class="size-4" />
            </Button>
            <Button
              size="sm"
              variant="destructive"
              @click="handleDelete(zone.id)"
            >
              <Trash2 class="size-4" />
            </Button>
          </div>
        </div>
      </div>
      <div
        v-else
        class="flex items-center justify-center gap-2 text-sm py-6 text-muted-foreground"
      >
        <InfoIcon class="size-4 inline" />
        {{ t('settings.visualizationZones.empty') }}
      </div>
    </CardContent>

    <AddVisualizationZoneDialog
      v-model:open="isDialogOpen"
      :zone="editingZone"
    />
  </Card>
</template>
