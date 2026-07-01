<template>
  <div class="competition-detail-page">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="router.push('/committee/competitions')">返回列表</el-button>
      <h2>{{ competition.name || '赛事详情' }}</h2>
    </div>

    <el-card v-loading="loading" shadow="never">
      <!-- 基本信息 -->
      <el-descriptions :column="2" border>
        <el-descriptions-item label="赛事名称">{{ competition.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="competition.status === 'ACTIVE' ? 'success' : 'info'">
            {{ competition.status === 'ACTIVE' ? '已激活' : '草稿' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="当前阶段">
          <el-tag :type="stageTagType(competition.stage)">{{ stageLabel(competition.stage) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ fmt(competition.createdAt) }}</el-descriptions-item>

        <el-descriptions-item label="基层组前缀">
          <el-tag type="primary" size="small">{{ competition.basicGroupPrefix || 'A' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="综合组前缀">
          <el-tag type="warning" size="small">{{ competition.comprehensiveGroupPrefix || 'B' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="进阶组前缀">
          <el-tag type="success" size="small">{{ competition.advancedGroupPrefix || 'C' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label=""> </el-descriptions-item>

        <el-descriptions-item label="报名开始">{{ fmt(competition.registerStart) }}</el-descriptions-item>
        <el-descriptions-item label="报名截止">{{ fmt(competition.registerEnd) }}</el-descriptions-item>
        <el-descriptions-item label="书审开始">{{ fmt(competition.bookReviewStart) }}</el-descriptions-item>
        <el-descriptions-item label="书审截止">{{ fmt(competition.bookReviewEnd) }}</el-descriptions-item>
        <el-descriptions-item label="面谈开始">{{ fmt(competition.interviewStart) }}</el-descriptions-item>
        <el-descriptions-item label="面谈截止">{{ fmt(competition.interviewEnd) }}</el-descriptions-item>
        <el-descriptions-item label="决赛开始">{{ fmt(competition.finalStart) }}</el-descriptions-item>
        <el-descriptions-item label="决赛截止">{{ fmt(competition.finalEnd) }}</el-descriptions-item>
      </el-descriptions>

      <!-- 操作按钮 -->
      <div class="actions">
        <el-button type="primary" @click="openEditDialog">
          <el-icon><Edit /></el-icon>修改配置
        </el-button>
        <el-button
          v-if="competition.status === 'DRAFT'"
          type="success"
          @click="handleActivate"
        >激活赛事</el-button>
        <el-button
          v-if="competition.status === 'ACTIVE'"
          type="warning"
          @click="handleDeactivate"
        >撤回激活</el-button>
        <el-button
          v-if="competition.status === 'ACTIVE'"
          type="primary"
          plain
          @click="openStageDialog"
        >推进阶段</el-button>
      </div>
    </el-card>

    <!-- 修改配置弹窗 -->
    <el-dialog v-model="editVisible" title="修改赛事配置" width="560px">
      <el-alert
        v-if="competition.status === 'ACTIVE'"
        type="warning"
        :closable="false"
        style="margin-bottom: 16px"
      >赛事已激活，名称和分组前缀不可修改。</el-alert>

      <el-form :model="editForm" label-width="110px">
        <!-- 名称和前缀仅 DRAFT 可改 -->
        <template v-if="competition.status === 'DRAFT'">
          <el-form-item label="赛事名称">
            <el-input v-model="editForm.name" placeholder="请输入赛事名称" />
          </el-form-item>
          <el-form-item label="基层组前缀" :error="prefixError.basic">
            <el-input
              v-model="editForm.basicGroupPrefix"
              placeholder="默认 A"
              maxlength="1"
              style="width:80px"
              @input="val => editForm.basicGroupPrefix = sanitizePrefixInput(val)"
            />
            <span class="prefix-hint">生成 {{ editForm.basicGroupPrefix || 'A' }}1、{{ editForm.basicGroupPrefix || 'A' }}2…</span>
          </el-form-item>
          <el-form-item label="综合组前缀" :error="prefixError.comprehensive">
            <el-input
              v-model="editForm.comprehensiveGroupPrefix"
              placeholder="默认 B"
              maxlength="1"
              style="width:80px"
              @input="val => editForm.comprehensiveGroupPrefix = sanitizePrefixInput(val)"
            />
            <span class="prefix-hint">生成 {{ editForm.comprehensiveGroupPrefix || 'B' }}1、{{ editForm.comprehensiveGroupPrefix || 'B' }}2…</span>
          </el-form-item>
          <el-form-item label="进阶组前缀" :error="prefixError.advanced">
            <el-input
              v-model="editForm.advancedGroupPrefix"
              placeholder="默认 C"
              maxlength="1"
              style="width:80px"
              @input="val => editForm.advancedGroupPrefix = sanitizePrefixInput(val)"
            />
            <span class="prefix-hint">生成 {{ editForm.advancedGroupPrefix || 'C' }}1、{{ editForm.advancedGroupPrefix || 'C' }}2…</span>
          </el-form-item>
          <el-divider />
        </template>

        <!-- 时间窗口（DRAFT 和 ACTIVE 都可改） -->
        <el-form-item label="报名开始">
          <el-date-picker v-model="editForm.registerStart" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="报名开始" style="width:220px" />
        </el-form-item>
        <el-form-item label="报名截止">
          <el-date-picker v-model="editForm.registerEnd" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" :default-time="new Date(2000,0,1,23,59,59)" placeholder="报名截止" style="width:220px" />
        </el-form-item>
        <el-form-item label="书审开始">
          <el-date-picker v-model="editForm.bookReviewStart" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="书审开始" style="width:220px" />
        </el-form-item>
        <el-form-item label="书审截止">
          <el-date-picker v-model="editForm.bookReviewEnd" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" :default-time="new Date(2000,0,1,23,59,59)" placeholder="书审截止" style="width:220px" />
        </el-form-item>
        <el-form-item label="面谈开始">
          <el-date-picker v-model="editForm.interviewStart" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="面谈开始" style="width:220px" />
        </el-form-item>
        <el-form-item label="面谈截止">
          <el-date-picker v-model="editForm.interviewEnd" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" :default-time="new Date(2000,0,1,23,59,59)" placeholder="面谈截止" style="width:220px" />
        </el-form-item>
        <el-form-item label="决赛开始">
          <el-date-picker v-model="editForm.finalStart" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="决赛开始" style="width:220px" />
        </el-form-item>
        <el-form-item label="决赛截止">
          <el-date-picker v-model="editForm.finalEnd" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" :default-time="new Date(2000,0,1,23,59,59)" placeholder="决赛截止" style="width:220px" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveConfig">保存</el-button>
      </template>
    </el-dialog>

    <!-- 推进阶段弹窗 -->
    <el-dialog v-model="stageVisible" title="推进当前阶段" width="360px">
      <el-form label-width="90px">
        <el-form-item label="目标阶段">
          <el-select v-model="targetStage" placeholder="选择阶段">
            <el-option label="报名阶段 (REGISTER)" value="REGISTER" />
            <el-option label="书审阶段 (BOOK_REVIEW)" value="BOOK_REVIEW" />
            <el-option label="面谈阶段 (INTERVIEW)" value="INTERVIEW" />
            <el-option label="决赛阶段 (FINAL)" value="FINAL" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stageVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingStage" @click="handleAdvanceStage">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { computePrefixErrors, hasPrefixError, sanitizePrefixInput } from '@/utils/groupPrefix'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import {
  getCompetition,
  updateCompetitionConfig,
  activateCompetition,
  deactivateCompetition
} from '@/api/competition'

const route = useRoute()
const router = useRouter()
const competitionId = route.params.id

const competition = ref({})
const loading = ref(false)

// 编辑配置
const editVisible = ref(false)
const saving = ref(false)
const editForm = ref({})

const prefixError = computed(() => {
  const f = editForm.value
  return computePrefixErrors(f.basicGroupPrefix, f.comprehensiveGroupPrefix, f.advancedGroupPrefix)
})

// 推进阶段
const stageVisible = ref(false)
const savingStage = ref(false)
const targetStage = ref('')

const STAGE_LABELS = { REGISTER: '报名阶段', BOOK_REVIEW: '书审阶段', INTERVIEW: '面谈阶段', FINAL: '决赛阶段' }
const STAGE_TYPES  = { REGISTER: 'success', BOOK_REVIEW: 'warning', INTERVIEW: 'warning', FINAL: 'danger' }
const stageLabel = (s) => STAGE_LABELS[s] || (s || '未开始')
const stageTagType = (s) => STAGE_TYPES[s] || 'info'
const fmt = (d) => d ? dayjs(d).format('YYYY-MM-DD HH:mm') : '-'

const loadCompetition = async () => {
  loading.value = true
  try {
    const res = await getCompetition(competitionId)
    if (res?.success && res.data) {
      competition.value = res.data
    }
  } catch {
    // 拦截器已处理
  } finally {
    loading.value = false
  }
}

const openEditDialog = () => {
  const c = competition.value
  editForm.value = {
    name: c.name,
    basicGroupPrefix: c.basicGroupPrefix || '',
    comprehensiveGroupPrefix: c.comprehensiveGroupPrefix || '',
    advancedGroupPrefix: c.advancedGroupPrefix || '',
    registerStart: c.registerStart || null,
    registerEnd: c.registerEnd || null,
    bookReviewStart: c.bookReviewStart || null,
    bookReviewEnd: c.bookReviewEnd || null,
    interviewStart: c.interviewStart || null,
    interviewEnd: c.interviewEnd || null,
    finalStart: c.finalStart || null,
    finalEnd: c.finalEnd || null,
  }
  editVisible.value = true
}

const handleSaveConfig = async () => {
  if (competition.value.status === 'DRAFT' && hasPrefixError(prefixError.value)) {
    ElMessage.warning('请修正前缀配置后再保存')
    return
  }
  saving.value = true
  try {
    // ACTIVE 时不传 name / prefix（锁定字段）
    const payload = { ...editForm.value }
    if (competition.value.status === 'ACTIVE') {
      delete payload.name
      delete payload.basicGroupPrefix
      delete payload.comprehensiveGroupPrefix
      delete payload.advancedGroupPrefix
    }
    // 空字符串前缀转 undefined
    ;['basicGroupPrefix','comprehensiveGroupPrefix','advancedGroupPrefix'].forEach(k => {
      if (payload[k] === '') delete payload[k]
    })
    const res = await updateCompetitionConfig(competitionId, payload)
    if (res && res.success === false) {
      ElMessage.error(res.message || '保存失败')
      return
    }
    if (res?.data) competition.value = res.data
    ElMessage.success('保存成功')
    editVisible.value = false
    if (!res?.data) loadCompetition()
  } catch {
    // 拦截器已处理
  } finally {
    saving.value = false
  }
}

const openStageDialog = () => {
  targetStage.value = competition.value.stage || ''
  stageVisible.value = true
}

const handleAdvanceStage = async () => {
  if (!targetStage.value) {
    ElMessage.warning('请选择目标阶段')
    return
  }
  savingStage.value = true
  try {
    const res = await updateCompetitionConfig(competitionId, { stage: targetStage.value })
    if (res && res.success === false) {
      ElMessage.error(res.message || '操作失败')
      return
    }
    if (res?.data) competition.value = res.data
    ElMessage.success('阶段已更新')
    stageVisible.value = false
    if (!res?.data) loadCompetition()
  } catch {
    // 拦截器已处理
  } finally {
    savingStage.value = false
  }
}

const handleActivate = async () => {
  try {
    await ElMessageBox.confirm(
      `确定激活赛事「${competition.value.name}」？激活后参赛者可报名，同年只允许一个激活赛事。`,
      '确认激活', { type: 'warning', confirmButtonText: '激活', cancelButtonText: '取消' }
    )
  } catch { return }
  try {
    const res = await activateCompetition(competitionId)
    if (res && res.success === false) { ElMessage.error(res.message || '激活失败'); return }
    ElMessage.success('激活成功')
    loadCompetition()
  } catch {}
}

const handleDeactivate = async () => {
  try {
    await ElMessageBox.confirm(
      `确定撤回赛事「${competition.value.name}」的激活？前提：无任何报名记录。`,
      '确认撤回', { type: 'warning', confirmButtonText: '撤回', cancelButtonText: '取消' }
    )
  } catch { return }
  try {
    const res = await deactivateCompetition(competitionId)
    if (res && res.success === false) { ElMessage.error(res.message || '撤回失败'); return }
    ElMessage.success('撤回成功')
    loadCompetition()
  } catch {}
}

onMounted(loadCompetition)
</script>

<style scoped lang="scss">
.competition-detail-page {
  padding: 20px;

  .page-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
    }
  }

  .actions {
    margin-top: 20px;
    display: flex;
    gap: 10px;
  }

  .prefix-hint {
    margin-left: 8px;
    color: #909399;
    font-size: 13px;
  }
}
</style>
