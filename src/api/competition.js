import request from '@/utils/request'

/**
 * 获取赛事列表
 */
export function getCompetitions(params) {
  return request({
    url: '/competitions',
    method: 'get',
    params
  })
}

/**
 * 创建赛事
 */
export function createCompetition(data) {
  return request({
    url: '/competitions',
    method: 'post',
    data
  })
}

/**
 * 获取赛事详情
 */
export function getCompetition(id) {
  return request({
    url: `/competitions/${id}`,
    method: 'get'
  })
}

/**
 * 更新赛事阶段
 */
export function updateCompetitionStage(id, data) {
  return request({
    url: `/competitions/${id}/stage`,
    method: 'put',
    data
  })
}

/**
 * 上传赛事模板
 */
export function uploadCompetitionTemplate(id, file, type) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('type', type)
  return request({
    url: `/competitions/${id}/templates`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取赛事模板列表
 */
export function getCompetitionTemplates(id) {
  return request({
    url: `/competitions/${id}/templates`,
    method: 'get'
  })
}

/**
 * 下载赛事模板
 */
export function downloadCompetitionTemplate(competitionId, templateId) {
  return request({
    url: `/competitions/${competitionId}/templates/${templateId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 删除赛事模板
 */
export function deleteCompetitionTemplate(competitionId, templateId) {
  return request({
    url: `/competitions/${competitionId}/templates/${templateId}`,
    method: 'delete'
  })
}
