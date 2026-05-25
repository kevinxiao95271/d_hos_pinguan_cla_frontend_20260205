<template>
  <div class="final-review-page">

    <!-- 顶部信息栏 -->
    <div class="page-header">
      <el-button :icon="ArrowLeft" plain @click="goBack">返回</el-button>
      <div class="project-info">
        <h2 class="project-title">{{ projectName }}</h2>
        <div class="meta-tags">
          <el-tag type="info" size="small">{{ institutionName }}</el-tag>
          <el-tag type="info" size="small" v-if="sessionCode">{{ sessionCode }}</el-tag>
          <el-tag type="info" size="small" v-if="sessionOrder">第 {{ sessionOrder }} 号上台</el-tag>
          <el-tag :type="scoreFormTagType" size="small">{{ scoreFormText }}</el-tag>
          <el-tag v-if="isViewMode" type="success" size="small">查看模式</el-tag>
          <el-tag v-if="isScored" type="success" size="small">已提交</el-tag>
        </div>
      </div>
    </div>

    <!-- 评分卡 -->
    <el-card v-loading="loading" class="score-card">
      <template #header>
        <div class="score-card-header">
          <span>{{ scoreFormText }} 评分表（满分 100 分）</span>
          <div class="total-display">
            合计：<span class="total-number">{{ computedTotal }}</span> 分
          </div>
        </div>
      </template>

      <div class="score-items">
        <div v-for="item in scoreItems" :key="item.key" class="score-item">
          <div class="item-info">
            <span class="item-name">{{ item.label }}</span>
            <span class="item-max-hint">满分 {{ item.max }} 分</span>
          </div>
          <div class="item-control">
            <el-slider
              v-model="form[item.key]"
              :min="0"
              :max="item.max"
              :step="0.5"
              :disabled="isViewMode"
              :show-tooltip="true"
              :marks="{ 0: '0', [item.max]: String(item.max) }"
              style="flex: 1; margin: 0 16px"
            />
            <el-input-number
              v-model="form[item.key]"
              :min="0"
              :max="item.max"
              :step="0.5"
              :precision="1"
              :disabled="isViewMode"
              size="default"
              style="width: 110px"
            />
          </div>
        </div>
      </div>

      <el-divider />

      <div class="total-row">
        <span class="total-label">合计得分</span>
        <span class="total-value-large">{{ computedTotal }} / 100</span>
      </div>

      <el-divider />

      <!-- 亮点 / 不足 -->
      <div class="opinion-section">
        <div class="opinion-item">
          <div class="opinion-label">亮点意见 <span class="optional">（选填，最多 1000 字）</span></div>
          <el-input
            v-model="form.highlight"
            type="textarea"
            :rows="3"
            maxlength="1000"
            show-word-limit
            :disabled="isViewMode"
            placeholder="请输入本项目的亮点意见…"
          />
        </div>
        <div class="opinion-item" style="margin-top: 16px">
          <div class="opinion-label">不足意见 <span class="optional">（选填，最多 1000 字）</span></div>
          <el-input
            v-model="form.weakness"
            type="textarea"
            :rows="3"
            maxlength="1000"
            show-word-limit
            :disabled="isViewMode"
            placeholder="请输入本项目的不足意见…"
          />
        </div>
      </div>
    </el-card>

    <!-- 操作栏 -->
    <div v-if="!isViewMode" class="action-bar">
      <el-button @click="goBack">取消</el-button>
      <el-button :loading="saving" @click="handleSaveDraft">暂存草稿</el-button>
      <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
        提交评分
      </el-button>
    </div>

    <!-- 提交成功感谢弹窗 -->
    <el-dialog
      v-model="showThankYou"
      :show-close="false"
      :close-on-click-modal="false"
      width="380px"
      align-center
    >
      <div class="thank-you">
        <div class="ty-icon">✅</div>
        <h2>评分已提交</h2>
        <p>感谢您认真完成本次决赛评审！</p>
      </div>
      <template #footer>
        <el-button type="primary" style="width: 100%" size="large" @click="goBack">返回任务列表</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { saveFinalScoreDraft, submitFinalScore } from '@/api/review'

const route = useRoute()
const router = useRouter()

// ── 路由参数 ────────────────────────────────────────────────
const taskId = computed(() => route.params.taskId)
const projectName = computed(() => route.query.projectName || '未知项目')
const institutionName = computed(() => route.query.institutionName || '')
const sessionCode = computed(() => route.query.sessionCode || '')
const sessionOrder = computed(() => route.query.sessionOrder || '')
const scoreForm = computed(() => (route.query.scoreForm || 'QCC').toUpperCase())
const isViewMode = computed(() => route.query.view === 'score' || route.query.status === 'SCORED')
const isScored = computed(() => route.query.status === 'SCORED')

// ── 评分字段定义（由 scoreForm 决定） ──────────────────────
const SCORE_ITEMS = {
  QCC: [
    { key: 'plan',         label: '1. 计划',     max: 10 },
    { key: 'problem',      label: '2. 项目结构', max: 15 },
    { key: 'action',       label: '3. 对策行动', max: 15 },
    { key: 'success',      label: '4. 成果表现', max: 20 },
    { key: 'review',       label: '5. 查验',     max: 5  },
    { key: 'operation',    label: '6. 整体运作', max: 15 },
    { key: 'presentation', label: '7. 现场表现', max: 20 }
  ],
  NON_QCC: [
    { key: 'plan',         label: '1. 选题',     max: 15 },
    { key: 'problem',      label: '2. 原因分析', max: 10 },
    { key: 'action',       label: '3. 计划',     max: 10 },
    { key: 'success',      label: '4. 实施',     max: 20 },
    { key: 'review',       label: '5. 成果表现', max: 10 },
    { key: 'operation',    label: '6. 检讨',     max: 10 },
    { key: 'presentation', label: '7. 整体运作', max: 15 },
    { key: 'item8',        label: '8. 现场表现', max: 10 }
  ],
  QFD: [
    { key: 'plan',    label: '1. 圈活动特征',   max: 15 },
    { key: 'problem', label: '2. 课题明确化',   max: 25 },
    { key: 'action',  label: '3. 方策拟定',     max: 25 },
    { key: 'success', label: '4. 执行力与成果', max: 25 },
    { key: 'review',  label: '5. 现场发表',     max: 10 }
  ]
}

const scoreItems = computed(() => SCORE_ITEMS[scoreForm.value] || SCORE_ITEMS.QCC)

const scoreFormText = computed(() => {
  const map = { QCC: 'QCC 问题解决型', NON_QCC: '非 QCC 课题达成型', QFD: 'QFD 质量功能展开' }
  return map[scoreForm.value] || scoreForm.value
})

const scoreFormTagType = computed(() => {
  if (scoreForm.value === 'QCC') return 'primary'
  if (scoreForm.value === 'QFD') return 'warning'
  return 'success'
})

// ── 表单数据 ────────────────────────────────────────────────

// 按 scoreForm 生成各字段默认值（总分默认 80，按权重比例拆分）
const createDefaultForm = (sf) => {
  const items = SCORE_ITEMS[sf] || SCORE_ITEMS.QCC
  const base = {}
  for (const item of items) {
    base[item.key] = item.max * 0.8
  }
  // 不属于本表单的字段置 null
  const allKeys = ['plan', 'problem', 'action', 'success', 'review', 'operation', 'presentation', 'item8']
  const usedKeys = new Set(items.map(i => i.key))
  for (const k of allKeys) {
    if (!usedKeys.has(k)) base[k] = null
  }
  base.highlight = ''
  base.weakness = ''
  return base
}

const form = ref(createDefaultForm(scoreForm.value))
const loading = ref(false)
const saving = ref(false)
const submitting = ref(false)
const showThankYou = ref(false)

// 根据 scoreForm 重置不参与评分的字段（当 scoreForm 已确定时无需再调，保留兼容）
const initFormByScoreForm = () => {
  const sf = scoreForm.value
  const items = SCORE_ITEMS[sf] || SCORE_ITEMS.QCC
  const usedKeys = new Set(items.map(i => i.key))
  for (const k of ['operation', 'presentation', 'item8']) {
    if (!usedKeys.has(k)) form.value[k] = null
  }
}

// ── 合计 ────────────────────────────────────────────────────
const computedTotal = computed(() => {
  let total = 0
  for (const item of scoreItems.value) {
    total += Number(form.value[item.key] ?? 0)
  }
  return Math.round(total * 10) / 10
})

// ── 从路由 draftScore 初始化（有草稿则覆盖，否则保持默认 80 分） ──
const loadDraftFromRoute = () => {
  const draft = route.query.draftScore
  if (!draft) {
    // 无草稿，默认值已由 createDefaultForm 设置好
    initFormByScoreForm()
    return
  }
  try {
    const d = typeof draft === 'string' ? JSON.parse(draft) : draft
    // 只覆盖草稿中有值的字段，null/undefined 保持默认
    for (const key of Object.keys(form.value)) {
      if (d[key] != null) form.value[key] = d[key]
    }
    form.value.highlight = d.highlight || ''
    form.value.weakness = d.weakness || ''
    initFormByScoreForm()
  } catch {
    initFormByScoreForm()
  }
}

// ── 保存草稿 ────────────────────────────────────────────────
const buildPayload = () => ({
  scoreForm: scoreForm.value,
  plan: form.value.plan,
  problem: form.value.problem,
  action: form.value.action,
  success: form.value.success,
  review: form.value.review,
  operation: scoreForm.value === 'QFD' ? null : (form.value.operation ?? null),
  presentation: scoreForm.value === 'QFD' ? null : (form.value.presentation ?? null),
  item8: scoreForm.value === 'NON_QCC' ? (form.value.item8 ?? null) : null,
  total: computedTotal.value,
  highlight: form.value.highlight || null,
  weakness: form.value.weakness || null
})

const handleSaveDraft = async () => {
  saving.value = true
  try {
    const res = await saveFinalScoreDraft(taskId.value, buildPayload())
    if (res.success) {
      ElMessage.success('草稿已保存')
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch {
    ElMessage.error('保存失败，请检查网络')
  } finally {
    saving.value = false
  }
}

// ── 提交评分 ────────────────────────────────────────────────
const handleSubmit = async () => {
  try {
    await ElMessageBox.confirm(
      `当前总分 ${computedTotal.value} 分，提交后不可修改，确认提交？`,
      '提交决赛评分',
      { confirmButtonText: '确认提交', cancelButtonText: '取消', type: 'warning' }
    )
    submitting.value = true
    const res = await submitFinalScore(taskId.value, buildPayload())
    if (res.success) {
      showThankYou.value = true
    } else {
      ElMessage.error(res.message || '提交失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

const goBack = () => router.push('/reviewer/dashboard')

onMounted(() => {
  loadDraftFromRoute()
})
</script>

<style scoped lang="scss">
.final-review-page {
  padding: 20px;
  max-width: 860px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;

  .project-info {
    flex: 1;
    .project-title {
      font-size: 18px;
      font-weight: 700;
      color: #303133;
      margin: 0 0 8px;
    }
    .meta-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
  }
}

.score-card {
  margin-bottom: 20px;
}

.score-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  .total-display {
    font-size: 14px;
    color: #606266;
    .total-number {
      font-size: 22px;
      font-weight: 700;
      color: #409eff;
    }
  }
}

.score-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.score-item {
  .item-info {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 8px;

    .item-name {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
    }
    .item-max-hint {
      font-size: 12px;
      color: #909399;
    }
  }

  .item-control {
    display: flex;
    align-items: center;
  }
}

.total-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 0;

  .total-label {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }

  .total-value-large {
    font-size: 24px;
    font-weight: 700;
    color: #409eff;
  }
}

.opinion-section {
  .opinion-label {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;

    .optional {
      font-size: 12px;
      font-weight: 400;
      color: #909399;
    }
  }
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 0;
}

.thank-you {
  text-align: center;
  padding: 20px 10px 10px;

  .ty-icon { font-size: 48px; margin-bottom: 12px; }
  h2 { font-size: 20px; font-weight: 700; color: #303133; margin: 0 0 10px; }
  p  { font-size: 14px; color: #606266; line-height: 1.8; margin: 0; }
}

/* 移动端 */
@media (max-width: 768px) {
  .final-review-page { padding: 12px; }
  .score-item .item-control { flex-direction: column; align-items: flex-start; gap: 10px; }
  .action-bar { flex-direction: column; .el-button { width: 100%; } }
}
</style>
