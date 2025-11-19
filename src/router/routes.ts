import { authRoutes } from '@/modules/auth/config/routes'
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
  {
    path: '/cookies',
    name: 'cookies',
    component: () => import('@/pages/CookiesPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: () => import('@/pages/PrivacyPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('@/pages/ContactPage.vue'),
    meta: { layout: 'authenticated' },
  },
  ...authRoutes,
  ...gearRoutes,
  ...settingsRoutes,
  ...userRoutes,
]
