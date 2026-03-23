/**
 * 将 GET /admin/reviews/score-list 返回的「按报名聚合」结构展平为表格行（每位评委一行）
 */
export function flattenScoreListRows(apiData, defaultStage) {
  const list = Array.isArray(apiData) ? apiData : []
  const rows = []
  for (const reg of list) {
    const reviewers = reg.reviewerScores
    if (!Array.isArray(reviewers) || reviewers.length === 0) continue
    for (const rs of reviewers) {
      rows.push({
        registrationId: reg.registrationId,
        projectName: reg.projectName,
        institutionName: reg.institutionName,
        institutionLevel: reg.institutionLevel,
        groupType: reg.groupType,
        groupCode: reg.groupCode,
        stage: reg.stage || defaultStage,
        scoredCount: reg.scoredCount,
        totalReviewers: reg.totalReviewers,
        avgTotal: reg.avgTotal,
        reviewerInstitutionName: rs.reviewerInstitutionName,
        /** 驳回接口 POST /admin/reviews/scores/return 使用 */
        reviewTaskId: rs.reviewTaskId,
        reviewerId: rs.reviewerId,
        reviewerName: rs.reviewerName,
        status: rs.status,
        submittedAt: rs.submittedAt,
        highlight: rs.highlight,
        weakness: rs.weakness,
        plan: rs.plan,
        problem: rs.problem,
        action: rs.action,
        success: rs.success,
        review: rs.review,
        operation: rs.operation,
        presentation: rs.presentation,
        topic: rs.topic,
        process: rs.process,
        interviewOperation: rs.interviewOperation,
        result: rs.result,
        total: rs.total
      })
    }
  }
  return rows
}

export function filterScoreRows(rows, { reviewerName, institutionName, groupType }) {
  let list = rows
  if (groupType) {
    list = list.filter(r => r.groupType === groupType)
  }
  if (reviewerName && String(reviewerName).trim()) {
    const k = reviewerName.trim().toLowerCase()
    list = list.filter(r => (r.reviewerName || '').toLowerCase().includes(k))
  }
  if (institutionName && String(institutionName).trim()) {
    const k = institutionName.trim().toLowerCase()
    list = list.filter(r => (r.institutionName || '').toLowerCase().includes(k))
  }
  return list
}
