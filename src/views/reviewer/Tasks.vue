<template>
  <div class="tasks-page">

    <!-- 统计卡片：总任务 → 待评分 → 已评分 → 已提交 -->
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
          <span class="stat-label">待评分</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-draft">
          <span class="stat-value">{{ computedStats.drafted }}</span>
          <span class="stat-label">已评分</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-scored">
          <span class="stat-value">{{ computedStats.scored }}</span>
          <span class="stat-label">已提交</span>
        </div>
      </el-col>
    </el-row>

    <!-- 草稿待提交横幅（面谈阶段改为单项提交，不显示此横幅） -->
    <transition name="banner-fade">
      <div v-if="draftTasks.length > 0 && activeStageTab !== 'INTERVIEW'" class="draft-banner">
        <div class="draft-banner-left">
          <span class="draft-banner-icon">⚠️</span>
          <div>
            <div class="draft-banner-title">各项目评分已自动保存，请确认无误后完成提交，避免遗漏</div>
          </div>
        </div>
        <el-button
          type="warning"
          size="large"
          :loading="submittingAll"
          @click="submitAllDrafts"
        >
          一键提交本阶段评审项目
        </el-button>
      </div>
    </transition>

    <!-- 阶段 Tab + 刷新 -->
    <div class="stage-tab-bar">
      <el-tabs v-model="activeStageTab" class="stage-tabs">
        <el-tab-pane v-if="!isMobile" name="BOOK">
          <template #label>
            <span>书面评审 <el-badge :value="stageTabCount('BOOK')" :hidden="stageTabCount('BOOK') === 0" type="warning" /></span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="INTERVIEW">
          <template #label>
            <span>面谈评审 <el-badge :value="stageTabCount('INTERVIEW')" :hidden="stageTabCount('INTERVIEW') === 0" type="danger" /></span>
          </template>
        </el-tab-pane>
        <el-tab-pane v-if="hasFinalTasks && !isMobile" name="FINAL">
          <template #label>
            <span>决赛评审 <el-badge :value="stageTabCount('FINAL')" :hidden="stageTabCount('FINAL') === 0" type="primary" /></span>
          </template>
        </el-tab-pane>
      </el-tabs>
      <el-button type="primary" plain size="small" @click="loadData" class="refresh-btn">刷新</el-button>
    </div>

    <!-- 待评分区域（PENDING / CONFIRMED / RETURNED） -->
    <el-card shadow="never" class="section-card" v-loading="loading">
      <template #header>
        <div class="section-header pending-header section-header-clickable" @click="sec.pending = !sec.pending">
          <span>待评分项目</span>
          <el-tag type="warning" round>{{ pendingTasksFiltered.length }}</el-tag>
          <span class="section-arrow" :class="{ collapsed: sec.pending }">›</span>
        </div>
      </template>
      <div v-show="!sec.pending">
        <el-empty v-if="pendingTasksFiltered.length === 0 && !loading" description="暂无待评分项目" :image-size="80" />
        <div v-for="task in pendingTasksFiltered" :key="task.id" class="task-row">
          <span class="task-name">{{ task.projectName || '-' }}</span>
          <div class="task-inline-meta">
            <el-tag v-if="task.status === 'RETURNED'" type="danger" size="small">已退回，请重评</el-tag>
            <el-tag v-else-if="task.status === 'CONFIRMED'" size="small">已确认</el-tag>
            <el-tag v-else type="warning" size="small">待评审</el-tag>
            <span class="meta-sep">·</span>
            <span class="meta-text">{{ task.institutionName || '-' }}</span>
            <el-tag v-if="task.institutionLevel" type="success" size="small">{{ task.institutionLevel }}</el-tag>
          </div>
          <div class="task-actions">
            <el-button type="primary" size="small" @click="goToReview(task)">评分</el-button>
            <el-button type="warning" size="small" plain @click="openRecuseDialog(task)">规避</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 已评分区域（DRAFT：已打分保存草稿，待提交） -->
    <el-card shadow="never" class="section-card" v-loading="loading">
      <template #header>
        <div class="section-header draft-header section-header-clickable" @click="sec.draft = !sec.draft">
          <span>已评分项目</span>
          <el-tag type="primary" round>{{ draftTasksFiltered.length }}</el-tag>
          <span class="section-arrow" :class="{ collapsed: sec.draft }">›</span>
        </div>
      </template>
      <div v-show="!sec.draft">
        <el-empty v-if="draftTasksFiltered.length === 0 && !loading" description="暂无已评分项目" :image-size="80" />
        <div v-for="task in draftTasksFiltered" :key="task.id" class="task-row task-row-draft">
          <span class="task-name">{{ task.projectName || '-' }}</span>
          <div class="task-inline-meta">
            <span v-if="task.total != null" class="task-score pending-score">{{ task.total }} 分</span>
            <el-tag type="primary" size="small">草稿</el-tag>
            <span class="meta-sep">·</span>
            <span class="meta-text">{{ task.institutionName || '-' }}</span>
            <el-tag v-if="task.institutionLevel" type="success" size="small">{{ task.institutionLevel }}</el-tag>
          </div>
          <div class="task-actions">
          <el-button size="small" @click="goToReview(task)">继续评分</el-button>
          <el-button v-if="task.stage === 'INTERVIEW'" type="primary" size="small" :loading="submittingId === task.id" @click="submitSingleDraft(task)">提交评分</el-button>
          <el-button type="warning" size="small" plain @click="openRecuseDialog(task)">规避</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 已提交区域（SCORED / COMPLETED） -->
    <el-card shadow="never" class="section-card" v-loading="loading">
      <template #header>
        <div class="section-header scored-header section-header-clickable" @click="sec.scored = !sec.scored">
          <span>已提交项目</span>
          <el-tag type="success" round>{{ scoredTasksFiltered.length }}</el-tag>
          <span class="section-arrow" :class="{ collapsed: sec.scored }">›</span>
        </div>
      </template>
      <div v-show="!sec.scored">
        <el-empty v-if="scoredTasksFiltered.length === 0 && !loading" description="暂无已提交项目" :image-size="80" />
        <div v-for="task in scoredTasksFiltered" :key="task.id" class="task-row">
          <span class="task-name">{{ task.projectName || '-' }}</span>
          <div class="task-inline-meta">
            <span v-if="task.total != null" class="task-score scored-score">{{ task.total }} 分</span>
            <el-tag type="success" size="small">已提交</el-tag>
            <span class="meta-sep">·</span>
            <span class="meta-text">{{ task.institutionName || '-' }}</span>
            <el-tag v-if="task.institutionLevel" type="success" size="small">{{ task.institutionLevel }}</el-tag>
          </div>
          <div class="task-actions">
            <el-button size="small" @click="viewScore(task)">查看评分</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 已规避区域（有规避任务时才显示） -->
    <el-card v-if="recusedTasksFiltered.length > 0" shadow="never" class="section-card">
      <template #header>
        <div class="section-header recused-header">
          <span>已规避任务</span>
          <el-tag type="info" round>{{ recusedTasksFiltered.length }}</el-tag>
        </div>
      </template>
      <div v-for="task in recusedTasksFiltered" :key="task.id" class="task-row task-row-muted">
        <span class="task-name">{{ task.projectName || '-' }}</span>
        <div class="task-inline-meta">
          <el-tag type="info" size="small">已规避</el-tag>
          <span class="meta-sep">·</span>
          <span class="meta-text">{{ task.institutionName || '-' }}</span>
          <el-tag v-if="task.institutionLevel" type="success" size="small">{{ task.institutionLevel }}</el-tag>
        </div>
        <div class="task-actions">
          <el-button size="small" type="danger" plain :loading="cancelRecusingId === task.id" @click="handleCancelRecuse(task)">撤销规避</el-button>
        </div>
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
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMyReviewTasks, getMyTaskStats, recuseReviewTask, cancelRecuse, getReviewScore, getInterviewScore, submitReviewScore, submitInterviewScore } from '@/api/review'
import { getRecuseReasons } from '@/api/dictionary'

const router = useRouter()

const tasks = ref([])
const loading = ref(false)
const submitting = ref(false)
const submittingAll = ref(false)
const taskStats = ref({})
const showThankYouDialog = ref(false)

// 规避相关
const recuseDialogVisible = ref(false)
const recusing = ref(false)
const recuseRow = ref(null)
const cancelRecusingId = ref(null)
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

// ── 阶段 Tab ─────────────────────────────────────────────────────
const activeStageTab = ref('BOOK')

// 是否存在决赛任务（动态显示 FINAL tab）
const hasFinalTasks = computed(() => tasks.value.some(t => t.stage === 'FINAL'))

// 当前 tab 对应的待处理任务数（用于 badge 提示）
const stageTabCount = (stage) =>
  tasks.value.filter(t => t.stage === stage && ['DRAFT', 'PENDING', 'CONFIRMED', 'RETURNED'].includes(t.status)).length

// 按当前 Tab 过滤全量任务
const filteredTasks = computed(() => tasks.value.filter(t => t.stage === activeStageTab.value))

// ── 各状态分区（均基于 filteredTasks，随 Tab 切换）─────────────────

// 待评分：PENDING + CONFIRMED + RETURNED（未打过分）
const pendingTasks = computed(() =>
  tasks.value.filter(t => ['PENDING', 'CONFIRMED', 'RETURNED'].includes(t.status))
)
const pendingTasksFiltered = computed(() =>
  filteredTasks.value.filter(t => ['PENDING', 'CONFIRMED', 'RETURNED'].includes(t.status))
)

// 已评分草稿：DRAFT（已打分，尚未提交）
const draftTasksFiltered = computed(() =>
  filteredTasks.value.filter(t => t.status === 'DRAFT')
)

// 已提交：SCORED / COMPLETED
const scoredTasks = computed(() =>
  tasks.value.filter(t => ['SCORED', 'COMPLETED'].includes(t.status))
)
const scoredTasksFiltered = computed(() =>
  filteredTasks.value.filter(t => ['SCORED', 'COMPLETED'].includes(t.status))
)

// 已规避
const recusedTasksFiltered = computed(() =>
  filteredTasks.value.filter(t => t.status === 'RECUSED')
)

// 统计卡片跟着当前 Tab 联动，始终反映当前阶段的数字
const computedStats = computed(() => ({
  total: filteredTasks.value.length,
  pendingSubmit: pendingTasksFiltered.value.length,
  drafted: draftTasksFiltered.value.length,
  scored: scoredTasksFiltered.value.length,
  recused: recusedTasksFiltered.value.length
}))

// 草稿任务（跟当前 Tab 联动，用于一键提交横幅判断）
const draftTasks = computed(() => filteredTasks.value.filter(t => t.status === 'DRAFT'))

// 分区折叠状态：count=0 时自动折叠，可手动点击展开
const sec = reactive({ pending: false, draft: false, scored: false })

watch(loading, (val) => {
  if (!val) {
    sec.pending = pendingTasksFiltered.value.length === 0
    sec.draft   = draftTasksFiltered.value.length === 0
    sec.scored  = scoredTasksFiltered.value.length === 0
  }
})

// 书审必填校验（从 API 草稿数据中检查，返回错误信息或 null）
const validateBookScore = (scoreData, projectName) => {
  const weakness = (scoreData.weakness || '').trim()
  if (!weakness) {
    return `《${projectName}》「不足之处」为必填项，请先进入评分页填写后再提交`
  }
  if (weakness.length < 60) {
    return `《${projectName}》「不足之处」至少需填写 60 字（当前 ${weakness.length} 字），请先进入评分页补充`
  }
  return null
}

// 单项提交（列表页直接提交草稿）
const submittingId = ref(null)

const submitSingleDraft = async (task) => {
  try {
    await ElMessageBox.confirm(
      `确认提交《${task.projectName}》的评分？提交后不可修改。`,
      '提交评分',
      { confirmButtonText: '确认提交', cancelButtonText: '取消', type: 'warning' }
    )
    submittingId.value = task.id
    const isInterview = task.stage === 'INTERVIEW'
    const scoreRes = isInterview
      ? await getInterviewScore(task.id)
      : await getReviewScore(task.id)
    if (!scoreRes.success || !scoreRes.data) {
      ElMessage.error('加载评分数据失败，请进入评分页确认后再提交')
      return
    }
    // 书审必填校验
    if (!isInterview) {
      const err = validateBookScore(scoreRes.data, task.projectName)
      if (err) { ElMessage.warning(err); return }
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
      ElMessage.success(`《${task.projectName}》评分已提交`)
      loadData()
    } else {
      ElMessage.error(res.message || '提交失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.message || '提交失败')
  } finally {
    submittingId.value = null
  }
}

const submitAllDrafts = async () => {
  const drafts = draftTasks.value
  if (!drafts.length) return

  // 检查当前 Tab 下是否还有未评分任务（PENDING / CONFIRMED / RETURNED 没有草稿的）
  const unscoredTasks = pendingTasksFiltered.value.filter(t => !['DRAFT'].includes(t.status))
  if (unscoredTasks.length > 0) {
    await ElMessageBox.alert(
      `还有 ${unscoredTasks.length} 个项目未评审，请全部完成后再提交。`,
      '无法提交',
      { confirmButtonText: '知道了', type: 'warning' }
    )
    return
  }

  try {
    await ElMessageBox.confirm(
      `当前阶段共 ${drafts.length} 项草稿评分将被正式提交，提交后不可修改。确认继续？`,
      '一键提交本阶段评审项目',
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
        // 书审必填校验
        if (!isInterview) {
          const err = validateBookScore(scoreRes.data, task.projectName)
          if (err) { errors.push(err); continue }
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
      const errHtml = errors.map((e, i) => `<div style="margin:6px 0;line-height:1.6">${i + 1}. ${e}</div>`).join('')
      await ElMessageBox.alert(
        `<div><b>${successCount} 项提交成功，${errors.length} 项需处理：</b>${errHtml}</div>`,
        '提交结果',
        { dangerouslyUseHTMLString: true, confirmButtonText: '知道了', type: 'warning' }
      )
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
      recuseReasons.value = res.success ? (res.data || []).filter(r => r.code !== 'KNOW_LEADER') : []
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

const handleCancelRecuse = async (task) => {
  try {
    await ElMessageBox.confirm(
      `确认撤销对「${task.projectName}」的规避申请？撤销后任务将恢复为可评分状态。`,
      '撤销规避',
      { confirmButtonText: '确认撤销', cancelButtonText: '取消', type: 'warning' }
    )
    cancelRecusingId.value = task.id
    const res = await cancelRecuse(task.id)
    if (res.success) {
      ElMessage.success('规避已撤销，任务已恢复')
      loadData()
    } else {
      ElMessage.error(res.message || '撤销失败')
    }
  } catch (e) {
    if (e !== 'cancel' && e !== false) ElMessage.error(e?.response?.data?.message || '撤销失败')
  } finally {
    cancelRecusingId.value = null
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

// ── 移动端检测 ─────────────────────────────────────────────────────
const isMobile = ref(window.innerWidth <= 768)
const onResize = () => { isMobile.value = window.innerWidth <= 768 }

// 移动端自动锁定到面谈 Tab
watch(isMobile, (mobile) => {
  if (mobile) activeStageTab.value = 'INTERVIEW'
}, { immediate: true })

onMounted(() => {
  window.addEventListener('resize', onResize)
  loadData()
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
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
.stat-draft {
  border-top: 3px solid #409EFF;
  .stat-value { color: #409EFF; }
  &::after { background: linear-gradient(90deg, #a0cfff, #409EFF); }
}

.stat-recused {
  border-top: 3px solid #909399;
  .stat-value { color: #909399; }
  &::after { background: linear-gradient(90deg, #c8cacc, #909399); }
}

/* 阶段 Tab 栏 */
.stage-tab-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
  .stage-tabs {
    flex: 1;
    :deep(.el-tabs__header) { margin-bottom: 0; }
    :deep(.el-tabs__item) { font-size: 15px; font-weight: 500; }
    :deep(.el-badge__content) { transform: translateY(-4px) translateX(4px); }
  }
  .refresh-btn { flex-shrink: 0; margin-left: 12px; }
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
.draft-header   { color: #409EFF; }
.scored-header  { color: #67C23A; }
.recused-header { color: #909399; }

.section-header-clickable {
  cursor: pointer;
  user-select: none;
  &:hover { opacity: 0.8; }
}

.section-arrow {
  margin-left: auto;
  font-size: 18px;
  color: #c0c4cc;
  transform: rotate(90deg);
  display: inline-block;
  transition: transform 0.2s;
  line-height: 1;

  &.collapsed {
    transform: rotate(0deg);
  }
}

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

/* ── 移动端适配 ── */
@media (max-width: 768px) {
  .stats-row {
    .el-col {
      padding: 0 4px !important;
    }
    .stat-card {
      padding: 10px 6px;
      .stat-value { font-size: 22px; }
      .stat-label { font-size: 11px; }
    }
  }

  .draft-banner {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 12px;

    .el-button { width: 100%; }
  }

  .task-row {
    flex-wrap: wrap;
    gap: 6px;
    padding: 10px 0;
  }

  .task-name {
    max-width: 100%;
    width: 100%;
    white-space: normal;
    word-break: break-all;
    font-size: 13px;
  }

  .task-inline-meta {
    flex-wrap: wrap;
    width: 100%;
  }

  .meta-text {
    max-width: 160px;
  }

  .task-actions {
    width: 100%;
    justify-content: flex-end;
    margin-left: 0;
  }
}
</style>
