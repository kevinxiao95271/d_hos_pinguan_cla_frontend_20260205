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
 * 获取评分详情
 */
export function getReviewScore(reviewTaskId) {
  return request({
    url: `/reviews/scores/${reviewTaskId}`,
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
 * 获取书审得分列表（组委会管理）
 */
export function getBookScores(params) {
  return request({
    url: '/admin/reviews/book-scores',
    method: 'get',
    params
  })
}

/**
 * 驳回评分
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
