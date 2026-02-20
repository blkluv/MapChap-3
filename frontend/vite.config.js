import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    hmr: {
      host: '0.0.0.0'
    },
    watch: {
      usePolling: true
    }
  },
  build: {
    outDir: 'dist'
  },
  // Разрешаем все хосты
  preview: {
    host: '0.0.0.0'
  }
})
