<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import {
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'
import ContainerIcon from '@/modules/gear/components/ContainerIcon.vue'
import { useGearV2 } from '@/modules/gear/composables/useGearV2'
import { GearRoutePath } from '@/modules/gear/routes'
import type { IGearItemV2, TContainerColor, TGearContainerType } from '@/modules/gear/types/gear.types.v2'

const props = defineProps<{
  container: IGearItemV2
  showDisambiguator?: boolean
}>()

const route = useRoute()
const { t } = useI18n()
const { getChildrenFromStore } = useGearV2()

const iconType = computed<TGearContainerType>(() => props.container.containerType ?? 'backpack')
const iconColor = computed<TContainerColor | null>(() => (props.container.color ?? null) as TContainerColor | null)

const disambiguator = computed<string>(() => {
  const type = props.container.containerType ?? 'other'
  const typeLabel = t(`gear.container.types.${type}`)
  const itemCount = getChildrenFromStore(props.container.id).length
  return t('gear.sidebar.containerDisambiguator', { type: typeLabel, count: itemCount })
})

const linkLabel = computed<string>(() => {
  if (!props.showDisambiguator) {
    return props.container.name
  }
  return `${props.container.name} (${disambiguator.value})`
})

const isActive = (containerId: string): boolean => {
  return route.params.id === containerId || route.params.containerId === containerId
}
</script>

<template>
  <SidebarMenuItem>
    <SidebarMenuButton :is-active="isActive(container.id)" as-child>
      <RouterLink
        :to="GearRoutePath.ContainerDetailById(container.id)"
        :aria-label="linkLabel"
        :title="linkLabel"
      >
        <ContainerIcon :type="iconType" :color="iconColor" :size="4" />
        <span class="truncate">{{ container.name }}</span>
        <span
          v-if="showDisambiguator"
          class="truncate text-xs text-muted-foreground"
        >
          {{ disambiguator }}
        </span>
      </RouterLink>
    </SidebarMenuButton>
  </SidebarMenuItem>
</template>
