import request from '@/utils/request'

/**
 * 获取我的报名列表 (从token获取申请人ID)
 */
export function getMyRegistrations() {
  return request({
    url: '/registrations/my',
    method: 'get'
  })
}

/**
 * 创建报名
 */
export function createRegistration(data) {
  return request({
    url: '/registrations',
    method: 'post',
    data
  })
}

/**
 * 更新报名基本信息
 */
export function updateRegistration(id, data) {
  return request({
    url: `/registrations/${id}`,
    method: 'put',
    data
  })
}

/**
 * 更新报名成员信息
 */
export function updateRegistrationMembers(id, data) {
  return request({
    url: `/registrations/${id}/members`,
    method: 'put',
    data
  })
}

/**
 * 更新活动说明
 */
export function updateRegistrationActivity(id, data) {
  return request({
    url: `/registrations/${id}/activity`,
    method: 'put',
    data
  })
}

/**
 * 更新项目摘要
 */
export function updateRegistrationSummary(id, data) {
  return request({
    url: `/registrations/${id}/summary`,
    method: 'put',
    data
  })
}

/**
 * 上传材料
 */
export function uploadRegistrationMaterial(id, file, type) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: `/registrations/${id}/materials?type=${type}`,
    method: 'post',
    data: formData,
    timeout: 300000,
    retry: 0,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 提交报名
 */
export function submitRegistration(id) {
  return request({
    url: `/registrations/${id}/submit`,
    method: 'post'
  })
}

/**
 * 退回报名
 */
export function returnRegistration(id, data) {
  return request({
    url: `/registrations/${id}/return`,
    method: 'post',
    data
  })
}

/**
 * 批准报名
 */
export function approveRegistration(id) {
  return request({
    url: `/registrations/${id}/approve`,
    method: 'post'
  })
}

/**
 * 根据申请人查询报名
 */
export function getRegistrationsByApplicant(applicantId) {
  return request({
    url: '/registrations/by-applicant',
    method: 'get',
    params: { applicantId }
  })
}

/**
 * 获取当前机构在指定赛事下的报名数量
 */
export function getRegistrationCountByInstitution(competitionId) {
  return request({
    url: '/registrations/count-by-institution',
    method: 'get',
    params: { competitionId }
  })
}

/**
 * 获取报名详情
 */
export function getRegistration(id) {
  return request({
    url: `/registrations/${id}`,
    method: 'get'
  })
}

/**
 * 获取报名详情 (别名)
 */
export function getRegistrationDetail(id) {
  return getRegistration(id)
}

/**
 * 获取报名评审结果
 */
export function getRegistrationReviewResults(id) {
  return request({
    url: `/registrations/${id}/review-results`,
    method: 'get'
  })
}

/**
 * 获取报名评审详情（汇总平均分）
 */
export function getRegistrationReviewDetails(id) {
  return request({
    url: `/registrations/${id}/review-details`,
    method: 'get'
  })
}

/**
 * 获取报名的评委评分详情（每个评委的详细评分）
 * @param {Number} id 报名ID
 * @param {String} stage 评审阶段 (可选: BOOK|INTERVIEW|FINAL)
 * @returns Promise
 */
export function getReviewerScores(id, stage = null) {
  const params = stage ? { stage } : {}
  return request({
    url: `/registrations/${id}/reviewer-scores`,
    method: 'get',
    params
  })
}

/**
 * 获取报名已发布反馈（参赛者只读）
 * GET /api/registrations/{id}/published-feedback
 */
export function getPublishedFeedback(id) {
  return request({
    url: `/registrations/${id}/published-feedback`,
    method: 'get'
  })
}

/**
 * 获取报名列表（支持筛选）
 */
export function getRegistrations(params) {
  return request({
    url: '/registrations',
    method: 'get',
    params
  })
}
