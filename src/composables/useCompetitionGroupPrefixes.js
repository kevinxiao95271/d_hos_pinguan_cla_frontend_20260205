import { ref, computed, unref, watch } from 'vue'
import { getCompetition } from '@/api/competition'
import {
  resolveGroupPrefix,
  buildGroupCodeList,
  buildAllGroupCodes,
} from '@/utils/groupPrefix'

/**
 * 按当前赛事配置加载分组前缀，生成分组下拉选项（Z1、B2…）
 * @param {import('vue').Ref<number|string|null>|number|string|null} competitionIdSource
 */
export function useCompetitionGroupPrefixes(competitionIdSource) {
  const competition = ref(null)
  const loading = ref(false)
  let lastLoadedId = null

  async function load(force = false) {
    const id = unref(competitionIdSource)
    if (!id) {
      competition.value = null
      lastLoadedId = null
      return
    }
    if (!force && lastLoadedId === id && competition.value) return

    loading.value = true
    try {
      const res = await getCompetition(id)
      if (res.success) {
        competition.value = res.data
        lastLoadedId = id
      }
    } catch (error) {
      console.error('加载赛事分组前缀失败:', error)
    } finally {
      loading.value = false
    }
  }

  function prefixForType(groupType) {
    return resolveGroupPrefix(groupType, competition.value)
  }

  function groupCodesForType(groupType, count = 10) {
    return buildGroupCodeList(prefixForType(groupType), count)
  }

  /** 响应式：赛事前缀加载完成后自动刷新选项 */
  function groupCodesForTypeComputed(groupTypeSource, count = 10) {
    return computed(() => {
      const groupType = unref(groupTypeSource)
      if (!groupType) return []
      return buildGroupCodeList(resolveGroupPrefix(groupType, competition.value), count)
    })
  }

  const allGroupCodes = computed(() => buildAllGroupCodes(competition.value))

  if (competitionIdSource != null && typeof competitionIdSource === 'object') {
    watch(competitionIdSource, () => load(true))
  }

  return {
    competition,
    loading,
    load,
    prefixForType,
    groupCodesForType,
    groupCodesForTypeComputed,
    allGroupCodes,
  }
}
