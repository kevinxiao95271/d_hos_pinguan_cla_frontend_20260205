<template>
  <div class="group-page">
    <StageProgress simple />

    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>决赛场次安排</span>
          <div class="header-actions">
            <el-tag type="info">共 {{ allSessions.length }} 个场次 · {{ totalProjects }} 个项目</el-tag>
            <el-button type="primary" plain size="small" :icon="Refresh" @click="loadSchedule">刷新</el-button>
          </div>
        </div>
      </template>

      <el-empty v-if="allSessions.length === 0 && !loading" description="暂无场次数据" />

      <!-- 日期 Tab -->
      <el-tabs v-else v-model="activeDate" class="date-tabs">
        <el-tab-pane
          v-for="date in dates"
          :key="date"
          :name="date"
          :label="`${date}（${sessionsByDate[date]?.length || 0} 场）`"
        >
          <div class="sessions-grid">
            <el-card
              v-for="session in sessionsByDate[date]"
              :key="session.sessionCode"
              class="session-card"
              shadow="hover"
            >
              <!-- 场次卡片头 -->
              <template #header>
                <div class="session-card-header">
                  <div class="session-name">{{ session.sessionCode }}</div>
                  <div class="session-meta">
                    <el-tag type="info" size="small">{{ session.totalCount }} 项</el-tag>
                    <el-tag v-if="session.qccCount" type="primary" size="small">QCC×{{ session.qccCount }}</el-tag>
                    <el-tag v-if="session.nonQccCount" type="success" size="small">非QCC×{{ session.nonQccCount }}</el-tag>
                    <el-tag v-if="session.qfdCount" type="warning" size="small">QFD×{{ session.qfdCount }}</el-tag>
                  </div>
                </div>
              </template>

              <!-- 项目列表 -->
              <div class="project-list">
                <div
                  v-for="proj in session.projects"
                  :key="proj.registrationId"
                  class="project-row"
                >
                  <span class="proj-order">{{ proj.sessionOrder }}</span>
                  <div class="proj-info">
                    <span class="proj-name" :title="proj.projectName">{{ proj.projectName }}</span>
                    <span class="proj-inst">{{ proj.institutionName }}</span>
                  </div>
                  <el-tag :type="scoreFormTagType(proj.scoreForm)" size="small" class="proj-form">
                    {{ scoreFormText(proj.scoreForm) }}
                  </el-tag>
                </div>
              </div>

            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 分配评委弹窗 -->
    <el-dialog
      v-model="assignDialogVisible"
      :title="`分配评委 — ${currentSession?.sessionCode}`"
      width="660px"
    >
      <el-alert type="info" :closable="false" style="margin-bottom: 14px">
        为「{{ currentSession?.sessionCode }}」场次内全部 <b>{{ currentSession?.totalCount }}</b> 个项目统一分配同一位评委，接口幂等。
      </el-alert>

      <el-form :inline="true" size="small" style="margin-bottom: 10px">
        <el-form-item label="搜索评委">
          <el-input v-model="reviewerKeyword" placeholder="姓名/机构" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button @click="loadReviewers" :loading="loadingReviewers">刷新</el-button>
        </el-form-item>
      </el-form>

      <el-table
        :data="filteredReviewers"
        v-loading="loadingReviewers"
        @row-click="selectReviewer"
        :row-class-name="reviewerRowClass"
        border
        stripe
        max-height="320"
        highlight-current-row
      >
        <el-table-column width="40" align="center">
          <template #default="{ row }">
            <el-radio :value="row.id" v-model="selectedReviewerId" @click.stop />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="姓名" width="90" />
        <el-table-column prop="title" label="职称" width="100" show-overflow-tooltip />
        <el-table-column prop="institutionName" label="所在机构" min-width="150" show-overflow-tooltip />
        <el-table-column label="背景" width="70" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.expertBackground === 'MANAGEMENT'" size="small">管理</el-tag>
            <el-tag v-else-if="row.expertBackground === 'MEDICAL'" type="success" size="small">医疗</el-tag>
            <el-tag v-else-if="row.expertBackground === 'NURSING'" type="warning" size="small">护理</el-tag>
            <el-tag v-else type="info" size="small">其他</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="selectedReviewerId" class="selected-info">
        已选：<b>{{ selectedReviewerName }}</b>
      </div>

      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="assigning"
          :disabled="!selectedReviewerId"
          @click="confirmAssign"
        >
          确认分配
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getCurrentCompetitionId, getCurrentCompetitionIdSync } from '@/utils/competition'
import { getFinalSessionSchedule, assignFinalReviewer, getReviewers } from '@/api/admin'

const competitionId = ref(getCurrentCompetitionIdSync())

// ── 场次数据 ────────────────────────────────────────────────
const allSessions = ref([])
const loading = ref(false)
const activeDate = ref('')

const dates = computed(() => [...new Set(allSessions.value.map(s => s.sessionDate))].sort())

const sessionsByDate = computed(() => {
  const map = {}
  for (const s of allSessions.value) {
    if (!map[s.sessionDate]) map[s.sessionDate] = []
    map[s.sessionDate].push(s)
  }
  return map
})

const totalProjects = computed(() => allSessions.value.reduce((sum, s) => sum + (s.totalCount || 0), 0))

const loadSchedule = async () => {
  if (!competitionId.value) return
  loading.value = true
  try {
    const res = await getFinalSessionSchedule(competitionId.value)
    if (res.success) {
      allSessions.value = res.data || []
      if (!activeDate.value && dates.value.length > 0) {
        activeDate.value = dates.value[0]
      }
    } else {
      ElMessage.error(res.message || '加载场次失败')
    }
  } catch {
    ElMessage.error('加载场次失败')
  } finally {
    loading.value = false
  }
}

// ── 分配评委 ────────────────────────────────────────────────
const assignDialogVisible = ref(false)
const currentSession = ref(null)
const reviewers = ref([])
const loadingReviewers = ref(false)
const reviewerKeyword = ref('')
const selectedReviewerId = ref(null)
const assigning = ref(false)

const filteredReviewers = computed(() => {
  if (!reviewerKeyword.value) return reviewers.value
  const kw = reviewerKeyword.value.toLowerCase()
  return reviewers.value.filter(r =>
    (r.name || '').toLowerCase().includes(kw) ||
    (r.institutionName || '').toLowerCase().includes(kw)
  )
})

const selectedReviewerName = computed(() => {
  const r = reviewers.value.find(r => r.id === selectedReviewerId.value)
  return r ? `${r.name}（${r.institutionName}）` : ''
})

const loadReviewers = async () => {
  loadingReviewers.value = true
  try {
    const res = await getReviewers({ competitionId: competitionId.value })
    reviewers.value = res.success ? (Array.isArray(res.data) ? res.data : []) : []
  } catch {
    ElMessage.error('加载评委失败')
  } finally {
    loadingReviewers.value = false
  }
}

const openAssignDialog = (session) => {
  currentSession.value = session
  selectedReviewerId.value = null
  reviewerKeyword.value = ''
  assignDialogVisible.value = true
  if (reviewers.value.length === 0) loadReviewers()
}

const selectReviewer = (row) => { selectedReviewerId.value = row.id }

const reviewerRowClass = ({ row }) =>
  selectedReviewerId.value === row.id ? 'selected-row' : ''

const confirmAssign = async () => {
  if (!selectedReviewerId.value || !currentSession.value) return
  assigning.value = true
  try {
    const res = await assignFinalReviewer(
      currentSession.value.sessionCode,
      competitionId.value,
      selectedReviewerId.value
    )
    if (res.success) {
      ElMessage.success(res.data || '分配成功')
      assignDialogVisible.value = false
    } else {
      ElMessage.error(res.message || '分配失败')
    }
  } catch {
    ElMessage.error('分配失败，请检查网络')
  } finally {
    assigning.value = false
  }
}

// ── 工具函数 ────────────────────────────────────────────────
const scoreFormTagType = (form) => {
  if (form === 'QCC') return 'primary'
  if (form === 'QFD') return 'warning'
  return 'success'
}

const scoreFormText = (form) => form === 'NON_QCC' ? '非QCC' : (form || '-')

onMounted(async () => {
  const id = await getCurrentCompetitionId()
  if (id) competitionId.value = id
  loadSchedule()
})
</script>

<style scoped lang="scss">
.group-page {
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

.date-tabs {
  :deep(.el-tabs__item) {
    font-size: 15px;
    font-weight: 600;
  }
}

/* 7 列卡片网格 */
.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  padding-top: 16px;
}

.session-card {
  :deep(.el-card__header) { padding: 12px 14px; }
  :deep(.el-card__body)   { padding: 10px 14px; }
}

.session-card-header {
  .session-name {
    font-size: 14px;
    font-weight: 700;
    color: #303133;
    margin-bottom: 6px;
  }
  .session-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
}

.project-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 220px;
  overflow-y: auto;
  margin-bottom: 10px;
}

.project-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  border-bottom: 1px solid #f5f5f5;
  padding-bottom: 5px;

  &:last-child { border-bottom: none; padding-bottom: 0; }

  .proj-order {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    background: #f0f2f5;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
    color: #606266;
  }

  .proj-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 1px;

    .proj-name {
      font-weight: 500;
      color: #303133;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .proj-inst {
      font-size: 11px;
      color: #909399;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .proj-form { flex-shrink: 0; }
}

.selected-info {
  margin-top: 10px;
  padding: 8px 12px;
  background: #f0f9eb;
  border-radius: 6px;
  color: #67c23a;
  font-size: 13px;
}

:deep(.selected-row > td) {
  background: #ecf5ff !important;
}
</style>
