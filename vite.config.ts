import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: process.env.VITE_PORT ? parseInt(process.env.VITE_PORT) : 5176,
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY_URL ?? 'http://localhost:8000',
        changeOrigin: true,
      },
    },
    watch: {
      ignored: ['**/backend/**'],
    },
  },
})
