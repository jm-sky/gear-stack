/**
 * Billing module routes
 */

import type { RouteRecordRaw } from 'vue-router'

export const billingRoutes: RouteRecordRaw[] = [
  {
    path: '/billing',
    name: 'billing',
    component: () => import('./pages/BillingPage.vue'),
    meta: {
      layout: 'authenticated',
      requiresAuth: true,
    },
  },
  {
    path: '/billing/success',
    name: 'billing-success',
    component: () => import('./pages/BillingSuccessPage.vue'),
    meta: {
      layout: 'authenticated',
      requiresAuth: true,
    },
  },
]

export const BillingRoutePath = {
  billing: () => '/billing',
  success: () => '/billing/success',
}
