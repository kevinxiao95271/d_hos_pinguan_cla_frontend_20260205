import request from '@/utils/request'

/**
 * 获取排名列表（优先读快照；需先 compute-ranking）
 * @param {Object} params - competitionId, stage: BOOK|INTERVIEW|FINAL, groupType 可选
 */
export function getRankings(params) {
  return request({
    url: '/admin/reviews/rankings',
    method: 'get',
    params
  })
}

/**
 * 触发系数调整排名计算并写入快照
 * @param {Object} data - { competitionId, stage, groupType? }
 */
export function computeRanking(data) {
  return request({
    url: '/admin/reviews/compute-ranking',
    method: 'post',
    data
  })
}

/**
 * 查询入围名单（含入围线、人工干预；依赖快照）
 * @param {Object} params - competitionId, stage, groupType 可选
 * @returns {Promise} success 时 data 可为：
 *   - 新结构：{ stage, snapshotAt, totalCount, shortlistCount, shortlistRatio, scope?, unifiedMode?, unifiedValue?, unifiedCutoff?, groupConfigs?, items[] }
 *   - 旧结构：items 数组（兼容）
 */
export function getAdminShortlist(params) {
  return request({
    url: '/admin/shortlist',
    method: 'get',
    params
  })
}

/**
 * 查询书审入围范围模式（各组独立 / 基层+综合统一排序）
 */
export function getBookScope() {
  return request({
    url: '/admin/shortlist/book-scope',
    method: 'get'
  })
}

/**
 * 切换书审入围范围
 * @param {Object} data - PER_GROUP: { scope:'PER_GROUP' }；UNIFIED: { scope:'UNIFIED', unifiedMode:'RATIO'|'COUNT', unifiedValue }
 */
export function saveBookScope(data) {
  return request({
    url: '/admin/shortlist/book-scope',
    method: 'put',
    data
  })
}

/**
 * 查询进阶组合分配置（书审/面谈权重与合分模式）
 */
export function getAdvancedRankingConfig() {
  return request({
    url: '/admin/shortlist/advanced-ranking-config',
    method: 'get'
  })
}

/**
 * 保存进阶组合分配置（三个字段均必填）
 * @param {Object} data - { bookWeight, interviewWeight, rankingMode }
 */
export function saveAdvancedRankingConfig(data) {
  return request({
    url: '/admin/shortlist/advanced-ranking-config',
    method: 'put',
    data
  })
}

/**
 * 查询入围配置（三组各一条）
 */
export function getShortlistConfig() {
  return request({
    url: '/admin/shortlist/config',
    method: 'get'
  })
}

/**
 * 保存入围配置（单组）
 * @param {Object} data - { groupType, mode: RATIO|COUNT, value }
 */
export function saveShortlistConfig(data) {
  return request({
    url: '/admin/shortlist/config',
    method: 'put',
    data
  })
}

/**
 * 人工干预入围
 * @param {Object} data - { registrationId, override: INCLUDE|EXCLUDE, note? }
 */
export function setShortlistOverride(data) {
  return request({
    url: '/admin/shortlist/override',
    method: 'put',
    data
  })
}

/**
 * 撤销人工干预
 */
export function deleteShortlistOverride(registrationId) {
  return request({
    url: `/admin/shortlist/override/${registrationId}`,
    method: 'delete'
  })
}

/**
 * @deprecated 旧接口，请优先使用 getAdminShortlist
 */
export function getShortlistLegacy(params) {
  return request({
    url: '/admin/reviews/shortlist',
    method: 'get',
    params
  })
}
