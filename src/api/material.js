import request from '@/utils/request'

/** 大文件上传（含 MinIO）可能超过默认 30s，单独放宽；不重试以免重复传整包 */
const MATERIAL_UPLOAD_TIMEOUT_MS = 300000

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
    timeout: MATERIAL_UPLOAD_TIMEOUT_MS,
    retry: 0,
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
    responseType: 'blob',
    timeout: MATERIAL_UPLOAD_TIMEOUT_MS
  })
}

/**
 * 预览 doc/docx 文件（后端转换为 PDF 返回）
 * @param {number} materialId - 材料ID
 * @returns {Promise<Blob>} PDF Blob
 */
export function previewMaterialAsPdf(materialId) {
  return request({
    url: `/materials/${materialId}/preview-pdf`,
    method: 'get',
    responseType: 'blob',
    timeout: MATERIAL_UPLOAD_TIMEOUT_MS
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
