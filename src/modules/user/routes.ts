import type { RouteRecordRaw } from 'vue-router'

export const UserRoutePaths = {
  profile: import.meta.env.VITE_USER_PROFILE_PATH ?? '/profile',
  profileEdit: import.meta.env.VITE_USER_PROFILE_EDIT_PATH ?? '/profile/edit',
  publicUserProfile: import.meta.env.VITE_USER_PUBLIC_USER_PROFILE_PATH ?? '/users/:userId/public',
} as const

export const UserRouteNames = {
  profile: 'profile',
  profileEdit: 'profileEdit',
  publicUserProfile: 'publicUserProfile',
} as const

export const userRoutes: RouteRecordRaw[] = [
  {
    path: UserRoutePaths.profile,
    name: UserRouteNames.profile,
    component: () => import('@/modules/user/pages/ProfileViewPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: UserRoutePaths.profileEdit,
    name: UserRouteNames.profileEdit,
    component: () => import('@/modules/user/pages/ProfileEditPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: UserRoutePaths.publicUserProfile,
    name: UserRouteNames.publicUserProfile,
    component: () => import('@/modules/user/pages/PublicUserProfilePage.vue'),
    meta: { layout: 'authenticated' },
  },
]

