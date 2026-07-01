<template>
  <div class="reviewer-profile-page">
    <el-card v-loading="loading">
      <template #header>
        <span style="font-weight: 600; font-size: 16px">专家信息</span>
      </template>

      <el-alert
        v-if="!loading && profileLoaded && !profileFilled"
        title="您尚未填写扩展信息，请完善下方表单并保存。"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />

      <!-- 只读账号信息（来自 user_accounts） -->
      <el-descriptions v-if="readonlyInfo.name" :column="2" border size="small" style="margin-bottom: 20px">
        <el-descriptions-item label="姓名">{{ readonlyInfo.name }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ readonlyInfo.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="所属单位" :span="2">{{ readonlyInfo.institutionName || userStore.institutionName || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="160px">

        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>

        <el-form-item label="职称" prop="title">
          <el-radio-group v-model="form.title">
            <el-radio-button v-for="t in TITLE_OPTIONS" :key="t" :value="t">{{ t }}</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio value="MALE">男</el-radio>
            <el-radio value="FEMALE">女</el-radio>
            <el-radio value="UNKNOWN">保密</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="职务" prop="position">
          <el-input v-model="form.position" placeholder="请输入职务" maxlength="100" style="width: 320px" />
        </el-form-item>

        <el-form-item label="科室" prop="department">
          <el-input v-model="form.department" placeholder="请输入科室" maxlength="100" style="width: 320px" />
        </el-form-item>

        <!-- 所属机构 -->
        <el-divider content-position="left">所属机构</el-divider>

        <el-form-item label="所属单位">
          <span style="margin-right: 16px">{{ userStore.institutionName || '未知机构' }}</span>
          <el-button size="small" @click="showInstitutionDialog = true">变更机构</el-button>
        </el-form-item>

        <!-- 证件信息 -->
        <el-divider content-position="left">证件信息</el-divider>

        <el-form-item label="身份证号" prop="idNumber">
          <el-input
            v-model="form.idNumber"
            placeholder="请输入身份证号"
            maxlength="18"
            style="width: 320px"
          />
          <span v-if="displayIdNumberMasked" style="margin-left: 12px; color: #909399; font-size: 13px">
            脱敏：{{ displayIdNumberMasked }}
          </span>
        </el-form-item>

        <el-form-item label="身份证正面" required>
          <div style="display: flex; align-items: center; gap: 16px">
            <div class="id-card-preview" @click="triggerIdCardInput('FRONT')">
              <img v-if="idCardFrontBlobUrl" :src="idCardFrontBlobUrl" />
              <div v-else-if="form.idCardFrontUrl" class="id-card-placeholder">图片加载中…</div>
              <div v-else class="id-card-placeholder">
                <el-icon :size="24"><Plus /></el-icon>
                <span>上传正面</span>
              </div>
              <div v-if="uploadingFront" class="id-card-uploading">上传中…</div>
            </div>
            <div style="font-size: 12px; color: #909399; line-height: 1.8">
              <div>点击图片区域选择文件上传</div>
              <div>支持 jpg / png，建议小于 5MB</div>
              <el-tag v-if="form.idCardFrontUrl" type="success" size="small" style="margin-top:4px">已上传</el-tag>
            </div>
            <input
              ref="frontFileInput"
              type="file"
              accept="image/*"
              style="display:none"
              @change="(e) => handleIdCardUpload('FRONT', e)"
            />
          </div>
        </el-form-item>

        <el-form-item label="身份证反面" required>
          <div style="display: flex; align-items: center; gap: 16px">
            <div class="id-card-preview" @click="triggerIdCardInput('BACK')">
              <img v-if="idCardBackBlobUrl" :src="idCardBackBlobUrl" />
              <div v-else-if="form.idCardBackUrl" class="id-card-placeholder">图片加载中…</div>
              <div v-else class="id-card-placeholder">
                <el-icon :size="24"><Plus /></el-icon>
                <span>上传反面</span>
              </div>
              <div v-if="uploadingBack" class="id-card-uploading">上传中…</div>
            </div>
            <div style="font-size: 12px; color: #909399; line-height: 1.8">
              <div>点击图片区域选择文件上传</div>
              <div>支持 jpg / png，建议小于 5MB</div>
              <el-tag v-if="form.idCardBackUrl" type="success" size="small" style="margin-top:4px">已上传</el-tag>
            </div>
            <input
              ref="backFileInput"
              type="file"
              accept="image/*"
              style="display:none"
              @change="(e) => handleIdCardUpload('BACK', e)"
            />
          </div>
        </el-form-item>

        <!-- 银行卡信息 -->
        <el-divider content-position="left">银行卡信息</el-divider>

        <el-form-item label="开户银行" prop="bankName">
          <el-input v-model="form.bankName" placeholder="请输入开户银行" maxlength="100" style="width: 320px" />
        </el-form-item>

        <el-form-item label="银行卡号" prop="bankCardNo">
          <el-input
            v-model="form.bankCardNo"
            placeholder="请输入银行卡号"
            maxlength="25"
            style="width: 320px"
          />
          <span v-if="displayBankCardMasked" style="margin-left: 12px; color: #909399; font-size: 13px">
            脱敏：{{ displayBankCardMasked }}
          </span>
        </el-form-item>

        <!-- 专业背景 -->
        <el-divider content-position="left">专业背景与能力</el-divider>

        <el-form-item label="专业背景（可多选）" prop="backgrounds" required>
          <div class="checkbox-group-wrap">
            <el-checkbox-group v-model="form.backgrounds" class="checkbox-group-grid">
              <el-checkbox v-for="item in BACKGROUND_OPTIONS" :key="item.value" :value="item.value">{{ item.label }}</el-checkbox>
            </el-checkbox-group>
            <el-input v-if="form.backgrounds.includes('OTHER')" v-model="form.backgroundsOther" placeholder="请填写其他专业背景" maxlength="255" style="width: 400px; margin-top: 8px" />
          </div>
        </el-form-item>

        <el-form-item label="熟悉的品管工具（可多选）" prop="tools" required>
          <div class="checkbox-group-wrap">
            <el-checkbox-group v-model="form.tools" class="checkbox-group-grid">
              <el-checkbox v-for="item in TOOL_OPTIONS" :key="item.value" :value="item.value">{{ item.label }}</el-checkbox>
            </el-checkbox-group>
            <el-input v-if="form.tools.includes('OTHER')" v-model="form.toolsOther" placeholder="请填写其他工具" maxlength="255" style="width: 400px; margin-top: 8px" />
          </div>
        </el-form-item>

        <el-form-item label="擅长评审主题（可多选）" prop="topics" required>
          <div class="checkbox-group-wrap">
            <el-checkbox-group v-model="form.topics" class="checkbox-group-grid">
              <el-checkbox v-for="item in TOPIC_OPTIONS" :key="item.value" :value="item.value">{{ item.label }}</el-checkbox>
            </el-checkbox-group>
            <el-input v-if="form.topics.includes('OTHER')" v-model="form.topicsOther" placeholder="请填写其他主题" maxlength="255" style="width: 400px; margin-top: 8px" />
          </div>
        </el-form-item>

        <el-form-item label="品管相关经验（可多选）" prop="experience" required>
          <div class="checkbox-group-wrap">
            <el-checkbox-group v-model="form.experience" class="checkbox-group-grid">
              <el-checkbox v-for="item in EXPERIENCE_OPTIONS" :key="item.value" :value="item.value">{{ item.label }}</el-checkbox>
            </el-checkbox-group>
          </div>
        </el-form-item>

        <!-- 账号安全 -->
        <el-divider content-position="left">账号安全</el-divider>

        <el-form-item label="登录密码">
          <el-button size="small" @click="showPasswordDialog = true">修改密码</el-button>
        </el-form-item>

        <!-- 底部保存按钮 -->
        <div style="text-align: center; margin-top: 32px; padding-bottom: 8px;">
          <el-button type="primary" size="large" :loading="saving" @click="handleSave" style="min-width: 140px;">
            保存专家信息
          </el-button>
        </div>

      </el-form>
    </el-card>
  </div>

  <!-- 修改密码弹窗 -->
  <el-dialog v-model="showPasswordDialog" title="修改密码" width="420px" :close-on-click-modal="false">
    <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="100px">
      <el-form-item label="当前密码" prop="oldPassword">
        <el-input v-model="pwdForm.oldPassword" type="password" show-password placeholder="请输入当前密码" />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input v-model="pwdForm.newPassword" type="password" show-password placeholder="6-20位密码" />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirmPassword">
        <el-input v-model="pwdForm.confirmPassword" type="password" show-password placeholder="再次输入新密码" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showPasswordDialog = false">取消</el-button>
      <el-button type="primary" :loading="changingPwd" @click="handleChangePassword">确认修改</el-button>
    </template>
  </el-dialog>

  <!-- 变更机构弹窗 -->
  <el-dialog
    v-model="showInstitutionDialog"
    title="变更所属单位"
    width="780px"
    :close-on-click-modal="false"
    @closed="selectedNewInstitution = null; instForm.reason = ''"
  >
    <div style="margin-bottom: 12px; color: #606266; font-size: 13px">
      当前机构：<strong>{{ userStore.institutionName || '未知机构' }}</strong>
    </div>

    <InstitutionSelector @select="selectedNewInstitution = $event" />

    <el-form ref="instFormRef" :model="instForm" label-width="80px" style="margin-top: 16px">
      <el-form-item label="变更原因">
        <el-input
          v-model="instForm.reason"
          type="textarea"
          :rows="2"
          placeholder="请输入变更原因（选填）"
          maxlength="500"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="showInstitutionDialog = false">取消</el-button>
      <el-button
        type="primary"
        :loading="changingInst"
        :disabled="!selectedNewInstitution"
        @click="handleChangeInstitution"
      >
        提交申请
      </el-button>
    </template>
  </el-dialog>

</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { getMyProfile, updateMyProfile, uploadMyIdCard, getMyIdCardStream, changeMyInstitution } from '@/api/reviewerProfile'
import { selfChangePassword } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import InstitutionSelector from '@/components/InstitutionSelector.vue'
import {
  hasReviewerProfileFilled,
  mapReviewerProfileToForm,
  mapFormToReviewerProfilePayload,
  maskIdNumber,
  maskBankCard,
} from '@/utils/reviewerProfile'

const router = useRouter()
const userStore = useUserStore()

// ── 枚举 ─────────────────────────────────────────────────────────────
const TITLE_OPTIONS = ['初级', '中级', '副高', '正高']

const BACKGROUND_OPTIONS = [
  { value: 'MANAGEMENT',    label: '管理' },
  { value: 'MEDICAL',       label: '医疗' },
  { value: 'NURSING',       label: '护理' },
  { value: 'QUALITY_MGMT',  label: '质量管理' },
  { value: 'PHARMACY',      label: '药学' },
  { value: 'MEDICAL_TECH',  label: '医技' },
  { value: 'MEDICAL_RECORDS', label: '病案管理' },
  { value: 'INFECTION_CTRL',  label: '院感' },
  { value: 'OTHER',         label: '其他' }
]

const TOOL_OPTIONS = [
  { value: 'PDCA',                 label: 'PDCA' },
  { value: 'FOCUS_PDCA',           label: 'FOCUS-PDCA' },
  { value: 'QFD',                  label: 'QFD' },
  { value: 'QCC_PROBLEM',          label: '品管圈（问题解决）' },
  { value: 'QCC_TOPIC',            label: '品管圈（课题达成）' },
  { value: 'CASE_IMPROVEMENT',     label: '专案改善' },
  { value: 'RCA',                  label: '根本原因分析' },
  { value: 'FMEA',                 label: '失效模式与效应分析' },
  { value: 'BENCHMARKING',         label: '标杆学习' },
  { value: 'SIX_S',                label: '6S 管理' },
  { value: 'LEAN',                 label: '精益管理（Lean）' },
  { value: 'SIX_SIGMA',            label: '六西格玛管理' },
  { value: 'EBM',                  label: '循证医学' },
  { value: 'BSC',                  label: '平衡计分卡' },
  { value: 'QRC',                  label: '品质报告卡' },
  { value: 'TQM',                  label: 'TQM' },
  { value: 'PROCESS_REENGINEERING', label: '流程改造' },
  { value: 'OTHER',                label: '其他' }
]

const TOPIC_OPTIONS = [
  { value: 'PATIENT_CARE',          label: '病人照护' },
  { value: 'MEDICAL_RECORDS',       label: '病历质量' },
  { value: 'TIME_EFFICIENCY',       label: '时间效率' },
  { value: 'COST_EFFECTIVENESS',    label: '成本效益' },
  { value: 'SAFETY_ENV',            label: '安全环境' },
  { value: 'SATISFACTION',          label: '满意度' },
  { value: 'EDUCATION',             label: '教育训练' },
  { value: 'MEDICAL_INFO',          label: '医疗信息' },
  { value: 'MEDICAL_QUALITY_SAFETY', label: '医疗质量与安全' },
  { value: 'PROCESS_REENGINEERING', label: '流程改造' },
  { value: 'DIGITAL_AI',            label: '数字化与人工智能' },
  { value: 'OTHER',                 label: '其他' }
]

const EXPERIENCE_OPTIONS = [
  { value: 'PROJECT_LEADER',   label: '担任过品管项目负责人' },
  { value: 'COACHED_PROJECT',  label: '辅导过品管参赛项目' },
  { value: 'UNIT_JUDGE',       label: '单位内品管大赛评委' },
  { value: 'CITY_JUDGE',       label: '市级/区级/县级品管大赛评委' },
  { value: 'PROVINCE_JUDGE',   label: '省级及以上品管大赛评委' }
]

// ── 状态 ─────────────────────────────────────────────────────────────
const loading = ref(false)
const saving = ref(false)
const profileLoaded = ref(false)
const profileFilled = ref(false)
const formRef = ref(null)
const readonlyInfo = reactive({ userId: null, name: '', phone: '', institutionName: '' })
const savedIdNumberMasked = ref('')
const savedBankCardMasked = ref('')

const displayIdNumberMasked = computed(() => {
  if (form.idNumber) return maskIdNumber(form.idNumber)
  return savedIdNumberMasked.value
})
const displayBankCardMasked = computed(() => {
  if (form.bankCardNo) return maskBankCard(form.bankCardNo)
  return savedBankCardMasked.value
})

// 身份证图片
const idCardFrontBlobUrl = ref('')
const idCardBackBlobUrl = ref('')
const uploadingFront = ref(false)
const uploadingBack = ref(false)
const frontFileInput = ref(null)
const backFileInput = ref(null)

const form = reactive({
  title: '',
  gender: '',
  position: '',
  department: '',
  idNumber: '',
  idCardFrontUrl: '',
  idCardBackUrl: '',
  bankName: '',
  bankCardNo: '',
  backgrounds: [],
  backgroundsOther: '',
  tools: [],
  toolsOther: '',
  topics: [],
  topicsOther: '',
  experience: []
})

// 修改密码
const showPasswordDialog = ref(false)
const changingPwd = ref(false)
const pwdFormRef = ref(null)
const pwdForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const pwdRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== pwdForm.newPassword) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

// 变更机构
const showInstitutionDialog = ref(false)
const changingInst = ref(false)
const instFormRef = ref(null)
const instForm = reactive({ reason: '' })
const selectedNewInstitution = ref(null)


const multiSelectRequired = (label) => ({
  validator: (rule, value, callback) => {
    if (!value || value.length === 0) callback(new Error(`${label}为必填项，请至少选择一项`))
    else callback()
  },
  trigger: 'change'
})

const rules = {
  title: [{ required: true, message: '职称为必填项', trigger: 'change' }],
  gender: [{ required: true, message: '性别为必填项', trigger: 'change' }],
  position: [{ required: true, message: '职务为必填项', trigger: 'blur' }],
  idNumber: [
    { required: true, message: '身份证号为必填项', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value && !/^\d{17}[\dXx]$/.test(value)) {
          callback(new Error('身份证号格式不正确'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  bankName: [{ required: true, message: '开户银行为必填项', trigger: 'blur' }],
  bankCardNo: [{ required: true, message: '银行卡号为必填项', trigger: 'blur' }],
  backgrounds: [multiSelectRequired('专业背景')],
  tools: [multiSelectRequired('擅长工具')],
  topics: [multiSelectRequired('擅长主题')],
  experience: [multiSelectRequired('品管相关经验')]
}

// ── API 与 Form 转换 ──────────────────────────────────────────────────
function applyProfileData(data) {
  if (!data) return
  readonlyInfo.userId = data.userId ?? null
  readonlyInfo.name = data.name ?? ''
  readonlyInfo.phone = data.phone ?? ''
  readonlyInfo.institutionName = data.institutionName ?? ''
  profileFilled.value = hasReviewerProfileFilled(data)

  const mapped = mapReviewerProfileToForm(data)
  if (!mapped) return
  Object.assign(form, mapped)
  savedIdNumberMasked.value = mapped.idNumberMasked
  savedBankCardMasked.value = mapped.bankCardNoMasked
  // 已有明文时不重复展示输入框内容（脱敏区展示 idNumberMasked）
  if (!data.idNumber && data.idNumberMasked) form.idNumber = ''
  if (!data.bankCardNo && data.bankCardNoMasked) form.bankCardNo = ''
}

// ── 身份证图片 ────────────────────────────────────────────────────────
function triggerIdCardInput(side) {
  if (side === 'FRONT') frontFileInput.value?.click()
  else backFileInput.value?.click()
}

async function loadIdCardImage(side) {
  try {
    const blob = await getMyIdCardStream(side)
    const url = URL.createObjectURL(new Blob([blob], { type: 'image/jpeg' }))
    if (side === 'FRONT') {
      if (idCardFrontBlobUrl.value) URL.revokeObjectURL(idCardFrontBlobUrl.value)
      idCardFrontBlobUrl.value = url
    } else {
      if (idCardBackBlobUrl.value) URL.revokeObjectURL(idCardBackBlobUrl.value)
      idCardBackBlobUrl.value = url
    }
  } catch (e) {
    // 404 表示未上传，忽略
  }
}

async function handleIdCardUpload(side, event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    return
  }
  if (side === 'FRONT') uploadingFront.value = true
  else uploadingBack.value = true
  try {
    const res = await uploadMyIdCard(side, file)
    if (res.success && res.data) {
      // 后端返回更新后的档案 DTO，回填 URL（object key）
      if (side === 'FRONT') {
        form.idCardFrontUrl = res.data.idCardFrontUrl || ''
      } else {
        form.idCardBackUrl = res.data.idCardBackUrl || ''
      }
      // 重新加载展示图
      await loadIdCardImage(side)
      ElMessage.success('上传成功')
    } else {
      ElMessage.error(res.message || '上传失败')
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || '上传失败')
  } finally {
    if (side === 'FRONT') uploadingFront.value = false
    else uploadingBack.value = false
    // 清空 input 以允许再次选同一文件
    event.target.value = ''
  }
}

// ── 生命周期 ──────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  try {
    const res = await getMyProfile()
    if (res.success && res.data) {
      applyProfileData(res.data)
      profileLoaded.value = true
      if (res.data.idCardFrontUrl) loadIdCardImage('FRONT')
      if (res.data.idCardBackUrl) loadIdCardImage('BACK')
    }
  } catch (e) {
    console.warn('获取档案失败:', e)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (idCardFrontBlobUrl.value) URL.revokeObjectURL(idCardFrontBlobUrl.value)
  if (idCardBackBlobUrl.value) URL.revokeObjectURL(idCardBackBlobUrl.value)
})

async function handleSave() {
  try {
    await formRef.value.validate()
    // 身份证照片单独检查（非表单字段）
    const photoMissing = []
    if (!form.idCardFrontUrl) photoMissing.push('身份证正面照片')
    if (!form.idCardBackUrl) photoMissing.push('身份证反面照片')
    if (photoMissing.length > 0) {
      ElMessage.error(`以下必填项未完成：${photoMissing.join('、')}`)
      return
    }
    saving.value = true
    const res = await updateMyProfile(mapFormToReviewerProfilePayload(form))
    if (res.success) {
      ElMessage.success('档案已保存')
      if (res.data) applyProfileData(res.data)
      else {
        const reload = await getMyProfile()
        if (reload.success && reload.data) applyProfileData(reload.data)
      }
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (e) {
    if (e !== false) {
      const msg = e?.response?.data?.message || e?.message || '保存失败'
      ElMessage.error(msg)
    }
  } finally {
    saving.value = false
  }
}

async function handleChangePassword() {
  try {
    await pwdFormRef.value.validate()
    changingPwd.value = true
    const res = await selfChangePassword({
      oldPassword: pwdForm.oldPassword,
      newPassword: pwdForm.newPassword,
      confirmPassword: pwdForm.confirmPassword
    })
    if (res.success) {
      ElMessage.success('密码修改成功，请使用新密码重新登录')
      showPasswordDialog.value = false
      // 清除 token，强制重新登录
      userStore.logout()
      router.push('/login')
    } else {
      ElMessage.error(res.message || '修改失败')
      // 原密码错误时清空原密码框，方便重新填写
      if (res.message && res.message.includes('原密码')) {
        pwdForm.oldPassword = ''
      }
    }
  } catch (e) {
    if (e !== false) {
      ElMessage.error(e?.response?.data?.message || e?.message || '修改失败')
    }
  } finally {
    changingPwd.value = false
  }
}

async function handleChangeInstitution() {
  if (!selectedNewInstitution.value) {
    ElMessage.warning('请先选择新机构')
    return
  }
  changingInst.value = true
  try {
    const res = await changeMyInstitution({
      newInstitutionId: selectedNewInstitution.value.id,
      reason: instForm.reason || undefined
    })
    if (res.success) {
      ElMessage.success('机构变更申请已提交')
      showInstitutionDialog.value = false
      selectedNewInstitution.value = null
      instForm.reason = ''
    } else {
      ElMessage.error(res.message || '提交失败')
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || e?.message || '提交失败')
  } finally {
    changingInst.value = false
  }
}

</script>

<style scoped lang="scss">
.reviewer-profile-page {
  padding: 20px;

  // 一级分区标题加粗
  :deep(.el-divider__text) {
    font-weight: 700;
    font-size: 14px;
    color: #303133;
  }
}

.checkbox-group-wrap {
  background: #f9fafb;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 10px 14px 4px;
  width: 100%;
}

.checkbox-group-grid {
  display: flex !important;
  flex-wrap: wrap;
  gap: 4px 0;

  :deep(.el-checkbox) {
    margin-right: 18px;
    margin-bottom: 8px;
    min-width: 140px;
  }
}

.id-card-preview {
  position: relative;
  width: 200px;
  height: 125px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  background: #fafafa;
  transition: border-color .2s;

  &:hover {
    border-color: #409eff;
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
}

.id-card-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #c0c4cc;
  font-size: 12px;
}

.id-card-uploading {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, .45);
  color: #fff;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
