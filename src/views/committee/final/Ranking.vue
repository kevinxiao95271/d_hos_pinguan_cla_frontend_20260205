<template>
  <div class="ranking-page">
    <StageProgress :stages="stagesList" current-stage="FINAL" simple />

    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>现场竞赛最终排名</span>
          <div class="header-actions">
            <el-button type="warning" :loading="computing" @click="handleCompute">
              重新计算排名
            </el-button>
            <el-button type="success" :loading="exporting" @click="handleExport">
              导出 Excel
            </el-button>
            <el-button type="primary" plain size="small" @click="loadRanking">刷新</el-button>
          </div>
        </div>
      </template>

      <el-empty
        v-if="ranking.length === 0 && !loading"
        description="暂无排名数据，请先确保各专场评委已全部提交评分，然后点击「重新计算排名」"
        :image-size="100"
      />

      <el-table v-else :data="ranking" border stripe>

        <!-- 排名 -->
        <el-table-column label="排名" width="70" align="center" fixed>
          <template #default="{ row }">
            <span :class="['rank-badge', `rank-${row.rank}`]">{{ row.rank }}</span>
          </template>
        </el-table-column>

        <!-- 项目名称 -->
        <el-table-column prop="projectName" label="项目名称" min-width="200" show-overflow-tooltip />

        <!-- 机构 -->
        <el-table-column prop="institutionName" label="参赛机构" width="160" show-overflow-tooltip />

        <!-- 专场 -->
        <el-table-column prop="sessionCode" label="所属专场" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="session-tag">{{ row.sessionCode }}</span>
          </template>
        </el-table-column>

        <!-- 上台顺序 -->
        <el-table-column prop="sessionOrder" label="上台顺序" width="80" align="center" />

        <!-- 评分表类型 + 去极值均分（核心信息并排） -->
        <el-table-column label="类型 / 均分" width="160" align="center">
          <template #default="{ row }">
            <div class="score-cell">
              <el-tag :type="scoreFormTagType(row.scoreForm)" size="small" class="form-tag">
                {{ scoreFormText(row.scoreForm) }}
              </el-tag>
              <span class="avg-score">{{ formatScore(row.trimmedAvg) }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- 参与评委数 -->
        <el-table-column label="评委数" width="70" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.judgeCount }}</el-tag>
          </template>
        </el-table-column>

        <!-- 备注 -->
        <el-table-column prop="note" label="备注" min-width="190" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="note-text">{{ row.note }}</span>
          </template>
        </el-table-column>

      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'
import { getCurrentCompetitionId, getCurrentCompetitionIdSync } from '@/utils/competition'
import { computeFinalRanking, exportFinalRanking, getFinalRankingMixed } from '@/api/admin'

const { stagesList } = useCompetitionStages()
const competitionId = ref(getCurrentCompetitionIdSync())

const ranking = ref([])
const loading = ref(false)
const computing = ref(false)
const exporting = ref(false)

const loadRanking = async () => {
  if (!competitionId.value) return
  loading.value = true
  try {
    const res = await getFinalRankingMixed(competitionId.value)
    ranking.value = res.success ? (res.data || []) : []
    if (!res.success) ElMessage.error(res.message || '加载排名失败')
  } catch {
    ElMessage.error('加载排名失败')
    ranking.value = []
  } finally {
    loading.value = false
  }
}

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

const handleExport = async () => {
  exporting.value = true
  try {
    const blob = await exportFinalRanking(competitionId.value)
    const url = URL.createObjectURL(blob instanceof Blob ? blob : new Blob([blob]))
    const a = document.createElement('a')
    a.href = url
    a.download = '现场竞赛排名.xlsx'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch {
    ElMessage.error('导出失败，请检查网络')
  } finally {
    exporting.value = false
  }
}

const formatScore = (val) => val == null ? '-' : Number(val).toFixed(2)

const scoreFormTagType = (form) => {
  if (form === 'QCC') return 'primary'
  if (form === 'QFD') return 'warning'
  return 'success'
}

const scoreFormText = (form) => {
  if (form === 'NON_QCC') return '非QCC'
  return form || '-'
}

onMounted(async () => {
  const id = await getCurrentCompetitionId()
  if (id) competitionId.value = id
  loadRanking()
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
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 700;
  background: #f5f7fa;
  color: #606266;

  &.rank-1 { background: #fff3cd; color: #856404; font-size: 16px; box-shadow: 0 0 0 2px #ffc10760; }
  &.rank-2 { background: #e8f4ff; color: #1677ff; box-shadow: 0 0 0 2px #409eff40; }
  &.rank-3 { background: #f0f9eb; color: #389e0d; box-shadow: 0 0 0 2px #67c23a40; }
}

.session-tag {
  font-size: 12px;
  color: #909399;
}

.score-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;

  .form-tag {
    font-size: 11px;
  }

  .avg-score {
    font-size: 18px;
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
