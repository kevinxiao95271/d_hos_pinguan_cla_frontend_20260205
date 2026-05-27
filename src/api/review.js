import request from '@/utils/request'

/**
 * 获取我的评审任务列表 (从token获取评委ID)
 */
export function getMyReviewTasks(params = {}) {
  return request({
    url: '/reviews/my-tasks',
    method: 'get',
    params
  })
}

/**
 * 获取评审任务列表 (旧接口，保留兼容)
 */
export function getReviewTasks(reviewerId) {
  return request({
    url: '/reviews/tasks',
    method: 'get',
    params: { reviewerId }
  })
}

/**
 * 更新评审任务状态
 */
export function updateReviewTaskStatus(data) {
  return request({
    url: '/reviews/tasks/status',
    method: 'put',
    data
  })
}

/**
 * 提交评分
 */
export function submitReviewScore(data) {
  return request({
    url: '/reviews/scores',
    method: 'post',
    data
  })
}

/**
 * 获取书审评分详情
 */
export function getReviewScore(reviewTaskId) {
  return request({
    url: `/reviews/scores/${reviewTaskId}`,
    method: 'get'
  })
}

/**
 * 获取面谈评分详情
 */
export function getInterviewScore(reviewTaskId) {
  return request({
    url: `/reviews/interview-scores/${reviewTaskId}`,
    method: 'get'
  })
}

/**
 * 获取评审汇总
 */
export function getReviewSummary(params) {
  return request({
    url: '/reviews/summary',
    method: 'get',
    params
  })
}

/**
 * 获取评审排名
 */
export function getReviewRankings(params) {
  return request({
    url: '/reviews/rankings',
    method: 'get',
    params
  })
}

/**
 * 组委会：按项目聚合的得分明细（含 reviewerScores）
 * GET /api/admin/reviews/score-list?competitionId=&stage=BOOK|INTERVIEW
 */
export function getAdminScoreList(params) {
  return request({
    url: '/admin/reviews/score-list',
    method: 'get',
    params
  })
}

/**
 * 书审得分列表：score-list + stage=BOOK
 */
export function getBookScores(params) {
  return getAdminScoreList({
    ...params,
    stage: 'BOOK'
  })
}

/**
 * 面谈得分列表：score-list + stage=INTERVIEW
 */
export function getInterviewScores(params) {
  return getAdminScoreList({
    ...params,
    stage: 'INTERVIEW'
  })
}

/**
 * 驳回评分
 * @param {Object} data - { reviewTaskId, reason? }
 */
export function returnScore(data) {
  return request({
    url: '/admin/reviews/scores/return',
    method: 'post',
    data
  })
}

/**
 * 获取评委列表（支持筛选）
 */
export function getReviewers(params) {
  return request({
    url: '/admin/reviewers',
    method: 'get',
    params
  })
}

export function exportReviewers() {
  return request({
    url: '/admin/reviewers/export',
    method: 'get',
    responseType: 'blob'
  })
}

export function downloadReviewerIdCards() {
  return request({
    url: '/admin/reviewers/id-cards/download',
    method: 'get',
    responseType: 'blob',
    timeout: 120000
  })
}

/**
 * 获取评委详情
 */
export function getReviewerDetail(id) {
  return request({
    url: `/admin/reviewers/${id}`,
    method: 'get'
  })
}

/**
 * 新增评委
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
 * 获取我的任务统计（待提交、已评分、已规避）
 */
export function getMyTaskStats() {
  return request({
    url: '/reviews/my-tasks/stats',
    method: 'get'
  })
}

/**
 * 书审草稿保存（所有分值字段可选）
 */
export function saveBookReviewDraft(data) {
  return request({
    url: '/reviews/scores/draft',
    method: 'put',
    data
  })
}

/**
 * 面谈草稿保存（所有分值字段可选）
 */
export function saveInterviewDraft(data) {
  return request({
    url: '/reviews/interview-scores/draft',
    method: 'put',
    data
  })
}

/**
 * 提交面谈评分
 */
export function submitInterviewScore(data) {
  return request({
    url: '/reviews/interview-scores',
    method: 'post',
    data
  })
}

/**
 * 规避评审任务
 * @param {number} taskId
 * @param {{ reasonCode: string, reasonOther?: string }} data
 */
export function recuseReviewTask(taskId, data) {
  return request({
    url: `/reviews/tasks/${taskId}/recuse`,
    method: 'post',
    data
  })
}

/**
 * 撤销规避（仅 RECUSED 状态可用）
 * 有草稿分 → DRAFT；无草稿 → PENDING
 * @param {number} taskId
 */
export function cancelRecuse(taskId) {
  return request({
    url: `/reviews/tasks/${taskId}/recuse`,
    method: 'delete'
  })
}

// ─────────────────────────────────────────────────────────────────
// 决赛阶段评分接口
// ─────────────────────────────────────────────────────────────────

/** 评委获取我的决赛任务列表 */
export function getFinalMyTasks() {
  return request({ url: '/reviews/final/my-tasks', method: 'get' })
}

/** 保存决赛评分草稿 */
export function saveFinalScoreDraft(taskId, data) {
  return request({ url: `/reviews/final/scores/${taskId}/draft`, method: 'put', data })
}

/** 提交决赛最终评分 */
export function submitFinalScore(taskId, data) {
  return request({ url: `/reviews/final/scores/${taskId}/submit`, method: 'put', data })
}

/** 申请规避决赛评审任务 */
export function recuseFinalScore(taskId, data) {
  return request({ url: `/reviews/final/scores/${taskId}/recuse`, method: 'put', data })
}

/** 撤销规避决赛评审任务 */
export function unrecuseFinalScore(taskId) {
  return request({ url: `/reviews/final/scores/${taskId}/recuse`, method: 'delete' })
}
