/**
 * 评审专家诚信须知（多类型，与后端 notice_key / pendingIntegrityNoticeKeys 对齐）
 * 旧字段 noticeConfirmed 仍由后端保留；前端优先使用 pendingIntegrityNoticeKeys。
 */
export const INTEGRITY_NOTICE_KEYS = {
  BOOK: 'BOOK',
  INTERVIEW: 'INTERVIEW'
}

/** pdfFile 相对 BASE_URL，文件放在 public/ */
export const INTEGRITY_NOTICES = {
  [INTEGRITY_NOTICE_KEYS.BOOK]: {
    title: '浙江省医院品管大赛专家须知',
    pdfFile: 'integrity_notice.pdf'
  },
  [INTEGRITY_NOTICE_KEYS.INTERVIEW]: {
    title: '浙江省医院品管大赛面谈环节专家须知',
    pdfFile: 'integrity_notice_interview.pdf'
  }
}

export function getIntegrityNoticeMeta(key) {
  return INTEGRITY_NOTICES[key] || null
}

/**
 * @param {object} loginData 登录接口 data
 * @returns {string[]} 待阅读顺序（已过滤未知 key）
 */
export function resolvePendingIntegrityNoticeKeys(loginData) {
  const keys = loginData?.pendingIntegrityNoticeKeys
  if (Array.isArray(keys)) {
    return keys.filter((k) => Boolean(INTEGRITY_NOTICES[k]))
  }
  if (loginData?.noticeConfirmed === false) {
    return [INTEGRITY_NOTICE_KEYS.BOOK]
  }
  return []
}
