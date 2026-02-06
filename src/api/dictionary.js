import request from '@/utils/request'

/**
 * 获取字典列表 - 按类型
 */
export function getDictionaryByType(type) {
  return request({
    url: `/dictionaries/${type}`,
    method: 'get'
  })
}

/**
 * 获取字典列表 - 按类型 (别名)
 */
export function getDictionaries(type) {
  return getDictionaryByType(type)
}

/**
 * 获取所有字典
 */
export function getAllDictionaries() {
  return request({
    url: '/dictionaries',
    method: 'get'
  })
}

/**
 * 创建字典
 */
export function createDictionary(data) {
  return request({
    url: '/dictionaries',
    method: 'post',
    data
  })
}

/**
 * 更新字典
 */
export function updateDictionary(id, data) {
  return request({
    url: `/dictionaries/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除字典
 */
export function deleteDictionary(id) {
  return request({
    url: `/dictionaries/${id}`,
    method: 'delete'
  })
}
