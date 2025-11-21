import { createRouter, createWebHistory } from 'vue-router'
import { protectRoutes } from '@/modules/auth/guards/authGuard'
import { routes } from './routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Install auth guard (only active when backend is enabled)
protectRoutes(router)

export default router
