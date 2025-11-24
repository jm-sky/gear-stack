import type { RouteRecordRaw } from 'vue-router'

export const GearRouteName = {
  Containers: 'gear-containers',
  AllItems: 'gear-all-items',
  ShoppingPlanning: 'gear-shopping-planning',
  ContainerNew: 'gear-container-new',
  ContainerDetail: 'gear-container-detail',
  ContainerEdit: 'gear-container-edit',
  ItemNew: 'gear-item-new',
  ItemEdit: 'gear-item-edit',
  PublicContainers: 'gear-public-containers',
  PublicContainerDetail: 'gear-public-container-detail',
}

export const GearRoutePath = {
  Containers: '/gear',
  AllItems: '/gear/items',
  ShoppingPlanning: '/gear/shopping',
  ContainerNew: '/gear/new',
  ContainerDetail: '/gear/:id',
  ContainerDetailById: (id: string) => `/gear/${id}`,
  ContainerEdit: '/gear/:id/edit',
  ContainerEditById: (id: string) => `/gear/${id}/edit`,
  ItemNew: '/gear/:containerId/items/new',
  ItemEdit: '/gear/:containerId/items/:itemId/edit',
  ItemEditById: (containerId: string, itemId: string) => `/gear/${containerId}/items/${itemId}/edit`,
  PublicContainers: '/gear/public',
  PublicContainerDetail: '/gear/public/:id',
  PublicContainerDetailById: (id: string) => `/gear/public/${id}`,
}

export const gearRoutes: RouteRecordRaw[] = [
  {
    path: GearRoutePath.Containers,
    name: GearRouteName.Containers,
    component: () => import('@/modules/gear/pages/ContainersListPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: GearRoutePath.AllItems,
    name: GearRouteName.AllItems,
    component: () => import('@/modules/gear/pages/AllItemsPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: GearRoutePath.ShoppingPlanning,
    name: GearRouteName.ShoppingPlanning,
    component: () => import('@/modules/gear/pages/ShoppingPlanningPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: GearRoutePath.ContainerNew,
    name: GearRouteName.ContainerNew,
    component: () => import('@/modules/gear/pages/ContainerFormPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: GearRoutePath.ContainerDetail,
    name: GearRouteName.ContainerDetail,
    component: () => import('@/modules/gear/pages/ContainerDetailPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: GearRoutePath.ContainerEdit,
    name: GearRouteName.ContainerEdit,
    component: () => import('@/modules/gear/pages/ContainerFormPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: GearRoutePath.ItemNew,
    name: GearRouteName.ItemNew,
    component: () => import('@/modules/gear/pages/ItemFormPage.vue'),
    meta: { layout: 'authenticated' },
  },
  // TODO: Implement ItemDetailPage
  // {
  //   path: '/gear/:containerId/items/:itemId',
  //   name: 'gear-item-detail',
  //   component: () => import('@/modules/gear/pages/ItemDetailPage.vue'),
  //   meta: { layout: 'authenticated' },
  // },
  {
    path: GearRoutePath.ItemEdit,
    name: GearRouteName.ItemEdit,
    component: () => import('@/modules/gear/pages/ItemFormPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: GearRoutePath.PublicContainers,
    name: GearRouteName.PublicContainers,
    component: () => import('@/modules/gear/pages/PublicContainersBrowserPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: GearRoutePath.PublicContainerDetail,
    name: GearRouteName.PublicContainerDetail,
    component: () => import('@/modules/gear/pages/PublicContainerDetailPage.vue'),
    meta: { layout: 'authenticated' },
  },
]

