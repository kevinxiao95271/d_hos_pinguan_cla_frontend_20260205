import request from '@/utils/request'

// ── 评委端（本人）──────────────────────────────────────────────────
export function getMyProfile() {
  return request({ url: '/reviewers/me/profile', method: 'get' })
}

export function updateMyProfile(data) {
  return request({ url: '/reviewers/me/profile', method: 'put', data })
}

/**
 * 上传身份证图片
 * @param {'FRONT'|'BACK'} side
 * @param {File} file
 */
export function uploadMyIdCard(side, file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: `/reviewers/me/profile/id-card?side=${side}`,
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 获取身份证图片二进制流（用于展示，需鉴权）
 * @param {'FRONT'|'BACK'} side
 */
export function getMyIdCardStream(side) {
  return request({
    url: `/reviewers/me/profile/id-card/${side}`,
    method: 'get',
    responseType: 'blob'
  })
}

// ── 管理端（admin 按 ID）──────────────────────────────────────────
export function getReviewerProfile(id) {
  return request({ url: `/admin/reviewers/${id}/profile`, method: 'get' })
}

export function updateReviewerProfile(id, data) {
  return request({ url: `/admin/reviewers/${id}/profile`, method: 'put', data })
}
