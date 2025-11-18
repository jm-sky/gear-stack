export const dashboardRoutes = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    meta: { requiresAuth: true },
    component: () => import('@/modules/dashboard/pages/DashboardPage.vue'),
  },
]
