import { createRouter, createWebHistory } from 'vue-router'
import { i18n } from '@/i18n'
import { protectAdminRoutes } from '@/modules/admin/guards/adminGuard'
import { protectRoutes } from '@/modules/auth/guards/authGuard'
import { config } from '@/shared/config/config'
import { routes } from './routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Install auth guard (only active when backend is enabled)
protectRoutes(router)
// Install admin guard (checks admin access after auth)
protectAdminRoutes(router)

// Set page title on route change
router.afterEach((to) => {
  if (typeof document === 'undefined') return

  const metaTitle = to.meta.title as string | undefined
  if (metaTitle) {
    // Use type assertion to handle union type compatibility
    const title = (i18n.global.t as (key: string) => string)(metaTitle)
    document.title = `${title} | ${config.app.name}`
  } else {
    document.title = config.app.name
  }
})

export default router
