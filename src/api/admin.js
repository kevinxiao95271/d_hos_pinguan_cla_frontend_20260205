import request from '@/utils/request'

/**
 * 批量分类报名
 */
export function batchClassifyRegistrations(data) {
  return request({
    url: '/admin/registrations/batch-classify',
    method: 'post',
    data
  })
}

/**
 * 自动分组
 */
export function autoGroupRegistrations(data) {
  return request({
    url: '/admin/registrations/auto-group',
    method: 'post',
    data
  })
}

/**
 * 获取面谈分组视图
 */
export function getInterviewGroups(params) {
  return request({
    url: '/admin/registrations/interview-groups',
    method: 'get',
    params
  })
}

/**
 * 自动分配评委
 */
export function autoAssignReviewers(data) {
  return request({
    url: '/admin/reviews/auto-assign',
    method: 'post',
    data
  })
}

/**
 * 筛选报名列表
 */
export function filterRegistrations(params) {
  return request({
    url: '/admin/registrations/filter',
    method: 'get',
    params
  })
}

/**
 * 获取决赛分组
 */
export function getFinalGroups(competitionId) {
  return request({
    url: '/admin/registrations/final-groups',
    method: 'get',
    params: { competitionId }
  })
}

/**
 * 创建评审任务（手动分配单个）
 */
export function createReviewTask(data) {
  return request({
    url: '/admin/reviews/tasks',
    method: 'post',
    data
  })
}

/**
 * 获取某阶段的所有评审任务
 */
export function getReviewTasksByStage(params) {
  return request({
    url: '/reviews/tasks/stage',
    method: 'get',
    params
  })
}

/**
 * 筛选评审任务
 */
export function filterReviewTasks(params) {
  return request({
    url: '/reviews/tasks/filter',
    method: 'get',
    params
  })
}

/**
 * 获取评审汇总
 */
export function getAdminReviewSummary(params) {
  return request({
    url: '/admin/reviews/summary',
    method: 'get',
    params
  })
}

/**
 * 获取评审排名
 */
export function getAdminReviewRankings(params) {
  return request({
    url: '/admin/reviews/rankings',
    method: 'get',
    params
  })
}

/**
 * 获取入围名单
 */
export function getShortlist(params) {
  return request({
    url: '/admin/reviews/shortlist',
    method: 'get',
    params
  })
}

/**
 * 获取专家反馈
 * @deprecated 已废弃，请使用 getReviewerScores (from '@/api/registration')
 * 新API: GET /api/registrations/{id}/reviewer-scores?stage={BOOK|INTERVIEW|FINAL}
 * 优势: 包含分项评分、评委完整信息、评审时间等详细数据
 */
export function getReviewFeedback(params) {
  return request({
    url: '/admin/reviews/feedback',
    method: 'get',
    params
  })
}

/**
 * 退回评分
 */
export function returnReviewScore(data) {
  return request({
    url: '/admin/reviews/scores/return',
    method: 'post',
    data
  })
}

/**
 * 获取评委列表
 */
export function getReviewers(params) {
  return request({
    url: '/admin/reviewers',
    method: 'get',
    params
  })
}

/**
 * 获取评委详情
 */
export function getReviewer(id) {
  return request({
    url: `/admin/reviewers/${id}`,
    method: 'get'
  })
}

/**
 * 创建评委
 */
export function createReviewer(data) {
  return request({
    url: '/admin/reviewers',
    method: 'post',
    data
  })
}

/**
 * 更新评委
 */
export function updateReviewer(id, data) {
  return request({
    url: `/admin/reviewers/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除评委
 */
export function deleteReviewer(id) {
  return request({
    url: `/admin/reviewers/${id}`,
    method: 'delete'
  })
}

/**
 * 获取数据源信息
 */
export function getDatasource() {
  return request({
    url: '/admin/datasource',
    method: 'get'
  })
}

/**
 * 切换数据源
 */
export function switchDatasource(data) {
  return request({
    url: '/admin/datasource/switch',
    method: 'post',
    data
  })
}

/**
 * 保存系统设置
 */
export function saveSetting(data) {
  return request({
    url: '/admin/settings',
    method: 'post',
    data
  })
}

/**
 * 获取系统设置
 */
export function getSetting(key) {
  return request({
    url: '/admin/settings',
    method: 'get',
    params: { key }
  })
}

/**
 * 获取统计概览
 */
export function getStatsSummary(params) {
  return request({
    url: '/admin/stats/summary',
    method: 'get',
    params
  })
}
