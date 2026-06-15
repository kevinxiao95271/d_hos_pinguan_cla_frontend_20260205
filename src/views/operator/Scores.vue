<template>
  <div class="operator-scores-page">
    <!-- 顶部操作栏 -->
    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="page-title">会场评分管理</span>
          <el-select
            v-model="selectedSession"
            placeholder="全部会场"
            clearable
            style="width: 260px"
          >
            <el-option label="全部会场" value="" />
            <el-option v-for="s in sessionOptions" :key="s" :label="s" :value="s" />
          </el-select>
          <el-input
            v-model="reviewerKeyword"
            placeholder="专家姓名搜索"
            clearable
            style="width: 160px"
          />
        </div>
        <div class="toolbar-right">
          <el-button :loading="loading" @click="loadScores">刷新</el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计摘要 -->
    <div class="stat-row">
      <el-card class="stat-card">
        <div class="stat-num">{{ stats.total }}</div>
        <div class="stat-label">总任务数</div>
      </el-card>
      <el-card class="stat-card scored">
        <div class="stat-num">{{ stats.scored }}</div>
        <div class="stat-label">已提交</div>
      </el-card>
      <el-card class="stat-card draft">
        <div class="stat-num">{{ stats.draft }}</div>
        <div class="stat-label">草稿</div>
      </el-card>
      <el-card class="stat-card pending">
        <div class="stat-num">{{ stats.pending }}</div>
        <div class="stat-label">待评分</div>
      </el-card>
      <el-card class="stat-card recused">
        <div class="stat-num">{{ stats.recused }}</div>
        <div class="stat-label">已回避</div>
      </el-card>
    </div>

    <!-- 按会场分组展示 -->
    <div v-loading="loading">
      <el-empty
        v-if="!loading && displayedSessions.length === 0"
        description="暂无数据"
        :image-size="80"
      />

      <div v-for="session in displayedSessions" :key="session" class="session-block">
        <div class="session-header">
          <span class="session-name">{{ session }}</span>
          <el-tag type="info" size="small">{{ groupedScores[session]?.length }} 条</el-tag>
        </div>
        <el-table :data="groupedScores[session]" border stripe size="small">
          <el-table-column prop="sessionOrder" label="顺序" width="55" align="center" />
          <el-table-column prop="projectName" label="项目名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="institutionName" label="参赛机构" width="150" show-overflow-tooltip />
          <el-table-column prop="scoreForm" label="类型" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="scoreFormTagType(row.scoreForm)" size="small">{{ row.scoreForm === 'NON_QCC' ? '非QCC' : row.scoreForm }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reviewerName" label="评审专家" width="90" show-overflow-tooltip />
          <el-table-column prop="reviewerPhone" label="联系电话" width="120" />
          <el-table-column label="状态" width="85" align="center">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="总分" width="70" align="center">
            <template #default="{ row }">
              <span v-if="row.total != null" class="score-val">{{ row.total }}</span>
              <span v-else class="score-empty">-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ row }">
              <el-button
                v-if="row.status === 'SCORED' || row.status === 'DRAFT'"
                type="danger"
                link
                size="small"
                @click="handleReject(row)"
              >
                驳回
              </el-button>
              <span v-else class="score-empty">-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFinalScores, rejectFinalScore } from '@/api/admin'
import { getCurrentCompetitionId, getCurrentCompetitionIdSync } from '@/utils/competition'

const competitionId = ref(getCurrentCompetitionIdSync())
const allScores = ref([])
const loading = ref(false)
const selectedSession = ref('')
const reviewerKeyword = ref('')

// ── 会场选项（保持顺序）──────────────────────────────────────
const sessionOptions = computed(() => {
  const seen = new Set()
  for (const r of allScores.value) {
    if (!seen.has(r.sessionCode)) seen.add(r.sessionCode)
  }
  return [...seen]
})

// ── 过滤后的数据 ─────────────────────────────────────────────
const filteredScores = computed(() => {
  let list = allScores.value
  if (selectedSession.value) list = list.filter(r => r.sessionCode === selectedSession.value)
  if (reviewerKeyword.value.trim()) {
    const kw = reviewerKeyword.value.trim()
    list = list.filter(r => r.reviewerName && r.reviewerName.includes(kw))
  }
  return list
})

// ── 展示的会场列表 ────────────────────────────────────────────
const displayedSessions = computed(() => {
  if (selectedSession.value) return [selectedSession.value]
  return sessionOptions.value
})

// ── 按 sessionCode 分组 ───────────────────────────────────────
const groupedScores = computed(() => {
  const map = {}
  for (const r of filteredScores.value) {
    if (!map[r.sessionCode]) map[r.sessionCode] = []
    map[r.sessionCode].push(r)
  }
  return map
})

// ── 统计 ─────────────────────────────────────────────────────
const stats = computed(() => {
  const rows = filteredScores.value
  return {
    total:   rows.length,
    scored:  rows.filter(r => r.status === 'SCORED').length,
    draft:   rows.filter(r => r.status === 'DRAFT').length,
    pending: rows.filter(r => r.status === 'PENDING').length,
    recused: rows.filter(r => r.status === 'RECUSED').length
  }
})

// ── 样式工具 ─────────────────────────────────────────────────
const scoreFormTagType = (f) => f === 'QCC' ? 'primary' : f === 'QFD' ? 'warning' : 'success'

const statusText = (s) => ({ PENDING: '待评分', DRAFT: '草稿', SCORED: '已提交', RECUSED: '已回避' }[s] || s)
const statusTagType = (s) => ({ PENDING: 'info', DRAFT: 'warning', SCORED: 'success', RECUSED: '' }[s] || 'info')

// ── 加载数据 ─────────────────────────────────────────────────
const loadScores = async () => {
  if (!competitionId.value) return
  loading.value = true
  try {
    const res = await getFinalScores(competitionId.value)
    allScores.value = res.success ? (res.data || []) : []
    if (!res.success) ElMessage.error(res.message || '加载失败')
  } catch {
    ElMessage.error('加载失败，请检查网络')
    allScores.value = []
  } finally {
    loading.value = false
  }
}

// ── 驳回 ─────────────────────────────────────────────────────
const handleReject = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认驳回「${row.reviewerName}」对「${row.projectName}」的评分？驳回后评委需重新提交评分。`,
      '驳回确认',
      { confirmButtonText: '确认驳回', cancelButtonText: '取消', type: 'warning', confirmButtonClass: 'el-button--danger' }
    )
    const res = await rejectFinalScore(row.taskId)
    if (res.success) {
      ElMessage.success('驳回成功，任务已重置为待评分')
      await loadScores()
    } else {
      ElMessage.error(res.message || '驳回失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败，请检查网络')
  }
}

onMounted(async () => {
  const id = await getCurrentCompetitionId()
  if (id) competitionId.value = id
  loadScores()
})
</script>

<style scoped lang="scss">
.operator-scores-page {
  padding: 20px;
}

.toolbar-card {
  margin-bottom: 16px;
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;

    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 12px;
      .page-title {
        font-size: 16px;
        font-weight: 700;
        white-space: nowrap;
      }
    }
  }
}

.stat-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;

  .stat-card {
    flex: 1;
    min-width: 90px;
    text-align: center;
    cursor: default;

    .stat-num {
      font-size: 28px;
      font-weight: 700;
      color: #303133;
      line-height: 1;
      margin-bottom: 4px;
    }
    .stat-label {
      font-size: 12px;
      color: #909399;
    }

    &.scored .stat-num  { color: #67c23a; }
    &.draft .stat-num   { color: #e6a23c; }
    &.pending .stat-num { color: #909399; }
    &.recused .stat-num { color: #f56c6c; }
  }
}

.session-block {
  margin-bottom: 24px;

  .session-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0 8px;
    border-bottom: 2px solid #409eff;
    margin-bottom: 10px;

    .session-name {
      font-size: 14px;
      font-weight: 700;
      color: #303133;
    }
  }
}

.score-val  { font-weight: 700; color: #409eff; }
.score-empty { color: #c0c4cc; }
</style>
