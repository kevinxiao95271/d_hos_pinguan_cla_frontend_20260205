import { getCompetitions } from '@/api/competition'

/**
 * 自动初始化当前赛事（用于赛事管理员）
 * 如果 localStorage 中没有 currentCompetitionId，自动获取第一个赛事并设置
 * @returns {Promise<number|null>} 返回当前赛事ID
 */
export async function ensureCurrentCompetition() {
  try {
    // 检查是否已经有当前赛事
    const currentCompetitionId = localStorage.getItem('currentCompetitionId')
    if (currentCompetitionId) {
      return parseInt(currentCompetitionId)
    }

    // 获取赛事列表
    const res = await getCompetitions()
    
    if (res.success && res.data && res.data.length > 0) {
      // 自动选择第一个赛事作为当前赛事
      const firstCompetition = res.data[0]
      localStorage.setItem('currentCompetitionId', firstCompetition.id)
      console.log('✅ 自动设置当前赛事:', firstCompetition.name, '(ID:', firstCompetition.id, ')')
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
 * @returns {number|null}
 */
export function getCurrentCompetitionId() {
  const id = localStorage.getItem('currentCompetitionId')
  return id ? parseInt(id) : null
}

/**
 * 设置当前赛事ID
 * @param {number} competitionId 赛事ID
 */
export function setCurrentCompetitionId(competitionId) {
  localStorage.setItem('currentCompetitionId', competitionId)
}

/**
 * 清除当前赛事ID
 */
export function clearCurrentCompetitionId() {
  localStorage.removeItem('currentCompetitionId')
}
