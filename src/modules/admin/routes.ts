import type { RouteRecordRaw } from 'vue-router'

export const AdminRoutePaths = {
  dashboard: '/admin',
  users: '/admin/users',
  containers: '/admin/containers',
  items: '/admin/items',
}

export const AdminRouteNames = {
  dashboard: 'admin-dashboard',
  users: 'admin-users',
  containers: 'admin-containers',
  items: 'admin-items',
}

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: AdminRoutePaths.dashboard,
    name: AdminRouteNames.dashboard,
    component: () => import('@/modules/admin/pages/AdminDashboardPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, requiresAdmin: true },
  },
  {
    path: AdminRoutePaths.users,
    name: AdminRouteNames.users,
    component: () => import('@/modules/admin/pages/AdminUsersPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, requiresAdmin: true },
  },
  {
    path: AdminRoutePaths.containers,
    name: AdminRouteNames.containers,
    component: () => import('@/modules/admin/pages/AdminContainersPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, requiresAdmin: true },
  },
  {
    path: AdminRoutePaths.items,
    name: AdminRouteNames.items,
    component: () => import('@/modules/admin/pages/AdminItemsPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, requiresAdmin: true },
  },
]
