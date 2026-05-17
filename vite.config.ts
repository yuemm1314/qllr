import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import UnoCSS from 'unocss/vite'
import path from 'node:path'

export default defineConfig({
  plugins: [vue(), UnoCSS()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  // 注意：如果将来要部署到 GitHub Pages 子路径，这里改成 '/qllr/'
  base: './',
  server: {
    port: 5173,
    open: true,
  },
})
