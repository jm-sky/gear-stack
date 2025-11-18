import './css/style.css'

import { vTooltip } from 'floating-vue'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import { i18n } from '@/i18n'
import App from './App.vue'
import router from './router'
import 'floating-vue/dist/style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)
app.directive('tooltip', vTooltip)

// Set HTML lang attribute based on initial locale
const initialLocale = typeof i18n.global.locale === 'string' ? i18n.global.locale : i18n.global.locale.value
document.documentElement.setAttribute('lang', initialLocale)

app.mount('#app')
