<template>
  <div class="registration-page">
    <!-- 跑马灯 -->
    <stage-progress
      current-stage="BOOK"
      :stages="stagesList"
    />
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>项目分组</span>
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
          <el-select v-model="filters.groupType" placeholder="全部" clearable style="width: 140px">
            <el-option label="基层组" value="BASIC" />
            <el-option label="综合组" value="COMPREHENSIVE" />
            <el-option label="进阶组" value="ADVANCED" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="分组">
          <el-select v-model="filters.groupCode" placeholder="全部" clearable style="width: 120px">
            <el-option
              v-for="code in groupCodes"
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
        
        <el-form-item label="品管工具">
          <el-select v-model="filters.methodLabel" placeholder="全部" clearable style="width: 180px">
            <el-option
              v-for="item in dictionaries.methods"
              :key="item.code"
              :label="item.label"
              :value="item.label"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadRegistrations">
            查询
          </el-button>
          <el-button @click="resetFilters">
            重置
          </el-button>
          <el-button type="success" @click="autoGroup">
            自动分组
          </el-button>
          <el-button type="warning" @click="batchClassify">
            批量分类
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 已选筛选条件展示 -->
      <div v-if="hasActiveFilters" class="active-filters">
        <span class="filter-label">当前筛选：</span>
        <el-tag
          v-if="filters.institutionName"
          closable
          @close="filters.institutionName = ''; loadRegistrations()"
          style="margin-right: 8px"
        >
          医疗机构：{{ filters.institutionName }}
        </el-tag>
        <el-tag
          v-if="filters.groupType"
          closable
          @close="filters.groupType = ''; loadRegistrations()"
          type="success"
          style="margin-right: 8px"
        >
          竞赛组别：{{ getGroupTypeText(filters.groupType) }}
        </el-tag>
        <el-tag
          v-if="filters.groupCode"
          closable
          @close="filters.groupCode = ''; loadRegistrations()"
          type="warning"
          style="margin-right: 8px"
        >
          分组：{{ filters.groupCode }}
        </el-tag>
        <el-tag
          v-if="filters.projectName"
          closable
          @close="filters.projectName = ''; loadRegistrations()"
          style="margin-right: 8px"
        >
          项目名称：{{ filters.projectName }}
        </el-tag>
        <el-tag
          v-if="filters.methodLabel"
          closable
          @close="filters.methodLabel = ''; loadRegistrations()"
          type="info"
          style="margin-right: 8px"
        >
          品管工具：{{ filters.methodLabel }}
        </el-tag>
      </div>
      
      <el-alert
        v-if="registrations.length === 0 && !loading"
        title="提示"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        暂无报名数据。请确保：1) 已创建赛事 2) 有参赛者报名 3) 筛选条件正确
      </el-alert>
      
      <el-table
        v-loading="loading"
        :data="registrations"
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="registrationId" label="项目编号" width="100" />
        <el-table-column prop="projectName" label="项目名称" min-width="180" />
        <el-table-column prop="institutionName" label="医疗机构名称" min-width="160" />
        <el-table-column prop="groupType" label="竞赛组别" width="100">
          <template #default="{ row }">
            {{ getGroupTypeText(row.groupType) }}
          </template>
        </el-table-column>
        <el-table-column prop="groupCode" label="分组" width="80" />
        <el-table-column prop="methodLabel" label="品管工具" min-width="140" />
        <el-table-column prop="applicantName" label="报名人" width="100" />
        <el-table-column prop="submittedAt" label="报名时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.submittedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button type="warning" size="small" @click="changeGroup(row)">
              变更分组
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 变更分组对话框 -->
    <el-dialog v-model="changeGroupDialogVisible" title="变更分组" width="400px">
      <el-alert
        title="提示：竞赛组别由报名时确定，无法更改。只能调整同组别内的分组编号。"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="changeGroupForm" label-width="100px">
        <el-form-item label="竞赛组别">
          <el-tag :type="getGroupTypeTagType(changeGroupForm.groupType)" size="large">
            {{ getGroupTypeText(changeGroupForm.groupType) }}
          </el-tag>
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">
            （报名时确定，不可更改）
          </span>
        </el-form-item>
        
        <el-form-item label="选中项目">
          <span style="color: #606266;">
            共 {{ changeGroupForm.registrationIds.length }} 个项目
          </span>
        </el-form-item>
        
        <el-form-item label="当前分组">
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <el-tag 
              v-for="code in changeGroupForm.currentGroupCode.split(', ')" 
              :key="code" 
              size="large"
            >
              {{ code }}
            </el-tag>
          </div>
          <span 
            v-if="changeGroupForm.currentGroupCode.includes(',')" 
            style="margin-left: 10px; color: #909399; font-size: 12px;"
          >
            （选中项目分布在多个分组）
          </span>
        </el-form-item>
        
        <el-form-item label="统一调整到">
          <el-select 
            v-model="changeGroupForm.groupCode" 
            placeholder="请选择目标分组"
          >
            <el-option
              v-for="code in availableGroupCodes"
              :key="code"
              :label="code"
              :value="code"
            />
          </el-select>
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">
            所有选中项目将调整到此分组
          </span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="changeGroupDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmChangeGroup"
          :disabled="!changeGroupForm.groupCode || changeGroupForm.groupCode === changeGroupForm.currentGroupCode"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      title="报名详情" 
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-loading="detailLoading">
        <el-descriptions v-if="currentDetail && currentDetail.registration" :column="2" border>
          <el-descriptions-item label="项目名称" :span="2">
            {{ currentDetail.registration.projectName }}
          </el-descriptions-item>
          <el-descriptions-item label="竞赛组别">
            {{ getGroupTypeText(currentDetail.registration.groupType) }}
          </el-descriptions-item>
          <el-descriptions-item label="分组">
            {{ currentDetail.registration.groupCode || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="品管工具" :span="2">
            <el-tag v-if="currentDetail.activityInfo?.methodLabel" type="success">
              {{ currentDetail.activityInfo.methodLabel }}
            </el-tag>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="主题类型" :span="2">
            {{ currentDetail.activityInfo?.subjectTypeLabel || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="活动主题" :span="2">
            {{ currentDetail.activityInfo?.theme || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="关键词" :span="2">
            {{ currentDetail.activityInfo?.keywords || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="平均工作年限">
            {{ currentDetail.activityInfo?.avgWorkYears || '-' }} 年
          </el-descriptions-item>
          <el-descriptions-item label="平均年龄">
            {{ currentDetail.activityInfo?.avgAge || '-' }} 岁
          </el-descriptions-item>
          <el-descriptions-item label="报名时间" :span="2">
            {{ formatDate(currentDetail.registration.submittedAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag v-if="currentDetail.registration.status === 'APPROVED'" type="success">已通过</el-tag>
            <el-tag v-else-if="currentDetail.registration.status === 'PENDING'" type="warning">待审核</el-tag>
            <el-tag v-else-if="currentDetail.registration.status === 'REJECTED'" type="danger">已驳回</el-tag>
            <el-tag v-else>{{ currentDetail.registration.status }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">项目参与人员</el-divider>
        <el-table 
          v-if="currentDetail?.members" 
          :data="currentDetail.members.filter(m => m.role === 'PARTICIPANT')" 
          border
          max-height="200"
        >
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="title" label="职称" width="120" />
          <el-table-column prop="department" label="科室" />
        </el-table>
        <el-empty v-else description="暂无参与人员" :image-size="80" />

        <el-divider content-position="left">辅导员</el-divider>
        <el-table 
          v-if="currentDetail?.members" 
          :data="currentDetail.members.filter(m => m.role === 'MENTOR')" 
          border
          max-height="200"
        >
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="title" label="职称" width="120" />
          <el-table-column prop="department" label="科室" />
        </el-table>
        <el-empty v-else description="暂无辅导员" :image-size="80" />
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'
import { filterRegistrations, batchClassifyRegistrations, autoGroupRegistrations } from '@/api/admin'
import { getRegistration } from '@/api/registration'
import { getDictionaryByType } from '@/api/dictionary'
import dayjs from 'dayjs'

const registrations = ref([])
const selectedRegistrations = ref([])
const loading = ref(false)

const dictionaries = reactive({
  methods: [],
  subjectTypes: []
})

// 使用 composable 获取跑马灯数据
const { stagesList } = useCompetitionStages()

const getCurrentCompetitionId = () => {
  const competitionId = localStorage.getItem('currentCompetitionId')
  return competitionId ? parseInt(competitionId) : 21
}

const filters = reactive({
  competitionId: getCurrentCompetitionId(),
  institutionName: '',
  groupType: '',
  groupCode: '',
  projectName: '',
  methodLabel: ''  // 修复：改为 methodLabel（后端期望中文标签）
})

const changeGroupDialogVisible = ref(false)
const changeGroupForm = reactive({
  registrationIds: [],
  groupType: '',
  currentGroupCode: '',
  groupCode: ''
})

const detailDialogVisible = ref(false)
const detailLoading = ref(false)
const currentDetail = ref(null)

// 动态提取可用的 groupCode
const groupCodes = computed(() => {
  const codes = new Set()
  registrations.value.forEach(r => {
    if (r.groupCode) codes.add(r.groupCode)
  })
  return Array.from(codes).sort()
})

// 根据选中的竞赛组别，动态生成可用的分组选项
const availableGroupCodes = computed(() => {
  const groupType = changeGroupForm.groupType
  if (!groupType) return []
  
  if (groupType === 'BASIC') {
    return ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10']
  } else if (groupType === 'COMPREHENSIVE') {
    return ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10']
  } else if (groupType === 'ADVANCED') {
    return ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10']
  }
  return []
})

// 检查是否有激活的筛选条件
const hasActiveFilters = computed(() => {
  return !!(
    filters.institutionName ||
    filters.groupType ||
    filters.groupCode ||
    filters.projectName ||
    filters.methodLabel
  )
})

const getGroupTypeText = (type) => {
  const map = {
    'BASIC': '基层组',
    'COMPREHENSIVE': '综合组',
    'ADVANCED': '进阶组'
  }
  return map[type] || type
}

const getGroupTypeTagType = (type) => {
  const map = {
    'BASIC': 'success',
    'COMPREHENSIVE': 'warning',
    'ADVANCED': 'danger'
  }
  return map[type] || ''
}

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const getMethodLabel = (code) => {
  const method = dictionaries.methods.find(m => m.code === code)
  return method ? method.label : code
}

const loadDictionaries = async () => {
  try {
    const [methodRes, subjectRes] = await Promise.all([
      getDictionaryByType('method'),
      getDictionaryByType('subject_type')
    ])
    
    if (methodRes.success) {
      dictionaries.methods = methodRes.data
    }
    if (subjectRes.success) {
      dictionaries.subjectTypes = subjectRes.data
    }
  } catch (error) {
    console.error('加载字典失败:', error)
  }
}

const loadRegistrations = async () => {
  loading.value = true
  try {
    const res = await filterRegistrations(filters)
    
    if (res.success) {
      registrations.value = res.data || []
      console.log(`✅ 加载到 ${registrations.value.length} 条报名数据`)
    } else {
      ElMessage.error(res.message || '加载报名数据失败')
      registrations.value = []
    }
  } catch (error) {
    console.error('❌ 加载报名数据失败:', error)
    ElMessage.error('加载失败，请检查网络')
    registrations.value = []
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.institutionName = ''
  filters.groupType = ''
  filters.groupCode = ''
  filters.projectName = ''
  filters.methodCode = ''
  loadRegistrations()
}

const handleSelectionChange = (selection) => {
  selectedRegistrations.value = selection
}

const viewDetail = async (row) => {
  detailDialogVisible.value = true
  detailLoading.value = true
  
  try {
    const res = await getRegistration(row.id)
    if (res.success) {
      currentDetail.value = res.data
    } else {
      ElMessage.error('加载详情失败')
    }
  } catch (error) {
    console.error('加载详情失败:', error)
    ElMessage.error('加载详情失败')
  } finally {
    detailLoading.value = false
  }
}

const changeGroup = (row) => {
  changeGroupDialogVisible.value = true
  changeGroupForm.registrationIds = [row.id]
  changeGroupForm.groupType = row.groupType
  changeGroupForm.currentGroupCode = row.groupCode || ''
  changeGroupForm.groupCode = ''
}

const batchClassify = () => {
  if (selectedRegistrations.value.length === 0) {
    ElMessage.warning('请先选择要批量分类的项目')
    return
  }
  
  // 检查所有选中项目的 groupType 是否一致
  const firstGroupType = selectedRegistrations.value[0].groupType
  const allSameGroupType = selectedRegistrations.value.every(r => r.groupType === firstGroupType)
  
  if (!allSameGroupType) {
    ElMessage.error('批量分类只能在同一竞赛组别内进行。请选择同一组别的项目。')
    return
  }
  
  changeGroupDialogVisible.value = true
  changeGroupForm.registrationIds = selectedRegistrations.value.map(r => r.id)
  changeGroupForm.groupType = firstGroupType
  
  // 显示所有选中项目的当前分组
  const currentCodes = [...new Set(selectedRegistrations.value.map(r => r.groupCode || '未分组'))]
  changeGroupForm.currentGroupCode = currentCodes.join(', ')
  changeGroupForm.groupCode = ''
}

const confirmChangeGroup = async () => {
  try {
    const res = await batchClassifyRegistrations({
      registrationIds: changeGroupForm.registrationIds,
      groupCode: changeGroupForm.groupCode
    })
    
    if (res.success) {
      ElMessage.success('分组调整成功')
      changeGroupDialogVisible.value = false
      loadRegistrations()
    } else {
      ElMessage.error(res.message || '分组调整失败')
    }
  } catch (error) {
    console.error('分组调整失败:', error)
    ElMessage.error('分组调整失败')
  }
}

const autoGroup = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要自动分配分组吗？将按每组10人自动分配到A组系列（A1、A2、A3...）',
      '提示',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    const res = await autoGroupRegistrations({
      competitionId: filters.competitionId,
      groupPrefix: 'A',  // 分组前缀
      groupSize: 10      // 每组人数
    })
    
    if (res.success) {
      ElMessage.success('自动分组成功')
      loadRegistrations()
    } else {
      ElMessage.error(res.message || '自动分组失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('自动分组失败:', error)
      ElMessage.error('自动分组失败')
    }
  }
}

onMounted(() => {
  loadDictionaries()
  loadRegistrations()
})
</script>

<style scoped lang="scss">
.registration-page {
  .filter-form {
    margin-bottom: 16px;
  }
  
  .active-filters {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    padding: 12px 16px;
    background-color: #f5f7fa;
    border-radius: 4px;
    margin-bottom: 20px;
    
    .filter-label {
      font-size: 14px;
      color: #606266;
      font-weight: 500;
      margin-right: 12px;
    }
    
    .el-tag {
      margin-bottom: 4px;
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
