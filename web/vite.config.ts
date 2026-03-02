import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    allowedHosts: ['158f-104-234-20-71.ngrok-free.app', '.ngrok-free.app'],
    proxy: {
      '/api': {
        target: 'http://localhost:8093',
        changeOrigin: true
      }
    }
  }
})
