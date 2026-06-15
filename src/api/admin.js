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
 * 管理端：查询已分配的评审任务（新接口）
 * @param {Object} params - { competitionId, stage, status }
 * @returns {Promise} 返回完整的任务列表，包含项目信息、评委信息等
 */
export function getAdminReviewTasks(params) {
  return request({
    url: '/admin/reviews/tasks',
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
 * 组委会：按项目获取反馈汇总（已脱敏）
 * GET /api/admin/reviews/project-feedback?competitionId=&stage=BOOK
 */
export function getProjectFeedback(params) {
  return request({
    url: '/admin/reviews/project-feedback',
    method: 'get',
    params
  })
}

/**
 * 组委会：项目反馈筛选项（组别/分组联动）
 * GET /api/admin/reviews/project-feedback/filter-options?competitionId=&stage=BOOK&groupType=
 */
export function getProjectFeedbackFilterOptions(params) {
  return request({
    url: '/admin/reviews/project-feedback/filter-options',
    method: 'get',
    params
  })
}

/**
 * 组委会：编辑单个项目反馈
 * PUT /api/admin/reviews/project-feedback/{registrationId}?stage=BOOK
 */
export function updateProjectFeedback(registrationId, data, stage = 'BOOK') {
  return request({
    url: `/admin/reviews/project-feedback/${registrationId}`,
    method: 'put',
    params: { stage },
    data
  })
}

/**
 * 组委会：发布/撤回单个项目反馈
 * POST /api/admin/reviews/project-feedback/{registrationId}/publish?stage=BOOK&published=true|false
 */
export function publishProjectFeedback(registrationId, stage = 'BOOK', published = true) {
  return request({
    url: `/admin/reviews/project-feedback/${registrationId}/publish`,
    method: 'post',
    params: { stage, published }
  })
}

/**
 * 组委会：按赛事批量发布/撤回反馈
 * POST /api/admin/reviews/project-feedback/publish?competitionId=&stage=BOOK&published=true|false
 */
export function batchPublishProjectFeedback(competitionId, stage = 'BOOK', published = true) {
  return request({
    url: '/admin/reviews/project-feedback/publish',
    method: 'post',
    params: { competitionId, stage, published }
  })
}

/**
 * 组委会：批量保存项目意见草稿
 * PUT /api/admin/reviews/project-feedback/batch?stage=BOOK
 */
export function batchSaveFeedbackDrafts(items, stage = 'BOOK') {
  return request({
    url: '/admin/reviews/project-feedback/batch',
    method: 'put',
    params: { stage },
    data: { items }
  })
}

/**
 * 组委会：导出项目意见反馈 Excel
 * GET /api/admin/reviews/project-feedback/export
 */
export function exportFeedbackExcel(competitionId, filters = {}) {
  const params = { competitionId, stage: 'BOOK' }
  if (filters.groupType) params.groupType = filters.groupType
  if (filters.groupCode) params.groupCode = filters.groupCode
  if (filters.projectName) params.projectName = filters.projectName
  if (filters.institutionName) params.institutionName = filters.institutionName
  if (typeof filters.published === 'boolean') params.published = filters.published
  return request({
    url: '/admin/reviews/project-feedback/export',
    method: 'get',
    params,
    responseType: 'blob'
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

/**
 * 查询历史数据
 * @param {Object} params - { region, competitionGroup, circleName, institutionName, projectName, year, page, size }
 */
export function getHistoricalData(params) {
  return request({
    url: '/historical-data',
    method: 'get',
    params
  })
}

/**
 * 重置用户密码（OPS专用）
 * @param {number} userId - 用户ID
 * @returns {Promise} 返回新密码 { newPassword: "XXXXXX" }
 */
export function resetUserPassword(userId) {
  return request({
    url: `/admin/users/${userId}/reset-password`,
    method: 'post'
  })
}

/**
 * 删除报名记录（OPS专用）
 * @param {number} registrationId - 报名ID
 * @returns {Promise}
 */
export function deleteRegistration(registrationId) {
  return request({
    url: `/admin/registrations/${registrationId}`,
    method: 'delete'
  })
}

// ─────────────────────────────────────────────────────────────────
// 决赛阶段管理接口
// ─────────────────────────────────────────────────────────────────

/** 获取决赛专场列表 */
export function getFinalSessions(competitionId) {
  return request({ url: '/admin/final/sessions', method: 'get', params: { competitionId } })
}

/** 一次获取全部场次对应表（含三天分组 + 各场项目列表） */
export function getFinalSessionSchedule(competitionId) {
  return request({ url: '/admin/final/session-schedule', method: 'get', params: { competitionId } })
}

/** 获取专场内项目列表 */
export function getFinalSessionProjects(sessionCode, competitionId) {
  return request({
    url: `/admin/final/sessions/${encodeURIComponent(sessionCode)}/projects`,
    method: 'get',
    params: { competitionId }
  })
}

/** 分配评委到专场（幂等） */
export function assignFinalReviewer(sessionCode, competitionId, reviewerId) {
  return request({
    url: `/admin/final/sessions/${encodeURIComponent(sessionCode)}/assign-reviewer`,
    method: 'post',
    params: { competitionId, reviewerId }
  })
}

/** 管理侧决赛评分汇总 */
export function getFinalScores(competitionId, sessionCode) {
  const params = { competitionId }
  if (sessionCode) params.sessionCode = sessionCode
  return request({ url: '/admin/final/scores', method: 'get', params })
}

/** 触发决赛排名计算（幂等，先清旧快照再重算） */
export function computeFinalRanking(competitionId) {
  return request({ url: '/admin/final/compute-ranking', method: 'post', params: { competitionId } })
}

/** 触发综合总分计算（书审/面谈D值 × 权重 + 现场均分 × 权重） */
export function computeTotalFinalRanking(competitionId) {
  return request({ url: '/admin/final/compute-total-ranking', method: 'post', params: { competitionId } })
}

/** 获取决赛排名结果 */
export function getFinalRanking(competitionId, sessionCode) {
  const params = { competitionId }
  if (sessionCode) params.sessionCode = sessionCode
  return request({ url: '/admin/final/ranking', method: 'get', params })
}

/** 导出决赛排名 Excel（blob） */
export function exportFinalRanking(competitionId, sessionCode) {
  const params = { competitionId }
  if (sessionCode) params.sessionCode = sessionCode
  return request({ url: '/admin/final/ranking/export', method: 'get', params, responseType: 'blob' })
}

/** 获取跨专场统一排名（全部专场混排，按 trimmedAvg 降序） */
export function getFinalRankingMixed(competitionId) {
  return request({ url: '/admin/final/ranking/mixed', method: 'get', params: { competitionId } })
}

/** OPERATOR：驳回已提交/草稿评分，任务重置为待评分 */
export function rejectFinalScore(taskId) {
  return request({ url: `/admin/final/scores/${taskId}/reject`, method: 'post' })
}
