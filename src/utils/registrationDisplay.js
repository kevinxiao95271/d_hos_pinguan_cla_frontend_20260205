/** 草稿/未提交：不展示对外项目编号 */
export function isDraftRegistration(row) {
  if (!row) return true
  if (row.draft === true || row.isDraft === true) return true
  return row.status === 'DRAFT'
}

/** 参赛者列表/详情：项目编号（草稿显示 -，已提交用 registrationCode 或正式 id） */
export function displayProjectCode(row) {
  if (!row || isDraftRegistration(row)) return '-'
  return row.registrationCode || row.projectCode || row.code || row.id || '-'
}

/** 参赛者端：草稿进编辑页，已提交/退回等进正式详情页 */
export function contestantRegistrationPath(row) {
  if (!row?.id) return '/contestant/dashboard'
  if (isDraftRegistration(row)) return `/contestant/register/${row.id}`
  return `/contestant/registration/${row.id}`
}
