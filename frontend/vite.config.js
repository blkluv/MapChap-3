import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: './',
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    allowedHosts: ['.emergentcf.cloud', '.emergentagent.com', '.preview.emergentagent.com', 'localhost'],
    cors: true
  },
  build: {
    outDir: 'dist'
  }
})
