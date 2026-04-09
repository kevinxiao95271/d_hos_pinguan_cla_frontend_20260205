<template>
  <div class="tasks-page">

    <!-- 统计卡片：总任务 → 待提交 → 已提交 → 已规避 -->
    <el-row :gutter="12" class="stats-row">
      <el-col :span="6">
        <div class="stat-card stat-total">
          <span class="stat-value">{{ computedStats.total }}</span>
          <span class="stat-label">总任务数</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-pending">
          <span class="stat-value">{{ computedStats.pendingSubmit }}</span>
          <span class="stat-label">待提交</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-scored">
          <span class="stat-value">{{ computedStats.scored }}</span>
          <span class="stat-label">已提交</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-recused">
          <span class="stat-value">{{ computedStats.recused }}</span>
          <span class="stat-label">已规避</span>
        </div>
      </el-col>
    </el-row>

    <!-- 草稿待提交横幅 -->
    <transition name="banner-fade">
      <div v-if="draftTasks.length > 0" class="draft-banner">
        <div class="draft-banner-left">
          <span class="draft-banner-icon">⚠️</span>
          <div>
            <div class="draft-banner-title">您有 {{ draftTasks.length }} 项评分草稿尚未提交</div>
            <div class="draft-banner-sub">评分已自动保存，请确认无误后完成提交，避免遗漏</div>
          </div>
        </div>
        <el-button
          type="warning"
          size="large"
          :loading="submittingAll"
          @click="submitAllDrafts"
        >
          一键提交全部草稿（{{ draftTasks.length }}项）
        </el-button>
      </div>
    </transition>

    <!-- 筛选栏 -->
    <el-card shadow="never" style="margin-bottom: 16px;">
      <el-form :inline="true" :model="filters">
        <el-form-item label="评审阶段">
          <el-select v-model="filters.stage" placeholder="全部" clearable style="width:120px">
            <el-option label="书审" value="BOOK" />
            <el-option label="面谈" value="INTERVIEW" />
            <el-option label="决赛" value="FINAL" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 待评分区域 -->
    <el-card shadow="never" class="section-card" v-loading="loading">
      <template #header>
        <div class="section-header pending-header">
          <span>待评分任务</span>
          <el-tag type="warning" round>{{ pendingTasks.length }}</el-tag>
        </div>
      </template>
      <el-empty v-if="pendingTasks.length === 0 && !loading" description="暂无待评分任务" :image-size="80" />
      <div v-for="task in pendingTasks" :key="task.id" class="task-row" :class="{ 'task-row-draft': task.status === 'DRAFT' }">
        <span class="task-name">{{ task.projectName || '-' }}</span>
        <div class="task-inline-meta">
          <span v-if="task.total != null" class="task-score pending-score">{{ task.total }} 分</span>
          <el-tag v-if="task.status === 'DRAFT'" type="primary" size="small">草稿</el-tag>
          <el-tag v-else-if="task.status === 'RETURNED'" type="danger" size="small">已退回，请重评</el-tag>
          <el-tag v-else-if="task.status === 'CONFIRMED'" size="small">已确认</el-tag>
          <el-tag v-else type="warning" size="small">待评审</el-tag>
          <span class="meta-sep">·</span>
          <span class="meta-text">{{ task.institutionName || '-' }}</span>
          <span class="meta-sep">·</span>
          <span class="meta-text">{{ getStageText(task.stage) }}</span>
          <el-tag v-if="task.institutionLevel" type="success" size="small">{{ task.institutionLevel }}</el-tag>
        </div>
        <div class="task-actions">
          <el-button v-if="['PENDING','CONFIRMED'].includes(task.status)" type="primary" size="small" @click="goToReview(task)">评分</el-button>
          <el-button v-if="['DRAFT','RETURNED'].includes(task.status)" size="small" @click="goToReview(task)">继续评分</el-button>
          <el-button v-if="['DRAFT','RETURNED'].includes(task.status)" type="primary" size="small" :loading="submitting" @click="handleSubmitScore(task)">提交评分</el-button>
          <el-button v-if="['PENDING','CONFIRMED','DRAFT','RETURNED'].includes(task.status)" type="warning" size="small" plain @click="openRecuseDialog(task)">规避</el-button>
        </div>
      </div>
    </el-card>

    <!-- 已评分区域 -->
    <el-card shadow="never" class="section-card" v-loading="loading">
      <template #header>
        <div class="section-header scored-header">
          <span>已提交任务</span>
          <el-tag type="success" round>{{ scoredTasks.length }}</el-tag>
        </div>
      </template>
      <el-empty v-if="scoredTasks.length === 0 && !loading" description="暂无已提交任务" :image-size="80" />
      <div v-for="task in scoredTasks" :key="task.id" class="task-row">
        <span class="task-name">{{ task.projectName || '-' }}</span>
        <div class="task-inline-meta">
          <span v-if="task.total != null" class="task-score scored-score">{{ task.total }} 分</span>
          <el-tag type="success" size="small">已提交</el-tag>
          <span class="meta-sep">·</span>
          <span class="meta-text">{{ task.institutionName || '-' }}</span>
          <span class="meta-sep">·</span>
          <span class="meta-text">{{ getStageText(task.stage) }}</span>
          <el-tag v-if="task.institutionLevel" type="success" size="small">{{ task.institutionLevel }}</el-tag>
        </div>
        <div class="task-actions">
          <el-button size="small" @click="viewScore(task)">查看评分</el-button>
        </div>
      </div>
    </el-card>

    <!-- 已规避区域（有规避任务时才显示） -->
    <el-card v-if="recusedTasks.length > 0" shadow="never" class="section-card">
      <template #header>
        <div class="section-header recused-header">
          <span>已规避任务</span>
          <el-tag type="info" round>{{ recusedTasks.length }}</el-tag>
        </div>
      </template>
      <div v-for="task in recusedTasks" :key="task.id" class="task-row task-row-muted">
        <span class="task-name">{{ task.projectName || '-' }}</span>
        <div class="task-inline-meta">
          <el-tag type="info" size="small">已规避</el-tag>
          <span class="meta-sep">·</span>
          <span class="meta-text">{{ task.institutionName || '-' }}</span>
          <span class="meta-sep">·</span>
          <span class="meta-text">{{ getStageText(task.stage) }}</span>
        </div>
        <div class="task-actions" />
      </div>
    </el-card>

  </div>

  <!-- 提交成功感谢弹窗 -->
  <el-dialog
    v-model="showThankYouDialog"
    :show-close="false"
    :close-on-click-modal="false"
    width="400px"
    align-center
  >
    <div class="thank-you-content">
      <div class="thank-you-icon">✅</div>
      <h2 class="thank-you-title">评分已提交</h2>
      <p class="thank-you-msg">感谢您认真完成本次评审工作！<br/>您的专业意见对项目质量提升至关重要。</p>
    </div>
    <template #footer>
      <el-button type="primary" size="large" style="width:100%" @click="showThankYouDialog = false">
        确定
      </el-button>
    </template>
  </el-dialog>

  <!-- 规避任务弹窗 -->
  <el-dialog v-model="recuseDialogVisible" title="申请规避评审任务" width="440px" :close-on-click-modal="false">
    <div style="margin-bottom: 12px; color: #606266">
      项目：<strong>{{ recuseRow?.projectName }}</strong>
    </div>
    <el-form ref="recuseFormRef" :model="recuseForm" :rules="recuseRules" label-width="90px">
      <el-form-item label="规避原因" prop="reasonCode">
        <el-select v-model="recuseForm.reasonCode" placeholder="请选择规避原因" style="width: 100%">
          <el-option
            v-for="item in recuseReasons"
            :key="item.code"
            :label="item.label || item.name || item.code"
            :value="item.code"
          />
        </el-select>
      </el-form-item>
      <el-form-item v-if="recuseForm.reasonCode === 'OTHER'" label="补充说明" prop="reasonOther">
        <el-input
          v-model="recuseForm.reasonOther"
          type="textarea"
          :rows="3"
          placeholder="请填写具体原因"
          maxlength="200"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="recuseDialogVisible = false">取消</el-button>
      <el-button type="warning" :loading="recusing" @click="confirmRecuse">确认规避</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMyReviewTasks, getMyTaskStats, recuseReviewTask, getReviewScore, getInterviewScore, submitReviewScore, submitInterviewScore } from '@/api/review'
import { getRecuseReasons } from '@/api/dictionary'

const router = useRouter()

const tasks = ref([])
const loading = ref(false)
const submitting = ref(false)
const submittingAll = ref(false)
const taskStats = ref({})
const filters = reactive({ stage: '' })
const showThankYouDialog = ref(false)

// 规避相关
const recuseDialogVisible = ref(false)
const recusing = ref(false)
const recuseRow = ref(null)
const recuseFormRef = ref(null)
const recuseReasons = ref([])
const recuseForm = reactive({ reasonCode: '', reasonOther: '' })
const recuseRules = {
  reasonCode: [{ required: true, message: '请选择规避原因', trigger: 'change' }],
  reasonOther: [
    {
      validator: (rule, value, callback) => {
        if (recuseForm.reasonCode === 'OTHER' && !value) callback(new Error('请填写补充说明'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

// 过滤后的任务（stage 做双重兜底：loadData 已做一次，这里再保一次）
const filteredTasks = computed(() => {
  const stage = filters.stage
  if (!stage) return tasks.value
  return tasks.value.filter(t => {
    const taskStage = t.stage || 'BOOK'
    return taskStage === stage
  })
})


// 排序由后端保证（DRAFT total倒序 → SCORED total倒序 → PENDING/CONFIRMED/RETURNED → RECUSED）
// 前端仅按状态分区，保持 API 返回顺序

// 待评分：DRAFT + PENDING + CONFIRMED + RETURNED
const pendingTasks = computed(() =>
  filteredTasks.value.filter(t => ['DRAFT', 'PENDING', 'CONFIRMED', 'RETURNED'].includes(t.status))
)

// 已提交：SCORED / COMPLETED
const scoredTasks = computed(() =>
  filteredTasks.value.filter(t => ['SCORED', 'COMPLETED'].includes(t.status))
)

// 已规避
const recusedTasks = computed(() =>
  filteredTasks.value.filter(t => t.status === 'RECUSED')
)

// 统计（优先用接口数据，回退用本地计算）
const computedStats = computed(() => {
  const s = taskStats.value
  return {
    total: s.total ?? tasks.value.length,
    pendingSubmit: s.pendingSubmit ?? pendingTasks.value.length,
    scored: s.scored ?? scoredTasks.value.length,
    recused: s.recused ?? recusedTasks.value.length
  }
})

// 草稿任务（横幅提醒基于全量任务，不受 stage 筛选影响）
const draftTasks = computed(() => tasks.value.filter(t => t.status === 'DRAFT'))

const submitAllDrafts = async () => {
  const drafts = draftTasks.value
  if (!drafts.length) return
  try {
    await ElMessageBox.confirm(
      `共 ${drafts.length} 项草稿评分将被正式提交，提交后不可修改。确认继续？`,
      '一键提交全部草稿',
      { confirmButtonText: '确认提交', cancelButtonText: '取消', type: 'warning' }
    )
    submittingAll.value = true
    let successCount = 0
    const errors = []
    for (const task of drafts) {
      try {
        const isInterview = task.stage === 'INTERVIEW'
        const scoreRes = isInterview
          ? await getInterviewScore(task.id)
          : await getReviewScore(task.id)
        if (!scoreRes.success || !scoreRes.data) {
          errors.push(`《${task.projectName}》加载评分失败`)
          continue
        }
        const submitData = { reviewTaskId: task.id, ...scoreRes.data }
        delete submitData.id
        delete submitData.status
        delete submitData.submittedAt
        delete submitData.createdAt
        delete submitData.updatedAt
        const res = isInterview
          ? await submitInterviewScore(submitData)
          : await submitReviewScore(submitData)
        if (res.success) {
          successCount++
        } else {
          errors.push(`《${task.projectName}》${res.message || '提交失败'}`)
        }
      } catch (e) {
        errors.push(`《${task.projectName}》${e?.response?.data?.message || '提交异常'}`)
      }
    }
    if (errors.length) {
      ElMessage.warning(`${successCount} 项提交成功，${errors.length} 项失败：${errors.join('；')}`)
    } else {
      showThankYouDialog.value = true
    }
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  } finally {
    submittingAll.value = false
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const [tasksRes, statsRes] = await Promise.allSettled([
      getMyReviewTasks({ page: 1, pageSize: 200 }),
      getMyTaskStats()
    ])
    if (tasksRes.status === 'fulfilled' && tasksRes.value.success) {
      const raw = tasksRes.value.data
      const list = Array.isArray(raw) ? raw : (raw?.list || raw?.records || raw?.content || [])
      console.log('📋 任务列表原始数据 stage 分布:', list.map(t => ({ id: t.reviewTaskId || t.id, stage: t.stage, status: t.status })))
      tasks.value = list.map(task => ({
        ...task,
        id: task.reviewTaskId || task.id,
        // 兼容后端 stage 字段为 null/undefined 的书审任务（书审是默认阶段）
        stage: task.stage || task.reviewStage || task.stageType || 'BOOK'
      }))
    } else if (tasksRes.status === 'fulfilled') {
      ElMessage.error(tasksRes.value.message || '加载失败')
    }
    if (statsRes.status === 'fulfilled' && statsRes.value.success) {
      taskStats.value = statsRes.value.data || {}
    }
  } catch (error) {
    console.error('❌ 加载评审任务失败:', error)
    ElMessage.error('加载评审任务失败')
  } finally {
    loading.value = false
  }
}

const openRecuseDialog = async (row) => {
  recuseRow.value = row
  recuseForm.reasonCode = ''
  recuseForm.reasonOther = ''
  if (recuseReasons.value.length === 0) {
    try {
      const res = await getRecuseReasons()
      recuseReasons.value = res.success ? (res.data || []) : []
    } catch {
      recuseReasons.value = []
    }
  }
  recuseDialogVisible.value = true
}

const confirmRecuse = async () => {
  try {
    await recuseFormRef.value.validate()
    recusing.value = true
    const res = await recuseReviewTask(recuseRow.value.id, {
      reasonCode: recuseForm.reasonCode,
      reasonOther: recuseForm.reasonOther || undefined
    })
    if (res.success) {
      ElMessage.success('规避申请已提交')
      recuseDialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    if (e !== false) ElMessage.error(e?.response?.data?.message || '操作失败')
  } finally {
    recusing.value = false
  }
}

const getStageText = (stage) => {
  const map = { BOOK: '书审', INTERVIEW: '面谈', FINAL: '决赛' }
  return map[stage] || stage
}

const goToReview = (row) => {
  router.push({
    path: `/reviewer/review/${row.id}`,
    query: {
      registrationId: row.registrationId,
      projectName: row.projectName,
      institutionName: row.institutionName,
      institutionLevel: row.institutionLevel,
      stage: row.stage || 'BOOK',
      status: row.status
    }
  })
}

const viewScore = (row) => {
  router.push({
    path: `/reviewer/review/${row.id}`,
    query: {
      view: 'score',
      registrationId: row.registrationId,
      projectName: row.projectName,
      institutionName: row.institutionName,
      stage: row.stage || 'BOOK'
    }
  })
}

const handleSubmitScore = async (task) => {
  try {
    submitting.value = true
    // 加载草稿评分数据
    const isInterview = task.stage === 'INTERVIEW'
    const scoreRes = isInterview
      ? await getInterviewScore(task.id)
      : await getReviewScore(task.id)

    if (!scoreRes.success) {
      ElMessage.error('加载评分数据失败，请进入页面重新确认')
      return
    }

    const scoreData = scoreRes.data || {}
    const total = task.total != null ? `${task.total} 分` : '暂无分值'

    await ElMessageBox.confirm(
      `当前总分：${total}，确认正式提交评分？提交后不可修改。`,
      `提交评分 — ${task.projectName}`,
      { confirmButtonText: '确认提交', cancelButtonText: '取消', type: 'warning' }
    )

    // 构建提交数据
    const submitData = { reviewTaskId: task.id, ...scoreData }
    delete submitData.id
    delete submitData.status
    delete submitData.submittedAt
    delete submitData.createdAt
    delete submitData.updatedAt

    const res = isInterview
      ? await submitInterviewScore(submitData)
      : await submitReviewScore(submitData)

    if (res.success) {
      showThankYouDialog.value = true
      loadData()
    } else {
      ElMessage.error(res.message || '提交失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.tasks-page {
  padding: 20px;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 12px 16px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #edf0f5;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.2s, transform 0.15s;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.09);
    transform: translateY(-1px);
  }

  // 底部渐变色条
  &::after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 4px;
    border-radius: 0 0 8px 8px;
  }

  .stat-value {
    font-size: 26px;
    font-weight: 700;
    line-height: 1;
    flex-shrink: 0;
  }

  .stat-label {
    font-size: 12px;
    color: #909399;
    white-space: nowrap;
    margin-top: 2px;
  }
}

.stat-total {
  border-top: 3px solid #409EFF;
  .stat-value { color: #409EFF; }
  &::after { background: linear-gradient(90deg, #a0cfff, #409EFF); }
}
.stat-pending {
  border-top: 3px solid #E6A23C;
  .stat-value { color: #E6A23C; }
  &::after { background: linear-gradient(90deg, #f5dba1, #E6A23C); }
}
.stat-scored {
  border-top: 3px solid #67C23A;
  .stat-value { color: #67C23A; }
  &::after { background: linear-gradient(90deg, #b3e19d, #67C23A); }
}
.stat-recused {
  border-top: 3px solid #909399;
  .stat-value { color: #909399; }
  &::after { background: linear-gradient(90deg, #c8cacc, #909399); }
}

/* 分区卡片 */
.section-card {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.pending-header { color: #E6A23C; }
.scored-header  { color: #67C23A; }
.recused-header { color: #909399; }

/* 草稿横幅 */
.draft-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #fffbe6 0%, #fff3cd 100%);
  border: 1.5px solid #faad14;
  border-radius: 10px;
  padding: 14px 20px;
  margin-bottom: 16px;
  gap: 16px;
}

.draft-banner-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.draft-banner-icon {
  font-size: 26px;
  flex-shrink: 0;
}

.draft-banner-title {
  font-size: 15px;
  font-weight: 700;
  color: #d48806;
  margin-bottom: 2px;
}

.draft-banner-sub {
  font-size: 12px;
  color: #ad6800;
  opacity: 0.85;
}

.banner-fade-enter-active,
.banner-fade-leave-active {
  transition: all 0.3s ease;
}
.banner-fade-enter-from,
.banner-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 任务行 —— 单行布局 */
.task-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;

  &:last-child { border-bottom: none; }
  &.task-row-muted .task-name { color: #909399; }

  // 草稿行：橙色左边框 + 浅橙背景，醒目提示未提交
  &.task-row-draft {
    background: #fffbf0;
    border-left: 3px solid #faad14;
    padding-left: 10px;
    margin-left: -10px;
    border-radius: 0 4px 4px 0;
  }
}

.task-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 220px;
  flex-shrink: 0;
}

.task-inline-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 1;
  min-width: 0;
  flex-wrap: nowrap;
  overflow: hidden;
}

.task-score {
  font-size: 13px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}

.pending-score { color: #E6A23C; background: #fdf6ec; }
.scored-score  { color: #67C23A; background: #f0f9eb; }

.meta-sep {
  color: #dcdfe6;
  font-size: 12px;
  flex-shrink: 0;
}

.meta-text {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 130px;
}

.task-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  margin-left: auto;
}

.thank-you-content {
  text-align: center;
  padding: 20px 10px 10px;

  .thank-you-icon { font-size: 48px; margin-bottom: 12px; }

  .thank-you-title {
    font-size: 20px;
    font-weight: 700;
    color: #303133;
    margin: 0 0 10px;
  }

  .thank-you-msg {
    font-size: 14px;
    color: #606266;
    line-height: 1.8;
    margin: 0;
  }
}
</style>
