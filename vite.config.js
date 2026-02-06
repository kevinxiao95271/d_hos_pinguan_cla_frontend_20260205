import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 6039,
    proxy: {
      '/api': {
        target: 'http://localhost:6031',
        changeOrigin: true,
        timeout: 60000  // 增加代理超时时间到 60 秒
      }
    }
  }
})
