<script setup lang="ts">
import { LayoutGrid, Package } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CommonPageHeader from '@/components/layout/CommonPageHeader.vue'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { useBackend } from '@/shared/composables/useBackend'
import type { IGearItemV2 } from '../types/gear.types.v2'
import VisualizationZone from '../components/visualization/VisualizationZone.vue'
import { useContainersWithChildren } from '../composables/useGearQueries'
import { useGearV2 } from '../composables/useGearV2'
import { ZONE_CONFIG, getVisualizationZone } from '../utils/visualizationZones'
import type { TVisualizationZone } from '../utils/visualizationZones'

const { t } = useI18n()
const { shouldUseAPI } = useBackend()
const { rootContainers: rootContainersFromStore } = useGearV2()

const { data: containersFromAPI, isLoading } = useContainersWithChildren({
  enabled: computed(() => shouldUseAPI.value),
})

const rootContainers = computed<IGearItemV2[]>(() => {
  if (shouldUseAPI.value) {
    return (containersFromAPI.value ?? []).filter(c => !c.parentItemId)
  }
  return rootContainersFromStore.value
})

const containersByZone = computed<Record<TVisualizationZone, IGearItemV2[]>>(() => {
  const result: Record<TVisualizationZone, IGearItemV2[]> = {
    body: [],
    carry: [],
    vehicle: [],
    home: [],
    other: [],
  }
  for (const container of rootContainers.value) {
    const zone = getVisualizationZone(container.containerType ?? 'other')
    result[zone].push(container)
  }
  return result
})

const hasAnyContainers = computed<boolean>(() => rootContainers.value.length > 0)

const visibleZones = computed(() =>
  ZONE_CONFIG.filter(z => z.id !== 'other' || containersByZone.value.other.length > 0)
)
</script>

<template>
  <AuthenticatedLayout>
    <CommonPageHeader
      :icon="LayoutGrid"
      :label="t('gear.visualization.title')"
      :description="t('gear.visualization.description')"
    />

    <div v-if="isLoading" class="flex items-center justify-center py-16">
      <div class="animate-spin size-8 rounded-full border-4 border-muted border-t-primary" />
    </div>

    <div v-else-if="!hasAnyContainers" class="flex flex-col items-center justify-center py-16 gap-4 text-muted-foreground">
      <Package class="size-12 opacity-40" />
      <p class="text-base">{{ t('gear.container.empty') }}</p>
      <p class="text-sm">{{ t('gear.container.emptyDescription') }}</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-8 sm:grid-cols-2 p-4">
      <VisualizationZone
        v-for="zoneConfig in visibleZones"
        :key="zoneConfig.id"
        :zone="zoneConfig.id"
        :containers="containersByZone[zoneConfig.id]"
      />
    </div>
  </AuthenticatedLayout>
</template>
