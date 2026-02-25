import { defineStore } from 'pinia'
import { login } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null')
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    role: (state) => state.userInfo?.role || '',
    userId: (state) => state.userInfo?.id || null,
    institutionId: (state) => state.userInfo?.institutionId || null,
    institutionName: (state) => state.userInfo?.institutionName || '',
    userName: (state) => state.userInfo?.name || '',
    isContestant: (state) => state.userInfo?.role === 'CONTESTANT',
    isReviewer: (state) => state.userInfo?.role === 'REVIEWER',
    isCommittee: (state) => state.userInfo?.role === 'COMMITTEE_ADMIN',
    isOps: (state) => state.userInfo?.role === 'OPS'
  },
  
  actions: {
    // 设置用户信息（注册或登录成功后调用）
    setUserInfo(userData) {
      this.token = userData.token
      this.userInfo = userData
      
      const loginTimestamp = Date.now()
      localStorage.setItem('token', userData.token)
      localStorage.setItem('userInfo', JSON.stringify(userData))
      localStorage.setItem('loginTime', new Date().toLocaleString('zh-CN'))
      localStorage.setItem('loginTimestamp', loginTimestamp.toString())
    },
    
    // 旧的登录方法（兼容现有代码）
    async login(loginData) {
      const res = await login(loginData)
      if (res.success && res.data) {
        this.setUserInfo(res.data)
      }
      return res
    },
    
    // 检查token是否过期（假设token有效期为2小时）
    isTokenExpired() {
      const loginTimestamp = localStorage.getItem('loginTimestamp')
      if (!loginTimestamp || !this.token) {
        return true
      }
      
      const now = Date.now()
      const elapsed = now - parseInt(loginTimestamp)
      const TWO_HOURS = 2 * 60 * 60 * 1000 // 2小时的毫秒数
      
      return elapsed > TWO_HOURS
    },
    
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('loginTime')
      localStorage.removeItem('loginTimestamp')
      localStorage.removeItem('currentCompetitionId')
    }
  }
})
