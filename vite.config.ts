import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'
import pkg from './package.json'

// https://vite.dev/config/
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
      VitePWA({
        registerType: 'prompt',
        includeAssets: [
          'icons/icon-16x16.png',
          'icons/icon-32x32.png',
          'icons/icon-48x48.png',
          'icons/icon-72x72.png',
          'icons/icon-96x96.png',
          'icons/icon-144x144.png',
          'icons/icon-192x192.png',
          'icons/icon-256x256.png',
          'icons/icon-512x512.png',
          'icons/icon-1024x1024.png',
          'icons/icon-60x60.png',
          'icons/icon-76x76.png',
          'icons/icon-120x120.png',
          'icons/icon-152x152.png',
          'icons/icon-180x180.png',
        ],
        manifest: {
          name: 'Gear Stack',
          short_name: 'Gear Stack',
          description: 'Gear Stack for managing survival gear and bug-out bag equipment.',
          theme_color: '#18181b',
          background_color: '#ffffff',
          display: 'standalone',
          orientation: 'portrait',
          scope: '/',
          start_url: '/',
          icons: [
            {
              src: 'icons/icon-16x16.png',
              sizes: '16x16',
              type: 'image/png',
            },
            {
              src: 'icons/icon-32x32.png',
              sizes: '32x32',
              type: 'image/png',
            },
            {
              src: 'icons/icon-48x48.png',
              sizes: '48x48',
              type: 'image/png',
            },
            {
              src: 'icons/icon-72x72.png',
              sizes: '72x72',
              type: 'image/png',
            },
            {
              src: 'icons/icon-96x96.png',
              sizes: '96x96',
              type: 'image/png',
            },
            {
              src: 'icons/icon-144x144.png',
              sizes: '144x144',
              type: 'image/png',
            },
            {
              src: 'icons/icon-192x192.png',
              sizes: '192x192',
              type: 'image/png',
              purpose: 'any maskable',
            },
            {
              src: 'icons/icon-256x256.png',
              sizes: '256x256',
              type: 'image/png',
            },
            {
              src: 'icons/icon-512x512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'any maskable',
            },
            {
              src: 'icons/icon-1024x1024.png',
              sizes: '1024x1024',
              type: 'image/png',
              purpose: 'any maskable',
            },
          ],
        },
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'google-fonts-cache',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365, // 1 year
                },
                cacheableResponse: {
                  statuses: [0, 200],
                },
              },
            },
            {
              urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'gstatic-fonts-cache',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365, // 1 year
                },
                cacheableResponse: {
                  statuses: [0, 200],
                },
              },
            },
            {
              urlPattern: /^https:\/\/api\./i,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'api-cache',
                expiration: {
                  maxEntries: 50,
                  maxAgeSeconds: 60 * 5, // 5 minutes
                },
                networkTimeoutSeconds: 10,
                cacheableResponse: {
                  statuses: [0, 200],
                },
              },
            },
          ],
        },
        devOptions: {
          enabled: false, // Disable PWA in dev mode for faster development
        },
      }),
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
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            // Vue core and ecosystem
            if (id.includes('vue') && !id.includes('node_modules')) {
              return
            }
            if (id.includes('node_modules/vue') || id.includes('node_modules/@vue')) {
              return 'vue-vendor'
            }
            // Vue Router
            if (id.includes('node_modules/vue-router')) {
              return 'vue-vendor'
            }
            // Pinia
            if (id.includes('node_modules/pinia')) {
              return 'vue-vendor'
            }
            // TanStack Query and Table
            if (id.includes('node_modules/@tanstack')) {
              return 'tanstack-vendor'
            }
            // UI libraries
            if (id.includes('node_modules/reka-ui') || id.includes('node_modules/lucide-vue-next')) {
              return 'ui-vendor'
            }
            // Validation libraries
            if (id.includes('node_modules/vee-validate') || id.includes('node_modules/@vee-validate') || id.includes('node_modules/zod')) {
              return 'validation-vendor'
            }
            // i18n
            if (id.includes('node_modules/vue-i18n')) {
              return 'i18n-vendor'
            }
            // Other large dependencies
            if (id.includes('node_modules/axios')) {
              return 'http-vendor'
            }
            if (id.includes('node_modules/date-fns')) {
              return 'utils-vendor'
            }
            if (id.includes('node_modules/floating-vue')) {
              return 'ui-vendor'
            }
            // All other node_modules
            if (id.includes('node_modules')) {
              return 'vendor'
            }
          },
        },
      },
      chunkSizeWarningLimit: 600, // Increase limit slightly since we're splitting chunks
    },
  }
})
