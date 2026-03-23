import { ref, computed, onMounted } from 'vue'
import { getCompetition } from '@/api/competition'
import { getCurrentCompetitionId } from '@/utils/competition'
import { toProgressStageKey } from '@/utils/competitionStage'

/**
 * 获取赛事阶段信息的 composable
 * 用于跑马灯展示
 */
export function useCompetitionStages() {
  const competition = ref({})

  const stagesList = computed(() => {
    const comp = competition.value
    return [
      { 
        key: 'REGISTRATION', 
        title: '报名', 
        startDate: comp.registerStart || null, 
        endDate: comp.registerEnd || null
      },
      { 
        key: 'BOOK', 
        title: '书审', 
        startDate: comp.bookReviewStart || null, 
        endDate: comp.bookReviewEnd || null
      },
      { 
        key: 'INTERVIEW', 
        title: '面谈', 
        startDate: comp.interviewStart || null, 
        endDate: comp.interviewEnd || null
      },
      { 
        key: 'FINAL', 
        title: '决赛', 
        startDate: comp.finalStart || null, 
        endDate: comp.finalEnd || null
      }
    ]
  })

  /** 供 StageProgress：兼容 BOOK_REVIEW 等与后端 stage 枚举 */
  const currentStageKey = computed(() => {
    const comp = competition.value
    const raw = comp.stage ?? comp.currentStage
    return toProgressStageKey(raw)
  })

  const loadCompetition = async () => {
    const competitionId = await getCurrentCompetitionId()
    if (!competitionId) {
      console.warn('⚠️ 未找到当前赛事ID')
      return
    }
    
    try {
      const res = await getCompetition(competitionId)
      if (res.success && res.data) {
        competition.value = res.data
        console.log('✅ 加载赛事信息:', res.data.name)
      }
    } catch (error) {
      console.error('❌ 加载赛事信息失败:', error)
    }
  }

  onMounted(() => {
    loadCompetition()
  })

  return {
    competition,
    stagesList,
    currentStageKey,
    loadCompetition
  }
}
