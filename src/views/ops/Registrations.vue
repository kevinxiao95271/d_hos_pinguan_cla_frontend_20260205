<template>
  <div class="ops-registrations-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报名列表管理</span>
        </div>
      </template>
      
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="赛事">
          <el-select v-model="filters.competitionId" placeholder="全部" clearable style="width: 200px" @change="loadRegistrations">
            <el-option
              v-for="comp in competitions"
              :key="comp.id"
              :label="comp.name"
              :value="comp.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 140px">
            <el-option label="草稿" value="DRAFT" />
            <el-option label="已提交" value="SUBMITTED" />
            <el-option label="已退回" value="RETURNED" />
            <el-option label="已批准" value="APPROVED" />
          </el-select>
        </el-form-item>
        
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
        
        <el-form-item label="项目名称">
          <el-input
            v-model="filters.projectName"
            placeholder="请输入项目名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="缴费回执">
          <el-select v-model="filters.hasPaymentProof" placeholder="全部" clearable style="width: 130px">
            <el-option label="已提交" :value="true" />
            <el-option label="未提交" :value="false" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadRegistrations">
            查询
          </el-button>
          <el-button @click="resetFilters">
            重置
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 已选筛选条件展示 -->
      <div v-if="hasActiveFilters" class="active-filters">
        <span class="filter-label">当前筛选：</span>
        <el-tag
          v-if="filters.competitionId"
          closable
          @close="filters.competitionId = null; loadRegistrations()"
          type="primary"
          style="margin-right: 8px"
        >
          赛事：{{ getCompetitionName(filters.competitionId) }}
        </el-tag>
        <el-tag
          v-if="filters.status"
          closable
          @close="filters.status = ''; loadRegistrations()"
          type="success"
          style="margin-right: 8px"
        >
          状态：{{ getStatusText(filters.status) }}
        </el-tag>
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
          type="warning"
          style="margin-right: 8px"
        >
          竞赛组别：{{ getGroupTypeText(filters.groupType) }}
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
          v-if="filters.hasPaymentProof !== null && filters.hasPaymentProof !== undefined && filters.hasPaymentProof !== ''"
          closable
          @close="filters.hasPaymentProof = null; loadRegistrations()"
          type="warning"
          style="margin-right: 8px"
        >
          缴费回执：{{ filters.hasPaymentProof ? '已提交' : '未提交' }}
        </el-tag>
      </div>
      
      <el-alert
        v-if="competitions.length === 0 && !loading"
        title="暂无赛事"
        type="warning"
        :closable="false"
        style="margin: 20px 0"
      >
        系统中还没有创建赛事，请先创建赛事后再查看报名列表
      </el-alert>
      
      <el-alert
        v-else-if="registrations.length === 0 && !loading && filters.competitionId"
        title="暂无报名数据"
        type="info"
        :closable="false"
        style="margin: 20px 0"
      >
        当前赛事暂无报名数据，请检查：1) 是否有参赛者报名 2) 筛选条件是否正确
      </el-alert>
      
      <el-table
        v-loading="loading"
        :data="registrations"
        border
        style="margin-top: 20px"
      >
        <el-table-column prop="registrationId" label="项目编号" width="100" />
        <el-table-column prop="projectName" label="项目名称" min-width="200" />
        <el-table-column prop="institutionName" label="医疗机构" min-width="160" />
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
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applicantName" label="报名人" width="100" />
        <el-table-column prop="submittedAt" label="提交时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.submittedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="材料" width="160">
          <template #default="{ row }">
            <div style="display:flex;flex-direction:column;gap:4px">
              <!-- 报名材料 -->
              <div>
                <span style="color:#909399;font-size:12px">报名材料：</span>
                <template v-if="row.materials && row.materials.length > 0">
                  <el-tag type="success" size="small">{{ row.materials.length }}个</el-tag>
                  <el-button type="primary" size="small" link @click="viewMaterials(row)" style="margin-left:4px">查看</el-button>
                </template>
                <el-tag v-else type="info" size="small">无</el-tag>
              </div>
              <!-- 缴费凭证 -->
              <div>
                <span style="color:#909399;font-size:12px">缴费凭证：</span>
                <template v-if="row.paymentProofs && row.paymentProofs.length > 0">
                  <el-tag type="warning" size="small">{{ row.paymentProofs.length }}张</el-tag>
                  <el-button type="warning" size="small" link @click="viewPaymentProof(row)" style="margin-left:4px">查看</el-button>
                </template>
                <el-tag v-else type="info" size="small">未上传</el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: center"
        @size-change="currentPage = 1; loadRegistrations()"
        @current-change="loadRegistrations"
      />
    </el-card>
    
    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="报名详情"
      width="90%"
      :close-on-click-modal="false"
    >
      <div v-loading="detailLoading">
        <el-descriptions v-if="currentDetail" :column="2" border>
          <el-descriptions-item label="项目编号">
            {{ currentDetail.registration?.id || currentDetail.id }}
          </el-descriptions-item>
          <el-descriptions-item label="项目名称">
            {{ currentDetail.registration?.projectName || currentDetail.projectName }}
          </el-descriptions-item>
          <el-descriptions-item label="医疗机构">
            {{ currentDetail.institution?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="机构等级">
            <el-tag v-if="currentDetail.institution?.level" type="success" size="small">
              {{ currentDetail.institution.level }}
            </el-tag>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="竞赛组别">
            {{ getGroupTypeText(currentDetail.registration?.groupType || currentDetail.groupType) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentDetail.registration?.status || currentDetail.status)" size="small">
              {{ getStatusText(currentDetail.registration?.status || currentDetail.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="项目负责人">
            {{ currentDetail.registration?.applicantName || currentDetail.applicantName || currentDetail._applicantName || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">
            {{ formatDate(currentDetail.registration?.submittedAt || currentDetail.submittedAt) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 成员信息 -->
        <el-divider content-position="left">团队成员</el-divider>
        <el-table v-if="currentDetail?.members && currentDetail.members.length > 0" :data="currentDetail.members" border>
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="{ row }">
              {{ row.role === 'PARTICIPANT' ? '参与人员' : '辅导员' }}
            </template>
          </el-table-column>
          <el-table-column prop="title" label="职称" />
          <el-table-column prop="department" label="科室" />
        </el-table>
        <el-empty v-else description="暂无成员信息" :image-size="80" />
        
        <!-- 材料文件 -->
        <el-divider content-position="left">材料文件</el-divider>
        <div v-if="currentDetail?.materials && currentDetail.materials.length > 0">
          <el-table :data="currentDetail.materials" border>
            <el-table-column prop="fileName" label="文件名" min-width="200" />
            <el-table-column prop="type" label="类型" width="120">
              <template #default="{ row }">
                {{ getMaterialTypeName(row.type) }}
              </template>
            </el-table-column>
            <el-table-column prop="fileSize" label="大小" width="100">
              <template #default="{ row }">
                {{ formatFileSize(row.fileSize) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160">
              <template #default="{ row }">
                <el-button 
                  v-if="canPreview(row.fileName)"
                  type="primary" 
                  size="small" 
                  @click="previewFile(row)"
                >
                  预览
                </el-button>
                <el-button 
                  type="success" 
                  size="small" 
                  @click="downloadFile(row)"
                >
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-empty v-else description="暂无材料文件" :image-size="80" />
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="imagePreviewVisible"
      title="图片预览"
      width="80%"
      :close-on-click-modal="true"
    >
      <div style="text-align: center;">
        <img :src="imagePreviewUrl" style="max-width: 100%; max-height: 70vh;" />
      </div>
    </el-dialog>

    <!-- 缴费凭证弹窗 -->
    <el-dialog
      v-model="proofDialogVisible"
      :title="`缴费凭证 (${currentProofList.length} 张) — ${currentProofReg?.projectName || ''}`"
      width="600px"
    >
      <el-empty v-if="currentProofList.length === 0" description="暂无缴费凭证" />
      <el-table v-else :data="currentProofList" border>
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="fileName" label="文件名" min-width="220" show-overflow-tooltip />
        <el-table-column prop="uploadedAt" label="上传时间" width="160" align="center">
          <template #default="{ row }">
            {{ formatDate(row.uploadedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="downloadProof(row)">下载</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="proofDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { filterRegistrations, deleteRegistration } from '@/api/admin'
import { getRegistration } from '@/api/registration'
import { downloadMaterial } from '@/api/material'
import { getCompetitions } from '@/api/competition'
import { getCurrentCompetitionId } from '@/utils/competition'
import dayjs from 'dayjs'

const loading = ref(false)
const detailLoading = ref(false)
const registrations = ref([])
const competitions = ref([])
const currentDetail = ref(null)
const detailDialogVisible = ref(false)
const imagePreviewVisible = ref(false)
const imagePreviewUrl = ref('')

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = reactive({
  competitionId: null,
  status: '',
  institutionName: '',
  groupType: '',
  projectName: '',
  hasPaymentProof: null
})

const hasActiveFilters = computed(() => {
  return filters.competitionId || filters.status || filters.institutionName ||
         filters.groupType || filters.projectName ||
         (filters.hasPaymentProof !== null && filters.hasPaymentProof !== undefined && filters.hasPaymentProof !== '')
})

const loadCompetitions = async () => {
  try {
    const res = await getCompetitions()
    if (res.success) {
      competitions.value = res.data || []
      
      // 优先使用后端全局当前赛事
      if (!filters.competitionId) {
        const currentCompetitionId = await getCurrentCompetitionId()
        if (currentCompetitionId) {
          filters.competitionId = currentCompetitionId
          console.log('✅ 使用全局当前赛事ID:', currentCompetitionId)
        } else if (competitions.value.length > 0) {
          // 如果没有全局当前赛事，选择第一个
          filters.competitionId = competitions.value[0].id
          console.log('✅ 自动选择第一个赛事:', competitions.value[0].name)
        }
      }
    }
  } catch (error) {
    console.error('加载赛事失败:', error)
  }
}

const loadRegistrations = async () => {
  // 如果没有选择赛事，不加载
  if (!filters.competitionId) {
    console.log('⚠️ 未选择赛事，跳过加载')
    return
  }
  
  loading.value = true
  try {
    const params = {
      competitionId: filters.competitionId,
      page: currentPage.value,
      size: pageSize.value
    }
    if (filters.status) params.status = filters.status
    if (filters.institutionName) params.institutionName = filters.institutionName
    if (filters.groupType) params.groupType = filters.groupType
    if (filters.projectName) params.projectName = filters.projectName
    if (filters.hasPaymentProof !== null && filters.hasPaymentProof !== undefined && filters.hasPaymentProof !== '') {
      params.hasPaymentProof = filters.hasPaymentProof
    }

    const res = await filterRegistrations(params)
    if (res.success) {
      registrations.value = res.data?.content || []
      total.value = res.data?.totalElements || 0
      currentPage.value = res.data?.pageNo ?? currentPage.value
      console.log('✅ 报名列表 第', currentPage.value, '页，共', total.value, '条')
    } else {
      ElMessage.error('加载失败')
    }
  } catch (error) {
    console.error('加载报名列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.competitionId = null
  filters.status = ''
  filters.institutionName = ''
  filters.groupType = ''
  filters.projectName = ''
  filters.hasPaymentProof = null
  currentPage.value = 1
  loadRegistrations()
}

const viewDetail = async (row) => {
  detailDialogVisible.value = true
  detailLoading.value = true
  
  try {
    const id = row.registrationId || row.id
    const res = await getRegistration(id)
    if (res.success) {
      currentDetail.value = res.data
      // 详情接口不含 applicantName，从列表行补充
      if (!currentDetail.value.applicantName && !currentDetail.value.registration?.applicantName) {
        currentDetail.value._applicantName = row.applicantName
      }
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

const viewMaterials = async (row) => {
  await viewDetail(row)
}

// 缴费凭证弹窗
const proofDialogVisible = ref(false)
const currentProofList = ref([])
const currentProofReg = ref(null)

const viewPaymentProof = (row) => {
  currentProofReg.value = row
  currentProofList.value = row.paymentProofs || []
  proofDialogVisible.value = true
}

const downloadProof = async (material) => {
  try {
    const blob = await downloadMaterial(material.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = material.fileName || '缴费凭证'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

// 判断文件是否可以预览（仅图片，PDF 统一走下载）
const canPreview = (fileName) => {
  if (!fileName) return false
  const lowerName = fileName.toLowerCase()
  return lowerName.endsWith('.jpg') || 
         lowerName.endsWith('.jpeg') || 
         lowerName.endsWith('.png') || 
         lowerName.endsWith('.gif')
}

// 预览文件
const previewFile = async (material) => {
  try {
    const blob = await downloadMaterial(material.id)
    const url = window.URL.createObjectURL(blob)
    const fileName = material.fileName.toLowerCase()
    
    if (fileName.endsWith('.pdf')) {
      // PDF在新窗口打开
      window.open(url, '_blank')
      // 延迟释放URL
      setTimeout(() => {
        window.URL.revokeObjectURL(url)
      }, 60000)
    } else if (['jpg', 'jpeg', 'png', 'gif'].some(ext => fileName.endsWith(ext))) {
      // 图片在弹窗中显示
      imagePreviewUrl.value = url
      imagePreviewVisible.value = true
    }
  } catch (error) {
    console.error('预览文件失败:', error)
    ElMessage.error('预览失败，请尝试下载')
  }
}

// 下载文件
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
    ElMessage.error('下载失败')
  }
}

// 删除报名
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认删除报名【${row.projectName}】？此操作将级联删除所有相关数据（评审任务、评分、材料文件等），且不可恢复！`,
      '危险操作',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'error',
        confirmButtonClass: 'el-button--danger'
      }
    )

    const registrationId = row.registrationId || row.id
    const res = await deleteRegistration(registrationId)

    if (res.success) {
      ElMessage.success('删除成功')
      loadRegistrations()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除报名失败:', error)
      const message = error.response?.data?.message || error.message || '删除失败'
      ElMessage.error(message)
    }
  }
}

const getCompetitionName = (id) => {
  const comp = competitions.value.find(c => c.id === id)
  return comp ? comp.name : ''
}

const getGroupTypeText = (type) => {
  const map = {
    'BASIC': '基层组',
    'COMPREHENSIVE': '综合组',
    'ADVANCED': '进阶组'
  }
  return map[type] || type
}

const getStatusText = (status) => {
  const map = {
    'DRAFT': '草稿',
    'SUBMITTED': '已提交',
    'RETURNED': '已退回',
    'APPROVED': '已批准'
  }
  return map[status] || status
}

const getStatusType = (status) => {
  const map = {
    'DRAFT': 'info',
    'SUBMITTED': 'success',
    'RETURNED': 'warning',
    'APPROVED': 'primary'
  }
  return map[status] || ''
}

const getMaterialTypeName = (type) => {
  const map = {
    'registration_form': '报名表',
    'result_report': '成果报告书',
    'evidence': '佐证材料'
  }
  return map[type] || type
}

const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(async () => {
  // 先加载赛事列表，再加载报名列表
  await loadCompetitions()
  // loadCompetitions会自动选择第一个赛事，然后才加载报名
  if (filters.competitionId) {
    loadRegistrations()
  }
})
</script>

<style scoped lang="scss">
.ops-registrations-page {
  padding: 20px;
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 18px;
    font-weight: 600;
  }
  
  .filter-form {
    margin-bottom: 20px;
  }
  
  .active-filters {
    margin-bottom: 20px;
    padding: 10px;
    background-color: #f5f7fa;
    border-radius: 4px;
    
    .filter-label {
      font-weight: 600;
      margin-right: 10px;
    }
  }
}
</style>
