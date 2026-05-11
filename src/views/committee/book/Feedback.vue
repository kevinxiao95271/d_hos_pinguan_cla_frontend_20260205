<template>
  <div class="feedback-page">
    <stage-progress current-stage="BOOK" :stages="stagesList" />

    <el-card class="feedback-card">
      <template #header>
        <div class="card-header">
          <span>专家意见反馈</span>
          <div class="actions">
            <el-button
              type="success"
              plain
              size="small"
              :disabled="!rows.length"
              :loading="publishing"
              @click="handleBatchPublish(true)"
            >
              批量发布
            </el-button>
            <el-button
              type="warning"
              plain
              size="small"
              :disabled="!rows.length"
              :loading="publishing"
              @click="handleBatchPublish(false)"
            >
              批量撤回
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="医疗机构">
          <el-input
            v-model="filters.institutionName"
            placeholder="请输入机构名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="竞赛组别">
          <el-select
            v-model="filters.groupType"
            placeholder="全部"
            clearable
            style="width: 140px"
            @change="handleGroupTypeChange"
          >
            <el-option
              v-for="type in groupTypeOptions"
              :key="type"
              :label="getGroupTypeText(type)"
              :value="type"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="分组">
          <el-select
            v-model="filters.groupCode"
            placeholder="全部"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="code in availableGroupCodes"
              :key="code"
              :label="code"
              :value="code"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="项目名称">
          <el-input
            v-model="filters.projectName"
            placeholder="请输入项目名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="发布状态">
          <el-select
            v-model="filters.published"
            placeholder="全部"
            clearable
            style="width: 120px"
          >
            <el-option label="已发布" :value="true" />
            <el-option label="未发布" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table
        v-loading="loading"
        :data="rows"
        border
        stripe
        max-height="calc(100vh - 260px)"
      >
        <el-table-column prop="registrationId" label="项目编号" width="90" align="center" />
        <el-table-column prop="projectName" label="项目名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="institutionName" label="医疗机构" min-width="170" show-overflow-tooltip />
        <el-table-column label="组别" width="100" align="center">
          <template #default="{ row }">
            {{ getGroupTypeText(row.groupType) }}
          </template>
        </el-table-column>
        <el-table-column prop="groupCode" label="分组" width="90" align="center" />
        <el-table-column label="亮点（最终展示）" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">{{ row.finalHighlight || '-' }}</template>
        </el-table-column>
        <el-table-column label="不足（最终展示）" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">{{ row.finalWeakness || '-' }}</template>
        </el-table-column>
        <el-table-column label="发布状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.published ? 'success' : 'info'">
              {{ row.published ? '已发布' : '未发布' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="170" align="center">
          <template #default="{ row }">{{ formatDateTime(row.updatedAt) }}</template>
        </el-table-column>
        <el-table-column label="发布时间" width="170" align="center">
          <template #default="{ row }">{{ formatDateTime(row.publishedAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-space>
              <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
              <el-button
                v-if="!row.published"
                type="success"
                link
                :loading="publishingRegistrationId === row.registrationId"
                @click="handlePublish(row, true)"
              >
                发布
              </el-button>
              <el-button
                v-else
                type="warning"
                link
                :loading="publishingRegistrationId === row.registrationId"
                @click="handlePublish(row, false)"
              >
                撤回
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && rows.length === 0" description="暂无反馈数据" />
    </el-card>

    <el-dialog
      v-model="editDialogVisible"
      width="92vw"
      top="4vh"
      :close-on-click-modal="false"
      :title="`编辑反馈 - ${currentRow?.projectName || ''}`"
    >
      <div class="edit-grid">
        <el-card shadow="never">
          <template #header>
            <span>评委原始汇总（脱敏）</span>
          </template>
          <div class="block-title">亮点</div>
          <div class="preview-block">{{ currentRow?.sourceHighlight || '-' }}</div>
          <div class="block-title">不足</div>
          <div class="preview-block">{{ currentRow?.sourceWeakness || '-' }}</div>
        </el-card>

        <el-card shadow="never">
          <template #header>
            <span>组委会编辑稿</span>
          </template>
          <el-form label-width="80px">
            <el-form-item label="亮点">
              <el-input
                v-model="editForm.highlight"
                type="textarea"
                :rows="6"
                maxlength="5000"
                show-word-limit
                placeholder="为空时默认回退原始汇总"
              />
            </el-form-item>
            <el-form-item label="不足">
              <el-input
                v-model="editForm.weakness"
                type="textarea"
                :rows="6"
                maxlength="5000"
                show-word-limit
                placeholder="为空时默认回退原始汇总"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <template #footer>
        <el-button @click="resetEditToSource">重置为原始汇总</el-button>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'
import { getCurrentCompetitionId } from '@/utils/competition'
import {
  getProjectFeedback,
  getProjectFeedbackFilterOptions,
  updateProjectFeedback,
  publishProjectFeedback,
  batchPublishProjectFeedback
} from '@/api/admin'
import dayjs from 'dayjs'

const { stagesList } = useCompetitionStages()

const loading = ref(false)
const saving = ref(false)
const publishing = ref(false)
const publishingRegistrationId = ref(null)
const rows = ref([])
const currentCompetitionId = ref(null)
const groupTypeOptions = ref([])
const availableGroupCodes = ref([])

const filters = reactive({
  institutionName: '',
  groupType: '',
  groupCode: '',
  projectName: '',
  published: null
})

const editDialogVisible = ref(false)
const currentRow = ref(null)
const editForm = reactive({
  highlight: '',
  weakness: ''
})

const formatDateTime = (value) => {
  if (!value) return '-'
  return dayjs(value).format('YYYY-MM-DD HH:mm:ss')
}

const getGroupTypeText = (type) => {
  const map = {
    BASIC: '基层组',
    COMPREHENSIVE: '综合组',
    ADVANCED: '进阶组'
  }
  return map[type] || type || '-'
}

const resetFilters = () => {
  filters.institutionName = ''
  filters.groupType = ''
  filters.groupCode = ''
  filters.projectName = ''
  filters.published = null
  loadFilterOptions()
  loadData()
}

const ensureCompetitionId = async () => {
  if (currentCompetitionId.value) {
    return currentCompetitionId.value
  }
  const competitionId = await getCurrentCompetitionId()
  if (!competitionId) {
    ElMessage.warning('请先选择赛事')
    return null
  }
  currentCompetitionId.value = competitionId
  return competitionId
}

const loadFilterOptions = async () => {
  const competitionId = await ensureCompetitionId()
  if (!competitionId) return

  try {
    const params = { competitionId, stage: 'BOOK' }
    if (filters.groupType) params.groupType = filters.groupType
    const res = await getProjectFeedbackFilterOptions(params)
    if (!res.success) {
      ElMessage.error(res.message || '加载筛选项失败')
      return
    }
    groupTypeOptions.value = res.data?.groupTypes || []
    availableGroupCodes.value = res.data?.groupCodes || []
    if (filters.groupCode && !availableGroupCodes.value.includes(filters.groupCode)) {
      filters.groupCode = ''
    }
  } catch (error) {
    console.error('加载筛选项失败:', error)
    ElMessage.error('加载筛选项失败')
  }
}

const handleGroupTypeChange = async () => {
  await loadFilterOptions()
  await loadData()
}

const loadData = async () => {
  const competitionId = await ensureCompetitionId()
  if (!competitionId) return

  loading.value = true
  try {
    const params = {
      competitionId,
      stage: 'BOOK'
    }
    if (filters.groupType) params.groupType = filters.groupType
    if (filters.groupCode && filters.groupCode.trim()) params.groupCode = filters.groupCode.trim()
    if (filters.projectName && filters.projectName.trim()) params.projectName = filters.projectName.trim()
    if (filters.institutionName && filters.institutionName.trim()) params.institutionName = filters.institutionName.trim()
    if (typeof filters.published === 'boolean') params.published = filters.published

    const res = await getProjectFeedback(params)
    if (!res.success) {
      throw new Error(res.message || '加载反馈失败')
    }
    rows.value = res.data || []
  } catch (error) {
    console.error('加载专家反馈失败:', error)
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const openEditDialog = (row) => {
  currentRow.value = row
  editForm.highlight = row.editedHighlight ?? row.sourceHighlight ?? ''
  editForm.weakness = row.editedWeakness ?? row.sourceWeakness ?? ''
  editDialogVisible.value = true
}

const resetEditToSource = () => {
  if (!currentRow.value) return
  editForm.highlight = currentRow.value.sourceHighlight ?? ''
  editForm.weakness = currentRow.value.sourceWeakness ?? ''
}

const saveEdit = async () => {
  if (!currentRow.value) return
  saving.value = true
  try {
    const payload = {
      highlight: editForm.highlight?.trim() || null,
      weakness: editForm.weakness?.trim() || null
    }
    const res = await updateProjectFeedback(currentRow.value.registrationId, payload, 'BOOK')
    if (!res.success) {
      ElMessage.error(res.message || '保存失败')
      return
    }
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    await loadData()
  } catch (error) {
    console.error('保存反馈失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handlePublish = async (row, nextPublished) => {
  const actionText = nextPublished ? '发布' : '撤回'
  try {
    await ElMessageBox.confirm(`确认${actionText}【${row.projectName}】反馈？`, `${actionText}确认`, {
      type: 'warning'
    })
    publishingRegistrationId.value = row.registrationId
    const res = await publishProjectFeedback(row.registrationId, 'BOOK', nextPublished)
    if (!res.success) {
      ElMessage.error(res.message || `${actionText}失败`)
      return
    }
    ElMessage.success(`${actionText}成功`)
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(`${actionText}反馈失败:`, error)
      ElMessage.error(`${actionText}失败`)
    }
  } finally {
    publishingRegistrationId.value = null
  }
}

const handleBatchPublish = async (nextPublished) => {
  const competitionId = await getCurrentCompetitionId()
  if (!competitionId) {
    ElMessage.warning('请先选择赛事')
    return
  }
  const actionText = nextPublished ? '批量发布' : '批量撤回'
  try {
    await ElMessageBox.confirm(
      `确认对当前赛事书审反馈执行${actionText}？`,
      `${actionText}确认`,
      { type: 'warning' }
    )
    publishing.value = true
    const res = await batchPublishProjectFeedback(competitionId, 'BOOK', nextPublished)
    if (!res.success) {
      ElMessage.error(res.message || `${actionText}失败`)
      return
    }
    ElMessage.success(`${actionText}成功`)
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(`${actionText}失败:`, error)
      ElMessage.error(`${actionText}失败`)
    }
  } finally {
    publishing.value = false
  }
}

onMounted(() => {
  loadFilterOptions()
  loadData()
})
</script>

<style scoped lang="scss">
.feedback-page {
  padding: 10px 12px;
}

.feedback-card {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    font-size: 16px;
    font-weight: 600;
  }

  .actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .filter-form {
    margin-bottom: 12px;
  }
}

.edit-grid {
  display: grid;
  grid-template-columns: 1fr 1.3fr;
  gap: 12px;
}

.block-title {
  margin-bottom: 8px;
  color: #606266;
  font-size: 12px;
}

.preview-block {
  min-height: 180px;
  max-height: 52vh;
  overflow: auto;
  padding: 8px 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  background: #fafafa;
}

:deep(.el-dialog__body) {
  padding-top: 8px;
  padding-bottom: 12px;
}

:deep(.el-form-item__label) {
  font-size: 13px;
}

:deep(.el-textarea__inner) {
  min-height: 220px !important;
  font-size: 13px;
  line-height: 1.6;
}
</style>
