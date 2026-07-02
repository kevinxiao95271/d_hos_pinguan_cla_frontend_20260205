<template>
  <div class="ranking-page">
    <StageProgress simple />

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
            <el-button type="warning" plain @click="openBatchCert" :disabled="allRanking.length === 0">
              生成奖状
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

      <div v-if="allRanking.length > 0" class="sort-bar">
        <span class="sort-label">排序方式：</span>
        <el-radio-group v-model="sortMode" size="small">
          <el-radio-button value="natural">自然顺序</el-radio-button>
          <el-radio-button value="rank">按现场均分 ↓</el-radio-button>
          <el-radio-button value="total">按综合总分 ↓</el-radio-button>
        </el-radio-group>
      </div>

      <el-tabs v-if="allRanking.length > 0" v-model="activeDate" type="border-card">
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
              <el-table-column label="排名" width="56" align="center">
                <template #default="{ row }">
                  <span :class="['rank-badge', `rank-${row.rank}`]">{{ row.rank }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="registrationCode" label="编号" width="72" align="center" />
              <el-table-column prop="projectName" label="项目名称" min-width="160" show-overflow-tooltip />
              <el-table-column prop="institutionName" label="参赛机构" width="140" show-overflow-tooltip />
              <el-table-column label="类型" width="72" align="center">
                <template #default="{ row }">
                  <el-tag :type="scoreFormTagType(row.scoreForm)" size="small">
                    {{ scoreFormText(row.scoreForm) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="书审D" width="78" align="center">
                <template #default="{ row }">
                  <span>{{ row.bookScoreD != null ? formatScore(row.bookScoreD) : '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="面谈D" width="78" align="center">
                <template #default="{ row }">
                  <span>{{ row.interviewScoreD != null ? formatScore(row.interviewScoreD) : '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="现场均分" width="82" align="center">
                <template #default="{ row }">
                  <span class="avg-score">{{ formatScore(row.trimmedAvg) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="得分算式" min-width="220" show-overflow-tooltip>
                <template #default="{ row }">
                  <span v-if="row.scoreFormula" class="formula-text">{{ row.scoreFormula }}</span>
                  <span v-else class="text-muted">-</span>
                </template>
              </el-table-column>
              <el-table-column label="综合总分" width="86" align="center">
                <template #default="{ row }">
                  <span class="total-score">{{ row.totalScore != null ? formatScore(row.totalScore) : '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="总分排名" width="76" align="center">
                <template #default="{ row }">
                  <span v-if="row.totalRank" :class="['rank-badge', `rank-${row.totalRank}`]">{{ row.totalRank }}</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="奖项" width="72" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.awardLevel === 'GOLD'"   type="warning" effect="dark" size="small">🥇 金奖</el-tag>
                  <el-tag v-else-if="row.awardLevel === 'SILVER'" type="info"    effect="dark" size="small" style="background:#8c9eb0;border-color:#8c9eb0">🥈 银奖</el-tag>
                  <el-tag v-else-if="row.awardLevel === 'BRONZE'" effect="dark"  size="small" style="background:#b87333;border-color:#b87333;color:#fff">🥉 铜奖</el-tag>
                  <el-tag v-else type="success" size="small">佳作奖</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="评委数" width="60" align="center">
                <template #default="{ row }">
                  <el-tag type="info" size="small">{{ row.judgeCount }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="note" label="备注" min-width="100" show-overflow-tooltip>
                <template #default="{ row }">
                  <span class="note-text">{{ row.note }}</span>
                </template>
              </el-table-column>
              <el-table-column label="奖状" width="80" align="center">
                <template #default="{ row }">
                  <el-button
                    v-if="row.awardLevel"
                    type="warning"
                    size="small"
                    plain
                    @click="openSingleCert(row)"
                  >奖状</el-button>
                  <span v-else style="color:#c0c4cc">-</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <CertificateDialog
      v-model="certVisible"
      :row="certRow"
      :list="certBatch ? allRanking : []"
      :competition-name="competitionName"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import CertificateDialog from '@/components/CertificateDialog.vue'
import { getCurrentCompetitionId, getCurrentCompetitionIdSync } from '@/utils/competition'
import { computeFinalRanking, computeTotalFinalRanking, exportFinalRanking, getFinalRanking } from '@/api/admin'
import { getCurrentCompetition } from '@/api/competition'

// ── 工具 ──────────────────────────────────────────────────
const formatScore = (val) => val == null ? '-' : Number(val).toFixed(2)
const scoreFormTagType = (form) => form === 'QCC' ? 'primary' : form === 'QFD' ? 'warning' : 'success'
const scoreFormText = (form) => form === 'NON_QCC' ? '非QCC' : (form || '-')

// ── 状态 ─────────────────────────────────────────────────
const competitionId = ref(getCurrentCompetitionIdSync())
const allRanking = ref([])
const loading = ref(false)
const computing = ref(false)
const computingTotal = ref(false)
const exporting = ref(false)
const activeDate = ref('')
const competitionName = ref('浙江省医院品管大赛')

// 证书弹窗
const certVisible = ref(false)
const certRow = ref(null)
const certBatch = ref(false)

const openSingleCert = (row) => {
  certRow.value = row
  certBatch.value = false
  certVisible.value = true
}
const openBatchCert = () => {
  certRow.value = null
  certBatch.value = true
  certVisible.value = true
}
// 排序模式：natural=自然顺序 | rank=按现场均分 | total=按综合总分
const sortMode = ref('total')

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

// byDateSession[date][sessionCode] = 该场次排名列表（按 sortMode 排序）
const byDateSession = computed(() => {
  const map = {}
  for (const r of allRanking.value) {
    const d = r.sessionDate || '未知'
    if (!map[d]) map[d] = {}
    if (!map[d][r.sessionCode]) map[d][r.sessionCode] = []
    map[d][r.sessionCode].push(r)
  }
  // 对每个专场内的数据按排序模式重排
  const sortFn = sortMode.value === 'rank'
    ? (a, b) => (a.rank ?? 999) - (b.rank ?? 999)
    : sortMode.value === 'total'
      ? (a, b) => (a.totalRank ?? 999) - (b.totalRank ?? 999)
      : (a, b) => (a.sessionOrder ?? 999) - (b.sessionOrder ?? 999)
  for (const d of Object.keys(map)) {
    for (const s of Object.keys(map[d])) {
      map[d][s] = [...map[d][s]].sort(sortFn)
    }
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
    a.download = `现场竞赛排名_${dayjs().format('YYYYMMDD_HHmm')}.xlsx`
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
  try {
    const res = await getCurrentCompetition()
    if (res.success && res.data?.name) competitionName.value = res.data.name
  } catch {}
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

  .sort-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 4px 14px;

    .sort-label {
      font-size: 13px;
      color: #606266;
      white-space: nowrap;
    }
  }

  .formula-text {
    font-size: 12px;
    color: #606266;
    font-family: monospace;
  }

  .text-muted {
    color: #c0c4cc;
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
