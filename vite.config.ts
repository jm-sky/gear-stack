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
    optimizeDeps: {
      // Exclude large @unovis dependencies that are only used in specific components
      // These will be loaded dynamically when needed
      exclude: [
        'elkjs',
        'maplibre-gl',
        'leaflet',
        '@unovis/ts/components/graph',
        '@unovis/ts/components/timeline',
        '@unovis/ts/components/topojson-map',
        '@unovis/ts/components/leaflet-map',
      ],
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
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            // Split vendor libraries into separate chunks
            if (id.includes('node_modules')) {
              // Vue core libraries (small, frequently used)
              if (id.includes('vue') && !id.includes('vue-router') && !id.includes('vue-i18n') && !id.includes('vue-sonner')) {
                return 'vendor-vue'
              }
              // Router (separate chunk for route-based code splitting)
              if (id.includes('vue-router')) {
                return 'vendor-router'
              }
              // State management (Pinia + TanStack Query)
              if (id.includes('pinia') || id.includes('@tanstack/vue-query')) {
                return 'vendor-state'
              }
              // i18n
              if (id.includes('vue-i18n')) {
                return 'vendor-i18n'
              }
              // UI libraries - split further for better tree-shaking
              if (id.includes('lucide-vue-next')) {
                return 'vendor-icons'
              }
              if (id.includes('@radix-vue') || id.includes('reka-ui')) {
                return 'vendor-ui-components'
              }
              if (id.includes('floating-vue')) {
                return 'vendor-tooltips'
              }
              // Notifications
              if (id.includes('vue-sonner') || id.includes('sonner')) {
                return 'vendor-notifications'
              }
              // Large visualization library (lazy loaded)
              // Split @unovis into separate chunks for better tree-shaking
              if (id.includes('@unovis')) {
                // Core @unovis components (used in charts)
                if (id.includes('@unovis/ts/components/donut') || id.includes('@unovis/ts/components/single-container')) {
                  return 'vendor-charts-core'
                }
                // Heavy @unovis components (graph, timeline, maps) - rarely used
                if (id.includes('@unovis/ts/components/graph') || 
                    id.includes('@unovis/ts/components/timeline') ||
                    id.includes('@unovis/ts/components/topojson-map') ||
                    id.includes('@unovis/ts/components/leaflet-map')) {
                  return 'vendor-charts-heavy'
                }
                // @unovis dependencies (elkjs, maplibre, leaflet) - only load when needed
                if (id.includes('elkjs') || id.includes('maplibre-gl') || id.includes('leaflet')) {
                  return 'vendor-charts-deps'
                }
                // All other @unovis code
                return 'vendor-charts'
              }
              // Form validation (large library)
              if (id.includes('vee-validate') || id.includes('@vee-validate')) {
                return 'vendor-forms'
              }
              // Markdown parsing (lazy loaded)
              if (id.includes('markdown-it')) {
                return 'vendor-markdown'
              }
              // Date utilities (large library, can be tree-shaken)
              if (id.includes('date-fns')) {
                return 'vendor-dates'
              }
              // QR code generation (lazy loaded)
              if (id.includes('qrcode')) {
                return 'vendor-qrcode'
              }
              // WebAuthn (lazy loaded for auth pages)
              if (id.includes('@simplewebauthn')) {
                return 'vendor-webauthn'
              }
              // Table library
              if (id.includes('@tanstack/vue-table')) {
                return 'vendor-table'
              }
              // Utilities
              if (id.includes('@vueuse/core')) {
                return 'vendor-vueuse'
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
