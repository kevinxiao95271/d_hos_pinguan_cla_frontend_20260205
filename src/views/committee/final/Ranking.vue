<template>
  <div class="ranking-page">
    <StageProgress :stages="stagesList" current-stage="FINAL" simple />

    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span class="title">现场竞赛排名</span>
          <div class="header-actions">
            <el-button type="warning" :loading="computing" @click="handleCompute">
              计算现场排名
            </el-button>
            <el-button type="danger" :loading="computingTotal" @click="handleComputeTotal">
              计算综合总分
            </el-button>
            <el-button type="success" :loading="exporting" @click="handleExport">
              导出 Excel
            </el-button>
            <el-button type="primary" plain size="small" @click="loadRanking">刷新</el-button>
          </div>
        </div>
      </template>

      <el-empty
        v-if="allRanking.length === 0 && !loading"
        description="暂无排名数据，请先确保各专场评委已全部提交评分，然后点击「重新计算排名」"
        :image-size="100"
      />

      <el-tabs v-else v-model="activeDate" type="border-card">
        <el-tab-pane
          v-for="date in dateOptions"
          :key="date"
          :label="`${date} (${byDate[date]?.length || 0}项)`"
          :name="date"
        >
          <div
            v-for="session in sessionsByDate[date]"
            :key="session"
            class="session-block"
          >
            <div class="session-title">{{ session }}</div>
            <el-table :data="byDateSession[date]?.[session] || []" border stripe size="small">
              <el-table-column label="排名" width="64" align="center">
                <template #default="{ row }">
                  <span :class="['rank-badge', `rank-${row.rank}`]">{{ row.rank }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="registrationCode" label="项目编号" width="90" align="center" />
              <el-table-column prop="projectName" label="项目名称" min-width="180" show-overflow-tooltip />
              <el-table-column prop="institutionName" label="参赛机构" width="150" show-overflow-tooltip />
              <el-table-column label="类型" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="scoreFormTagType(row.scoreForm)" size="small">
                    {{ scoreFormText(row.scoreForm) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="现场均分" width="90" align="center">
                <template #default="{ row }">
                  <span class="avg-score">{{ formatScore(row.trimmedAvg) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="书审/面谈D" width="100" align="center">
                <template #default="{ row }">
                  <span>{{ row.bookReviewScore != null ? formatScore(row.bookReviewScore) : '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="综合总分" width="90" align="center">
                <template #default="{ row }">
                  <span class="total-score">{{ row.totalScore != null ? formatScore(row.totalScore) : '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="总分排名" width="80" align="center">
                <template #default="{ row }">
                  <span v-if="row.totalRank" :class="['rank-badge', `rank-${row.totalRank}`]">{{ row.totalRank }}</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="评委数" width="64" align="center">
                <template #default="{ row }">
                  <el-tag type="info" size="small">{{ row.judgeCount }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="note" label="备注" min-width="120" show-overflow-tooltip>
                <template #default="{ row }">
                  <span class="note-text">{{ row.note }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'
import { getCurrentCompetitionId, getCurrentCompetitionIdSync } from '@/utils/competition'
import { computeFinalRanking, computeTotalFinalRanking, exportFinalRanking, getFinalRanking } from '@/api/admin'

// ── 工具 ──────────────────────────────────────────────────
const formatScore = (val) => val == null ? '-' : Number(val).toFixed(2)
const scoreFormTagType = (form) => form === 'QCC' ? 'primary' : form === 'QFD' ? 'warning' : 'success'
const scoreFormText = (form) => form === 'NON_QCC' ? '非QCC' : (form || '-')

// ── 状态 ─────────────────────────────────────────────────
const { stagesList } = useCompetitionStages()
const competitionId = ref(getCurrentCompetitionIdSync())
const allRanking = ref([])
const loading = ref(false)
const computing = ref(false)
const computingTotal = ref(false)
const exporting = ref(false)
const activeDate = ref('')

// ── 按日期分层 computed ───────────────────────────────────
// 保持日期顺序稳定（按首次出现顺序）
const dateOptions = computed(() => {
  const seen = new Set()
  for (const r of allRanking.value) {
    if (r.sessionDate && !seen.has(r.sessionDate)) seen.add(r.sessionDate)
  }
  return [...seen]
})

// byDate[date] = 该日期所有条目
const byDate = computed(() => {
  const map = {}
  for (const r of allRanking.value) {
    const d = r.sessionDate || '未知'
    if (!map[d]) map[d] = []
    map[d].push(r)
  }
  return map
})

// sessionsByDate[date] = 该日期内的有序场次列表
const sessionsByDate = computed(() => {
  const map = {}
  for (const r of allRanking.value) {
    const d = r.sessionDate || '未知'
    if (!map[d]) map[d] = []
    if (!map[d].includes(r.sessionCode)) map[d].push(r.sessionCode)
  }
  return map
})

// byDateSession[date][sessionCode] = 该场次排名列表
const byDateSession = computed(() => {
  const map = {}
  for (const r of allRanking.value) {
    const d = r.sessionDate || '未知'
    if (!map[d]) map[d] = {}
    if (!map[d][r.sessionCode]) map[d][r.sessionCode] = []
    map[d][r.sessionCode].push(r)
  }
  return map
})

// ── 数据加载 ──────────────────────────────────────────────
const loadRanking = async () => {
  if (!competitionId.value) return
  loading.value = true
  try {
    const res = await getFinalRanking(competitionId.value)
    allRanking.value = res.success ? (res.data || []) : []
    if (!res.success) ElMessage.error(res.message || '加载排名失败')
    // 默认激活第一个日期 tab
    if (dateOptions.value.length) activeDate.value = dateOptions.value[0]
  } catch {
    ElMessage.error('加载排名失败')
    allRanking.value = []
  } finally {
    loading.value = false
  }
}

// ── 重新计算 ──────────────────────────────────────────────
const handleCompute = async () => {
  try {
    await ElMessageBox.confirm(
      '将重新计算所有专场排名（先清除旧快照），确认继续？',
      '重新计算排名',
      { confirmButtonText: '确认计算', cancelButtonText: '取消', type: 'warning' }
    )
    computing.value = true
    const res = await computeFinalRanking(competitionId.value)
    if (res.success) {
      ElMessage.success(res.data || '排名计算完成')
      await loadRanking()
    } else {
      ElMessage.error(res.message || '计算失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('计算失败，请检查网络')
  } finally {
    computing.value = false
  }
}

// ── 综合总分计算 ───────────────────────────────────────────
const handleComputeTotal = async () => {
  try {
    await ElMessageBox.confirm(
      '将基于现场均分 + 书审/面谈D值计算综合总分，请确保现场排名已先行计算，确认继续？',
      '计算综合总分',
      { confirmButtonText: '确认计算', cancelButtonText: '取消', type: 'warning' }
    )
    computingTotal.value = true
    const res = await computeTotalFinalRanking(competitionId.value)
    if (res.success) {
      ElMessage.success(res.data || '综合总分计算完成')
      await loadRanking()
    } else {
      ElMessage.error(res.message || '计算失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('计算失败，请检查网络')
  } finally {
    computingTotal.value = false
  }
}

// ── 导出 ──────────────────────────────────────────────────
const handleExport = async () => {
  exporting.value = true
  try {
    const blob = await exportFinalRanking(competitionId.value)
    const url = URL.createObjectURL(blob instanceof Blob ? blob : new Blob([blob]))
    const a = document.createElement('a')
    a.href = url
    a.download = '现场竞赛排名_全场.xlsx'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch {
    ElMessage.error('导出失败，请检查网络')
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  const id = await getCurrentCompetitionId()
  if (id) competitionId.value = id
  await loadRanking()
})
</script>

<style scoped lang="scss">
.ranking-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;

  .title {
    font-size: 15px;
    font-weight: 600;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.session-block {
  margin-bottom: 28px;

  .session-title {
    font-size: 14px;
    font-weight: 700;
    color: #303133;
    padding: 6px 0 8px;
    border-bottom: 2px solid #409eff;
    margin-bottom: 10px;
  }
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 700;
  background: #f5f7fa;
  color: #606266;

  &.rank-1 { background: #fff3cd; color: #856404; font-size: 15px; box-shadow: 0 0 0 2px #ffc10760; }
  &.rank-2 { background: #e8f4ff; color: #1677ff; box-shadow: 0 0 0 2px #409eff40; }
  &.rank-3 { background: #f0f9eb; color: #389e0d; box-shadow: 0 0 0 2px #67c23a40; }
}

.score-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;

  .total-score {
    font-size: 17px;
    font-weight: 700;
    color: #e6a23c;
  }

  .avg-score {
    font-size: 17px;
    font-weight: 700;
    color: #409eff;
    line-height: 1;
  }
}

.note-text {
  font-size: 12px;
  color: #909399;
}
</style>
