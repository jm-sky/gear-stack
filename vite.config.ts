import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import pkg from './package.json'
import { pwaPlugin } from './pwa.config'

// https://vite.dev/config/Pfix
export default defineConfig(({ mode }) => {
  const root = fileURLToPath(new URL('./', import.meta.url))
  const envVars = loadEnv(mode, root, 'VITE_')

  return {
    define: {
      __APP_VERSION__: JSON.stringify(pkg.version),
      __BUILD_DATE__: JSON.stringify(new Date().toISOString()),
    },
    plugins: [
      tailwindcss(),
      vue(),
      pwaPlugin,
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
      port: envVars.VITE_PORT ? parseInt(envVars.VITE_PORT) : 5176,
      proxy: {
        '/api': {
          target: envVars.VITE_API_PROXY_URL ?? 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
    watch: {
      ignored: ['**/backend/**'],
    },
    build: {
      chunkSizeWarningLimit: 600,
      sourcemap: true, // Generate source maps to satisfy Lighthouse performance audit
      cssCodeSplit: true, // Split CSS into separate chunks for better caching
    
    },
  }
})
