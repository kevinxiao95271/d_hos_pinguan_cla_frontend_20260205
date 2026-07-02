<template>
  <div class="score-page">
    <el-card class="score-card">
      <template #header>
        <div class="card-header">
          <span>书审专家打分列表</span>
          <div class="filter-inline">
            <el-select v-model="filters.groupType" clearable placeholder="全部组别" size="small" style="width: 110px" @change="loadData">
              <el-option label="基层组" value="BASIC" />
              <el-option label="综合组" value="COMPREHENSIVE" />
              <el-option label="进阶组" value="ADVANCED" />
            </el-select>
            <el-select v-model="filters.reviewerStatus" clearable placeholder="评审状态" size="small" style="width: 110px" @change="loadData">
              <el-option label="待评分" value="PENDING" />
              <el-option label="草稿" value="DRAFT" />
              <el-option label="已评分" value="SCORED" />
              <el-option label="已驳回" value="RETURNED" />
              <el-option label="已回避" value="RECUSED" />
            </el-select>
            <el-input v-model="filters.keyword" clearable placeholder="项目名 / 机构名" size="small" style="width: 160px" @clear="loadData" @keyup.enter="loadData" />
            <el-input v-model="filters.reviewerName" clearable placeholder="评委姓名" size="small" style="width: 120px" @clear="loadData" @keyup.enter="loadData" />
            <el-button type="primary" size="small" @click="loadData">查询</el-button>
            <el-button size="small" @click="resetFilters">重置</el-button>
            <el-button v-if="userStore.isOps || userStore.isCommittee" type="success" plain size="small" :disabled="scores.length === 0" @click="exportExcel">导出 Excel</el-button>
          </div>
        </div>
      </template>

      <!-- 评分列表：顶部 + 底部双向滚动轨 -->
      <div class="dual-scroll-wrapper">
        <div ref="topScrollRef" class="dual-scroll-track dual-scroll-top" @scroll="onTopScroll">
          <div ref="topScrollInnerRef" class="dual-scroll-inner"></div>
        </div>
        <el-table v-top-scrollbar
          ref="tableRef"
          v-loading="loading"
          :data="scores"
          border
          stripe
          style="width: 100%"
          max-height="calc(100vh - 200px)"
        >
          <el-table-column prop="registrationId" label="项目编号" width="80" align="center" />
          <el-table-column label="决赛顺序" width="80" align="center">
            <template #default="{ row }">
              <span v-if="row.finalSessionOrder != null">{{ row.finalSessionOrder }}</span>
              <span v-else style="color:#c0c4cc">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="projectName" label="项目名称" min-width="200" show-overflow-tooltip />
          <el-table-column prop="institutionName" label="医疗机构" min-width="200" show-overflow-tooltip />
          <el-table-column prop="groupCode" label="分组" width="80" align="center" />
          <el-table-column prop="total" label="总分" width="90" align="center">
            <template #default="{ row }">
              <el-tag type="success" size="large">{{ formatScore1(row.total) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="项目均分" width="88" align="center">
            <template #default="{ row }">{{ formatScore1(row.avgTotal) }}</template>
          </el-table-column>
          <el-table-column prop="reviewerName" label="评委姓名" width="100" align="center" />
          <el-table-column label="评委进度" width="100" align="center">
            <template #default="{ row }">
              {{ row.scoredCount != null ? row.scoredCount : '-' }} /
              {{ row.totalReviewers != null ? row.totalReviewers : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="submittedAt" label="提交时间" width="160" align="center">
            <template #default="{ row }">{{ formatDate(row.submittedAt) }}</template>
          </el-table-column>
          <el-table-column prop="institutionLevel" label="机构等级" width="110" align="center" />
          <el-table-column prop="groupType" label="组别" width="90" align="center">
            <template #default="{ row }">{{ getGroupTypeText(row.groupType) }}</template>
          </el-table-column>
          <el-table-column label="评分详情" width="400">
            <template #default="{ row }">
              <div class="score-details">
                <div class="score-item"><span class="label">计划:</span><span class="value">{{ formatScore1(row.plan) }}</span></div>
                <div class="score-item"><span class="label">问题:</span><span class="value">{{ formatScore1(row.problem) }}</span></div>
                <div class="score-item"><span class="label">行动:</span><span class="value">{{ formatScore1(row.action) }}</span></div>
                <div class="score-item"><span class="label">成效:</span><span class="value">{{ formatScore1(row.success) }}</span></div>
                <div class="score-item"><span class="label">回顾:</span><span class="value">{{ formatScore1(row.review) }}</span></div>
                <div class="score-item"><span class="label">运作:</span><span class="value">{{ formatScore1(row.operation) }}</span></div>
                <div class="score-item"><span class="label">展示:</span><span class="value">{{ formatScore1(row.presentation) }}</span></div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ row }">
              <el-button type="danger" size="small" :disabled="row.status !== 'SCORED'" @click="handleReturn(row)">驳回</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 统计信息 -->
      <div v-if="scores.length > 0" class="score-count-bar">共 {{ scores.length }} 条评委评分记录</div>

      <!-- 空状态 -->
      <el-empty v-if="!loading && scores.length === 0" description="暂无评分记录" />
    </el-card>

    <!-- 驳回对话框 -->
    <el-dialog v-model="returnDialogVisible" title="驳回评分" width="500px">
      <el-form :model="returnForm" :rules="returnRules" ref="returnFormRef" label-width="80px">
        <el-form-item label="项目名称"><span>{{ currentScore?.projectName }}</span></el-form-item>
        <el-form-item label="评委"><span>{{ currentScore?.reviewerName }}</span></el-form-item>
        <el-form-item label="总分">
          <el-tag type="success">{{ formatScore1(currentScore?.total) }} 分</el-tag>
        </el-form-item>
        <el-form-item label="驳回原因" prop="reason">
          <el-input v-model="returnForm.reason" type="textarea" :rows="4" placeholder="请输入驳回原因" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="returnDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="returning" @click="confirmReturn">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBookScores, returnScore } from '@/api/review'
import { getCurrentCompetitionId } from '@/utils/competition'
import { flattenScoreListRows } from '@/utils/scoreListFlatten'
import { useUserStore } from '@/stores/user'
import * as XLSX from 'xlsx'
import dayjs from 'dayjs'

const userStore = useUserStore()

const loading = ref(false)
const scores = ref([])

const filters = reactive({
  groupType: '',
  reviewerStatus: '',
  keyword: '',
  reviewerName: ''
})

const returnDialogVisible = ref(false)
const returning = ref(false)
const currentScore = ref(null)
const returnFormRef = ref(null)
const returnForm = reactive({ reason: '' })
const returnRules = {
  reason: [
    { required: true, message: '请输入驳回原因', trigger: 'blur' },
    { min: 5, message: '驳回原因至少5个字符', trigger: 'blur' }
  ]
}

// 双向滚动轨同步
const tableRef = ref(null)
const topScrollRef = ref(null)
const topScrollInnerRef = ref(null)
let tableBodyEl = null
let isSyncingTop = false
let isSyncingTable = false
let scrollResizeObserver = null

const getTableBodyEl = () => tableRef.value?.$el?.querySelector('.el-scrollbar__wrap')

const onTopScroll = () => {
  if (isSyncingTable) return
  isSyncingTop = true
  const el = getTableBodyEl()
  if (el) el.scrollLeft = topScrollRef.value.scrollLeft
  isSyncingTop = false
}

const onTableBodyScroll = () => {
  if (isSyncingTop) return
  isSyncingTable = true
  if (topScrollRef.value) topScrollRef.value.scrollLeft = tableBodyEl.scrollLeft
  isSyncingTable = false
}

const updateTopScrollWidth = () => {
  const el = getTableBodyEl()
  if (el && topScrollInnerRef.value) {
    topScrollInnerRef.value.style.width = el.scrollWidth + 'px'
  }
}

const initDualScroll = () => {
  tableBodyEl = getTableBodyEl()
  if (!tableBodyEl) return
  tableBodyEl.addEventListener('scroll', onTableBodyScroll)
  updateTopScrollWidth()
  scrollResizeObserver = new ResizeObserver(updateTopScrollWidth)
  scrollResizeObserver.observe(tableBodyEl)
}

onBeforeUnmount(() => {
  if (tableBodyEl) tableBodyEl.removeEventListener('scroll', onTableBodyScroll)
  if (scrollResizeObserver) scrollResizeObserver.disconnect()
})

const loadData = async () => {
  const competitionId = await getCurrentCompetitionId()
  if (!competitionId) { ElMessage.warning('请先选择赛事'); return }
  loading.value = true
  try {
    const params = { competitionId }
    if (filters.groupType) params.groupType = filters.groupType
    if (filters.reviewerStatus) params.reviewerStatus = filters.reviewerStatus
    if (filters.keyword && filters.keyword.trim()) params.keyword = filters.keyword.trim()
    if (filters.reviewerName && filters.reviewerName.trim()) params.reviewerName = filters.reviewerName.trim()

    const res = await getBookScores(params)
    if (res.success) {
      scores.value = flattenScoreListRows(res.data || [], 'BOOK')
      nextTick(updateTopScrollWidth)
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载书审得分失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.groupType = ''
  filters.reviewerStatus = ''
  filters.keyword = ''
  filters.reviewerName = ''
  loadData()
}

const handleReturn = (score) => {
  currentScore.value = score
  returnForm.reason = ''
  returnDialogVisible.value = true
}

const confirmReturn = async () => {
  try {
    await returnFormRef.value.validate()
    await ElMessageBox.confirm(
      `确认驳回【${currentScore.value.projectName}】的评分？评分记录将被删除，任务状态将变为"待重评"。`,
      '确认驳回',
      { confirmButtonText: '确认驳回', cancelButtonText: '取消', type: 'warning' }
    )
    const taskId = currentScore.value.reviewTaskId
    if (taskId == null) { ElMessage.error('缺少 reviewTaskId，无法驳回'); return }
    returning.value = true
    const res = await returnScore({ reviewTaskId: taskId, reason: returnForm.reason })
    if (res.success) {
      ElMessage.success('驳回成功')
      returnDialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.message || '驳回失败')
    }
  } catch (error) {
    if (error !== 'cancel') { console.error('驳回失败:', error); ElMessage.error('驳回失败') }
  } finally {
    returning.value = false
  }
}

const getGroupTypeText = (type) => ({ BASIC: '基层组', COMPREHENSIVE: '综合组', ADVANCED: '进阶组' }[type] || type)

function formatScore1(v) {
  if (v == null || v === '') return '-'
  const n = Number(v)
  return Number.isFinite(n) ? n.toFixed(2) : '-'
}

const formatDate = (dateStr) => dateStr ? dayjs(dateStr).format('YYYY-MM-DD HH:mm') : '-'

const exportExcel = () => {
  const rows = scores.value.map(r => ({
    '项目编号': r.registrationId ?? '',
    '项目名称': r.projectName ?? '',
    '医疗机构': r.institutionName ?? '',
    '分组': r.groupCode ?? '',
    '总分': r.total != null ? Number(Number(r.total).toFixed(1)) : '',
    '项目均分': r.avgTotal != null ? Number(Number(r.avgTotal).toFixed(2)) : '',
    '评委姓名': r.reviewerName ?? '',
    '已打分/总评委': `${r.scoredCount ?? '-'}/${r.totalReviewers ?? '-'}`,
    '提交时间': formatDate(r.submittedAt),
    '机构等级': r.institutionLevel ?? '',
    '组别': getGroupTypeText(r.groupType),
    '评委机构': r.reviewerInstitutionName ?? '',
    '评审状态': ({ PENDING: '待评分', DRAFT: '草稿', SCORED: '已评分', RETURNED: '已驳回', RECUSED: '已回避' }[r.status] || r.status || ''),
    '计划': r.plan != null ? Number(Number(r.plan).toFixed(1)) : '',
    '问题': r.problem != null ? Number(Number(r.problem).toFixed(1)) : '',
    '行动': r.action != null ? Number(Number(r.action).toFixed(1)) : '',
    '成效': r.success != null ? Number(Number(r.success).toFixed(1)) : '',
    '回顾': r.review != null ? Number(Number(r.review).toFixed(1)) : '',
    '运作': r.operation != null ? Number(Number(r.operation).toFixed(1)) : '',
    '展示': r.presentation != null ? Number(Number(r.presentation).toFixed(1)) : '',
  }))
  const ws = XLSX.utils.json_to_sheet(rows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '书审专家打分')
  XLSX.writeFile(wb, `书审专家打分_${dayjs().format('YYYYMMDD_HHmm')}.xlsx`)
}

onMounted(() => {
  loadData()
  nextTick(() => { initDualScroll() })
})
</script>

<style scoped lang="scss">

.score-page {
  padding: 20px;

  .score-card {
    :deep(.el-card__header) { padding: 10px 16px; }
    :deep(.el-card__body) { padding: 12px 16px; }
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 15px;
    font-weight: 600;

    .filter-inline {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: normal;
    }
  }

  .score-count-bar {
    margin-top: 8px;
    font-size: 12px;
    color: #909399;
    text-align: right;
  }

  .score-details {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    .score-item {
      display: flex;
      align-items: center;
      font-size: 13px;
      .label { color: #909399; margin-right: 4px; }
      .value { color: #409eff; font-weight: 500; }
    }
  }
}

.dual-scroll-wrapper {
  position: relative;

  :deep(.el-scrollbar__bar.is-vertical),
  :deep(.el-scrollbar__bar.is-vertical:hover) {
    width: 10px !important;
    opacity: 1 !important;
    right: 0;
  }
  :deep(.el-scrollbar__bar.is-vertical .el-scrollbar__thumb) {
    background: #6b7280;
    border-radius: 5px;
    opacity: 1 !important;
    &:hover { background: #374151; }
  }
  :deep(.el-scrollbar__wrap) {
    scrollbar-width: thin;
    scrollbar-color: #6b7280 #e5e7eb;
  }
}

.dual-scroll-track {
  overflow-x: auto;
  overflow-y: hidden;
  width: 100%;
  &::-webkit-scrollbar { height: 8px; }
  &::-webkit-scrollbar-track { background: #f5f5f5; border-radius: 4px; }
  &::-webkit-scrollbar-thumb { background: #c0c4cc; border-radius: 4px;
    &:hover { background: #909399; }
  }
}
.dual-scroll-top { margin-bottom: 2px; }
.dual-scroll-inner { height: 1px; min-width: 100%; }
</style>
