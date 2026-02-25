import request from '@/utils/request'

/**
 * 查询用户列表（分页）
 */
export function queryUsers(data) {
  return request({
    url: '/admin/users/query',
    method: 'post',
    data
  })
}

/**
 * 获取用户详情
 */
export function getUserDetail(userId) {
  return request({
    url: `/admin/users/${userId}`,
    method: 'get'
  })
}

/**
 * 创建评委账号
 */
export function createReviewer(data) {
  return request({
    url: '/admin/users/reviewers',
    method: 'post',
    data
  })
}

/**
 * 禁用用户
 */
export function disableUser(userId) {
  return request({
    url: `/admin/users/${userId}/disable`,
    method: 'put'
  })
}

/**
 * 启用用户
 */
export function enableUser(userId) {
  return request({
    url: `/admin/users/${userId}/enable`,
    method: 'put'
  })
}

/**
 * 获取用户统计信息
 */
export function getUserStatistics() {
  return request({
    url: '/admin/users/statistics',
    method: 'get'
  })
}
