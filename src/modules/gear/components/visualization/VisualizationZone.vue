<script setup lang="ts">
import { Backpack, Car, Package, PersonStanding, Warehouse } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Component } from 'vue'
import type { IGearItemV2 } from '../../types/gear.types.v2'
import type { TVisualizationZone } from '../../utils/visualizationZones'
import VisualizationContainerCard from './VisualizationContainerCard.vue'

const { zone, containers } = defineProps<{
  zone: TVisualizationZone
  containers: IGearItemV2[]
}>()

const { t } = useI18n()

const ZONE_ICONS: Record<TVisualizationZone, Component> = {
  body: PersonStanding,
  carry: Backpack,
  vehicle: Car,
  home: Warehouse,
  other: Package,
}

const ZoneIcon = computed<Component>(() => ZONE_ICONS[zone])
const labelKey = computed<string>(() => `gear.visualization.zones.${zone}`)
</script>

<template>
  <div class="flex flex-col gap-3">
    <h2 class="text-base font-semibold text-foreground">
      {{ t(labelKey) }}
    </h2>
    <div class="flex flex-row gap-5 items-start">
      <div class="w-20 h-24 shrink-0 flex items-center justify-center text-muted-foreground/40">
        <component :is="ZoneIcon" class="size-16" />
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
  </div>
</template>
