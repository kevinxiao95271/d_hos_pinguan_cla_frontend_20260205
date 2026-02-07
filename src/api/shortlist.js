import request from '@/utils/request'

/**
 * 入围管理相关API
 */

/**
 * 获取排名列表（书审或面谈）
 * @param {Object} params - 查询参数
 * @param {Number} params.competitionId - 赛事ID
 * @param {String} params.stage - 阶段: BOOK | INTERVIEW
 * @param {String} params.groupType - 组别（可选）: BASIC | ADVANCED | COMPREHENSIVE
 */
export function getRankings(params) {
  return request({
    url: '/admin/reviews/rankings',
    method: 'get',
    params
  })
}

/**
 * 获取入围名单（可选，可用rankings代替）
 * @param {Object} params - 查询参数
 * @param {Number} params.competitionId - 赛事ID
 * @param {String} params.stage - 阶段: BOOK | INTERVIEW
 * @param {String} params.groupType - 组别（可选）
 * @param {Number} params.limit - 限制数量（可选）
 * @param {Number} params.minAvgTotal - 最低分数线（可选）
 */
export function getShortlist(params) {
  return request({
    url: '/admin/reviews/shortlist',
    method: 'get',
    params
  })
}
