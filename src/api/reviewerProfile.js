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

/**
 * 修改本人所属机构
 * @param {{ newInstitutionId: number, reason?: string }} data
 */
export function changeMyInstitution(data) {
  return request({
    url: '/reviewers/me/institution',
    method: 'put',
    data
  })
}

/**
 * 获取本人机构变更历史
 */
export function getMyInstitutionHistory() {
  return request({
    url: '/reviewers/me/institution/history',
    method: 'get'
  })
}

// ── 管理端（admin 按 ID）──────────────────────────────────────────
export function getReviewerProfile(id) {
  return request({ url: `/admin/reviewers/${id}/profile`, method: 'get' })
}

export function updateReviewerProfile(id, data) {
  return request({ url: `/admin/reviewers/${id}/profile`, method: 'put', data })
}

/**
 * 管理员修改评委所属机构
 */
export function adminChangeReviewerInstitution(id, data) {
  return request({ url: `/admin/reviewers/${id}/institution`, method: 'put', data })
}

/**
 * 管理员查看评委机构变更历史
 */
export function adminGetReviewerInstitutionHistory(id) {
  return request({ url: `/admin/reviewers/${id}/institution/history`, method: 'get' })
}
