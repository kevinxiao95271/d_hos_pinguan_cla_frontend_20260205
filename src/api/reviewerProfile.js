import request from '@/utils/request'

// ── 评委端（本人）──────────────────────────────────────────────────
export function getMyProfile() {
  return request({ url: '/reviewers/me/profile', method: 'get' })
}

export function updateMyProfile(data) {
  return request({ url: '/reviewers/me/profile', method: 'put', data })
}

// ── 管理端（admin 按 ID）──────────────────────────────────────────
export function getReviewerProfile(id) {
  return request({ url: `/admin/reviewers/${id}/profile`, method: 'get' })
}

export function updateReviewerProfile(id, data) {
  return request({ url: `/admin/reviewers/${id}/profile`, method: 'put', data })
}
