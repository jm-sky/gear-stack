import './css/style.css'

import { vTooltip } from 'floating-vue'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import { i18n } from '@/i18n'
import App from './App.vue'
import router from './router'
import 'floating-vue/dist/style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
app.directive('tooltip', vTooltip)

app.mount('#app')
