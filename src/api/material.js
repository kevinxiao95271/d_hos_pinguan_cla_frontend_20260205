import request from '@/utils/request'

/**
 * 上传材料文件
 * @param {number} registrationId - 报名ID
 * @param {FormData} formData - 包含file、type和contentType字段的FormData
 */
export function uploadMaterial(registrationId, formData) {
  return request({
    url: `/registrations/${registrationId}/materials`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 下载材料文件（带权限控制）
 * @param {number} materialId - 材料ID
 * @returns {Promise<Blob>} 文件Blob
 */
export function downloadMaterial(materialId) {
  return request({
    url: `/materials/${materialId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 获取报名的所有材料列表
 * @param {number} registrationId - 报名ID
 */
export function getMaterialsByRegistration(registrationId) {
  return request({
    url: `/materials/registration/${registrationId}`,
    method: 'get'
  })
}

/**
 * 删除材料文件
 * @param {number} materialId - 材料ID
 */
export function deleteMaterial(materialId) {
  return request({
    url: `/materials/${materialId}`,
    method: 'delete'
  })
}
