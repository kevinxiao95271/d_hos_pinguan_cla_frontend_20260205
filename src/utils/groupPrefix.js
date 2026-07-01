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
