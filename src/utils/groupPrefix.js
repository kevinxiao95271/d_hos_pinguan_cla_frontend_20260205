/** 各组别默认前缀（赛事未配置时 fallback，与创建赛事页一致） */
export const DEFAULT_GROUP_PREFIXES = {
  BASIC: 'A',
  COMPREHENSIVE: 'B',
  ADVANCED: 'C',
}

const GROUP_TYPE_PREFIX_FIELD = {
  BASIC: 'basicGroupPrefix',
  COMPREHENSIVE: 'comprehensiveGroupPrefix',
  ADVANCED: 'advancedGroupPrefix',
}

/** 从赛事对象解析某组别的分组前缀字母 */
export function resolveGroupPrefix(groupType, competition) {
  const field = GROUP_TYPE_PREFIX_FIELD[groupType]
  const configured = field && competition ? competition[field] : null
  if (configured) return configured
  return DEFAULT_GROUP_PREFIXES[groupType] || 'A'
}

/** 生成 ${prefix}1 … ${prefix}N 分组编号列表 */
export function buildGroupCodeList(prefix, count = 10) {
  const p = prefix || 'A'
  return Array.from({ length: count }, (_, i) => `${p}${i + 1}`)
}

/** 三组前缀各生成 count 个编号（用于跨组别筛选） */
export function buildAllGroupCodes(competition, count = 10) {
  return [
    ...buildGroupCodeList(resolveGroupPrefix('BASIC', competition), count),
    ...buildGroupCodeList(resolveGroupPrefix('COMPREHENSIVE', competition), count),
    ...buildGroupCodeList(resolveGroupPrefix('ADVANCED', competition), count),
  ]
}

/** 单个大写字母 + 三者不重复 */
export function computePrefixErrors(basic, comprehensive, advanced) {
  const check = (val, others) => {
    if (!val) return ''
    if (!/^[A-Z]$/.test(val)) return '须为单个大写字母（A-Z）'
    if (others.filter(Boolean).includes(val)) return '三组前缀不能重复'
    return ''
  }
  return {
    basic: check(basic, [comprehensive, advanced]),
    comprehensive: check(comprehensive, [basic, advanced]),
    advanced: check(advanced, [basic, comprehensive]),
  }
}

export function hasPrefixError(errors) {
  return !!(errors.basic || errors.comprehensive || errors.advanced)
}

export function sanitizePrefixInput(val) {
  return (val || '').toUpperCase().replace(/[^A-Z]/g, '').slice(0, 1)
}
