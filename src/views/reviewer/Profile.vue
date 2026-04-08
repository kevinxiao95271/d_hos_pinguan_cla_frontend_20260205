<template>
  <div class="reviewer-profile-page">
    <el-card v-loading="loading">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600; font-size: 16px">我的档案</span>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="140px">

        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>

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

        <!-- 证件信息 -->
        <el-divider content-position="left">证件信息</el-divider>

        <el-form-item label="身份证号" prop="idNumber">
          <el-input
            v-model="form.idNumber"
            placeholder="请输入身份证号"
            maxlength="18"
            style="width: 320px"
            @input="autoMaskId"
          />
          <span v-if="form.idNumberMasked" style="margin-left: 12px; color: #909399; font-size: 13px">
            脱敏：{{ form.idNumberMasked }}
          </span>
        </el-form-item>

        <el-form-item label="身份证正面">
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

        <el-form-item label="身份证反面">
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
            @input="autoMaskBank"
          />
          <span v-if="form.bankCardNoMasked" style="margin-left: 12px; color: #909399; font-size: 13px">
            脱敏：{{ form.bankCardNoMasked }}
          </span>
        </el-form-item>

        <!-- 专业背景 -->
        <el-divider content-position="left">专业背景与能力</el-divider>

        <el-form-item label="专业背景">
          <el-checkbox-group v-model="form.backgrounds">
            <el-checkbox v-for="item in BACKGROUND_OPTIONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="擅长工具">
          <el-checkbox-group v-model="form.tools">
            <el-checkbox v-for="item in TOOL_OPTIONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="擅长主题">
          <el-checkbox-group v-model="form.topics">
            <el-checkbox v-for="item in TOPIC_OPTIONS" :key="item.value" :value="item.value">
              {{ item.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getMyProfile, updateMyProfile, uploadMyIdCard, getMyIdCardStream } from '@/api/reviewerProfile'

// ── 枚举 ─────────────────────────────────────────────────────────────
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

// ── 状态 ─────────────────────────────────────────────────────────────
const loading = ref(false)
const saving = ref(false)
const formRef = ref(null)

// 身份证图片
const idCardFrontBlobUrl = ref('')
const idCardBackBlobUrl = ref('')
const uploadingFront = ref(false)
const uploadingBack = ref(false)
const frontFileInput = ref(null)
const backFileInput = ref(null)

const form = reactive({
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

const rules = {
  idNumber: [
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
  ]
}

// ── 脱敏辅助 ─────────────────────────────────────────────────────────
function maskIdNumber(v) {
  if (!v || v.length < 10) return ''
  return v.slice(0, 6) + '********' + v.slice(-4)
}

function maskBankCard(v) {
  if (!v || v.length < 8) return ''
  return v.slice(0, 4) + ' **** **** ' + v.slice(-4)
}

function autoMaskId() {
  form.idNumberMasked = maskIdNumber(form.idNumber)
}

function autoMaskBank() {
  form.bankCardNoMasked = maskBankCard(form.bankCardNo)
}

// ── API 与 Form 转换 ──────────────────────────────────────────────────
function apiToForm(data) {
  if (!data) return
  form.gender = data.gender || 'UNKNOWN'
  form.position = data.position || ''
  form.idNumber = data.idNumber || ''
  form.idNumberMasked = data.idNumberMasked || maskIdNumber(data.idNumber || '')
  form.idCardFrontUrl = data.idCardFrontUrl || ''
  form.idCardBackUrl = data.idCardBackUrl || ''
  form.bankName = data.bankName || ''
  form.bankCardNo = data.bankCardNo || ''
  form.bankCardNoMasked = data.bankCardNoMasked || maskBankCard(data.bankCardNo || '')
  form.backgrounds = safeJsonParse(data.backgroundsJson)
  form.tools = safeJsonParse(data.toolsJson)
  form.topics = safeJsonParse(data.topicsJson)
}

function formToApi() {
  return {
    gender: form.gender,
    position: form.position || null,
    idNumber: form.idNumber || null,
    idNumberMasked: maskIdNumber(form.idNumber),
    idCardFrontUrl: form.idCardFrontUrl || null,
    idCardBackUrl: form.idCardBackUrl || null,
    bankName: form.bankName || null,
    bankCardNo: form.bankCardNo || null,
    bankCardNoMasked: maskBankCard(form.bankCardNo),
    backgroundsJson: JSON.stringify(form.backgrounds),
    toolsJson: JSON.stringify(form.tools),
    topicsJson: JSON.stringify(form.topics)
  }
}

function safeJsonParse(str) {
  if (!str) return []
  try { return JSON.parse(str) } catch { return [] }
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
      apiToForm(res.data)
      // 有 object key 则加载图片流
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
    saving.value = true
    const res = await updateMyProfile(formToApi())
    if (res.success) {
      ElMessage.success('档案已保存')
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
</script>

<style scoped lang="scss">
.reviewer-profile-page {
  padding: 20px;

  :deep(.el-checkbox) {
    margin-right: 12px;
    margin-bottom: 6px;
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
