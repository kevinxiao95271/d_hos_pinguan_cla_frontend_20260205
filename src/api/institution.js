import request from '@/utils/request'

/**
 * 获取机构列表
 * 注意：后端已将此接口改为POST方式，使用/search端点
 * 原因：数据量过大(42K+)，必须使用分页查询
 */
export function getInstitutions(params) {
  return request({
    url: '/institutions/search',
    method: 'post',
    data: params  // POST使用data，不是params
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

/**
 * 搜索机构（高性能，支持分页）
 * 公开接口，无需Token
 */
export function searchInstitutions(data) {
  return request({
    url: '/institutions/search',
    method: 'post',
    data,
    skipAuth: true
  })
}

/**
 * 获取热门地区
 * 公开接口，无需Token
 */
export function getHotRegions(limit = 10) {
  return request({
    url: '/institutions/hot-regions',
    method: 'get',
    params: { limit },
    skipAuth: true
  })
}

/**
 * 获取所有地区列表（区县级别）
 * 公开接口，无需Token
 */
export function getAllRegions() {
  return request({
    url: '/institutions/regions',
    method: 'get',
    skipAuth: true
  })
}

/**
 * 获取城市列表（市级别，推荐使用）
 * 公开接口，无需Token
 */
export function getCities() {
  return request({
    url: '/institutions/cities',
    method: 'get',
    skipAuth: true
  })
}

/**
 * 获取指定城市的区县列表
 * 公开接口，无需Token
 */
export function getDistricts(city) {
  return request({
    url: '/institutions/districts',
    method: 'get',
    params: { city },
    skipAuth: true
  })
}

/**
 * 获取所有等级列表
 * 公开接口，无需Token
 */
export function getAllLevels() {
  return request({
    url: '/institutions/levels',
    method: 'get',
    skipAuth: true
  })
}

/**
 * 自动完成（输入提示）
 * 公开接口，无需Token
 */
export function autocomplete(prefix) {
  return request({
    url: '/institutions/autocomplete',
    method: 'get',
    params: { prefix },
    skipAuth: true
  })
}
