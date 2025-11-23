import type { RouteRecordRaw } from 'vue-router'

export const userRoutes: RouteRecordRaw[] = [
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/modules/user/pages/ProfileViewPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: '/profile/edit',
    name: 'profileEdit',
    component: () => import('@/modules/user/pages/ProfileEditPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: '/users/:userId/public',
    name: 'publicUserProfile',
    component: () => import('@/modules/user/pages/PublicUserProfilePage.vue'),
    meta: { layout: 'authenticated' },
  },
]

