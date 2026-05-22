import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { writeFileSync } from 'fs'

// 每次 build / dev 启动时自动生成 version.txt（年月日时分秒）
const genVersionPlugin = () => ({
  name: 'gen-version',
  buildStart() {
    const now = new Date()
    const pad = n => String(n).padStart(2, '0')
    const ts = `${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
    writeFileSync(resolve(__dirname, 'public/version.txt'), ts)
    console.log(`[gen-version] version.txt => ${ts}`)
  }
})

export default defineConfig(({ mode }) => {
  const base = process.env.VITE_BASE_PATH || (mode === 'production' ? '/pgds/' : '/')

  return {
    base,
    plugins: [vue(), genVersionPlugin()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    preview: {
      port: 6039,
      proxy: {
        '/api': {
          target: 'http://localhost:6031',
          changeOrigin: true
        }
      }
    },
    server: {
      port: 6039,
      proxy: {
        '/api': {
          target: 'http://localhost:6031',
          changeOrigin: true,
          // 大文件上传走代理时，较短超时会导致 ERR_EMPTY_RESPONSE；开发环境放宽
          timeout: 0,
          proxyTimeout: 0
        }
      }
    }
  }
})
