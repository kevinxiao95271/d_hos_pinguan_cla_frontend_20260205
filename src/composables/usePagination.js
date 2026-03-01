/**
 * 分页功能 Composable
 * 支持后端分页和兼容非分页数据
 */
import { ref, computed } from 'vue'

export function usePagination(options = {}) {
  const defaultPageSize = options.defaultPageSize || 50
  const pageSizes = options.pageSizes || [10, 20, 50, 100, 200]

  // 分页状态
  const currentPage = ref(1)
  const pageSize = ref(defaultPageSize)
  const totalCount = ref(0)
  const totalPages = ref(0)
  const hasNext = ref(false)
  const hasPrevious = ref(false)

  // 计算属性
  const showPagination = computed(() => totalCount.value > 0)

  /**
   * 判断是否为分页结果
   * 支持两种格式：
   * - 自定义格式: { content, pageNo, pageSize, totalCount, totalPages, hasNext, hasPrevious }
   * - Spring Data 格式: { content, number, size, totalElements, totalPages }
   * @param {*} data
   * @returns {boolean}
   */
  function isPageResult(data) {
    return data && typeof data === 'object' && 'content' in data &&
      ('pageNo' in data || 'number' in data)
  }

  /**
   * 从API响应中提取数据列表
   * @param {Array|Object} data - API返回的data字段
   * @returns {Array} - 数据列表
   */
  function extractDataList(data) {
    if (!data) return []

    if (isPageResult(data)) {
      // 兼容自定义格式 (pageNo/totalCount) 和 Spring Data 格式 (number/totalElements)
      const isSpringData = 'number' in data && !('pageNo' in data)
      currentPage.value = isSpringData ? data.number + 1 : data.pageNo
      pageSize.value = data.pageSize ?? data.size ?? pageSize.value
      totalCount.value = data.totalCount ?? data.totalElements ?? 0
      totalPages.value = data.totalPages ?? 0
      hasNext.value = data.hasNext ?? (currentPage.value < totalPages.value)
      hasPrevious.value = data.hasPrevious ?? (currentPage.value > 1)
      return data.content || []
    } else {
      // 非分页结果（数组）
      const list = Array.isArray(data) ? data : []
      totalCount.value = list.length
      totalPages.value = 1
      hasNext.value = false
      hasPrevious.value = false
      return list
    }
  }

  /**
   * 重置分页到第一页
   */
  function resetPagination() {
    currentPage.value = 1
    totalCount.value = 0
    totalPages.value = 0
    hasNext.value = false
    hasPrevious.value = false
  }

  /**
   * 获取分页参数（用于API请求）
   * @returns {Object}
   */
  function getPaginationParams() {
    return {
      page: currentPage.value,
      size: pageSize.value
    }
  }

  return {
    // 状态
    currentPage,
    pageSize,
    totalCount,
    totalPages,
    hasNext,
    hasPrevious,
    pageSizes,
    
    // 计算属性
    showPagination,
    
    // 方法
    isPageResult,
    extractDataList,
    resetPagination,
    getPaginationParams
  }
}
