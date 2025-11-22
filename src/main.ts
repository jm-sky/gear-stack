import './css/style.css'

import { VueQueryPlugin } from '@tanstack/vue-query'
import { QueryClient } from '@tanstack/vue-query'
import { vTooltip } from 'floating-vue'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import { i18n } from '@/i18n'
import App from './App.vue'
import router from './router'
import { config } from './shared/config/config'
import { loadRecaptchaScript } from './shared/utils/recaptcha'
import 'floating-vue/dist/style.css'

// Set page title from app config
if (typeof document !== 'undefined') {
  document.title = config.app.name
}

// Load reCAPTCHA script early (non-blocking)
if (config.recaptcha.enabled) {
  loadRecaptchaScript().catch(console.error)
}

const app = createApp(App)
const pinia = createPinia()

// Create query client with default configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
})

app.use(pinia)
app.use(router)
app.use(VueQueryPlugin, { queryClient })
app.use(i18n)
app.directive('tooltip', vTooltip)

// Set HTML lang attribute based on initial locale
// TODO: Move to app initialization?
const initialLocale = typeof i18n.global.locale === 'string' ? i18n.global.locale : i18n.global.locale.value
document.documentElement.setAttribute('lang', initialLocale)

// Global error handler for chunk loading errors
window.addEventListener('error', (event) => {
  const error = event.error

  // Check if it's a chunk load error
  const isChunkLoadError =
    error?.name === 'ChunkLoadError' ||
    error?.message?.includes('Failed to fetch dynamically imported module') ||
    error?.message?.includes('Importing a module script failed') ||
    (error?.message?.includes('fetch') && error?.message?.includes('chunk'))

  if (isChunkLoadError) {
    // Prevent default error handling
    event.preventDefault()

    // Get current locale
    const currentLocale = typeof i18n.global.locale === 'string' ? i18n.global.locale : i18n.global.locale.value
    const isPolish = currentLocale === 'pl'

    // Show user-friendly message with confirm dialog
    const title = isPolish ? 'Nowa wersja aplikacji' : 'New Version Available'
    const message = isPolish
      ? 'Aplikacja została zaktualizowana. Aby kontynuować, należy odświeżyć stronę.'
      : 'A new version of the application is available. The page needs to be reloaded to continue.'
    const description = isPolish ? 'Zapisz swoją pracę przed odświeżeniem.' : 'Please save your work before reloading.'

    const shouldRefresh = window.confirm(`${title}\n\n${message}\n\n${description}`)

    if (shouldRefresh) {
      window.location.reload()
    }
  }
})

app.mount('#app')
