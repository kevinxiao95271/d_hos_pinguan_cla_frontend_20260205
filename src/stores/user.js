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
    async login(loginData) {
      const res = await login(loginData)
      if (res.success && res.data) {
        this.token = res.data.token
        this.userInfo = res.data
        localStorage.setItem('token', res.data.token)
        localStorage.setItem('userInfo', JSON.stringify(res.data))
        localStorage.setItem('loginTime', new Date().toLocaleString('zh-CN'))
      }
      return res
    },
    
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('loginTime')
      localStorage.removeItem('currentCompetitionId')
    }
  }
})
