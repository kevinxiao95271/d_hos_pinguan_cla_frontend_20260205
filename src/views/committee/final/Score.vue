<template>
  <div class="score-page">
    <StageProgress :stages="stagesList" current-stage="FINAL" simple />

    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>现场打分汇总</span>
          <div class="header-actions">
            <!-- 专场筛选 -->
            <el-select
              v-model="filterSession"
              placeholder="全部专场"
              clearable
              style="width: 240px"
              @change="loadScores"
            >
              <el-option
                v-for="s in sessions"
                :key="s.sessionCode"
                :label="s.sessionCode"
                :value="s.sessionCode"
              />
            </el-select>
            <el-button type="primary" plain size="small" @click="loadScores">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 统计摘要 -->
      <el-row :gutter="12" class="summary-row">
        <el-col :span="6">
          <div class="stat-card">
            <span class="stat-val">{{ scores.length }}</span>
            <span class="stat-lbl">总任务数</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card pending">
            <span class="stat-val">{{ countByStatus('PENDING') }}</span>
            <span class="stat-lbl">待评分</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card draft">
            <span class="stat-val">{{ countByStatus('DRAFT') }}</span>
            <span class="stat-lbl">草稿</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card scored">
            <span class="stat-val">{{ countByStatus('SCORED') }}</span>
            <span class="stat-lbl">已提交</span>
          </div>
        </el-col>
      </el-row>

      <el-table v-top-scrollbar :data="scores" border stripe max-height="600">
        <el-table-column prop="sessionCode" label="专场" min-width="180" show-overflow-tooltip />
        <el-table-column prop="sessionOrder" label="顺序" width="60" align="center" />
        <el-table-column prop="projectName" label="项目名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="institutionName" label="参赛机构" width="150" show-overflow-tooltip />
        <el-table-column prop="groupCode" label="组别" width="70" align="center" />
        <el-table-column prop="reviewerName" label="评审专家" width="100" show-overflow-tooltip />
        <el-table-column prop="scoreForm" label="评分表" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="scoreFormTagType(row.scoreForm)" size="small">{{ row.scoreForm }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'SCORED'" type="success" size="small">已提交</el-tag>
            <el-tag v-else-if="row.status === 'DRAFT'" type="primary" size="small">草稿</el-tag>
            <el-tag v-else type="info" size="small">待评分</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="总分" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.total != null" class="score-value">{{ row.total }}</span>
            <span v-else class="score-empty">-</span>
          </template>
        </el-table-column>

        <el-table-column label="详细评分" width="80" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.scoreItems?.length"
              link
              type="primary"
              size="small"
              @click="showDetail(row)"
            >
              查看
            </el-button>
            <span v-else class="score-empty">-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 详细评分弹窗 -->
    <el-dialog v-model="detailVisible" :title="`评分详情 — ${detailRow?.projectName}`" width="500px">
      <template v-if="detailRow">
        <!-- 头部：评分表类型 + 总分 -->
        <div class="detail-header">
          <div class="detail-meta">
            <el-tag :type="scoreFormTagType(detailRow.scoreForm)" size="default">
              {{ detailRow.scoreForm === 'NON_QCC' ? '非QCC' : detailRow.scoreForm }}
            </el-tag>
            <span class="detail-institution">{{ detailRow.institutionName }}</span>
          </div>
          <div class="detail-total">
            总分 <span class="detail-total-val">{{ detailRow.total }}</span> 分
          </div>
        </div>

        <!-- 细节分列表（直接遍历 scoreItems） -->
        <div class="score-items-list">
          <div
            v-for="item in detailRow.scoreItems"
            :key="item.label"
            class="score-item-row"
          >
            <span class="si-label">{{ item.label }}</span>
            <div class="si-bar-wrap">
              <div
                class="si-bar"
                :style="{ width: (item.score / item.maxScore * 100) + '%' }"
              />
            </div>
            <span class="si-score">{{ item.score }}</span>
            <span class="si-max">/ {{ item.maxScore }}</span>
          </div>
        </div>

        <!-- 亮点 / 不足 -->
        <template v-if="detailRow.draftScore">
          <div v-if="detailRow.draftScore.highlight" class="opinion-block">
            <div class="opinion-label">亮点意见</div>
            <div class="opinion-content">{{ detailRow.draftScore.highlight }}</div>
          </div>
          <div v-if="detailRow.draftScore.weakness" class="opinion-block">
            <div class="opinion-label">不足意见</div>
            <div class="opinion-content">{{ detailRow.draftScore.weakness }}</div>
          </div>
        </template>
      </template>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'
import { getCurrentCompetitionId, getCurrentCompetitionIdSync } from '@/utils/competition'
import { getFinalScores, getFinalSessions } from '@/api/admin'

const { stagesList } = useCompetitionStages()
const competitionId = ref(getCurrentCompetitionIdSync())

const sessions = ref([])
const scores = ref([])
const loading = ref(false)
const filterSession = ref('')

const countByStatus = (status) => scores.value.filter(s => s.status === status).length

const loadSessions = async () => {
  if (!competitionId.value) return
  try {
    const res = await getFinalSessions(competitionId.value)
    sessions.value = res.success ? (res.data || []) : []
  } catch { /* ignore */ }
}

const loadScores = async () => {
  if (!competitionId.value) return
  loading.value = true
  try {
    const res = await getFinalScores(competitionId.value, filterSession.value || undefined)
    scores.value = res.success ? (res.data || []) : []
    if (!res.success) ElMessage.error(res.message || '加载评分数据失败')
  } catch {
    ElMessage.error('加载评分数据失败')
    scores.value = []
  } finally {
    loading.value = false
  }
}

const scoreFormTagType = (form) => {
  if (form === 'QCC') return 'primary'
  if (form === 'QFD') return 'warning'
  return 'success'
}

// 详情弹窗
const detailVisible = ref(false)
const detailRow = ref(null)

const showDetail = (row) => {
  detailRow.value = row
  detailVisible.value = true
}

onMounted(async () => {
  const id = await getCurrentCompetitionId()
  if (id) competitionId.value = id
  await Promise.all([loadSessions(), loadScores()])
})
</script>

<style scoped lang="scss">
.score-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.summary-row {
  margin-bottom: 16px;
}

.stat-card {
  background: #fff;
  border: 1px solid #edf0f5;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-top: 3px solid #909399;
  .stat-val { font-size: 24px; font-weight: 700; color: #909399; }
  .stat-lbl { font-size: 12px; color: #909399; }
  &.pending { border-top-color: #e6a23c; .stat-val { color: #e6a23c; } }
  &.draft   { border-top-color: #409eff; .stat-val { color: #409eff; } }
  &.scored  { border-top-color: #67c23a; .stat-val { color: #67c23a; } }
}

.score-value {
  font-weight: 700;
  color: #409eff;
}

.score-empty {
  color: #c0c4cc;
}

.opinion-text {
  font-size: 12px;
  color: #606266;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;

  .detail-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    .detail-institution { font-size: 13px; color: #909399; }
  }

  .detail-total {
    font-size: 14px;
    color: #606266;
    .detail-total-val {
      font-size: 22px;
      font-weight: 700;
      color: #409eff;
      margin: 0 2px;
    }
  }
}

.score-items-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.score-item-row {
  display: flex;
  align-items: center;
  gap: 8px;

  .si-label {
    width: 72px;
    font-size: 13px;
    font-weight: 500;
    color: #303133;
    flex-shrink: 0;
    text-align: right;
  }

  .si-bar-wrap {
    flex: 1;
    height: 8px;
    background: #f0f2f5;
    border-radius: 4px;
    overflow: hidden;
  }

  .si-bar {
    height: 100%;
    background: linear-gradient(90deg, #a0cfff, #409eff);
    border-radius: 4px;
    transition: width 0.4s ease;
  }

  .si-score {
    font-size: 14px;
    font-weight: 700;
    color: #409eff;
    width: 32px;
    text-align: right;
    flex-shrink: 0;
  }

  .si-max {
    font-size: 12px;
    color: #c0c4cc;
    flex-shrink: 0;
  }
}

.opinion-block {
  margin-top: 12px;
  .opinion-label {
    font-size: 13px;
    font-weight: 600;
    color: #606266;
    margin-bottom: 4px;
  }
  .opinion-content {
    font-size: 13px;
    color: #303133;
    white-space: pre-wrap;
    line-height: 1.6;
    padding: 8px 10px;
    background: #f5f7fa;
    border-radius: 4px;
  }
}
</style>
