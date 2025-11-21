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

app.mount('#app')
