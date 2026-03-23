/**
 * 赛事 API 返回的 stage → StageProgress 等组件使用的步骤 key
 */
export function toProgressStageKey(apiStage) {
  if (!apiStage) return 'REGISTRATION'
  const m = {
    REGISTER: 'REGISTRATION',
    REGISTRATION: 'REGISTRATION',
    BOOK: 'BOOK',
    BOOK_REVIEW: 'BOOK',
    INTERVIEW: 'INTERVIEW',
    INTERVIEW_REVIEW: 'INTERVIEW',
    FINAL: 'FINAL'
  }
  return m[apiStage] || apiStage
}

/**
 * 赛事列表等处的阶段中文（与后端枚举对齐）
 */
export function getCompetitionStageDisplay(apiStage) {
  const m = {
    REGISTER: '报名中',
    REGISTRATION: '报名中',
    BOOK: '书审中',
    BOOK_REVIEW: '书审中',
    INTERVIEW: '面谈中',
    INTERVIEW_REVIEW: '面谈中',
    FINAL: '决赛中'
  }
  return m[apiStage] || apiStage || '-'
}
