import { getCompetitions, getCurrentCompetition, setCurrentCompetition } from '@/api/competition'

/**
 * 自动初始化当前赛事（用于赛事管理员）
 * 优先从后端API获取全局当前赛事，如果没有则自动设置第一个赛事
 * @returns {Promise<number|null>} 返回当前赛事ID
 */
export async function ensureCurrentCompetition() {
  try {
    // 1. 首先尝试从后端获取当前赛事
    const currentRes = await getCurrentCompetition()
    if (currentRes.success && currentRes.data) {
      console.log('✅ 获取到当前赛事ID:', currentRes.data)
      return currentRes.data
    }

    // 2. 如果后端没有当前赛事，获取第一个赛事并设置
    const res = await getCompetitions()
    
    if (res.success && res.data && res.data.length > 0) {
      const firstCompetition = res.data[0]
      
      // 尝试设置到后端
      try {
        await setCurrentCompetition(firstCompetition.id)
        console.log('✅ 自动设置当前赛事:', firstCompetition.name, '(ID:', firstCompetition.id, ')')
      } catch (err) {
        console.warn('⚠️ 设置当前赛事失败（可能是权限不足）:', err.message)
      }
      
      return firstCompetition.id
    } else {
      console.warn('⚠️ 暂无赛事数据')
      return null
    }
  } catch (error) {
    console.error('❌ 初始化赛事失败:', error)
    return null
  }
}

/**
 * 获取当前赛事ID
 * 优先从后端API获取，失败时从localStorage fallback
 * @returns {Promise<number|null>}
 */
export async function getCurrentCompetitionId() {
  try {
    const res = await getCurrentCompetition()
    if (res.success && res.data) {
      // 同步到localStorage作为缓存
      localStorage.setItem('currentCompetitionId', res.data)
      return res.data
    }
  } catch (error) {
    // 静默处理，API可能未实现（404）或网络失败
    // 直接fallback到localStorage，不打印警告
  }
  
  // Fallback到localStorage
  const id = localStorage.getItem('currentCompetitionId')
  return id ? parseInt(id) : null
}

/**
 * 获取当前赛事ID (同步版本，用于非async场景)
 * 仅从localStorage读取缓存值
 * @returns {number|null}
 */
export function getCurrentCompetitionIdSync() {
  const id = localStorage.getItem('currentCompetitionId')
  return id ? parseInt(id) : null
}

/**
 * 设置当前赛事ID
 * 尝试更新后端，失败时仅更新localStorage
 * @param {number} competitionId 赛事ID
 * @returns {Promise<boolean>} 是否设置成功
 */
export async function setCurrentCompetitionId(competitionId) {
  try {
    const res = await setCurrentCompetition(competitionId)
    if (res.success) {
      // 同步到localStorage
      localStorage.setItem('currentCompetitionId', competitionId)
      return true
    } else {
      console.error('❌ 后端设置当前赛事失败:', res.message)
      // 降级：仅更新localStorage
      localStorage.setItem('currentCompetitionId', competitionId)
      return true
    }
  } catch (error) {
    // API未实现或失败时，降级到仅localStorage
    console.warn('⚠️ 后端API不可用，仅更新本地缓存')
    localStorage.setItem('currentCompetitionId', competitionId)
    return true
  }
}

/**
 * 清除当前赛事ID (仅清除本地缓存)
 */
export function clearCurrentCompetitionId() {
  localStorage.removeItem('currentCompetitionId')
}
