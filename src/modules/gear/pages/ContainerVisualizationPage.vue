<script setup lang="ts">
import { LayoutGrid, Package } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import { Button } from '@/components/ui/button'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useBackend } from '@/shared/composables/useBackend'
import type { IGearItemV2 } from '../types/gear.types.v2'
import AddVisualizationZoneDialog from '../components/visualization/AddVisualizationZoneDialog.vue'
import VisualizationZone from '../components/visualization/VisualizationZone.vue'
import { useContainersWithChildren } from '../composables/useGearQueries'
import { useGearSettings } from '../composables/useGearSettings'
import { useGearV2 } from '../composables/useGearV2'
import { getActionIcon } from '../utils/actionIcons'
import { getDefaultZoneIcon, getZoneIcon, resolveZoneId, ZONE_CONFIG } from '../utils/visualizationZones'

const { t } = useI18n()
const { shouldUseAPI } = useBackend()
const { rootContainers: rootContainersFromStore } = useGearV2()
const { visualizationCustomZones, settings, setContainerZone } = useGearSettings()

const AddIcon = getActionIcon('create')
const isAddZoneDialogOpen = ref(false)

const { data: containersFromAPI, isLoading } = useContainersWithChildren({
  enabled: computed(() => shouldUseAPI.value),
})

const rootContainers = computed<IGearItemV2[]>(() => {
  if (shouldUseAPI.value) {
    return (containersFromAPI.value ?? []).filter(c => !c.parentItemId)
  }
  return rootContainersFromStore.value
})

interface IResolvedZone {
  id: string
  label: string
  icon: ReturnType<typeof getZoneIcon>
  customZoneId: string | null
}

const resolvedZones = computed<IResolvedZone[]>(() => [
  ...ZONE_CONFIG.map(zoneConfig => ({
    id: zoneConfig.id,
    label: t(zoneConfig.labelKey),
    icon: getDefaultZoneIcon(zoneConfig.id),
    customZoneId: null,
  })),
  ...visualizationCustomZones.value.map(zone => ({
    id: zone.id,
    label: zone.name,
    icon: getZoneIcon(zone.iconKey),
    customZoneId: zone.id,
  })),
])

const containersByZone = computed<Record<string, IGearItemV2[]>>(() => {
  const result: Record<string, IGearItemV2[]> = {}
  for (const zone of resolvedZones.value) {
    result[zone.id] = []
  }
  for (const container of rootContainers.value) {
    const zoneId = resolveZoneId(container, settings.value.visualizationPlacements)
    ;(result[zoneId] ??= []).push(container)
  }
  return result
})

const hasAnyContainers = computed<boolean>(() => rootContainers.value.length > 0)

const visibleZones = computed<IResolvedZone[]>(() =>
  resolvedZones.value.filter(z => z.id !== 'other' || (containersByZone.value.other?.length ?? 0) > 0)
)

function handleDrop(containerId: string, zoneId: string): void {
  setContainerZone(containerId, zoneId)
}
</script>

<template>
  <AuthenticatedLayout>
    <CommonPageHeader
      :icon="LayoutGrid"
      :label="t('gear.visualization.title')"
      :description="t('gear.visualization.description')"
    >
      <template #actions>
        <Button variant="outline" size="sm" @click="isAddZoneDialogOpen = true">
          <AddIcon class="size-4" />
          {{ t('gear.visualization.addZone') }}
        </Button>
      </template>
    </CommonPageHeader>

    <div v-if="isLoading" class="flex items-center justify-center py-16">
      <div class="animate-spin size-8 rounded-full border-4 border-muted border-t-primary" />
    </div>

    <div v-else-if="!hasAnyContainers" class="flex flex-col items-center justify-center py-16 gap-4 text-muted-foreground">
      <Package class="size-12 opacity-40" />
      <p class="text-base">
        {{ t('gear.container.empty') }}
      </p>
      <p class="text-sm">
        {{ t('gear.container.emptyDescription') }}
      </p>
    </div>

    <div v-else class="grid grid-cols-1 gap-8 sm:grid-cols-2 p-4">
      <VisualizationZone
        v-for="resolvedZone in visibleZones"
        :key="resolvedZone.id"
        :zone-id="resolvedZone.id"
        :label="resolvedZone.label"
        :icon="resolvedZone.icon"
        :containers="containersByZone[resolvedZone.id] ?? []"
        :custom-zone="visualizationCustomZones.find(z => z.id === resolvedZone.customZoneId) ?? null"
        @drop="handleDrop"
      />
    </div>

    <AddVisualizationZoneDialog v-model:open="isAddZoneDialogOpen" />
  </AuthenticatedLayout>
</template>
