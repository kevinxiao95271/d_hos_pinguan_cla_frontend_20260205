<template>
  <div class="feedback-page">
<el-card class="feedback-card">
      <template #header>
        <div class="card-header">
          <span>专家意见反馈</span>
          <div class="actions">
            <!-- 导出 Excel -->
            <el-button
              size="small"
              plain
              :loading="exporting"
              :disabled="!rows.length"
              @click="handleExport"
            >
              导出 Excel
            </el-button>

            <!-- 批量符号替换 Popover -->
            <el-popover
              v-model:visible="batchPopoverVisible"
              placement="bottom-end"
              :width="340"
              trigger="click"
            >
              <template #reference>
                <el-button
                  size="small"
                  plain
                  :loading="batchSaving"
                  :disabled="!rows.length"
                >
                  批量符号替换
                </el-button>
              </template>

              <div class="batch-replace-panel">
                <div class="batch-replace-title">作用于当前筛选结果（{{ rows.length }} 条）的亮点和不足字段</div>

                <!-- A：数字序号 → 自定义符号 -->
                <div class="batch-replace-section">
                  <div class="batch-replace-label">① 行首数字序号 → 符号</div>
                  <div class="batch-replace-desc">如 <code>1.</code> <code>2、</code> <code>3。</code> 等替换为指定字符</div>
                  <div class="batch-replace-row">
                    <span>替换为</span>
                    <el-input v-model="digitReplaceChar" size="small" style="width:60px" maxlength="2" />
                    <el-button
                      type="primary"
                      size="small"
                      :loading="batchSaving"
                      @click="handleBatchDigitReplace"
                    >
                      全量替换并保存
                    </el-button>
                  </div>
                </div>

                <el-divider style="margin: 10px 0" />

                <!-- B：行首字符 → 另一字符 -->
                <div class="batch-replace-section">
                  <div class="batch-replace-label">② 行首指定符号替换</div>
                  <div class="batch-replace-desc">只替换每行行首的字符，不动内容</div>
                  <div class="batch-replace-row">
                    <span>从</span>
                    <el-input v-model="charReplaceFrom" size="small" style="width:52px" maxlength="2" placeholder="▶" />
                    <span>→</span>
                    <el-input v-model="charReplaceTo" size="small" style="width:52px" maxlength="2" placeholder="●" />
                    <el-button
                      type="primary"
                      size="small"
                      :loading="batchSaving"
                      @click="handleBatchCharReplace"
                    >
                      全量替换并保存
                    </el-button>
                  </div>
                </div>
              </div>
            </el-popover>

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

          <!-- 单条替换工具栏（复用批量配置，仅作用于本条 editForm） -->
          <div class="inline-replace-toolbar">
            <span class="toolbar-title">替换工具</span>
            <div class="toolbar-group">
              <span class="toolbar-label">① 数字序号→</span>
              <el-input v-model="digitReplaceChar" size="small" style="width:52px" maxlength="2" />
              <el-button size="small" @click="applyDigitReplaceToForm">替换本条</el-button>
            </div>
            <el-divider direction="vertical" />
            <div class="toolbar-group">
              <span class="toolbar-label">② 行首</span>
              <el-input v-model="charReplaceFrom" size="small" style="width:44px" maxlength="2" placeholder="▶" />
              <span>→</span>
              <el-input v-model="charReplaceTo" size="small" style="width:44px" maxlength="2" placeholder="●" />
              <el-button size="small" @click="applyCharReplaceToForm">替换本条</el-button>
            </div>
          </div>

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
  <!-- 批量替换结果 / 重试对话框 -->
    <el-dialog
    v-model="batchResultVisible"
    title="批量替换保存结果"
    width="480px"
    :close-on-click-modal="false"
  >
    <div class="batch-result-summary">
      <el-result
        :icon="batchResultFailedItems.length === 0 ? 'success' : 'warning'"
        :title="batchResultFailedItems.length === 0
          ? `全部保存成功，共 ${batchResultTotal} 条`
          : `成功 ${batchResultSuccessCount} 条，失败 ${batchResultFailedItems.length} 条`"
        :sub-title="batchResultFailedItems.length === 0
          ? '所有记录的替换内容已写入数据库'
          : `共 ${batchResultTotal} 条，以下记录保存失败，可点击重试`"
      />
      <el-table
        v-if="batchResultFailedItems.length > 0"
        :data="batchResultFailedItems"
        border
        size="small"
        max-height="240"
        style="margin-top: 8px"
      >
        <el-table-column prop="registrationId" label="项目编号" width="90" align="center" />
        <el-table-column prop="projectName" label="项目名称" min-width="160" show-overflow-tooltip />
      </el-table>
    </div>
    <template #footer>
      <el-button @click="batchResultVisible = false">
        {{ batchResultFailedItems.length === 0 ? '关闭' : '放弃' }}
      </el-button>
      <el-button
        v-if="batchResultFailedItems.length > 0"
        type="primary"
        :loading="batchSaving"
        @click="retryFailedItems"
      >
        重试失败项（{{ batchResultFailedItems.length }} 条）
      </el-button>
    </template>
  </el-dialog>

  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCurrentCompetitionId } from '@/utils/competition'
import {
  getProjectFeedback,
  getProjectFeedbackFilterOptions,
  updateProjectFeedback,
  publishProjectFeedback,
  batchPublishProjectFeedback,
  batchSaveFeedbackDrafts,
  exportFeedbackExcel
} from '@/api/admin'
import dayjs from 'dayjs'

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

// ─── 符号替换工具 ────────────────────────────────────────────────────────────

// 共享配置（单条弹窗和批量操作复用同一套参数）
const digitReplaceChar = ref('●')
const charReplaceFrom = ref('')
const charReplaceTo = ref('●')

// 批量操作状态
const batchSaving = ref(false)
const batchPopoverVisible = ref(false)
const batchResultVisible = ref(false)
const batchResultTotal = ref(0)
const batchResultSuccessCount = ref(0)
const batchResultFailedItems = ref([])

// 行首数字序号替换：匹配 1. / 1、/ 1。/ 1, / 1） 等常见写法
const replaceDigitSymbol = (text, char) => {
  if (!text) return text
  return text.replace(/^(\d+\s*[.。、,，:：）)]\s*)/gm, char + ' ')
}

// 行首指定字符替换
const replaceLineStartChar = (text, from, to) => {
  if (!text || !from) return text
  const escaped = from.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`^${escaped}`, 'gm'), to)
}

// 单条：作用于当前编辑弹窗的 editForm
const applyDigitReplaceToForm = () => {
  if (!digitReplaceChar.value) { ElMessage.warning('请输入替换字符'); return }
  editForm.highlight = replaceDigitSymbol(editForm.highlight, digitReplaceChar.value)
  editForm.weakness = replaceDigitSymbol(editForm.weakness, digitReplaceChar.value)
}

const applyCharReplaceToForm = () => {
  if (!charReplaceFrom.value) { ElMessage.warning('请输入要替换的字符'); return }
  editForm.highlight = replaceLineStartChar(editForm.highlight, charReplaceFrom.value, charReplaceTo.value)
  editForm.weakness = replaceLineStartChar(editForm.weakness, charReplaceFrom.value, charReplaceTo.value)
}

// 工具：将数组切割为指定大小的块
const chunkArray = (arr, size) => {
  const chunks = []
  for (let i = 0; i < arr.length; i += size) chunks.push(arr.slice(i, i + size))
  return chunks
}

// 批量执行保存，返回失败项列表
const executeBatchSave = async (items) => {
  const failedItems = []
  const chunks = chunkArray(items, 200)
  for (const chunk of chunks) {
    try {
      const res = await batchSaveFeedbackDrafts(
        chunk.map(i => ({ registrationId: i.registrationId, highlight: i.highlight || null, weakness: i.weakness || null }))
      )
      if (!res.success) failedItems.push(...chunk)
    } catch {
      failedItems.push(...chunk)
    }
  }
  return failedItems
}

// 批量替换入口：传入替换函数，对 rows 全量处理后保存
const runBatchReplace = async (replaceFunc) => {
  if (!rows.value.length) { ElMessage.warning('当前无数据'); return }
  batchPopoverVisible.value = false
  batchSaving.value = true
  const items = rows.value.map(row => ({
    registrationId: row.registrationId,
    projectName: row.projectName,
    highlight: replaceFunc(row.editedHighlight ?? row.sourceHighlight ?? ''),
    weakness: replaceFunc(row.editedWeakness ?? row.sourceWeakness ?? '')
  }))
  batchResultTotal.value = items.length
  batchResultSuccessCount.value = 0
  batchResultFailedItems.value = []
  try {
    const failed = await executeBatchSave(items)
    batchResultSuccessCount.value = items.length - failed.length
    batchResultFailedItems.value = failed
    if (failed.length === 0) {
      await loadData()
    }
    batchResultVisible.value = true
  } finally {
    batchSaving.value = false
  }
}

const handleBatchDigitReplace = async () => {
  if (!digitReplaceChar.value) { ElMessage.warning('请输入替换字符'); return }
  try {
    await ElMessageBox.confirm(
      `将对当前筛选结果 ${rows.value.length} 条记录，把行首数字序号替换为「${digitReplaceChar.value}」并保存，是否继续？`,
      '批量替换确认',
      { type: 'warning' }
    )
    await runBatchReplace(text => replaceDigitSymbol(text, digitReplaceChar.value))
  } catch (e) { if (e !== 'cancel') throw e }
}

const handleBatchCharReplace = async () => {
  if (!charReplaceFrom.value) { ElMessage.warning('请输入要替换的字符'); return }
  try {
    await ElMessageBox.confirm(
      `将对当前筛选结果 ${rows.value.length} 条记录，把行首「${charReplaceFrom.value}」替换为「${charReplaceTo.value}」并保存，是否继续？`,
      '批量替换确认',
      { type: 'warning' }
    )
    await runBatchReplace(text => replaceLineStartChar(text, charReplaceFrom.value, charReplaceTo.value))
  } catch (e) { if (e !== 'cancel') throw e }
}

// 重试失败项
const retryFailedItems = async () => {
  const items = [...batchResultFailedItems.value]
  batchResultVisible.value = false
  batchSaving.value = true
  try {
    const failed = await executeBatchSave(items)
    batchResultSuccessCount.value += items.length - failed.length
    batchResultFailedItems.value = failed
    if (failed.length === 0) {
      await loadData()
    }
    batchResultVisible.value = true
  } finally {
    batchSaving.value = false
  }
}

// 导出 Excel
const exporting = ref(false)
const handleExport = async () => {
  const competitionId = await ensureCompetitionId()
  if (!competitionId) return
  exporting.value = true
  try {
    const blob = await exportFeedbackExcel(competitionId, {
      groupType: filters.groupType || undefined,
      groupCode: filters.groupCode || undefined,
      projectName: filters.projectName || undefined,
      institutionName: filters.institutionName || undefined,
      published: typeof filters.published === 'boolean' ? filters.published : undefined
    })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '项目意见反馈-书审.xlsx'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
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

// 批量替换 Popover 内部
.batch-replace-panel {
  .batch-replace-title {
    font-size: 12px;
    color: #909399;
    margin-bottom: 10px;
  }
  .batch-replace-section {
    .batch-replace-label {
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 4px;
    }
    .batch-replace-desc {
      font-size: 12px;
      color: #909399;
      margin-bottom: 8px;
      code {
        background: #f4f4f5;
        padding: 0 3px;
        border-radius: 2px;
      }
    }
    .batch-replace-row {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }
  }
}

// 编辑弹窗内单条替换工具栏
.inline-replace-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 10px;
  background: #f9fafb;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 13px;

  .toolbar-title {
    font-weight: 600;
    color: #606266;
    margin-right: 4px;
  }
  .toolbar-group {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .toolbar-label {
    color: #606266;
    white-space: nowrap;
  }
}
</style>
