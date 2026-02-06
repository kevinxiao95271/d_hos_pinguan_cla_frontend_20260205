import request from '@/utils/request'

/**
 * 获取机构列表
 */
export function getInstitutions(params) {
  return request({
    url: '/institutions',
    method: 'get',
    params
  })
}

/**
 * 获取机构详情
 */
export function getInstitution(id) {
  return request({
    url: `/institutions/${id}`,
    method: 'get'
  })
}

/**
 * 创建机构
 */
export function createInstitution(data) {
  return request({
    url: '/institutions',
    method: 'post',
    data
  })
}

/**
 * 更新机构
 */
export function updateInstitution(id, data) {
  return request({
    url: `/institutions/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除机构
 */
export function deleteInstitution(id) {
  return request({
    url: `/institutions/${id}`,
    method: 'delete'
  })
}

/**
 * 导入机构
 */
export function importInstitutions(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/institutions/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
