/**
 * 评审专家诚信须知（与后端 pendingIntegrityNoticeKeys 对齐）
 * 现只保留一份强制须知：2026年专家评审纪律及评审要求
 * BOOK key 复用（后端仍会下发），INTERVIEW 已移除（前端直接跳过）
 */
export const INTEGRITY_NOTICE_KEYS = {
  BOOK: 'BOOK'
}

/** pdfFile 相对 BASE_URL，文件放在 public/ */
export const INTEGRITY_NOTICES = {
  [INTEGRITY_NOTICE_KEYS.BOOK]: {
    title: '2026年专家评审纪律及评审要求',
    pdfFile: 'reviewer_discipline.pdf'
  }
  // INTERVIEW 已移除，后端若下发该 key 前端自动跳过
}

export function getIntegrityNoticeMeta(key) {
  return INTEGRITY_NOTICES[key] || null
}

/**
 * @param {object} loginData 登录接口 data
 * @returns {string[]} 待阅读顺序（已过滤未知 key，去重）
 */
export function resolvePendingIntegrityNoticeKeys(loginData) {
  const keys = loginData?.pendingIntegrityNoticeKeys
  if (Array.isArray(keys)) {
    // 过滤掉 INTEGRITY_NOTICES 中没有配置的 key（含 INTERVIEW），并去重
    const seen = new Set()
    return keys.filter((k) => {
      if (!INTEGRITY_NOTICES[k] || seen.has(k)) return false
      seen.add(k)
      return true
    })
  }
  if (loginData?.noticeConfirmed === false) {
    return [INTEGRITY_NOTICE_KEYS.BOOK]
  }
  return []
}
