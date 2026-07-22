<script setup lang="ts">
import { refDebounced } from '@vueuse/core'
import { BackpackIcon, BookIcon, Globe, Info, Package, Search, ShoppingCart } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import SidebarMenuContainerItem from '@/components/layout/SidebarMenuContainerItem.vue'
import { Input } from '@/components/ui/input'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarSeparator,
} from '@/components/ui/sidebar'
import { useGearV2 } from '@/modules/gear/composables/useGearV2'
import { GearRoutePath } from '@/modules/gear/routes'
import { PublicRoutePaths } from '@/router/publicRoutes'
import type { IGearItemV2 } from '@/modules/gear/types/gear.types.v2'

const { t } = useI18n()
// Load containers through the active V2 service (API or localStorage) into the store
const { rootContainers: rootContainersV2, getItems } = useGearV2()
onMounted(() => {
  getItems({ itemType: 'container' }).catch(() => {})
})

// Linki: Mój sprzęt
const myGearLinks = computed(() => [
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
])

// Linki: Publiczne
const publicLinks = computed(() => [
  {
    to: GearRoutePath.PublicContainers,
    label: t('gear.publicContainers.navTitle', 'Public Browser'),
    icon: Globe,
  },
  {
    to: GearRoutePath.CatalogueBrowser,
    label: t('gear.catalogue.navTitle', 'Catalogue'),
    icon: BookIcon,
  },
])

// Root kontenery posortowane: ulubione + alfabetycznie
const rootContainers = computed<IGearItemV2[]>(() => {
  // Sortowanie: najpierw ulubione, potem alfabetycznie
  return [...rootContainersV2.value].sort((a, b) => {
    // Najpierw ulubione
    if (a.favorite && !b.favorite) return -1
    if (!a.favorite && b.favorite) return 1
    // Potem alfabetycznie
    return a.name.localeCompare(b.name)
  })
})

const duplicateContainerNames = computed<Set<string>>(() => {
  const counts = new Map<string, number>()
  for (const container of rootContainers.value) {
    counts.set(container.name, (counts.get(container.name) ?? 0) + 1)
  }
  return new Set(
    [...counts.entries()]
      .filter(([, count]) => count > 1)
      .map(([name]) => name),
  )
})

const containerSearch = ref<string>('')
const containerSearchDebounced = refDebounced(containerSearch, 250)

const favoriteContainers = computed<IGearItemV2[]>(() => {
  return rootContainers.value.filter(container => container.favorite)
})

const filteredContainers = computed<IGearItemV2[]>(() => {
  const query = containerSearchDebounced.value.trim().toLowerCase()
  let list = rootContainers.value

  if (showFavoritesSection.value) {
    const favoriteIds = new Set(favoriteContainers.value.map(container => container.id))
    list = list.filter(container => !favoriteIds.has(container.id))
  }

  if (!query) {
    return list
  }
  return list.filter(container => container.name.toLowerCase().includes(query))
})

const showFavoritesSection = computed<boolean>(() => {
  return favoriteContainers.value.length > 0 && !containerSearchDebounced.value.trim()
})
</script>

<template>
  <Sidebar collapsible="icon">
    <SidebarContent class="overflow-x-hidden max-h-[90vh] overflow-y-auto">
      <!-- Sekcja: Mój sprzęt -->
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('navigation.myGear', 'My Gear') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="link in myGearLinks" :key="link.to">
              <RouterLink v-slot="{ href, navigate, isActive }" :to="link.to" custom>
                <SidebarMenuButton
                  :is-active="isActive"
                  as="a"
                  :href="href"
                  @click="navigate"
                >
                  <component :is="link.icon" />
                  <span>{{ link.label }}</span>
                </SidebarMenuButton>
              </RouterLink>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- Separator -->
      <SidebarSeparator class="group-data-[collapsible=icon]:w-auto!" />

      <!-- Sekcja: Publiczne -->
      <SidebarGroup>
        <SidebarGroupLabel>{{ t('navigation.public', 'Public') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="link in publicLinks" :key="link.to">
              <RouterLink v-slot="{ href, navigate, isActive }" :to="link.to" custom>
                <SidebarMenuButton
                  :is-active="isActive"
                  as="a"
                  :href="href"
                  @click="navigate"
                >
                  <component :is="link.icon" />
                  <span>{{ link.label }}</span>
                </SidebarMenuButton>
              </RouterLink>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- Separator -->
      <SidebarSeparator class="group-data-[collapsible=icon]:w-auto!" />

      <!-- Sekcja: Lista kontenerów -->
      <SidebarGroup class="max-h-[70vh] overflow-y-auto">
        <SidebarGroupLabel>{{ t('gear.page.containers', 'Containers') }}</SidebarGroupLabel>
        <SidebarGroupContent>
          <div class="px-2 pb-2 group-data-[collapsible=icon]:hidden">
            <div class="relative">
              <Search class="absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                v-model="containerSearch"
                type="search"
                :placeholder="t('gear.sidebar.searchContainers')"
                class="h-8 pl-8"
                :aria-label="t('gear.sidebar.searchContainers')"
              />
            </div>
          </div>

          <SidebarMenu v-if="showFavoritesSection">
            <p class="px-2 pb-1 text-xs font-medium text-muted-foreground">
              {{ t('gear.sidebar.favorites') }}
            </p>
            <SidebarMenuContainerItem
              v-for="container in favoriteContainers"
              :key="`favorite-${container.id}`"
              :container="container"
              :show-disambiguator="duplicateContainerNames.has(container.name)"
            />
          </SidebarMenu>

          <SidebarMenu v-if="filteredContainers.length > 0">
            <SidebarMenuContainerItem
              v-for="container in filteredContainers"
              :key="container.id"
              :container="container"
              :show-disambiguator="duplicateContainerNames.has(container.name)"
            />
          </SidebarMenu>

          <p
            v-else-if="containerSearchDebounced.trim()"
            class="px-4 py-2 text-sm text-muted-foreground"
          >
            {{ t('gear.sidebar.noContainersFound') }}
          </p>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter>
      <SidebarMenu>
        <SidebarMenuItem>
          <RouterLink v-slot="{ href, navigate, isActive }" :to="PublicRoutePaths.about" custom>
            <SidebarMenuButton
              :is-active="isActive"
              as="a"
              :href="href"
              @click="navigate"
            >
              <Info class="size-4" />
              <span>{{ t('common.pages.about', 'About') }}</span>
            </SidebarMenuButton>
          </RouterLink>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>

    <SidebarRail />
  </Sidebar>
</template>

