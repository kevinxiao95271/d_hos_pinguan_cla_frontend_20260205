<template>
  <div class="interview-group-page">
    <stage-progress current-stage="INTERVIEW" :stages="stagesList" />
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>面谈分组（仅进阶组）</span>
        </div>
      </template>
      
      <!-- 面谈池视图 -->
      <div>
        <el-form :inline="true" :model="filters" class="filter-form">
          <el-form-item label="医疗机构">
            <el-input
              v-model="filters.institutionName"
              placeholder="请输入机构名称"
              clearable
              style="width: 150px"
            />
          </el-form-item>
          
          <el-form-item label="分组">
            <el-select v-model="filters.groupCode" placeholder="全部" clearable style="width: 100px">
              <el-option label="未分组" value="" />
              <el-option
                v-for="code in advancedGroupCodes"
                :key="code"
                :label="code"
                :value="code"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="品管工具">
            <el-select v-model="filters.methodCode" placeholder="全部" clearable style="width: 140px">
              <el-option
                v-for="item in dictionaries.methods"
                :key="item.code"
                :label="item.label"
                :value="item.code"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="项目名称">
            <el-input
              v-model="filters.projectName"
              placeholder="请输入项目名称"
              clearable
              style="width: 150px"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="loadPoolData" size="small">查询</el-button>
            <el-button @click="resetFilters" size="small">重置</el-button>
            <el-button type="success" @click="autoGroupInterview" :disabled="poolData.length === 0" size="small">自动分组</el-button>
            <el-button type="warning" @click="batchGroupInterview" :disabled="selectedItems.length === 0" size="small">批量分组</el-button>
          </el-form-item>
        </el-form>
        
        <el-alert
          v-if="poolData.length === 0 && !loading"
          title="提示"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          暂无进阶组待分组数据
        </el-alert>
        
        <el-table
          v-loading="loading"
          :data="poolData"
          border
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="registrationId" label="项目编号" width="100" />
          <el-table-column prop="projectName" label="项目名称" min-width="180" />
          <el-table-column prop="institutionName" label="医疗机构名称" min-width="160" />
          <el-table-column prop="institutionLevel" label="机构等级" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.institutionLevel" type="success" size="small">
                {{ row.institutionLevel }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="groupCode" label="分组" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.groupCode" type="success">{{ row.groupCode }}</el-tag>
              <el-tag v-else type="info">未分组</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="methodLabel" label="品管工具" min-width="140" />
          <el-table-column prop="applicantName" label="报名人" width="100" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="viewDetail(row)">
                详情
              </el-button>
              <el-button type="warning" size="small" @click="changeInterviewGroup(row)">
                分组
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页器 -->
        <div v-if="showPagination" class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="totalCount"
            :page-sizes="pageSizes"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadPoolData"
            @current-change="loadPoolData"
          />
        </div>
      </div>
    </el-card>
    
    <!-- 分组对话框 -->
    <el-dialog v-model="groupDialogVisible" title="设置分组" width="400px">
      <el-form :model="groupForm" label-width="100px">
        <el-form-item label="选中项目">
          <span style="color: #606266;">
            共 {{ groupForm.registrationIds.length }} 个项目
          </span>
        </el-form-item>
        
        <el-form-item label="当前分组">
          <el-tag v-if="groupForm.currentGroupCode" type="warning">
            {{ groupForm.currentGroupCode }}
          </el-tag>
          <el-tag v-else type="info">未分组</el-tag>
        </el-form-item>
        
        <el-form-item label="目标分组">
          <el-select 
            v-model="groupForm.groupCode" 
            placeholder="请选择分组"
            style="width: 100%"
          >
            <el-option
              v-for="code in advancedGroupCodes"
              :key="code"
              :label="code"
              :value="code"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="groupDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmGroup"
          :disabled="!groupForm.groupCode"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 详情对话框（复用书审阶段的详情展示） -->
    <el-dialog 
      v-model="detailDialogVisible" 
      title="报名详情" 
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-loading="detailLoading">
        <!-- 机构信息 -->
        <el-descriptions v-if="currentDetail?.institution" title="机构信息" :column="2" border>
          <el-descriptions-item label="医疗机构名称">
            {{ currentDetail.institution.name }}
          </el-descriptions-item>
          <el-descriptions-item label="机构等级">
            <el-tag v-if="currentDetail.institution.level" type="success">
              {{ currentDetail.institution.level }}
            </el-tag>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="机构编号">
            {{ currentDetail.institution.code || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="所在地区">
            {{ currentDetail.institution.region || '-' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 项目基本信息 -->
        <el-descriptions v-if="currentDetail?.registration" title="项目信息" :column="2" border style="margin-top: 20px">
          <el-descriptions-item label="项目名称" :span="2">
            {{ currentDetail.registration.projectName }}
          </el-descriptions-item>
          <el-descriptions-item label="竞赛组别">
            {{ getGroupTypeText(currentDetail.registration.groupType) }}
          </el-descriptions-item>
          <el-descriptions-item label="分组">
            <el-tag v-if="currentDetail.registration.groupCode" type="success">
              {{ currentDetail.registration.groupCode }}
            </el-tag>
            <span v-else>未分组</span>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 活动信息 -->
        <el-descriptions v-if="currentDetail?.activityInfo" title="活动信息" :column="2" border style="margin-top: 20px">
          <el-descriptions-item label="活动主题" :span="2">
            {{ currentDetail.activityInfo.theme || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="关键词" :span="2">
            {{ currentDetail.activityInfo.keywords || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="主题类型">
            {{ currentDetail.activityInfo.subjectTypeLabel || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="品管工具">
            <el-tag v-if="currentDetail.activityInfo.methodLabel" type="success">
              {{ currentDetail.activityInfo.methodLabel }}
            </el-tag>
            <span v-else>未填写</span>
          </el-descriptions-item>
          <el-descriptions-item label="改善就医环境">
            {{ getExperienceImproveDisplay(currentDetail.activityInfo) }}
          </el-descriptions-item>
          <el-descriptions-item label="医疗质量相关主题">
            {{ getQualityTopicDisplay(currentDetail.activityInfo) }}
          </el-descriptions-item>
          <el-descriptions-item label="平均工作年限">
            {{ currentDetail.activityInfo.avgWorkYears || '-' }} 年
          </el-descriptions-item>
          <el-descriptions-item label="平均年龄">
            {{ currentDetail.activityInfo.avgAge || '-' }} 岁
          </el-descriptions-item>
          <el-descriptions-item label="是否跨部门">
            <el-tag :type="currentDetail.activityInfo.crossDepartment ? 'success' : 'info'">
              {{ currentDetail.activityInfo.crossDepartment ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否与数字化/AI相关">
            <el-tag :type="currentDetail.activityInfo.relatedToDigitalAi ? 'success' : 'info'">
              {{ currentDetail.activityInfo.relatedToDigitalAi ? '是' : '否' }}
            </el-tag>
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
import { usePagination } from '@/composables/usePagination'
import { filterRegistrations, batchClassifyRegistrations } from '@/api/admin'
import { getRegistration } from '@/api/registration'
import { getDictionaryByType } from '@/api/dictionary'

const { stagesList } = useCompetitionStages()

// 分页
const {
  currentPage,
  pageSize,
  totalCount,
  pageSizes,
  showPagination,
  extractDataList,
  resetPagination,
  getPaginationParams
} = usePagination({ defaultPageSize: 50 })

const loading = ref(false)
const poolData = ref([])
const selectedItems = ref([])

const dictionaries = reactive({
  methods: []
})

const getCurrentCompetitionId = () => {
  const competitionId = localStorage.getItem('currentCompetitionId')
  return competitionId ? parseInt(competitionId) : 21
}

const filters = reactive({
  competitionId: getCurrentCompetitionId(),
  groupType: 'ADVANCED', // 固定为进阶组
  institutionName: '',
  groupCode: null,
  methodCode: '',
  projectName: ''
})

const groupDialogVisible = ref(false)
const groupForm = reactive({
  registrationIds: [],
  currentGroupCode: '',
  groupCode: ''
})

const detailDialogVisible = ref(false)
const detailLoading = ref(false)
const currentDetail = ref(null)

// 进阶组分组代码（C1-C10）
const advancedGroupCodes = computed(() => {
  return Array.from({ length: 10 }, (_, i) => `C${i + 1}`)
})

const getGroupTypeText = (type) => {
  const map = {
    'BASIC': '基层组',
    'COMPREHENSIVE': '综合组',
    'ADVANCED': '进阶组'
  }
  return map[type] || type
}

// 处理"其他"选项 - 改善就医环境
const getExperienceImproveDisplay = (activityInfo) => {
  if (!activityInfo) {
    return '未填写'
  }
  
  // 如果选择了"其他"，显示自定义内容
  if (activityInfo.experienceImproveCode === 'other') {
    return activityInfo.experienceImproveOther || '其他'
  }
  
  // 直接显示Label，不回退到Code
  return activityInfo.experienceImproveLabel || '未填写'
}

// 处理"其他"选项 - 医疗质量相关主题
const getQualityTopicDisplay = (activityInfo) => {
  if (!activityInfo) {
    return '未填写'
  }
  
  // 如果选择了"其他"，显示自定义内容
  if (activityInfo.qualityTopicCode === 'other') {
    return activityInfo.qualityTopicOther || '其他'
  }
  
  // 直接显示Label，不回退到Code
  return activityInfo.qualityTopicLabel || '未填写'
}

// 加载面谈池数据（仅进阶组）
const loadPoolData = async () => {
  loading.value = true
  try {
    const res = await filterRegistrations({
      ...filters,
      ...getPaginationParams()
    })
    
    if (res.success) {
      poolData.value = extractDataList(res.data)
      console.log(`✅ 加载进阶组数据 ${poolData.value.length} 条`)
    } else {
      ElMessage.error(res.message || '加载数据失败')
      poolData.value = []
    }
  } catch (error) {
    console.error('❌ 加载数据失败:', error)
    ElMessage.error('加载失败，请检查网络')
    poolData.value = []
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.institutionName = ''
  filters.groupCode = null
  filters.methodCode = ''
  filters.projectName = ''
  resetPagination()
  loadPoolData()
}

const loadDictionaries = async () => {
  try {
    const methodRes = await getDictionaryByType('method')
    if (methodRes.success) {
      dictionaries.methods = methodRes.data
    }
  } catch (error) {
    console.error('加载字典失败:', error)
  }
}

const handleSelectionChange = (selection) => {
  selectedItems.value = selection
}

const viewDetail = async (row) => {
  detailDialogVisible.value = true
  detailLoading.value = true
  
  try {
    const res = await getRegistration(row.registrationId)
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

const changeInterviewGroup = (row) => {
  groupDialogVisible.value = true
  groupForm.registrationIds = [row.registrationId]
  groupForm.currentGroupCode = row.groupCode || ''
  groupForm.groupCode = ''
}

const batchGroupInterview = () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请先选择要分组的项目')
    return
  }
  
  groupDialogVisible.value = true
  groupForm.registrationIds = selectedItems.value.map(r => r.registrationId)
  
  // 显示所有选中项目的当前分组
  const currentCodes = [...new Set(selectedItems.value.map(r => r.groupCode || '未分组'))]
  groupForm.currentGroupCode = currentCodes.join(', ')
  groupForm.groupCode = ''
}

const confirmGroup = async () => {
  try {
    const res = await batchClassifyRegistrations({
      registrationIds: groupForm.registrationIds,
      groupCode: groupForm.groupCode
    })
    
    if (res.success) {
      ElMessage.success('分组设置成功')
      groupDialogVisible.value = false
      loadPoolData()
    } else {
      ElMessage.error(res.message || '分组设置失败')
    }
  } catch (error) {
    console.error('分组设置失败:', error)
    ElMessage.error('分组设置失败')
  }
}

const autoGroupInterview = async () => {
  try {
    await ElMessageBox.prompt('请输入每组人数', '自动分组', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^[1-9]\d*$/,
      inputErrorMessage: '请输入有效的数字',
      inputValue: '6'
    }).then(async ({ value }) => {
      const groupSize = parseInt(value)
      
      // 前端计算分桶
      const ungroupedItems = poolData.value.filter(item => !item.groupCode)
      if (ungroupedItems.length === 0) {
        ElMessage.warning('没有未分组的项目')
        return
      }
      
      const totalGroups = Math.ceil(ungroupedItems.length / groupSize)
      let successCount = 0
      
      for (let i = 0; i < totalGroups; i++) {
        const start = i * groupSize
        const end = Math.min(start + groupSize, ungroupedItems.length)
        const batch = ungroupedItems.slice(start, end)
        const groupCode = `C${i + 1}`
        
        try {
          const res = await batchClassifyRegistrations({
            registrationIds: batch.map(item => item.id),
            groupCode: groupCode
          })
          
          if (res.success) {
            successCount++
          }
        } catch (error) {
          console.error(`分组 ${groupCode} 失败:`, error)
        }
      }
      
      ElMessage.success(`自动分组完成，成功 ${successCount}/${totalGroups} 组`)
      loadPoolData()
    })
  } catch (error) {
    if (error !== 'cancel') {
      console.error('自动分组失败:', error)
    }
  }
}

onMounted(() => {
  loadDictionaries()
  loadPoolData()
})
</script>

<style scoped lang="scss">
.interview-group-page {
  .filter-form {
    margin-bottom: 16px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
