import { gearRoutes } from '@/modules/gear/routes'
import { settingsRoutes } from '@/modules/settings/routes'
import { userRoutes } from '@/modules/user/routes'
import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/HomePage.vue'),
    meta: { layout: 'authenticated' },
  },
  ...gearRoutes,
  ...settingsRoutes,
  ...userRoutes,
]
