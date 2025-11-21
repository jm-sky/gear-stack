import type { RouteRecordRaw } from 'vue-router'

export const GearRouteName = {
  Containers: 'gear-containers',
  AllItems: 'gear-all-items',
  ContainerNew: 'gear-container-new',
  ContainerDetail: 'gear-container-detail',
  ContainerEdit: 'gear-container-edit',
  ItemNew: 'gear-item-new',
  ItemEdit: 'gear-item-edit',
}

export const GearRoutePath = {
  Containers: '/gear',
  AllItems: '/gear/items',
  ContainerNew: '/gear/new',
  ContainerDetail: '/gear/:id',
  ContainerEdit: '/gear/:id/edit',
  ItemNew: '/gear/:containerId/items/new',
  ItemEdit: '/gear/:containerId/items/:itemId/edit',
}

export const gearRoutes: RouteRecordRaw[] = [
  {
    path: GearRoutePath.Containers,
    name: GearRouteName.Containers,
    component: () => import('@/modules/gear/pages/ContainersListPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true },
  },
  {
    path: GearRoutePath.AllItems,
    name: GearRouteName.AllItems,
    component: () => import('@/modules/gear/pages/AllItemsPage.vue'),
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
]

