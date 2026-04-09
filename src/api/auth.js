import request from '@/utils/request'

/**
 * 登录（旧版，已废弃，仅用于兼容）
 * @deprecated 请使用 loginWithPassword
 */
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * 参赛者注册
 * 公开接口，无需Token
 */
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data,
    skipAuth: true
  })
}

/**
 * 密码登录（推荐）
 * 公开接口，无需Token
 */
export function loginWithPassword(data) {
  return request({
    url: '/auth/login-with-password',
    method: 'post',
    data,
    skipAuth: true
  })
}

/**
 * 修改密码
 */
export function changePassword(userId, data) {
  return request({
    url: `/auth/change-password/${userId}`,
    method: 'post',
    data
  })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  return request({
    url: '/auth/current',
    method: 'get'
  })
}

/**
 * 确认已阅读诚信须知
 */
export function confirmIntegrityNotice() {
  return request({
    url: '/auth/notice/confirm',
    method: 'post'
  })
}

/**
 * 本人修改密码（需要验证旧密码）
 * @param {{ oldPassword, newPassword }} data
 */
export function selfChangePassword(data) {
  return request({
    url: '/auth/self-change-password',
    method: 'post',
    data
  })
}
