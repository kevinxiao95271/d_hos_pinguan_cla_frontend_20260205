import { ref } from 'vue'
import { computeRanking, getComputeRankingStatus } from '@/api/shortlist'

const POLL_INTERVAL = 2000   // 每 2 秒轮询一次
const MAX_WAIT_MS  = 120000  // 最多等待 2 分钟

/**
 * 封装异步算分 + 轮询逻辑
 *
 * @param {Function} onSuccess - (snapshotCount: number) => void  计算成功回调
 * @param {Function} [onError]  - (errMsg: string) => void        失败回调（可选）
 *
 * 返回：
 *   computing    - Ref<Boolean>  按钮 loading 状态
 *   statusText   - Ref<String>   进度文案（可直接绑定到页面）
 *   progress     - Ref<Number>   进度百分比 0~100
 *   progressMsg  - Ref<String>   后端返回的进度阶段描述
 *   triggerCompute(data)         触发计算，data = { competitionId, stage, groupType?, interviewOnly? }
 */
export function useComputeRanking(onSuccess, onError) {
  const computing   = ref(false)
  const statusText  = ref('')
  const progress    = ref(0)
  const progressMsg = ref('')
  let pollTimer     = null
  let startTime     = 0

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  function startPolling(jobId) {
    startTime = Date.now()
    pollTimer = setInterval(async () => {
      // 超时保护
      if (Date.now() - startTime > MAX_WAIT_MS) {
        stopPolling()
        computing.value  = false
        statusText.value = '等待超时，请稍后手动刷新'
        onError?.('等待超时')
        return
      }

      try {
        const res = await getComputeRankingStatus(jobId)
        if (!res.success) {
          stopPolling()
          computing.value  = false
          statusText.value = `查询失败：${res.message}`
          onError?.(res.message)
          return
        }

        const { status, snapshotCount, error, progress: pct, progressMsg: pMsg } = res.data
        if (pct != null)  progress.value    = pct
        if (pMsg != null) progressMsg.value = pMsg

        if (status === 'SUCCESS') {
          stopPolling()
          computing.value   = false
          progress.value    = 100
          progressMsg.value = 'SUCCESS'
          statusText.value  = `计算完成，共写入 ${snapshotCount} 条快照`
          onSuccess?.(snapshotCount)
        } else if (status === 'FAILED') {
          stopPolling()
          computing.value   = false
          statusText.value  = `计算失败：${error}`
          onError?.(error)
        }
        // RUNNING：继续等待，不做任何操作
      } catch (e) {
        stopPolling()
        computing.value   = false
        statusText.value  = `网络异常：${e.message}`
        onError?.(e.message)
      }
    }, POLL_INTERVAL)
  }

  async function triggerCompute(data) {
    if (computing.value) return
    computing.value   = true
    progress.value    = 0
    progressMsg.value = '任务已启动'
    statusText.value  = '正在提交任务...'

    try {
      const res = await computeRanking(data)
      if (!res.success) {
        computing.value  = false
        statusText.value = `提交失败：${res.message}`
        onError?.(res.message)
        return
      }

      const jobId = res.data?.jobId
      if (!jobId) {
        // 兼容旧版（直接返回 integer）
        const count = typeof res.data === 'number' ? res.data : null
        computing.value  = false
        statusText.value = count != null ? `计算完成，共写入 ${count} 条快照` : '计算完成'
        onSuccess?.(count)
        return
      }

      statusText.value  = '计算中，请稍候...'
      progressMsg.value = '初始化中...'
      startPolling(jobId)
    } catch (e) {
      computing.value  = false
      statusText.value = `提交失败：${e.message}`
      onError?.(e.message)
    }
  }

  return { computing, statusText, progress, progressMsg, triggerCompute }
}
