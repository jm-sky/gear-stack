<script setup lang="ts">
import { BackpackIcon, Globe, Package, ShoppingCart } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import SidebarMenuContainerItem from '@/components/layout/SidebarMenuContainerItem.vue'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarSeparator,
} from '@/components/ui/sidebar'
import { useGear } from '@/modules/gear/composables/useGear'
import { GearRoutePath } from '@/modules/gear/routes'
import { getRootContainers } from '@/modules/gear/utils/containerNesting'
import type { IGearContainer } from '@/modules/gear/types/gear.types'

const { t } = useI18n()
const route = useRoute()
const { containers } = useGear()

// Główne linki nawigacyjne
const navLinks = computed(() => [
  {
    to: GearRoutePath.Containers,
    label: t('gear.page.title', 'Gear'),
    icon: BackpackIcon,
  },
  {
    to: GearRoutePath.AllItems,
    label: t('gear.allItems.navTitle', 'All Items'),
    icon: Package,
  },
  {
    to: GearRoutePath.ShoppingPlanning,
    label: t('gear.shopping.navTitle', 'Shopping'),
    icon: ShoppingCart,
  },
  {
    to: GearRoutePath.PublicContainers,
    label: t('gear.publicContainers.navTitle', 'Public Browser'),
    icon: Globe,
  },
])

// Root kontenery posortowane: ulubione + alfabetycznie
const rootContainers = computed<IGearContainer[]>(() => {
  const allContainers = containers.value
  const roots = getRootContainers(allContainers)

  // Sortowanie: najpierw ulubione, potem alfabetycznie
  return [...roots].sort((a, b) => {
    // Najpierw ulubione
    if (a.favorite && !b.favorite) return -1
    if (!a.favorite && b.favorite) return 1
    // Potem alfabetycznie
    return a.name.localeCompare(b.name)
  })
})

// Sprawdzanie czy link jest aktywny
const isLinkActive = (path: string): boolean => {
  return route.path === path || route.path.startsWith(path + '/')
}

</script>

<template>
  <Sidebar collapsible="icon">
    <SidebarContent>
      <!-- Sekcja: Główne linki nawigacyjne -->
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('navigation.main', 'Navigation') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="link in navLinks" :key="link.to">
              <SidebarMenuButton :is-active="isLinkActive(link.to)" as-child>
                <RouterLink :to="link.to">
                  <component :is="link.icon" />
                  <span>{{ link.label }}</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- Separator -->
      <SidebarSeparator class="group-data-[collapsible=icon]:w-auto!" />

      <!-- Sekcja: Lista kontenerów -->
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('gear.page.containers', 'Containers') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu v-if="rootContainers.length > 0">
            <SidebarMenuContainerItem
              v-for="container in rootContainers"
              :key="container.id"
              :container="container"
            />
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarRail />
  </Sidebar>
</template>

