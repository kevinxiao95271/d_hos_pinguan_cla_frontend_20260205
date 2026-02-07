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
