<template>
  <div class="my-registrations-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的报名</span>
          <div class="header-actions">
            <el-select
              v-model="selectedCompetitionId"
              placeholder="选择赛事届别"
              style="width: 320px; margin-right: 12px;"
              :loading="competitionsLoading"
              @change="loadRegistrations"
            >
              <el-option
                v-for="item in competitionOptions"
                :key="item.competitionId"
                :label="formatCompetitionOption(item)"
                :value="item.competitionId"
              />
            </el-select>
            <el-button type="primary" @click="goToCreate">
              新建报名
            </el-button>
          </div>
        </div>
      </template>

      <el-alert
        v-if="selectedCompetitionSummary"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px;"
      >
        {{ selectedCompetitionSummary }}
      </el-alert>
      
      <el-table :data="registrations" v-loading="loading" border>
        <el-table-column label="项目编号" width="100" align="center">
          <template #default="{ row }">
            {{ displayProjectCode(row) }}
          </template>
        </el-table-column>
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
              <el-button
                v-if="row.status !== 'DRAFT'"
                size="small"
                @click="viewDetail(row)"
              >
                查看详情
              </el-button>
              <el-button
                v-if="row.status === 'SUBMITTED'"
                type="warning"
                size="small"
                @click="viewResults(row.id)"
              >
                查看反馈
              </el-button>

              <!-- 缴费三件套：仅已提交 -->
              <template v-if="row.status === 'SUBMITTED'">
                <el-button
                  class="payment-btn-muted"
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

    <!-- 现场竞赛通知（所有参赛者可见） -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span style="font-size:16px; font-weight:600;">现场竞赛通知</span>
      </template>
      <div class="notice-file-links">
        <el-link
          underline="never"
          style="color: #67b3e8;"
          @click="openNoticeFile({ name: '关于举办2026年浙江省医院品管大赛现场竞赛的通知', url: `${base}competition_notice.pdf` })"
        >
          📄 关于举办2026年浙江省医院品管大赛现场竞赛的通知
        </el-link>
        <el-link
          underline="never"
          style="color: #67b3e8;"
          @click="openNoticeFile({ name: '2026年浙江省医院品管大赛现场汇报注意事项和排程', url: `${base}presentation_schedule.pdf` })"
        >
          📄 2026年浙江省医院品管大赛现场汇报注意事项和排程
        </el-link>
        <el-link
          underline="never"
          style="color: #67b3e8;"
          @click="openNoticeFile({ name: '关于公布2026年浙江省医院品管大赛获奖名单的通知', url: `${base}award_notice.pdf` })"
        >
          📄 关于公布2026年浙江省医院品管大赛获奖名单的通知
        </el-link>
      </div>
    </el-card>

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
import { useUserStore } from '@/stores/user'
import {
  getMyRegistrations,
  getMyCompetitions,
  submitRegistration as submitReg,
  getRegistration,
  uploadRegistrationMaterial,
  getRegistrationCountByInstitution
} from '@/api/registration'
import { getCompetitions } from '@/api/competition'
import { downloadMaterial } from '@/api/material'
import FilePreviewDialog from '@/components/FilePreviewDialog.vue'
import { displayProjectCode, contestantRegistrationPath } from '@/utils/registrationDisplay'
import dayjs from 'dayjs'

const PAYMENT_URL = 'https://mm.sciconf.cn/cn/minisite/index/35899'

const router = useRouter()
const userStore = useUserStore()

const registrations = ref([])
const loading = ref(false)
const myCompetitions = ref([])
const competitionsLoading = ref(false)
const selectedCompetitionId = ref(null)

const defaultCompetitionId = computed(() => userStore.currentCompetitionId)

const isViewingCurrentCompetition = computed(() => {
  if (!selectedCompetitionId.value || !defaultCompetitionId.value) return true
  return Number(selectedCompetitionId.value) === Number(defaultCompetitionId.value)
})

/** 下拉选项：所有 ACTIVE 赛事 + 历史报名赛事，去重合并，最新在前 */
const competitionOptions = computed(() => myCompetitions.value)

const selectedCompetitionMeta = computed(() =>
  competitionOptions.value.find(c => Number(c.competitionId) === Number(selectedCompetitionId.value))
)

const selectedCompetitionSummary = computed(() => {
  const meta = selectedCompetitionMeta.value
  if (!meta) return ''
  const parts = []
  if (meta.competitionName) parts.push(meta.competitionName)
  if (meta.registrationCount != null || meta.draftCount != null) {
    parts.push(`正式 ${meta.registrationCount ?? 0} 条，草稿 ${meta.draftCount ?? 0} 条`)
  }
  if (meta.current || isViewingCurrentCompetition.value) parts.push('（当前届）')
  return parts.join(' · ')
})

const formatCompetitionOption = (item) => {
  const name = item.competitionName || '赛事'
  const counts = item.registrationCount != null
    ? `正式${item.registrationCount}/草稿${item.draftCount ?? 0}`
    : '暂无报名'
  const tags = []
  if (item.active) tags.push('报名中')
  if (item.current) tags.push('当前届')
  const tagStr = tags.length ? ` · ${tags.join('·')}` : ''
  return `${name}（${counts}）${tagStr}`
}

const loadMyCompetitions = async () => {
  competitionsLoading.value = true
  try {
    // ① 拉全量赛事（含 status 字段）
    // ② 拉我已报名的历届（/registrations/my-competitions 后端路由目前有 bug，降级处理）
    const [activeRes, mineRes] = await Promise.allSettled([
      getCompetitions(),
      getMyCompetitions()
    ])

    const allComps = (activeRes.status === 'fulfilled' && activeRes.value.success)
      ? (activeRes.value.data || [])
      : []
    const activeList = allComps.filter(c => c.status === 'ACTIVE')
    const activeIds = new Set(activeList.map(c => String(c.id)))

    // my-competitions 成功时用历史报名统计；400/失败时降级为空
    const mine = (mineRes.status === 'fulfilled' && mineRes.value.success)
      ? (mineRes.value.data || [])
      : []
    const mineIds = new Set(mine.map(c => String(c.competitionId)))

    // 已报名赛事：补充 active 标记
    const mineEnriched = mine.map(c => ({
      ...c,
      active: activeIds.has(String(c.competitionId)),
      current: String(c.competitionId) === String(defaultCompetitionId.value)
    }))

    // ACTIVE 赛事中用户尚未报名的 → 补充进来（暂无报名数据）
    const extraActive = activeList
      .filter(c => !mineIds.has(String(c.id)))
      .map(c => ({
        competitionId: c.id,
        competitionName: c.name,
        year: c.createdAt ? new Date(c.createdAt).getFullYear() : null,
        registrationCount: null,  // 未知，不显示报名数
        draftCount: null,
        active: true,
        current: String(c.id) === String(defaultCompetitionId.value)
      }))

    // 合并，新赛事在前
    myCompetitions.value = [...mineEnriched, ...extraActive]
      .sort((a, b) => Number(b.competitionId) - Number(a.competitionId))

    // my-competitions 接口失败时，fallback：用 /registrations 逐个赛事查报名数
    if (!mine.length && activeList.length) {
      const countResults = await Promise.allSettled(
        activeList.map(c => getMyRegistrations({ competitionId: c.id }))
      )
      myCompetitions.value = activeList.map((c, i) => {
        const res = countResults[i]
        const regs = (res.status === 'fulfilled' && res.value.success) ? (res.value.data || []) : []
        const submitted = regs.filter(r => r.status !== 'DRAFT').length
        const drafts = regs.filter(r => r.status === 'DRAFT').length
        return {
          competitionId: c.id,
          competitionName: c.name,
          year: c.createdAt ? new Date(c.createdAt).getFullYear() : null,
          registrationCount: submitted,
          draftCount: drafts,
          active: true,
          current: String(c.id) === String(defaultCompetitionId.value)
        }
      }).sort((a, b) => Number(b.competitionId) - Number(a.competitionId))
    }

  } catch (error) {
    console.warn('加载赛事列表失败:', error)
  } finally {
    competitionsLoading.value = false
  }
}

const loadRegistrations = async () => {
  if (!selectedCompetitionId.value) return
  loading.value = true
  try {
    const res = await getMyRegistrations({ competitionId: selectedCompetitionId.value })
    if (res.success) {
      registrations.value = res.data || []
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

const loadData = async () => {
  await loadMyCompetitions()
  if (!selectedCompetitionId.value) {
    // 优先：userStore 当前届 → 列表里 current 标记 → 第一条 ACTIVE → 第一条
    const currentInList = myCompetitions.value.find(c => c.current)
    const firstActive   = myCompetitions.value.find(c => c.active)
    selectedCompetitionId.value =
      defaultCompetitionId.value ??
      currentInList?.competitionId ??
      firstActive?.competitionId ??
      myCompetitions.value[0]?.competitionId ??
      null
  }
  if (selectedCompetitionId.value) {
    await loadRegistrations()
  }
}

const backToCurrentCompetition = async () => {
  if (!defaultCompetitionId.value) {
    ElMessage.warning('未获取到当前届赛事')
    return
  }
  selectedCompetitionId.value = defaultCompetitionId.value
  await loadRegistrations()
}

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

const goToCreate = () => {
  const query = {}
  const cid = selectedCompetitionId.value || defaultCompetitionId.value
  if (cid) query.competitionId = cid
  router.push({ path: '/contestant/register/new', query })
}
const editRegistration = (id) => router.push(`/contestant/register/${id}`)
const viewDetail = (row) => router.push(contestantRegistrationPath(row))
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
      await loadRegistrations()
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
    flex-wrap: wrap;
    gap: 12px;
    font-size: 18px;
    font-weight: 600;

    .header-actions {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }
  }
}

.notice-file-links {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
}

.payment-btn-muted.el-button {
  color: #475569;
  background-color: #f8fafc;
  border-color: #cbd5e1;
}

.payment-btn-muted.el-button:hover,
.payment-btn-muted.el-button:focus-visible {
  color: #334155;
  background-color: #f1f5f9;
  border-color: #94a3b8;
}
</style>
