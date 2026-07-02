<template>
  <div class="registration-page">
    <!-- 跑马灯 -->
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
          <el-select v-model="filters.methodCode" placeholder="全部" clearable style="width: 180px">
            <el-option
              v-for="item in dictionaries.methods"
              :key="item.code"
              :label="item.label"
              :value="item.code"
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
          v-if="filters.methodCode"
          closable
          @close="filters.methodCode = ''; loadRegistrations()"
          type="info"
          style="margin-right: 8px"
        >
          品管工具：{{ getMethodLabel(filters.methodCode) }}
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
      
      <!-- 顶部横向滚动条 -->
      <div class="top-scrollbar-wrapper" ref="topScrollbar" @scroll="syncScroll('top')">
        <div class="top-scrollbar-content"></div>
      </div>
      
      <div class="table-container" ref="tableContainer" @scroll="syncScroll('table')">
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
        <el-table-column prop="institutionLevel" label="机构等级" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.institutionLevel" type="success" size="small">
              {{ row.institutionLevel }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
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
      </div>

      <!-- 分页器 -->
      <div v-if="showPagination" class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalCount"
          :page-sizes="pageSizes"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadRegistrations"
          @current-change="loadRegistrations"
        />
      </div>
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
            {{ currentDetail.registration.groupCode || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="报名时间">
            {{ formatDate(currentDetail.registration.submittedAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag v-if="currentDetail.registration.status === 'APPROVED'" type="success">已通过</el-tag>
            <el-tag v-else-if="currentDetail.registration.status === 'PENDING'" type="warning">待审核</el-tag>
            <el-tag v-else-if="currentDetail.registration.status === 'REJECTED'" type="danger">已驳回</el-tag>
            <el-tag v-else>{{ currentDetail.registration.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="项目负责人">
            {{ currentDetail._applicantName || '-' }}
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
            {{ currentDetail.activityInfo.subjectTypeLabel || currentDetail.activityInfo.subjectTypeCode || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="品管工具">
            <el-tag v-if="currentDetail.activityInfo.methodLabel" type="success">
              {{ currentDetail.activityInfo.methodLabel }}
            </el-tag>
            <span v-else>{{ currentDetail.activityInfo.methodCode || '未填写' }}</span>
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
            <el-table-column label="操作" width="140">
              <template #default="{ row }">
                <el-button v-if="canPreview(row.fileName)" type="success" size="small" @click="previewFile(row)">预览</el-button>
                <el-button type="primary" size="small" @click="downloadFile(row)">下载</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 文件预览 -->
    <FilePreviewDialog
      v-model="filePreviewVisible"
      :material-id="previewMaterialId"
      :file-name="previewFileName"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePagination } from '@/composables/usePagination'
import { filterRegistrations, batchClassifyRegistrations, autoGroupRegistrations } from '@/api/admin'
import { getRegistration } from '@/api/registration'
import { getDictionaryByType } from '@/api/dictionary'
import { downloadMaterial } from '@/api/material'
import FilePreviewDialog from '@/components/FilePreviewDialog.vue'
import { getCurrentCompetitionId, getCurrentCompetitionIdSync } from '@/utils/competition'
import { useCompetitionGroupPrefixes } from '@/composables/useCompetitionGroupPrefixes'
import dayjs from 'dayjs'

//分页
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

const registrations = ref([])
const selectedRegistrations = ref([])
const loading = ref(false)

// 顶部滚动条相关
const topScrollbar = ref(null)
const tableContainer = ref(null)
let isScrolling = false

const dictionaries = reactive({
  methods: [],
  subjectTypes: []
})

// 使用 composable 获取跑马灯数据
const filters = reactive({
  competitionId: getCurrentCompetitionIdSync(),
  institutionName: '',
  groupType: '',
  groupCode: '',
  projectName: '',
  methodCode: ''
})

const competitionIdRef = computed(() => filters.competitionId)
const { load: loadGroupPrefixes, prefixForType, groupCodesForTypeComputed } = useCompetitionGroupPrefixes(competitionIdRef)

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

// 根据赛事配置的前缀 + 组别，生成分组下拉（如 Z1、Z2…）
const availableGroupCodes = groupCodesForTypeComputed(computed(() => changeGroupForm.groupType))

// 检查是否有激活的筛选条件
const hasActiveFilters = computed(() => {
  return !!(
    filters.institutionName ||
    filters.groupType ||
    filters.groupCode ||
    filters.projectName ||
    filters.methodCode
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

// 查看材料（列表页）
const viewMaterials = async (row) => {
  detailDialogVisible.value = true
  detailLoading.value = true
  
  try {
    const res = await getRegistration(row.registrationId)
    if (res.success) {
      currentDetail.value = res.data
      currentDetail.value._applicantName = row.applicantName
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

const filePreviewVisible = ref(false)
const previewMaterialId = ref(null)
const previewFileName = ref('')

const canPreview = (fileName) => {
  if (!fileName) return false
  const ext = fileName.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'docx', 'xlsx', 'xls'].includes(ext)
}

const previewFile = (material) => {
  previewMaterialId.value = material.id
  previewFileName.value = material.fileName || '文件预览'
  filePreviewVisible.value = true
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
    const res = await filterRegistrations({
      ...filters,
      ...getPaginationParams()
    })
    
    if (res.success) {
      registrations.value = extractDataList(res.data)
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
  resetPagination()
  loadRegistrations()
}

const handleSelectionChange = (selection) => {
  selectedRegistrations.value = selection
}

const viewDetail = async (row) => {
  detailDialogVisible.value = true
  detailLoading.value = true
  
  try {
    const res = await getRegistration(row.registrationId)
    if (res.success) {
      currentDetail.value = res.data
      currentDetail.value._applicantName = row.applicantName
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
  changeGroupForm.registrationIds = [row.registrationId]
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
  changeGroupForm.registrationIds = selectedRegistrations.value.map(r => r.registrationId)
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
    // 检查是否选择了竞赛组别
    if (!filters.groupType) {
      ElMessage.warning('请先选择竞赛组别再进行自动分组')
      return
    }
    
    const groupPrefix = prefixForType(filters.groupType)
    
    const groupTypeText = getGroupTypeText(filters.groupType)
    
    await ElMessageBox.confirm(
      `确定要对【${groupTypeText}】进行自动分组吗？将按每组25人自动分配到${groupPrefix}组系列（${groupPrefix}1、${groupPrefix}2、${groupPrefix}3...）`,
      '提示',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    const res = await autoGroupRegistrations({
      competitionId: filters.competitionId,
      groupType: filters.groupType,  // 指定组别
      groupPrefix: groupPrefix,      // 根据组别自动选择前缀
      groupSize: 25                  // 每组人数
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
  if (!topScrollbar.value || !tableContainer.value) {
    return
  }
  const tableBody = tableContainer.value.querySelector('.el-table__body-wrapper')
  if (tableBody) {
    const scrollContent = topScrollbar.value.querySelector('.top-scrollbar-content')
    if (scrollContent) {
      const tableWidth = tableBody.scrollWidth
      scrollContent.style.width = `${tableWidth}px`
    }
  }
}

onMounted(async () => {
  // 加载当前赛事ID
  const competitionId = await getCurrentCompetitionId()
  if (competitionId) {
    filters.competitionId = competitionId
  }
  await loadGroupPrefixes(true)

  loadDictionaries()
  loadRegistrations()
  
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
watch(registrations, () => {
  setTimeout(() => {
    updateTopScrollbarWidth()
  }, 300)
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
