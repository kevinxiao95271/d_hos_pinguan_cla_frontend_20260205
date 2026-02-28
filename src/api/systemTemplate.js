import request from '@/utils/request'

/**
 * 获取有效的系统模版列表
 * 场景：用户注册时下载模版（后端应该是公开接口，但前端正常带token）
 */
export function getActiveTemplates() {
  return request({
    url: '/system-templates/active',
    method: 'get'
  })
}

/**
 * 下载系统模版文件
 * @param {number} templateId - 模版ID
 * @returns {Promise<Blob>} 文件Blob
 */
export function downloadTemplate(templateId) {
  return request({
    url: `/system-templates/${templateId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 获取所有模版（包括历史版本） - OPS专用
 */
export function getAllTemplates() {
  return request({
    url: '/system-templates',
    method: 'get'
  })
}

/**
 * 上传新版本模版 - OPS专用
 * @param {FormData} formData - 包含file字段的FormData
 */
export function uploadTemplate(formData) {
  return request({
    url: '/system-templates/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除模版（软删除） - OPS专用
 * @param {number} templateId - 模版ID
 */
export function deleteTemplate(templateId) {
  return request({
    url: `/system-templates/${templateId}`,
    method: 'delete'
  })
}
