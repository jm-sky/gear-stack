import type { RouteRecordRaw } from 'vue-router'

export const AdminRoutePaths = {
  dashboard: '/admin',
  users: '/admin/users',
  containers: '/admin/containers',
  items: '/admin/items',
  limits: '/admin/limits',
}

export const AdminRouteNames = {
  dashboard: 'admin-dashboard',
  users: 'admin-users',
  containers: 'admin-containers',
  items: 'admin-items',
  limits: 'admin-limits',
}

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: AdminRoutePaths.dashboard,
    name: AdminRouteNames.dashboard,
    component: () => import('@/modules/admin/pages/AdminDashboardPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, requiresAdmin: true, title: 'admin.dashboard.title' },
  },
  {
    path: AdminRoutePaths.users,
    name: AdminRouteNames.users,
    component: () => import('@/modules/admin/pages/AdminUsersPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, requiresAdmin: true, title: 'admin.users.title' },
  },
  {
    path: AdminRoutePaths.containers,
    name: AdminRouteNames.containers,
    component: () => import('@/modules/admin/pages/AdminContainersPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, requiresAdmin: true, title: 'admin.containers.title' },
  },
  {
    path: AdminRoutePaths.items,
    name: AdminRouteNames.items,
    component: () => import('@/modules/admin/pages/AdminItemsPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, requiresAdmin: true, title: 'admin.items.title' },
  },
  {
    path: AdminRoutePaths.limits,
    name: AdminRouteNames.limits,
    component: () => import('@/modules/admin/pages/AdminLimitsPage.vue'),
    meta: { layout: 'authenticated', requiresAuth: true, requiresAdmin: true, title: 'admin.limits.title' },
  },
]
