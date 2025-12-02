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
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            // Split vendor libraries into separate chunks
            if (id.includes('node_modules')) {
              // Vue core libraries
              if (id.includes('vue') || id.includes('@vue')) {
                return 'vendor-vue'
              }
              // Router
              if (id.includes('vue-router')) {
                return 'vendor-router'
              }
              // UI libraries
              if (id.includes('lucide-vue-next') || id.includes('@radix-vue') || id.includes('floating-vue')) {
                return 'vendor-ui'
              }
              // State management
              if (id.includes('pinia') || id.includes('@tanstack/vue-query')) {
                return 'vendor-state'
              }
              // i18n
              if (id.includes('vue-i18n')) {
                return 'vendor-i18n'
              }
              // Other large dependencies
              if (id.includes('vue-sonner') || id.includes('sonner')) {
                return 'vendor-notifications'
              }
              // All other node_modules
              return 'vendor'
            }
          },
        },
      },
    },
  }
})
