<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'
import type { IGearItemV2 } from '../../types/gear.types.v2'
import type { TVisualizationZone } from '../../utils/visualizationZones'
import VisualizationContainerCard from './VisualizationContainerCard.vue'

const BodySilhouette = defineAsyncComponent(() => import('./BodySilhouette.vue'))
const BackpackSilhouette = defineAsyncComponent(() => import('./BackpackSilhouette.vue'))
const CarSilhouette = defineAsyncComponent(() => import('./CarSilhouette.vue'))
const CabinetSilhouette = defineAsyncComponent(() => import('./CabinetSilhouette.vue'))

const { zone, containers } = defineProps<{
  zone: TVisualizationZone
  containers: IGearItemV2[]
}>()

const { t } = useI18n()

const silhouette = computed(() => {
  if (zone === 'body') return BodySilhouette
  if (zone === 'carry') return BackpackSilhouette
  if (zone === 'vehicle') return CarSilhouette
  if (zone === 'home') return CabinetSilhouette
  return null
})

const labelKey = computed<string>(() => `gear.visualization.zones.${zone}`)
</script>

<template>
  <div class="flex flex-col gap-3">
    <h2 class="text-base font-semibold text-foreground">
      {{ t(labelKey) }}
    </h2>
    <div class="flex flex-row gap-5 items-start">
      <div class="w-20 shrink-0 text-muted-foreground/50">
        <component :is="silhouette" v-if="silhouette" />
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
