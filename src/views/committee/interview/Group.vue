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
        
        <!-- 顶部横向滚动条 -->
        <div class="top-scrollbar-wrapper" ref="topScrollbar" @scroll="syncScroll('top')">
          <div class="top-scrollbar-content"></div>
        </div>
        
        <div class="table-container" ref="tableContainer" @scroll="syncScroll('table')">
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
          <el-table-column label="材料" width="120">
            <template #default="{ row }">
              <div v-if="row.materials && row.materials.length > 0">
                <el-tag type="success" size="small">{{ row.materials.length }}个文件</el-tag>
                <el-button 
                  type="primary" 
                  size="small" 
                  link
                  @click="viewMaterials(row)"
                  style="margin-left: 5px;"
                >
                  查看
                </el-button>
              </div>
              <el-tag v-else type="info" size="small">无材料</el-tag>
            </template>
          </el-table-column>
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
        </div>

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
          <el-descriptions-item label="项目编号">
            {{ currentDetail.registration.registrationId || currentDetail.registration.id || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="竞赛组别">
            {{ getGroupTypeText(currentDetail.registration.groupType) }}
          </el-descriptions-item>
          <el-descriptions-item label="项目名称" :span="2">
            {{ currentDetail.registration.projectName }}
          </el-descriptions-item>
          <el-descriptions-item label="分组">
            <el-tag v-if="currentDetail.registration.groupCode" type="success">
              {{ currentDetail.registration.groupCode }}
            </el-tag>
            <span v-else>未分组</span>
          </el-descriptions-item>
          <el-descriptions-item label="报名时间">
            {{ formatDate(currentDetail.registration.submittedAt) }}
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
        
        <!-- 项目摘要 -->
        <el-card v-if="currentDetail?.projectSummary" class="summary-card" style="margin-top: 20px">
          <template #header>
            <h3>项目摘要</h3>
          </template>
          <div class="summary-content">
            <div class="summary-item" v-if="currentDetail.projectSummary.theme">
              <h4>主题</h4>
              <p>{{ currentDetail.projectSummary.theme }}</p>
            </div>
            <div class="summary-item" v-if="currentDetail.projectSummary.plan">
              <h4>计划</h4>
              <p>{{ currentDetail.projectSummary.plan }}</p>
            </div>
            <div class="summary-item" v-if="currentDetail.projectSummary.problem">
              <h4>问题结构与对策措施探讨</h4>
              <p>{{ currentDetail.projectSummary.problem }}</p>
            </div>
            <div class="summary-item" v-if="currentDetail.projectSummary.action">
              <h4>对策行动过程</h4>
              <p>{{ currentDetail.projectSummary.action }}</p>
            </div>
            <div class="summary-item" v-if="currentDetail.projectSummary.success">
              <h4>成果表现</h4>
              <p>{{ currentDetail.projectSummary.success }}</p>
            </div>
            <div class="summary-item" v-if="currentDetail.projectSummary.discussion">
              <h4>讨论总结</h4>
              <p>{{ currentDetail.projectSummary.discussion }}</p>
            </div>
            <div class="summary-item" v-if="currentDetail.projectSummary.operation">
              <h4>运作</h4>
              <p>{{ currentDetail.projectSummary.operation }}</p>
            </div>
            <div class="summary-item" v-if="currentDetail.projectSummary.presentation">
              <h4>展示</h4>
              <p>{{ currentDetail.projectSummary.presentation }}</p>
            </div>
          </div>
        </el-card>

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
        
        <!-- 材料文件 -->
        <div v-if="currentDetail?.materials && currentDetail.materials.length > 0">
          <el-divider content-position="left">材料文件</el-divider>
          <el-table :data="currentDetail.materials" border>
            <el-table-column label="类型" width="160">
              <template #default="{ row }">
                {{ getMaterialTypeLabel(row.type) }}
              </template>
            </el-table-column>
            <el-table-column prop="fileName" label="文件名" />
            <el-table-column prop="uploadedAt" label="上传时间" width="160">
              <template #default="{ row }">
                {{ row.uploadedAt ? row.uploadedAt.replace('T',' ').substring(0,16) : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="downloadFile(row)">
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'
import { usePagination } from '@/composables/usePagination'
import { filterRegistrations, batchClassifyRegistrations } from '@/api/admin'
import { getRegistration } from '@/api/registration'
import { getDictionaryByType } from '@/api/dictionary'
import { downloadMaterial } from '@/api/material'
import { getCurrentCompetitionId, getCurrentCompetitionIdSync } from '@/utils/competition'
import dayjs from 'dayjs'

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

// 顶部滚动条相关
const topScrollbar = ref(null)
const tableContainer = ref(null)
let isScrolling = false

const dictionaries = reactive({
  methods: []
})

const filters = reactive({
  competitionId: getCurrentCompetitionIdSync(),
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

// 格式化日期时间
const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
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
    // 兼容不同的字段名：registrationId 或 id
    const id = row.registrationId || row.id
    
    if (!id) {
      console.error('❌ 缺少项目ID:', row)
      ElMessage.error('缺少项目ID，无法查看详情')
      detailDialogVisible.value = false
      return
    }
    
    console.log('⏳ 正在加载详情，ID:', id)
    const res = await getRegistration(id)
    
    if (res.success) {
      currentDetail.value = res.data
      console.log('✅ 详情加载成功:', res.data)
    } else {
      console.error('❌ 加载详情失败:', res.message)
      ElMessage.error(res.message || '加载详情失败')
    }
  } catch (error) {
    console.error('❌ 加载详情异常:', error)
    ElMessage.error('加载详情失败: ' + (error.message || '未知错误'))
  } finally {
    detailLoading.value = false
  }
}

// 查看材料（列表页）
const viewMaterials = async (row) => {
  detailDialogVisible.value = true
  detailLoading.value = true
  
  try {
    const id = row.registrationId || row.id
    if (!id) {
      console.error('❌ 缺少项目ID:', row)
      ElMessage.error('缺少项目ID')
      detailDialogVisible.value = false
      return
    }
    
    const res = await getRegistration(id)
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

const getMaterialTypeLabel = (type) => {
  const map = {
    'REGISTRATION_FORM_DOC': '报名表 Word',
    'REGISTRATION_FORM_PDF': '报名表 PDF',
    'REGISTRATION_FORM': '报名表',
    'REPORT': '成果报告书',
    'EVIDENCE': '佐证材料',
    'payment_proof': '缴费凭证'
  }
  return map[type] || type
}

// 下载材料文件
const downloadFile = async (material) => {
  try {
    const blob = await downloadMaterial(material.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = material.fileName || '材料文件'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载文件失败:', error)
    ElMessage.error('下载失败，请检查权限或稍后重试')
  }
}

const changeInterviewGroup = (row) => {
  // 兼容不同的字段名：registrationId 或 id
  const id = row.registrationId || row.id
  
  if (!id) {
    console.error('❌ 缺少项目ID:', row)
    ElMessage.error('缺少项目ID，无法设置分组')
    return
  }
  
  groupDialogVisible.value = true
  groupForm.registrationIds = [id]
  groupForm.currentGroupCode = row.groupCode || ''
  groupForm.groupCode = ''
  console.log('📝 设置分组，项目ID:', id)
}

const batchGroupInterview = () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请先选择要分组的项目')
    return
  }
  
  // 兼容不同的字段名：registrationId 或 id
  const registrationIds = selectedItems.value.map(r => r.registrationId || r.id).filter(id => id)
  
  if (registrationIds.length === 0) {
    console.error('❌ 所有选中项目都缺少ID:', selectedItems.value)
    ElMessage.error('选中项目缺少ID，无法批量分组')
    return
  }
  
  groupDialogVisible.value = true
  groupForm.registrationIds = registrationIds
  
  // 显示所有选中项目的当前分组
  const currentCodes = [...new Set(selectedItems.value.map(r => r.groupCode || '未分组'))]
  groupForm.currentGroupCode = currentCodes.join(', ')
  groupForm.groupCode = ''
  console.log('📝 批量设置分组，项目数量:', registrationIds.length)
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
      inputValue: '25'
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
        
        // 兼容不同的字段名：id 或 registrationId
        const batchIds = batch.map(item => item.id || item.registrationId).filter(id => id)
        
        if (batchIds.length === 0) {
          console.error(`❌ 分组 ${groupCode} 的项目缺少ID:`, batch)
          continue
        }
        
        try {
          const res = await batchClassifyRegistrations({
            registrationIds: batchIds,
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

// 同步滚动函数
const syncScroll = (source) => {
  if (isScrolling) return
  isScrolling = true
  
  console.log('滚动事件触发:', source, '滚动位置:', source === 'top' ? topScrollbar.value?.scrollLeft : tableContainer.value?.scrollLeft)
  
  if (source === 'top' && topScrollbar.value && tableContainer.value) {
    const targetScroll = topScrollbar.value.scrollLeft
    const tableBody = tableContainer.value.querySelector('.el-table__body-wrapper')
    if (tableBody) {
      tableBody.scrollLeft = targetScroll
      console.log('同步到表格:', targetScroll)
    }
  } else if (source === 'table' && topScrollbar.value && tableContainer.value) {
    const tableBody = tableContainer.value.querySelector('.el-table__body-wrapper')
    if (tableBody) {
      topScrollbar.value.scrollLeft = tableBody.scrollLeft
      console.log('同步到顶部:', tableBody.scrollLeft)
    }
  }
  
  setTimeout(() => {
    isScrolling = false
  }, 10)
}

// 更新顶部滚动条宽度
const updateTopScrollbarWidth = () => {
  console.log('updateTopScrollbarWidth 被调用')
  if (topScrollbar.value && tableContainer.value) {
    const tableBody = tableContainer.value.querySelector('.el-table__body-wrapper')
    console.log('找到的元素:', tableBody)
    if (tableBody) {
      const scrollContent = topScrollbar.value.querySelector('.top-scrollbar-content')
      if (scrollContent) {
        const tableWidth = tableBody.scrollWidth
        scrollContent.style.width = `${tableWidth}px`
        console.log('✅ 更新顶部滚动条宽度:', tableWidth, 'px')
      }
    }
  } else {
    console.log('❌ 找不到 ref 元素:', { topScrollbar: topScrollbar.value, tableContainer: tableContainer.value })
  }
}

onMounted(async () => {
  // 加载当前赛事ID
  const competitionId = await getCurrentCompetitionId()
  if (competitionId) {
    filters.competitionId = competitionId
  }
  
  loadDictionaries()
  loadPoolData()
  
  // 初始化顶部滚动条 - 延迟确保表格渲染完成
  setTimeout(() => {
    updateTopScrollbarWidth()
    
    // 给表格内部的滚动容器添加滚动监听
    if (tableContainer.value) {
      const tableBody = tableContainer.value.querySelector('.el-table__body-wrapper')
      if (tableBody) {
        tableBody.addEventListener('scroll', () => {
          if (!isScrolling) {
            syncScroll('table')
          }
        })
        console.log('✅ 表格滚动监听已添加')
      }
    }
  }, 1000)
  
  // 监听窗口大小变化
  window.addEventListener('resize', updateTopScrollbarWidth)
})

// 监听数据变化，更新顶部滚动条
watch(poolData, () => {
  setTimeout(() => {
    updateTopScrollbarWidth()
  }, 300)
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
  
  // 顶部横向滚动条
  .top-scrollbar-wrapper {
    width: 100%;
    height: 20px;
    overflow-x: scroll !important; // 强制显示横向滚动条
    overflow-y: hidden;
    margin-bottom: 5px;
    background: #fafafa;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    
    &::-webkit-scrollbar {
      width: 16px;
      height: 16px;
    }
    
    &::-webkit-scrollbar-track {
      background: #f5f7fa;
      border-radius: 8px;
      border: 1px solid #dcdfe6;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #409eff;
      border-radius: 8px;
      border: 2px solid #f5f7fa;
      
      &:hover {
        background: #337ecc;
      }
    }
    
    .top-scrollbar-content {
      height: 1px;
      width: 100%; // 宽度会通过JS动态设置
    }
  }
  
  .table-container {
    width: 100%;
    max-height: 600px;
    overflow-x: auto;
    overflow-y: auto;
    
    // 自定义滚动条样式 - 更宽更明显
    &::-webkit-scrollbar {
      width: 16px;
      height: 16px;
    }
    
    &::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 8px;
      border: 1px solid #dcdfe6;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #409eff;
      border-radius: 8px;
      border: 2px solid #f1f1f1;
      
      &:hover {
        background: #337ecc;
      }
    }
    
    // 滚动条角落
    &::-webkit-scrollbar-corner {
      background: #f1f1f1;
    }
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
  
  .summary-card {
    .summary-content {
      padding: 10px;
      
      .summary-item {
        margin-bottom: 20px;
        
        h4 {
          color: #409EFF;
          margin-bottom: 10px;
          font-size: 16px;
        }
        
        p {
          white-space: pre-wrap;
          word-break: break-word;
          line-height: 1.8;
          color: #606266;
        }
      }
    }
  }
}
</style>
