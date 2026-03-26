import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  // 添加重试配置
  retry: 2,
  retryDelay: 1000
})

// 用于防止重复弹窗和跳转
let isRefreshing = false

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 如果配置了skipAuth，则不添加Token（用于公开接口）
    if (!config.skipAuth) {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const rt = response.config?.responseType
    if (rt === 'blob' || rt === 'arraybuffer') {
      return response.data
    }
    const res = response.data

    // 后端统一返回格式: { success, data, message }
    if (res && typeof res === 'object' && res.success === false) {
      return res
    }

    return res
  },
  async error => {
    const config = error.config
    
    // 如果是超时错误且还有重试次数，则重试（config.retry 为 0 时必须显式传入数字，不能用 || 默认值）
    if (error.code === 'ECONNABORTED' && config && !config.__retryCount) {
      config.__retryCount = config.__retryCount || 0

      const maxRetry = typeof config.retry === 'number' ? config.retry : (request.defaults.retry ?? 0)

      if (config.__retryCount < maxRetry) {
        config.__retryCount += 1
        
        const delay = config.retryDelay || request.defaults.retryDelay || 1000
        console.log(`⏳ 请求超时，${delay}ms 后进行第 ${config.__retryCount} 次重试...`)
        
        // 等待一段时间后重试
        await new Promise(resolve => setTimeout(resolve, delay))
        
        return request(config)
      }
    }
    
    if (error.response) {
      const status = error.response.status
      const url = error.config?.url || '未知接口'
      
      if (status === 401) {
        // 防止重复处理
        if (!isRefreshing) {
          isRefreshing = true
          
          // 打印调试信息（开发环境）
          if (import.meta.env.DEV) {
            console.error('🔴 401 未授权:', {
              url,
              token: localStorage.getItem('token')?.substring(0, 20) + '...',
              response: error.response.data
            })
          }
          
          ElMessage.error('登录已过期，请重新登录')
          
          // 清除本地存储
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          localStorage.removeItem('currentCompetitionId')
          
          // 延迟跳转，确保只跳转一次
          setTimeout(() => {
            if (router.currentRoute.value.path !== '/login') {
              router.push('/login')
            }
            // 重置标志
            setTimeout(() => {
              isRefreshing = false
            }, 1000)
          }, 500)
        }
      } else if (status === 403) {
        console.error('🔴 403 无权限:', url)
        ElMessage.error('没有权限访问')
      } else if (status === 404) {
        console.error('🔴 404 未找到:', url)
        ElMessage.error('请求的资源不存在')
      } else if (status >= 500) {
        console.error('🔴 服务器错误:', url, error.response.data)
        ElMessage.error('服务器错误，请稍后重试')
      } else {
        console.error('🔴 请求错误:', status, url, error.response.data)
        ElMessage.error(error.response.data?.message || '请求失败')
      }
    } else if (error.code === 'ECONNABORTED') {
      const url = error.config?.url || '未知接口'
      const retryCount = error.config?.__retryCount || 0
      
      console.error('🔴 请求超时:', url)
      
      if (retryCount > 0) {
        ElMessage.error(`请求超时（已重试 ${retryCount} 次），请检查网络或后端服务状态`)
      } else {
        ElMessage.error('请求超时，请稍后重试')
      }
      
      // 如果是登录超时，给出更详细的提示
      if (url.includes('/auth/login')) {
        console.error('💡 登录超时建议：')
        console.error('   1. 检查后端服务是否正常运行 (http://localhost:6031)')
        console.error('   2. 检查网络连接')
        console.error('   3. 尝试刷新页面重试')
      }
    } else if (error.code === 'ERR_NETWORK') {
      console.error('🔴 网络错误 - 无法连接到后端:', error)
      ElMessage.error('网络错误，请检查后端服务是否启动')
    } else {
      console.error('🔴 未知错误:', error)
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default request
