<template>
  <div class="my-registrations-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的报名</span>
          <el-button type="primary" @click="goToCreate">
            新建报名
          </el-button>
        </div>
      </template>
      
      <el-table :data="registrations" v-loading="loading" border>
        <el-table-column prop="id" label="项目编号" width="100" />
        <el-table-column prop="projectName" label="项目名称" min-width="200" />
        <el-table-column prop="institutionName" label="医疗机构" width="180" />
        <el-table-column prop="institutionLevel" label="机构等级" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.institutionLevel" type="success" size="small">
              {{ row.institutionLevel }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="groupType" label="竞赛组别" width="120">
          <template #default="{ row }">
            {{ getGroupTypeText(row.groupType) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column prop="submittedAt" label="提交时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.submittedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-space :size="4" wrap>
              <template v-if="row.status === 'DRAFT'">
                <el-button type="primary" size="small" @click="editRegistration(row.id)">编辑</el-button>
                <el-button type="success" size="small" @click="submitRegistration(row.id, row.competitionId)">提交</el-button>
              </template>
              <template v-else-if="row.status === 'RETURNED'">
                <el-tag type="warning" size="small" style="margin-right:4px">已被驳回</el-tag>
                <el-button type="primary" size="small" @click="editRegistration(row.id)">修改后重新提交</el-button>
              </template>
              <template v-else-if="row.status === 'SUBMITTED'">
                <el-button size="small" disabled style="cursor:not-allowed;opacity:.6">已提交</el-button>
              </template>
              <el-button size="small" @click="viewDetail(row.id)">查看详情</el-button>
              <el-button
                v-if="row.status === 'SUBMITTED'"
                size="small"
                @click="viewResults(row.id)"
              >
                查看评审结果
              </el-button>

              <!-- 缴费三件套：仅已提交 -->
              <template v-if="row.status === 'SUBMITTED'">
                <el-button
                  type="warning"
                  size="small"
                  @click="goToPay"
                >
                  报名缴费
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  :loading="uploadingId === row.id"
                  @click="openUpload(row)"
                >
                  上传凭证
                </el-button>
                <el-button
                  size="small"
                  @click="viewProof(row)"
                >
                  查看凭证({{ proofCount(row.id) }})
                </el-button>
              </template>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 上传凭证对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传缴费凭证" width="420px" :close-on-click-modal="false">
      <el-alert
        title="支持格式：jpg / jpeg / png / gif / webp，单文件不超过 10MB"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      />
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".jpg,.jpeg,.png,.gif,.webp"
        :on-change="onFileChange"
        :on-remove="() => { pendingFile = null }"
        :file-list="uploadFileList"
        drag
      >
        <el-icon style="font-size: 48px; color: #c0c4cc"><Upload /></el-icon>
        <div style="margin-top: 8px; color: #606266">拖拽文件到此处，或<em>点击上传</em></div>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="uploadingId !== null"
          :disabled="!pendingFile"
          @click="confirmUpload"
        >
          确认上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看凭证对话框 -->
    <el-dialog v-model="proofDialogVisible" :title="`缴费凭证 (${currentProofList.length} 张)`" width="560px">
      <div v-loading="proofLoading">
        <el-empty v-if="!proofLoading && currentProofList.length === 0" description="暂无缴费凭证" />
        <el-table v-else :data="currentProofList" border>
          <el-table-column type="index" label="#" width="50" align="center" />
          <el-table-column prop="fileName" label="文件名" min-width="200" show-overflow-tooltip />
          <el-table-column prop="uploadedAt" label="上传时间" width="160" align="center">
            <template #default="{ row }">
              {{ formatDate(row.uploadedAt) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="130" align="center">
            <template #default="{ row }">
              <el-button v-if="canPreview(row.fileName)" type="success" size="small" link @click="previewProof(row)">预览</el-button>
              <el-button type="primary" size="small" link @click="downloadProof(row)">下载</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="proofDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 面谈通知文件区（仅进阶组可见） -->
    <el-card v-if="hasAdvancedGroup" style="margin-top: 20px;">
      <template #header>
        <span style="font-size:16px; font-weight:600;">面谈通知文件</span>
      </template>
      <div class="notice-file-links">
        <el-link
          v-for="file in noticeFiles"
          :key="file.url"
          underline="never"
          style="color: #67b3e8;"
          @click="openNoticeFile(file)"
        >
          📄 {{ file.name }}
        </el-link>
      </div>
    </el-card>

    <!-- 文件预览 -->
    <FilePreviewDialog
      v-model="filePreviewVisible"
      :material-id="previewMaterialId"
      :file-url="previewFileUrl"
      :file-name="previewFileName"
      :show-download="previewShowDownload"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { getMyRegistrations, submitRegistration as submitReg, getRegistration, uploadRegistrationMaterial, getRegistrationCountByInstitution } from '@/api/registration'
import { downloadMaterial } from '@/api/material'
import FilePreviewDialog from '@/components/FilePreviewDialog.vue'
import dayjs from 'dayjs'

const PAYMENT_URL = 'https://mm.sciconf.cn/cn/minisite/index/35899'

const router = useRouter()

const registrations = ref([])
const loading = ref(false)

// key: registrationId -> payment_proof materials 数组
const proofMap = reactive({})

// 上传凭证
const uploadDialogVisible = ref(false)
const uploadRef = ref(null)
const uploadFileList = ref([])
const pendingFile = ref(null)
const uploadingId = ref(null)
const currentUploadReg = ref(null)

// 查看凭证
const proofDialogVisible = ref(false)
const proofLoading = ref(false)
const currentProofList = ref([])

const proofCount = (regId) => (proofMap[regId] || []).length

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMyRegistrations()
    if (res.success) {
      registrations.value = res.data || []
      // 并行拉取所有报名的 payment_proof 材料
      loadAllProofs()
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载报名列表失败:', error)
    ElMessage.error('加载报名列表失败')
  } finally {
    loading.value = false
  }
}

const loadAllProofs = async () => {
  const submitted = registrations.value.filter(r => r.status === 'SUBMITTED')
  if (!submitted.length) return
  const results = await Promise.allSettled(submitted.map(r => getRegistration(r.id)))
  results.forEach((result, idx) => {
    const regId = submitted[idx].id
    if (result.status === 'fulfilled' && result.value.success) {
      proofMap[regId] = result.value.data?.paymentProofs || []
    } else {
      proofMap[regId] = []
    }
  })
}

const goToPay = () => {
  window.open(PAYMENT_URL, '_blank')
}

const openUpload = (row) => {
  currentUploadReg.value = row
  uploadFileList.value = []
  pendingFile.value = null
  uploadDialogVisible.value = true
}

const onFileChange = (file) => {
  const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowed.includes(file.raw?.type)) {
    ElMessage.error('只支持 jpg / jpeg / png / gif / webp 格式')
    uploadFileList.value = []
    pendingFile.value = null
    return false
  }
  if (file.raw?.size > 10 * 1024 * 1024) {
    ElMessage.error('文件不能超过 10MB')
    uploadFileList.value = []
    pendingFile.value = null
    return false
  }
  pendingFile.value = file.raw
}

const confirmUpload = async () => {
  if (!pendingFile.value || !currentUploadReg.value) return

  const regId = currentUploadReg.value.id
  const existingIds = new Set((proofMap[regId] || []).map(m => m.id))

  uploadingId.value = regId
  try {
    const res = await uploadRegistrationMaterial(regId, pendingFile.value, 'payment_proof')
    if (res.success) {
      if (existingIds.has(res.data.id)) {
        ElMessage.warning('该凭证已存在，已忽略重复上传')
      } else {
        ElMessage.success('上传成功')
        // 更新本地 proofMap
        if (!proofMap[regId]) proofMap[regId] = []
        proofMap[regId].push(res.data)
      }
      uploadDialogVisible.value = false
    } else {
      ElMessage.error(res.message || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败，请稍后重试')
  } finally {
    uploadingId.value = null
  }
}

const viewProof = async (row) => {
  proofDialogVisible.value = true
  proofLoading.value = true
  try {
    const res = await getRegistration(row.id)
    if (res.success) {
      currentProofList.value = res.data?.paymentProofs || []
      proofMap[row.id] = currentProofList.value
    }
  } catch (error) {
    console.error('加载凭证失败:', error)
  } finally {
    proofLoading.value = false
  }
}

const filePreviewVisible = ref(false)
const previewMaterialId = ref(null)
const previewFileName = ref('')
const previewFileUrl = ref(null)
const previewShowDownload = ref(false)

// 面谈通知静态文件（仅进阶组可见）
const hasAdvancedGroup = computed(() =>
  registrations.value.some(r => r.groupType === 'ADVANCED')
)

const base = import.meta.env.BASE_URL
const noticeFiles = [
  { name: '关于组织2026年浙江省医院品管大赛进阶组项目面谈的函', url: `${base}interview_notice.pdf` },
  { name: '附件1.2026年浙江省医院品管大赛面谈须知', url: `${base}interview_guide.pdf` },
  { name: '附件2.2026年浙江省医院品管大赛进阶组面谈排程', url: `${base}interview_schedule.pdf` }
]

const openNoticeFile = (file) => {
  previewMaterialId.value = null
  previewFileUrl.value = file.url
  previewFileName.value = file.name + '.pdf'
  previewShowDownload.value = true
  filePreviewVisible.value = true
}

const canPreview = (fileName) => {
  if (!fileName) return false
  const ext = fileName.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'docx', 'xlsx', 'xls'].includes(ext)
}

const previewProof = (material) => {
  previewMaterialId.value = material.id
  previewFileUrl.value = null
  previewFileName.value = material.fileName || '文件预览'
  previewShowDownload.value = false
  filePreviewVisible.value = true
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
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

const getGroupTypeText = (type) => {
  const map = { BASIC: '基层组', COMPREHENSIVE: '综合组', ADVANCED: '进阶组' }
  return map[type] || type
}

const getStatusType = (status) => {
  const map = { DRAFT: 'info', SUBMITTED: 'success', APPROVED: 'success', RETURNED: 'warning' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { DRAFT: '草稿', SUBMITTED: '已提交', APPROVED: '已通过', RETURNED: '已退回' }
  return map[status] || status
}

const formatDate = (date) => date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'

const goToCreate = () => router.push('/contestant/register/new')
const editRegistration = (id) => router.push(`/contestant/register/${id}`)
const viewDetail = (id) => router.push(`/contestant/registration/${id}`)
const viewResults = (id) => router.push(`/contestant/registration/${id}/results`)

const submitRegistration = async (id, competitionId) => {
  try {
    // 提交前检查机构项目数量上限
    if (competitionId) {
      const countRes = await getRegistrationCountByInstitution(competitionId)
      if (countRes.success && countRes.data >= 8) {
        ElMessage.error('您所在机构在本次赛事中已提交 8 个项目，已达上限，无法继续提交')
        return
      }
    }
    await ElMessageBox.confirm('确认提交报名？提交后将无法修改。', '确认提交', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const res = await submitReg(id)
    if (res.success) {
      ElMessage.success('提交成功')
      loadData()
    } else {
      ElMessage.error(res.message || '提交失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
      ElMessage.error('提交失败')
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.my-registrations-page {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
  }
}

.notice-file-links {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
}
</style>
