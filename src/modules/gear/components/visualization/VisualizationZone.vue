<script setup lang="ts">
import { MoreVertical } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import type { IGearItemV2 } from '../../types/gear.types.v2'
import type { IVisualizationCustomZone } from '../../types/gearSettings.types'
import { useGearSettings } from '../../composables/useGearSettings'
import { getActionIcon } from '../../utils/actionIcons'
import AddVisualizationZoneDialog from './AddVisualizationZoneDialog.vue'
import VisualizationContainerCard from './VisualizationContainerCard.vue'
import type { Component } from 'vue'

const { zoneId, label, icon, containers, customZone } = defineProps<{
  zoneId: string
  label: string
  icon: Component
  containers: IGearItemV2[]
  customZone?: IVisualizationCustomZone | null
}>()

const emit = defineEmits<{
  drop: [containerId: string, zoneId: string]
}>()

const { t } = useI18n()
const { removeVisualizationZone } = useGearSettings()

const EditIcon = getActionIcon('edit')
const DeleteIcon = getActionIcon('delete')

const isDragOver = ref(false)
const isEditDialogOpen = ref(false)

const isCustom = computed<boolean>(() => customZone != null)

function handleDragOver(event: DragEvent): void {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
  isDragOver.value = true
}

function handleDragLeave(): void {
  isDragOver.value = false
}

function handleDrop(event: DragEvent): void {
  event.preventDefault()
  isDragOver.value = false
  const containerId = event.dataTransfer?.getData('text/plain')
  if (containerId) {
    emit('drop', containerId, zoneId)
  }
}

function handleEdit(): void {
  isEditDialogOpen.value = true
}

function handleDelete(): void {
  if (!customZone) return
  if (!confirm(t('gear.visualization.confirmDeleteZone'))) return
  removeVisualizationZone(customZone.id)
}
</script>

<template>
  <div
    class="flex flex-col gap-3 rounded-lg p-2 transition-colors"
    :class="isDragOver ? 'bg-accent/50 ring-2 ring-primary ring-offset-2' : ''"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <div class="flex items-center justify-between">
      <h2 class="text-base font-semibold text-foreground">
        {{ label }}
      </h2>

      <DropdownMenu v-if="isCustom">
        <DropdownMenuTrigger as-child>
          <Button
            v-tooltip.bottom="t('gear.actions.moreActions')"
            variant="ghost"
            size="sm"
            class="size-8 p-0"
            :aria-label="t('gear.actions.moreActions')"
          >
            <MoreVertical class="size-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem @click="handleEdit">
            <EditIcon class="size-4" />
            {{ t('gear.actions.edit') }}
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            class="text-destructive hover:text-destructive! hover:bg-destructive/4!"
            @click="handleDelete"
          >
            <DeleteIcon class="size-4" />
            {{ t('gear.actions.delete') }}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>

    <div class="flex flex-row gap-5 items-start">
      <div class="w-20 h-24 shrink-0 flex items-center justify-center text-muted-foreground/40">
        <component :is="icon" class="size-16" />
      </div>
      <div class="flex flex-col gap-2 flex-1 min-w-0">
        <VisualizationContainerCard
          v-for="container in containers"
          :key="container.id"
          :container="container"
        />
        <p
          v-if="containers.length === 0"
          class="text-sm text-muted-foreground py-3 italic"
        >
          {{ t('gear.visualization.zoneEmpty') }}
        </p>
      </div>
    </div>

    <AddVisualizationZoneDialog
      v-if="customZone"
      v-model:open="isEditDialogOpen"
      :zone="customZone"
    />
  </div>
</template>
