<template>
  <div class="reviewers-container">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">评审专家管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增评委
          </el-button>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :model="filters" :inline="true" style="margin-bottom: 20px">
        <el-form-item label="机构">
          <el-select
            v-model="filters.institutionId"
            placeholder="输入机构名称搜索"
            filterable
            remote
            clearable
            :remote-method="searchFilterInst"
            :loading="filterInstLoading"
            style="width: 200px"
          >
            <el-option
              v-for="inst in filterInstOptions"
              :key="inst.id"
              :label="inst.name"
              :value="inst.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="专家背景">
          <el-input v-model="filters.expertBackground" placeholder="请输入专家背景" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 评委列表 -->
      <el-table :data="reviewers" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="phone" label="手机号" width="130" align="center" />
        <el-table-column prop="name" label="姓名" width="120" align="center" />
        <el-table-column prop="title" label="职称" width="150" align="center" />
        <el-table-column prop="institutionName" label="所属机构" min-width="200" />
        <el-table-column prop="expertBackground" label="专家背景" width="150">
          <template #default="{ row }">
            {{ row.expertBackground || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="currentLoad" label="当前负荷" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.currentLoad > 10 ? 'danger' : row.currentLoad > 5 ? 'warning' : 'success'">
              {{ row.currentLoad || 0 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="info" size="small" @click="openDetail(row)">详情</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 统计信息 -->
      <div style="margin-top: 20px; color: #666; font-size: 14px">
        共 {{ reviewers.length }} 位评审专家
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" maxlength="50" />
        </el-form-item>
        <el-form-item label="职称" prop="title">
          <el-input v-model="form.title" placeholder="请输入职称" maxlength="50" />
        </el-form-item>
        <el-form-item label="所属机构" prop="institutionId">
          <el-select
            v-model="form.institutionId"
            placeholder="输入机构名称搜索"
            filterable
            remote
            :remote-method="searchFormInst"
            :loading="formInstLoading"
            style="width: 100%"
          >
            <el-option
              v-for="inst in formInstOptions"
              :key="inst.id"
              :label="inst.name"
              :value="inst.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="专家背景">
          <el-input
            v-model="form.expertBackground"
            type="textarea"
            :rows="3"
            placeholder="请输入专家背景（选填）"
            maxlength="500"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="drawerTitle"
      direction="rtl"
      size="640px"
      @close="drawerTab = 'basic'"
    >
      <el-tabs v-model="drawerTab" style="height: 100%">
        <!-- Tab 1: 基本信息（只读） -->
        <el-tab-pane label="基本信息" name="basic">
          <el-descriptions :column="2" border size="small" style="margin-top: 8px">
            <el-descriptions-item label="ID">{{ drawerRow.id }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ drawerRow.phone }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ drawerRow.name }}</el-descriptions-item>
            <el-descriptions-item label="职称">{{ drawerRow.title || '-' }}</el-descriptions-item>
            <el-descriptions-item label="所属机构" :span="2">{{ drawerRow.institutionName || '-' }}</el-descriptions-item>
            <el-descriptions-item label="当前负荷">{{ drawerRow.currentLoad ?? 0 }}</el-descriptions-item>
            <el-descriptions-item label="专家背景" :span="2">{{ drawerRow.expertBackground || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <!-- Tab 2: 扩展档案 -->
        <el-tab-pane label="扩展档案" name="profile" lazy>
          <div v-loading="profileLoading" style="padding: 4px 0">
            <el-form
              ref="profileFormRef"
              :model="profileForm"
              :rules="profileRules"
              label-width="130px"
            >
              <el-divider content-position="left">基本信息</el-divider>

              <el-form-item label="性别">
                <el-radio-group v-model="profileForm.gender">
                  <el-radio value="MALE">男</el-radio>
                  <el-radio value="FEMALE">女</el-radio>
                  <el-radio value="UNKNOWN">保密</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="职务">
                <el-input v-model="profileForm.position" placeholder="请输入职务" maxlength="100" style="width: 280px" />
              </el-form-item>

              <el-divider content-position="left">证件信息</el-divider>

              <el-form-item label="身份证号" prop="idNumber">
                <el-input
                  v-model="profileForm.idNumber"
                  placeholder="请输入身份证号"
                  maxlength="18"
                  style="width: 280px"
                  @input="profileAutoMaskId"
                />
                <span v-if="profileForm.idNumberMasked" style="margin-left: 12px; color: #909399; font-size: 12px">
                  {{ profileForm.idNumberMasked }}
                </span>
              </el-form-item>

              <el-form-item label="身份证正面">
                <div style="display: flex; align-items: center; gap: 10px">
                  <el-image
                    v-if="profileForm.idCardFrontUrl"
                    :src="profileForm.idCardFrontUrl"
                    style="width: 130px; height: 80px; border-radius: 4px; border: 1px solid #eee"
                    fit="cover"
                    :preview-src-list="[profileForm.idCardFrontUrl]"
                  />
                  <el-input v-model="profileForm.idCardFrontUrl" placeholder="图片 URL" style="width: 240px" clearable />
                </div>
              </el-form-item>

              <el-form-item label="身份证反面">
                <div style="display: flex; align-items: center; gap: 10px">
                  <el-image
                    v-if="profileForm.idCardBackUrl"
                    :src="profileForm.idCardBackUrl"
                    style="width: 130px; height: 80px; border-radius: 4px; border: 1px solid #eee"
                    fit="cover"
                    :preview-src-list="[profileForm.idCardBackUrl]"
                  />
                  <el-input v-model="profileForm.idCardBackUrl" placeholder="图片 URL" style="width: 240px" clearable />
                </div>
              </el-form-item>

              <el-divider content-position="left">银行卡信息</el-divider>

              <el-form-item label="开户银行">
                <el-input v-model="profileForm.bankName" placeholder="请输入开户银行" maxlength="100" style="width: 280px" />
              </el-form-item>

              <el-form-item label="银行卡号">
                <el-input
                  v-model="profileForm.bankCardNo"
                  placeholder="请输入银行卡号"
                  maxlength="25"
                  style="width: 280px"
                  @input="profileAutoMaskBank"
                />
                <span v-if="profileForm.bankCardNoMasked" style="margin-left: 12px; color: #909399; font-size: 12px">
                  {{ profileForm.bankCardNoMasked }}
                </span>
              </el-form-item>

              <el-divider content-position="left">专业背景与能力</el-divider>

              <el-form-item label="专业背景">
                <el-checkbox-group v-model="profileForm.backgrounds">
                  <el-checkbox v-for="item in BACKGROUND_OPTIONS" :key="item.value" :value="item.value">
                    {{ item.label }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item label="擅长工具">
                <el-checkbox-group v-model="profileForm.tools">
                  <el-checkbox v-for="item in TOOL_OPTIONS" :key="item.value" :value="item.value">
                    {{ item.label }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item label="擅长主题">
                <el-checkbox-group v-model="profileForm.topics">
                  <el-checkbox v-for="item in TOPIC_OPTIONS" :key="item.value" :value="item.value">
                    {{ item.label }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" :loading="profileSaving" @click="saveProfile">保存扩展档案</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- Tab 3: 机构变更 -->
        <el-tab-pane label="机构变更" name="institution" lazy>
          <div style="padding: 4px 0">
            <!-- 变更记录 -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px">
              <span style="font-weight:600">机构变更记录</span>
              <el-button type="primary" size="small" @click="showInstChangeForm = !showInstChangeForm">
                {{ showInstChangeForm ? '收起' : '发起变更' }}
              </el-button>
            </div>

            <!-- 发起变更表单 -->
            <el-card v-if="showInstChangeForm" shadow="never" style="margin-bottom:16px; background:#fafafa">
              <el-form ref="instChangeFormRef" :model="instChangeForm" label-width="90px" size="small">
                <el-form-item label="当前机构">
                  <span>{{ drawerRow.institutionName || '-' }}</span>
                </el-form-item>
                <el-form-item label="新机构" required>
                  <el-select
                    v-model="instChangeForm.newInstitutionId"
                    filterable
                    remote
                    :remote-method="searchInstForChange"
                    :loading="instChangeSearching"
                    placeholder="输入关键词搜索机构"
                    style="width: 100%"
                    value-key="id"
                  >
                    <el-option
                      v-for="item in instChangeOptions"
                      :key="item.id"
                      :label="item.name"
                      :value="item.id"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="变更原因">
                  <el-input v-model="instChangeForm.reason" type="textarea" :rows="2" maxlength="500" placeholder="选填" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" size="small" :loading="instChanging" @click="submitInstChange">提交变更</el-button>
                  <el-button size="small" @click="showInstChangeForm = false">取消</el-button>
                </el-form-item>
              </el-form>
            </el-card>

            <!-- 历史记录表格 -->
            <el-table :data="instHistory" border size="small" v-loading="instHistoryLoading" empty-text="暂无变更记录">
              <el-table-column prop="oldInstitutionName" label="原机构" min-width="140" />
              <el-table-column prop="newInstitutionName" label="新机构" min-width="140" />
              <el-table-column prop="reason" label="原因" min-width="100" />
              <el-table-column prop="changedByName" label="操作人" width="80" />
              <el-table-column prop="changedAt" label="时间" width="140">
                <template #default="{ row }">
                  {{ row.changedAt ? row.changedAt.replace('T',' ').substring(0,16) : '-' }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getReviewers, createReviewer, updateReviewer, deleteReviewer } from '@/api/review'
import { autocomplete, searchInstitutions } from '@/api/institution'
import { getReviewerProfile, updateReviewerProfile, adminChangeReviewerInstitution, adminGetReviewerInstitutionHistory } from '@/api/reviewerProfile'

// ── 枚举（与 Profile.vue 保持一致） ─────────────────────────────────
const BACKGROUND_OPTIONS = [
  { value: 'MANAGEMENT', label: '医院管理' },
  { value: 'MEDICAL', label: '医疗' },
  { value: 'NURSING', label: '护理' },
  { value: 'QUALITY_MANAGEMENT', label: '质量管理' },
  { value: 'PHARMACY', label: '药学' },
  { value: 'MEDICAL_TECH', label: '医技' },
  { value: 'MEDICAL_RECORD', label: '病案' },
  { value: 'INFECTION_CONTROL', label: '院感' },
  { value: 'OTHER', label: '其他' }
]
const TOOL_OPTIONS = [
  { value: 'PDCA', label: 'PDCA' },
  { value: 'FOCUS_PDCA', label: 'FOCUS-PDCA' },
  { value: 'QFD', label: 'QFD' },
  { value: 'QCC_PROBLEM_SOLVING', label: 'QCC问题解决型' },
  { value: 'QCC_TOPIC_ACHIEVEMENT', label: 'QCC课题达成型' },
  { value: 'PROJECT_IMPROVEMENT', label: '专案改善' },
  { value: 'RCA', label: 'RCA' },
  { value: 'FMEA', label: 'FMEA' },
  { value: 'BENCHMARKING', label: '标杆管理' },
  { value: 'S6', label: '6S' },
  { value: 'LEAN', label: '精益管理' },
  { value: 'SIX_SIGMA', label: '六西格玛' },
  { value: 'EBM', label: '循证管理' },
  { value: 'BSC', label: 'BSC' },
  { value: 'QUALITY_REPORT_CARD', label: '品质报告卡' },
  { value: 'TRM', label: 'TRM' },
  { value: 'PROCESS_REDESIGN', label: '流程再造' },
  { value: 'OTHER', label: '其他' }
]
const TOPIC_OPTIONS = [
  { value: 'PATIENT_CARE', label: '患者照护' },
  { value: 'MEDICAL_RECORD_QUALITY', label: '病历质量' },
  { value: 'TIME_EFFICIENCY', label: '效率提升' },
  { value: 'COST_EFFECTIVENESS', label: '成本效益' },
  { value: 'SAFETY_ENVIRONMENT', label: '安全环境' },
  { value: 'SATISFACTION', label: '满意度' },
  { value: 'EDUCATION_TRAINING', label: '教育培训' },
  { value: 'MEDICAL_INFORMATION', label: '医疗信息化' },
  { value: 'MEDICAL_QUALITY_SAFETY', label: '医疗质量与安全' },
  { value: 'PROCESS_REDESIGN', label: '流程再造' },
  { value: 'DIGITAL_AI', label: '数字化/AI' },
  { value: 'OTHER', label: '其他' }
]

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增评委')
const isEdit = ref(false)
const currentId = ref(null)
const formRef = ref(null)

const reviewers = ref([])

// 筛选栏机构远程搜索
const filterInstOptions = ref([])
const filterInstLoading = ref(false)

// 表单机构远程搜索
const formInstOptions = ref([])
const formInstLoading = ref(false)

const filters = reactive({
  institutionId: null,
  expertBackground: ''
})

const form = reactive({
  phone: '',
  name: '',
  title: '',
  institutionId: null,
  expertBackground: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在2-50个字符', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入职称', trigger: 'blur' }
  ],
  institutionId: [
    { required: true, message: '请选择所属机构', trigger: 'change' }
  ]
}

// 筛选栏机构远程搜索（输入关键词后才查询）
const searchFilterInst = async (query) => {
  if (!query || query.trim().length < 1) {
    filterInstOptions.value = []
    return
  }
  filterInstLoading.value = true
  try {
    const res = await autocomplete(query.trim())
    if (res.success) filterInstOptions.value = res.data || []
  } catch (error) {
    console.error('搜索机构失败:', error)
  } finally {
    filterInstLoading.value = false
  }
}

// 表单机构远程搜索
const searchFormInst = async (query) => {
  if (!query || query.trim().length < 1) {
    formInstOptions.value = []
    return
  }
  formInstLoading.value = true
  try {
    const res = await autocomplete(query.trim())
    if (res.success) formInstOptions.value = res.data || []
  } catch (error) {
    console.error('搜索机构失败:', error)
  } finally {
    formInstLoading.value = false
  }
}

// 加载评委列表
const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.institutionId) params.institutionId = filters.institutionId
    if (filters.expertBackground) params.expertBackground = filters.expertBackground

    const res = await getReviewers(params)
    if (res.success) {
      // 处理返回数据，可能是数组或者包含content的对象
      if (Array.isArray(res.data)) {
        reviewers.value = res.data
      } else if (res.data && Array.isArray(res.data.content)) {
        reviewers.value = res.data.content
      } else {
        reviewers.value = []
      }
      ElMessage.success('加载成功')
    }
  } catch (error) {
    console.error('加载评委列表失败:', error)
    ElMessage.error('加载失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 重置筛选条件
const resetFilters = () => {
  filters.institutionId = null
  filters.expertBackground = ''
  loadData()
}

// 新增评委
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增评委'
  dialogVisible.value = true
}

// 编辑评委
const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.id
  dialogTitle.value = '编辑评委'

  form.phone = row.phone
  form.name = row.name
  form.title = row.title
  form.institutionId = row.institutionId
  form.expertBackground = row.expertBackground || ''

  // 预填当前机构到选项，保证已选值能正确显示
  if (row.institutionId && row.institutionName) {
    formInstOptions.value = [{ id: row.institutionId, name: row.institutionName }]
  }

  dialogVisible.value = true
}

// 删除评委
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除评委 "${row.name}" 吗？删除后将无法恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await deleteReviewer(row.id)
    if (res.success) {
      ElMessage.success('删除成功')
      loadData()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除评委失败:', error)
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    const data = {
      phone: form.phone,
      name: form.name,
      title: form.title,
      institutionId: form.institutionId,
      expertBackground: form.expertBackground || null
    }
    
    let res
    if (isEdit.value) {
      res = await updateReviewer(currentId.value, data)
    } else {
      res = await createReviewer(data)
    }
    
    if (res.success) {
      ElMessage.success(isEdit.value ? '更新成功' : '新增成功')
      dialogVisible.value = false
      loadData()
    }
  } catch (error) {
    if (error !== false) {
      console.error('提交表单失败:', error)
      ElMessage.error('操作失败: ' + (error.message || '未知错误'))
    }
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  form.phone = ''
  form.name = ''
  form.title = ''
  form.institutionId = null
  form.expertBackground = ''
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// ── 详情抽屉 ─────────────────────────────────────────────────────────
const drawerVisible = ref(false)
const drawerTab = ref('basic')
const drawerTitle = ref('')
const drawerRow = ref({})

// 扩展档案状态
const profileLoading = ref(false)
const profileSaving = ref(false)
const profileFormRef = ref(null)
const profileForm = reactive({
  gender: 'UNKNOWN',
  position: '',
  idNumber: '',
  idNumberMasked: '',
  idCardFrontUrl: '',
  idCardBackUrl: '',
  bankName: '',
  bankCardNo: '',
  bankCardNoMasked: '',
  backgrounds: [],
  tools: [],
  topics: []
})
const profileRules = {
  idNumber: [
    {
      validator: (rule, value, callback) => {
        if (value && !/^\d{17}[\dXx]$/.test(value)) callback(new Error('身份证号格式不正确'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

function safeJsonParse(str) {
  if (!str) return []
  try { return JSON.parse(str) } catch { return [] }
}
function maskIdNumber(v) {
  if (!v || v.length < 10) return ''
  return v.slice(0, 6) + '********' + v.slice(-4)
}
function maskBankCard(v) {
  if (!v || v.length < 8) return ''
  return v.slice(0, 4) + ' **** **** ' + v.slice(-4)
}
function profileAutoMaskId() {
  profileForm.idNumberMasked = maskIdNumber(profileForm.idNumber)
}
function profileAutoMaskBank() {
  profileForm.bankCardNoMasked = maskBankCard(profileForm.bankCardNo)
}

function apiToProfileForm(data) {
  profileForm.gender = data.gender || 'UNKNOWN'
  profileForm.position = data.position || ''
  profileForm.idNumber = data.idNumber || ''
  profileForm.idNumberMasked = data.idNumberMasked || maskIdNumber(data.idNumber || '')
  profileForm.idCardFrontUrl = data.idCardFrontUrl || ''
  profileForm.idCardBackUrl = data.idCardBackUrl || ''
  profileForm.bankName = data.bankName || ''
  profileForm.bankCardNo = data.bankCardNo || ''
  profileForm.bankCardNoMasked = data.bankCardNoMasked || maskBankCard(data.bankCardNo || '')
  profileForm.backgrounds = safeJsonParse(data.backgroundsJson)
  profileForm.tools = safeJsonParse(data.toolsJson)
  profileForm.topics = safeJsonParse(data.topicsJson)
}

function resetProfileForm() {
  profileForm.gender = 'UNKNOWN'
  profileForm.position = ''
  profileForm.idNumber = ''
  profileForm.idNumberMasked = ''
  profileForm.idCardFrontUrl = ''
  profileForm.idCardBackUrl = ''
  profileForm.bankName = ''
  profileForm.bankCardNo = ''
  profileForm.bankCardNoMasked = ''
  profileForm.backgrounds = []
  profileForm.tools = []
  profileForm.topics = []
}

async function loadProfile(id) {
  profileLoading.value = true
  resetProfileForm()
  try {
    const res = await getReviewerProfile(id)
    if (res.success && res.data) apiToProfileForm(res.data)
  } catch (e) {
    console.warn('获取扩展档案失败:', e)
  } finally {
    profileLoading.value = false
  }
}

async function saveProfile() {
  try {
    await profileFormRef.value.validate()
    profileSaving.value = true
    const payload = {
      gender: profileForm.gender,
      position: profileForm.position || null,
      idNumber: profileForm.idNumber || null,
      idNumberMasked: maskIdNumber(profileForm.idNumber),
      idCardFrontUrl: profileForm.idCardFrontUrl || null,
      idCardBackUrl: profileForm.idCardBackUrl || null,
      bankName: profileForm.bankName || null,
      bankCardNo: profileForm.bankCardNo || null,
      bankCardNoMasked: maskBankCard(profileForm.bankCardNo),
      backgroundsJson: JSON.stringify(profileForm.backgrounds),
      toolsJson: JSON.stringify(profileForm.tools),
      topicsJson: JSON.stringify(profileForm.topics)
    }
    const res = await updateReviewerProfile(drawerRow.value.id, payload)
    if (res.success) {
      ElMessage.success('扩展档案已保存')
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (e) {
    if (e !== false) {
      ElMessage.error(e?.response?.data?.message || e?.message || '保存失败')
    }
  } finally {
    profileSaving.value = false
  }
}

// ── 机构变更 Tab ──────────────────────────────────────────────────
const showInstChangeForm = ref(false)
const instChanging = ref(false)
const instChangeSearching = ref(false)
const instChangeOptions = ref([])
const instHistoryLoading = ref(false)
const instHistory = ref([])
const instChangeFormRef = ref(null)
const instChangeForm = reactive({ newInstitutionId: null, reason: '' })

async function searchInstForChange(keyword) {
  if (!keyword) return
  instChangeSearching.value = true
  try {
    const res = await searchInstitutions({ keyword, page: 0, size: 20 })
    instChangeOptions.value = res.success ? (res.data.content || []) : []
  } catch { instChangeOptions.value = [] }
  finally { instChangeSearching.value = false }
}

async function loadInstHistory(id) {
  instHistoryLoading.value = true
  instHistory.value = []
  try {
    const res = await adminGetReviewerInstitutionHistory(id)
    instHistory.value = res.success ? (res.data || []) : []
  } catch { instHistory.value = [] }
  finally { instHistoryLoading.value = false }
}

async function submitInstChange() {
  if (!instChangeForm.newInstitutionId) {
    ElMessage.warning('请选择新机构')
    return
  }
  instChanging.value = true
  try {
    const res = await adminChangeReviewerInstitution(drawerRow.value.id, {
      newInstitutionId: instChangeForm.newInstitutionId,
      reason: instChangeForm.reason || undefined
    })
    if (res.success) {
      ElMessage.success('机构已变更')
      showInstChangeForm.value = false
      instChangeForm.newInstitutionId = null
      instChangeForm.reason = ''
      loadInstHistory(drawerRow.value.id)
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  } finally {
    instChanging.value = false
  }
}

function openDetail(row) {
  drawerRow.value = row
  drawerTitle.value = `评委详情 — ${row.name}`
  drawerTab.value = 'basic'
  drawerVisible.value = true
}

// 切换 Tab 时按需加载
watch(drawerTab, (tab) => {
  const id = drawerRow.value.id
  if (!id) return
  if (tab === 'profile') loadProfile(id)
  if (tab === 'institution') loadInstHistory(id)
})

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.reviewers-container {
  padding: 20px;
  
  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;
  }
  
  :deep(.el-card__body) {
    padding: 20px;
  }
}
</style>
