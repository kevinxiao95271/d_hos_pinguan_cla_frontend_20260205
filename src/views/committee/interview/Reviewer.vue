<template>
  <div class="reviewer-assignment-page">
    <!-- 阶段进度 -->
    <StageProgress :stages="stagesList" current-stage="INTERVIEW" simple />

    <div class="page-header">
      <h2>面谈评委分配</h2>
      <div class="header-actions">
        <el-button type="success" @click="showAssignedTasksDialog">
          <el-icon><List /></el-icon>
          查看已分配任务
        </el-button>
        <el-button type="primary" @click="showAutoAssignDialog">
          <el-icon><MagicStick /></el-icon>
          自动分配
        </el-button>
      </div>
    </div>

    <el-alert type="warning" :closable="false" style="margin-bottom: 20px;">
      <div style="font-size: 13px;">
        📌 面谈阶段仅对 <el-tag type="danger" size="small">进阶组</el-tag> 项目分配评委
      </div>
    </el-alert>

    <div class="content-wrapper">
      <!-- 左侧：进阶组报名列表 -->
      <el-card class="left-panel" shadow="hover">
        <template #header>
          <div class="panel-header">
            <span style="font-weight: 600;">📋 进阶组报名列表</span>
            <el-tag type="danger">共 {{ registrations.length }} 项</el-tag>
          </div>
        </template>

        <!-- 筛选 -->
        <el-form :inline="true" size="small" style="margin-bottom: 15px;">
          <el-form-item label="分组">
            <el-select v-model="registrationFilter.groupCode" placeholder="全部" clearable style="width: 120px">
              <el-option label="未分组" value="" />
              <el-option
                v-for="code in advancedGroupCodes"
                :key="code"
                :label="code"
                :value="code"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="项目名称">
            <el-input v-model="registrationFilter.projectName" placeholder="输入项目名称" clearable style="width: 180px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadRegistrations">查询</el-button>
            <el-button @click="resetRegistrationFilter">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 报名表格 -->
        <el-table
          :data="registrations"
          v-loading="loadingRegistrations"
          height="600"
          @selection-change="handleRegistrationSelectionChange"
          size="small"
          border
        >
          <el-table-column type="selection" width="45" />
          <el-table-column prop="registrationId" label="编号" width="80" />
          <el-table-column prop="projectName" label="项目名称" show-overflow-tooltip min-width="150" />
          <el-table-column prop="institutionName" label="机构" show-overflow-tooltip width="180" />
          <el-table-column prop="institutionLevel" label="机构等级" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.institutionLevel" type="success" size="small">
                {{ row.institutionLevel }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="groupCode" label="分组" width="90">
            <template #default="{ row }">
              <el-tag v-if="row.groupCode" type="success" size="small">{{ row.groupCode }}</el-tag>
              <el-tag v-else type="info" size="small">未分组</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="methodLabel" label="品管工具" show-overflow-tooltip width="120" />
        </el-table>

        <!-- 报名列表分页器 -->
        <div v-if="regShowPagination" class="pagination-container">
          <el-pagination
            v-model:current-page="regCurrentPage"
            v-model:page-size="regPageSize"
            :total="regTotalCount"
            :page-sizes="regPageSizes"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadRegistrations"
            @current-change="loadRegistrations"
          />
        </div>
      </el-card>

      <!-- 右侧：评委列表 -->
      <el-card class="right-panel" shadow="hover">
        <template #header>
          <div class="panel-header">
            <span style="font-weight: 600;">👨‍⚖️ 评委列表</span>
            <el-tag type="success">共 {{ reviewers.length }} 位</el-tag>
          </div>
        </template>

        <!-- 评委操作 -->
        <div style="margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
          <el-button type="primary" size="small" @click="handleManualAssign" :disabled="selectedRegistrations.length === 0 || selectedReviewers.length === 0">
            <el-icon><User /></el-icon>
            分配评委 ({{ selectedRegistrations.length }} 项 × {{ selectedReviewers.length }} 位)
          </el-button>
          <el-button size="small" @click="loadReviewers">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <el-alert
          v-if="selectedRegistrations.length > 0"
          :title="`已选 ${selectedRegistrations.length} 个报名项目`"
          type="info"
          :closable="false"
          style="margin-bottom: 15px;"
        />

        <!-- 评委表格 -->
        <el-table
          :data="reviewers"
          v-loading="loadingReviewers"
          height="580"
          @selection-change="handleReviewerSelectionChange"
          :row-class-name="getReviewerRowClass"
          size="small"
          border
        >
          <el-table-column type="selection" width="45" :selectable="isReviewerSelectable" />
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column prop="title" label="职称" width="100" />
          <el-table-column prop="institutionName" label="机构" show-overflow-tooltip min-width="120" />
          <el-table-column prop="institutionLevel" label="机构等级" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.institutionLevel" type="success" size="small">
                {{ row.institutionLevel }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag v-if="isSameInstitution(row)" type="danger" size="small">同机构</el-tag>
              <el-tag v-else type="success" size="small">可分配</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="背景" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.expertBackground === 'MANAGEMENT'" size="small">管理</el-tag>
              <el-tag v-else-if="row.expertBackground === 'MEDICAL'" type="success" size="small">医疗</el-tag>
              <el-tag v-else-if="row.expertBackground === 'NURSING'" type="warning" size="small">护理</el-tag>
              <el-tag v-else-if="row.expertBackground" size="small">其他</el-tag>
              <el-tag v-else type="info" size="small">未设置</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="负荷" width="70">
            <template #default="{ row }">
              <el-tag :type="getLoadTagType(row.currentLoad)" size="small">
                {{ row.currentLoad ?? 0 }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 自动分配对话框 -->
    <el-dialog v-model="autoAssignDialogVisible" title="自动分配面谈评委" width="500px">
      <el-form :model="autoAssignForm" label-width="140px">
        <el-form-item label="每个项目评委数">
          <el-input-number 
            v-model="autoAssignForm.reviewersPerRegistration" 
            :min="1" 
            :max="5"
            style="width: 100%"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            建议每个项目分配 2-3 位评委
          </div>
        </el-form-item>
        <el-form-item label="自动分配说明">
          <el-alert type="info" :closable="false">
            <div style="font-size: 13px; line-height: 1.6;">
              系统将自动为所有进阶组报名分配评委，并满足：<br>
              • 同机构回避<br>
              • 评审负荷均衡<br>
              • 避免重复评审<br>
              • 背景科学搭配
            </div>
          </el-alert>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="autoAssignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAutoAssign" :loading="autoAssigning">
          确认分配
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看已分配任务对话框 -->
    <el-dialog 
      v-model="assignedTasksDialogVisible" 
      title="面谈阶段 - 已分配任务" 
      width="1200px"
      :close-on-click-modal="false"
    >
      <div v-loading="loadingAssignedTasks">
        <el-alert 
          v-if="allAssignedTasks.length === 0" 
          type="info" 
          :closable="false"
          style="margin-bottom: 15px"
        >
          暂无已分配的评审任务
        </el-alert>

        <el-table 
          v-else
          :data="allAssignedTasks" 
          border 
          stripe
          max-height="500"
          style="width: 100%"
        >
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column prop="projectName" label="项目名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="institutionName" label="医疗机构" width="160" show-overflow-tooltip />
          <el-table-column prop="groupType" label="组别" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.groupType === 'BASIC'" type="success" size="small">基层组</el-tag>
              <el-tag v-else-if="row.groupType === 'COMPREHENSIVE'" type="primary" size="small">综合组</el-tag>
              <el-tag v-else-if="row.groupType === 'ADVANCED'" type="warning" size="small">进阶组</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="groupCode" label="分组" width="80" align="center" />
          <el-table-column prop="reviewerName" label="评委姓名" width="100" />
          <el-table-column prop="reviewerTitle" label="职称" width="120" show-overflow-tooltip />
          <el-table-column prop="reviewerInstitutionName" label="评委机构" width="160" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'PENDING'" type="info" size="small">待评审</el-tag>
              <el-tag v-else-if="row.status === 'CONFIRMED'" type="primary" size="small">已确认</el-tag>
              <el-tag v-else-if="row.status === 'SCORED'" type="success" size="small">已评分</el-tag>
              <el-tag v-else type="warning" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 15px; text-align: right; color: #606266;">
          共 {{ allAssignedTasks.length }} 条任务记录
        </div>
      </div>
      <template #footer>
        <el-button @click="assignedTasksDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick, User, Refresh, List } from '@element-plus/icons-vue'
import { filterRegistrations, getReviewers, createReviewTask, autoAssignReviewers, getAdminReviewTasks } from '@/api/admin'
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'
import { usePagination } from '@/composables/usePagination'
import { getCurrentCompetitionId, getCurrentCompetitionIdSync } from '@/utils/competition'

const { stagesList } = useCompetitionStages()

const competitionId = ref(getCurrentCompetitionIdSync())

// 报名列表分页
const {
  currentPage: regCurrentPage,
  pageSize: regPageSize,
  totalCount: regTotalCount,
  pageSizes: regPageSizes,
  showPagination: regShowPagination,
  extractDataList: regExtractDataList,
  resetPagination: regResetPagination,
  getPaginationParams: regGetPaginationParams
} = usePagination({ defaultPageSize: 50 })

// 报名列表（仅进阶组）
const registrations = ref([])
const loadingRegistrations = ref(false)
const selectedRegistrations = ref([])
const registrationFilter = ref({
  competitionId: competitionId.value,
  groupType: 'ADVANCED', // 固定为进阶组
  groupCode: '',
  projectName: ''
})

// 评委列表
const reviewers = ref([])
const loadingReviewers = ref(false)
const selectedReviewers = ref([])

// 自动分配
const autoAssignDialogVisible = ref(false)
const autoAssigning = ref(false)
const autoAssignForm = ref({
  reviewersPerRegistration: 2
})

// 查看已分配任务
const assignedTasksDialogVisible = ref(false)
const loadingAssignedTasks = ref(false)
const allAssignedTasks = ref([])

// 进阶组分组代码（C1-C10）
const advancedGroupCodes = computed(() => {
  return Array.from({ length: 10 }, (_, i) => `C${i + 1}`)
})

// 加载报名列表
const loadRegistrations = async () => {
  loadingRegistrations.value = true
  try {
    const res = await filterRegistrations({
      ...registrationFilter.value,
      ...regGetPaginationParams()
    })
    if (res.success) {
      registrations.value = regExtractDataList(res.data)
      console.log(`✅ 加载进阶组报名列表成功：${registrations.value.length} 条`)
    } else {
      ElMessage.error(res.message || '加载报名列表失败')
      registrations.value = []
    }
  } catch (error) {
    console.error('❌ 加载报名列表失败:', error)
    ElMessage.error('加载失败，请检查网络')
    registrations.value = []
  } finally {
    loadingRegistrations.value = false
  }
}

// 加载评委列表
const loadReviewers = async () => {
  loadingReviewers.value = true
  try {
    const res = await getReviewers({
      competitionId: competitionId.value
    })
    if (res.success) {
      // 直接使用返回的数组，不使用分页
      reviewers.value = Array.isArray(res.data) ? res.data : []
      console.log(`✅ 加载评委列表成功：${reviewers.value.length} 位`)
    } else {
      ElMessage.error(res.message || '加载评委列表失败')
      reviewers.value = []
    }
  } catch (error) {
    console.error('❌ 加载评委列表失败:', error)
    ElMessage.error('加载失败，请检查网络')
    reviewers.value = []
  } finally {
    loadingReviewers.value = false
  }
}

// 重置筛选
const resetRegistrationFilter = () => {
  regResetPagination()
  registrationFilter.value = {
    competitionId: competitionId.value,
    groupType: 'ADVANCED',
    groupCode: '',
    projectName: ''
  }
  loadRegistrations()
}

// 处理评委列表每页数目变化
const handleReviewerPageSizeChange = () => {
  // 改变每页数目时，重置到第一页
// 选中报名
const handleRegistrationSelectionChange = (selection) => {
  selectedRegistrations.value = selection
  console.log('✅ 选中报名:', selection.length, '项')
}

// 选中评委
const handleReviewerSelectionChange = (selection) => {
  selectedReviewers.value = selection
  console.log('✅ 选中评委:', selection)
}

// 判断评委是否与选中的报名项目同机构
const isSameInstitution = (reviewer) => {
  if (selectedRegistrations.value.length === 0) return false
  
  // 使用 institutionName 比较（报名列表API不返回institutionId）
  return selectedRegistrations.value.some(
    registration => registration.institutionName === reviewer.institutionName
  )
}

// 评委是否可选
const isReviewerSelectable = (row) => {
  if (selectedRegistrations.value.length === 0) return true
  return !isSameInstitution(row)
}

// 评委行样式
const getReviewerRowClass = ({ row }) => {
  if (isSameInstitution(row)) {
    return 'disabled-row'
  }
  return ''
}

// 手动分配
const handleManualAssign = async () => {
  if (selectedRegistrations.value.length === 0) {
    ElMessage.warning('请先选择至少一个报名项目')
    return
  }
  if (selectedReviewers.value.length === 0) {
    ElMessage.warning('请至少选择一位评委')
    return
  }

  // 检查是否有同机构冲突
  const conflicts = []
  
  selectedRegistrations.value.forEach(registration => {
    selectedReviewers.value.forEach(reviewer => {
      // 使用 institutionName 比较（报名列表API不返回institutionId）
      if (registration.institutionName === reviewer.institutionName) {
        conflicts.push({
          project: registration.projectName,
          reviewer: reviewer.name,
          institution: registration.institutionName
        })
      }
    })
  })

  // 如果有任何冲突，直接阻止并提示
  if (conflicts.length > 0) {
    const conflictMessages = conflicts.slice(0, 10).map(c => 
      `• ${c.project} ← ${c.reviewer} (${c.institution})`
    ).join('\n')
    
    ElMessageBox.alert(
      `检测到同机构回避冲突，无法分配：\n\n${conflictMessages}${conflicts.length > 10 ? `\n... 还有 ${conflicts.length - 10} 个冲突` : ''}\n\n请重新选择其他医院的评委。`,
      '同机构回避',
      {
        confirmButtonText: '知道了',
        type: 'warning'
      }
    )
    return
  }

  const totalTasks = selectedRegistrations.value.length * selectedReviewers.value.length

  try {
    await ElMessageBox.confirm(
      `确认为 ${selectedRegistrations.value.length} 个项目分配 ${selectedReviewers.value.length} 位评委？\n（共 ${totalTasks} 个评审任务）`,
      '确认分配',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    // 生成所有任务
    const tasks = []
    selectedRegistrations.value.forEach(registration => {
      selectedReviewers.value.forEach(reviewer => {
        tasks.push({
          registrationId: registration.registrationId,
          reviewerId: reviewer.id,
          stage: 'INTERVIEW',
          projectName: registration.projectName,
          reviewerName: reviewer.name
        })
      })
    })

    let successCount = 0
    let failedList = []

    // 逐个提交任务
    for (const task of tasks) {
      try {
        const res = await createReviewTask({
          registrationId: task.registrationId,
          reviewerId: task.reviewerId,
          stage: task.stage
        })
        if (res.success) {
          successCount++
        } else {
          failedList.push(`${task.projectName} → ${task.reviewerName}: ${res.message}`)
        }
      } catch (error) {
        failedList.push(`${task.projectName} → ${task.reviewerName}: ${error.message || '网络错误'}`)
      }
    }

    if (successCount > 0) {
      ElMessage.success(`成功分配 ${successCount} 个评审任务`)
      loadReviewers() // 刷新评委负荷
    }

    if (failedList.length > 0) {
      ElMessageBox.alert(
        failedList.slice(0, 10).join('\n') + (failedList.length > 10 ? `\n... 还有 ${failedList.length - 10} 条错误` : ''),
        '部分分配失败',
        {
          confirmButtonText: '确定',
          type: 'warning'
        }
      )
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('❌ 手动分配失败:', error)
      ElMessage.error('分配失败')
    }
  }
}

// 显示自动分配对话框
const showAutoAssignDialog = () => {
  autoAssignDialogVisible.value = true
}

// 自动分配
const handleAutoAssign = async () => {
  autoAssigning.value = true
  try {
    const res = await autoAssignReviewers({
      competitionId: competitionId.value,
      stage: 'INTERVIEW',
      reviewersPerRegistration: autoAssignForm.value.reviewersPerRegistration
    })

    if (res.success) {
      ElMessage.success('自动分配成功')
      autoAssignDialogVisible.value = false
      loadReviewers() // 刷新评委负荷
      loadRegistrations() // 刷新报名列表
    } else {
      ElMessage.error(res.message || '自动分配失败')
    }
  } catch (error) {
    console.error('❌ 自动分配失败:', error)
    ElMessage.error('自动分配失败，请检查网络')
  } finally {
    autoAssigning.value = false
  }
}

// 显示已分配任务对话框
const showAssignedTasksDialog = async () => {
  assignedTasksDialogVisible.value = true
  await loadAllAssignedTasks()
}

// 加载所有已分配的任务
const loadAllAssignedTasks = async () => {
  loadingAssignedTasks.value = true
  try {
    const res = await getAdminReviewTasks({
      competitionId: competitionId.value,
      stage: 'INTERVIEW'
    })
    
    if (res.success) {
      allAssignedTasks.value = res.data || []
      console.log('✅ 加载所有已分配任务:', allAssignedTasks.value.length, '条')
    } else {
      ElMessage.error(res.message || '加载失败')
      allAssignedTasks.value = []
    }
  } catch (error) {
    console.error('❌ 加载已分配任务失败:', error)
    ElMessage.error('加载失败，请检查网络')
    allAssignedTasks.value = []
  } finally {
    loadingAssignedTasks.value = false
  }
}

// 负荷标签类型
const getLoadTagType = (load) => {
  if (!load || load === 0) return 'info'
  if (load < 5) return 'success'
  if (load < 10) return 'warning'
  return 'danger'
}

onMounted(async () => {
  // 加载当前赛事ID
  const currentCompetitionId = await getCurrentCompetitionId()
  if (currentCompetitionId) {
    competitionId.value = currentCompetitionId
  }
  
  loadRegistrations()
  loadReviewers()
})
</script>

<style scoped>
.reviewer-assignment-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.left-panel,
.right-panel {
  height: 750px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-card__body) {
  padding: 15px;
  height: calc(100% - 60px);
  overflow: auto;
}

:deep(.disabled-row) {
  background-color: #f5f5f5;
  opacity: 0.6;
  cursor: not-allowed;
}

:deep(.disabled-row:hover > td) {
  background-color: #f5f5f5 !important;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
