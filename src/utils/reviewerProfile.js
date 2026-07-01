/** 解析 backgroundsJson / toolsJson / topicsJson / experienceJson */
export function parseReviewerJsonField(str) {
  if (!str) return []
  try {
    const parsed = JSON.parse(str)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

/**
 * 是否已填写扩展档案（案例 A vs B）
 * data 不为 null，且任意可编辑核心字段（如 gender）非 null → 已填写
 */
export function hasReviewerProfileFilled(data) {
  if (!data) return false
  const scalarFields = [
    'gender', 'position', 'department', 'idNumber', 'bankName', 'bankCardNo',
    'idCardFrontUrl', 'idCardBackUrl',
  ]
  if (scalarFields.some((key) => data[key] != null && data[key] !== '')) return true
  return ['backgroundsJson', 'toolsJson', 'topicsJson', 'experienceJson'].some(
    (key) => parseReviewerJsonField(data[key]).length > 0
  )
}

/** 扩展信息 Tab：多选 JSON 区块是否至少有一项 */
export function hasReviewerMultiSelectExtension(dataOrForm) {
  if (!dataOrForm) return false
  const keys = ['backgroundsJson', 'toolsJson', 'topicsJson', 'experienceJson']
  const arrayKeys = ['backgrounds', 'tools', 'topics', 'experience']
  if ('backgrounds' in dataOrForm) {
    return arrayKeys.some((key) => Array.isArray(dataOrForm[key]) && dataOrForm[key].length > 0)
  }
  return keys.some((key) => parseReviewerJsonField(dataOrForm[key]).length > 0)
}

export function maskIdNumber(v) {
  if (!v || v.length < 10) return ''
  return v.slice(0, 6) + '********' + v.slice(-4)
}

export function maskBankCard(v) {
  if (!v || v.length < 8) return ''
  return v.slice(0, 4) + ' **** **** ' + v.slice(-4)
}

/** GET /reviewers/me/profile → 表单模型 */
export function mapReviewerProfileToForm(data) {
  if (!data) return null
  return {
    title: data.title ?? '',
    gender: data.gender ?? '',
    position: data.position ?? '',
    department: data.department ?? '',
    idNumber: data.idNumber ?? '',
    idNumberMasked: data.idNumberMasked || maskIdNumber(data.idNumber || ''),
    idCardFrontUrl: data.idCardFrontUrl ?? '',
    idCardBackUrl: data.idCardBackUrl ?? '',
    bankName: data.bankName ?? '',
    bankCardNo: data.bankCardNo ?? '',
    bankCardNoMasked: data.bankCardNoMasked || maskBankCard(data.bankCardNo || ''),
    backgrounds: parseReviewerJsonField(data.backgroundsJson),
    backgroundsOther: data.backgroundsOther ?? '',
    tools: parseReviewerJsonField(data.toolsJson),
    toolsOther: data.toolsOther ?? '',
    topics: parseReviewerJsonField(data.topicsJson),
    topicsOther: data.topicsOther ?? '',
    experience: parseReviewerJsonField(data.experienceJson),
  }
}

/** PUT /reviewers/me/profile — 仅传可编辑字段 */
export function mapFormToReviewerProfilePayload(form) {
  return {
    title: form.title || null,
    gender: form.gender || null,
    position: form.position || null,
    department: form.department || null,
    idNumber: form.idNumber || null,
    idCardFrontUrl: form.idCardFrontUrl || null,
    idCardBackUrl: form.idCardBackUrl || null,
    bankName: form.bankName || null,
    bankCardNo: form.bankCardNo || null,
    backgroundsJson: JSON.stringify(form.backgrounds || []),
    backgroundsOther: form.backgroundsOther || null,
    toolsJson: JSON.stringify(form.tools || []),
    toolsOther: form.toolsOther || null,
    topicsJson: JSON.stringify(form.topics || []),
    topicsOther: form.topicsOther || null,
    experienceJson: JSON.stringify(form.experience || []),
  }
}

export const GENDER_LABEL = { MALE: '男', FEMALE: '女', UNKNOWN: '保密' }
