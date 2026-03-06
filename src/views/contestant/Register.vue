<template>
  <div class="register-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>赛事报名</span>
        </div>
      </template>
      
      <!-- 步骤条 -->
      <div class="steps-container">
        <el-steps :active="currentStep" align-center finish-status="success">
          <el-step title="报名表" />
          <el-step title="活动说明" />
          <el-step title="项目摘要" />
          <el-step title="提交资料" />
        </el-steps>
      </div>
      
      <!-- 步骤1: 报名表 -->
      <div v-show="currentStep === 0" class="step-content">
        <el-form
          ref="basicFormRef"
          :model="basicForm"
          :rules="basicRules"
          label-width="140px"
        >
          <el-divider content-position="left">机构基本信息</el-divider>
          
          <el-form-item label="医疗机构名称">
            <el-input v-model="institutionInfo.name" disabled />
          </el-form-item>
          
          <el-form-item label="机构编号">
            <el-input v-model="institutionInfo.code" disabled />
          </el-form-item>
          
          <el-form-item label="统一社会信用代码">
            <el-input v-model="institutionInfo.uscc" disabled />
          </el-form-item>
          
          <el-divider content-position="left">项目信息</el-divider>
          
          <el-form-item label="参赛项目名称" prop="projectName">
            <el-input
              v-model="basicForm.projectName"
              placeholder="请输入项目名称，不多于100字"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="竞赛组别" prop="groupType">
            <el-radio-group v-model="basicForm.groupType">
              <el-radio value="ADVANCED">进阶组</el-radio>
              <el-radio value="COMPREHENSIVE">综合组</el-radio>
              <el-tooltip
                :disabled="!isThirdLevel"
                content="基层组仅限二级及以下医疗机构报名，三级机构不可选"
                placement="top"
              >
                <el-radio value="BASIC" :disabled="isThirdLevel">基层组</el-radio>
              </el-tooltip>
            </el-radio-group>
          </el-form-item>
          
          <el-divider content-position="left">项目参与人员（不多于20人）</el-divider>
          
          <div class="members-section">
            <el-button
              type="primary"
              size="small"
              :disabled="participants.length >= 20"
              @click="addParticipant"
            >
              添加参与人员
            </el-button>
            
            <div class="members-list">
              <el-card
                v-for="(item, index) in participants"
                :key="index"
                class="member-card"
              >
                <el-form-item label="姓名" :prop="`participants.${index}.name`">
                  <el-input v-model="item.name" placeholder="请输入姓名" />
                </el-form-item>
                <el-form-item label="职称" :prop="`participants.${index}.title`">
                  <el-input v-model="item.title" placeholder="请输入职称" />
                </el-form-item>
                <el-form-item label="科室" :prop="`participants.${index}.department`">
                  <el-input v-model="item.department" placeholder="请输入科室" />
                </el-form-item>
                <el-button
                  type="danger"
                  size="small"
                  @click="removeParticipant(index)"
                >
                  删除
                </el-button>
              </el-card>
            </div>
          </div>
          
          <el-divider content-position="left">辅导员（不多于20人）</el-divider>
          
          <div class="members-section">
            <el-button
              type="primary"
              size="small"
              :disabled="mentors.length >= 20"
              @click="addMentor"
            >
              添加辅导员
            </el-button>
            
            <div class="members-list">
              <el-card
                v-for="(item, index) in mentors"
                :key="index"
                class="member-card"
              >
                <el-form-item label="姓名" :prop="`mentors.${index}.name`">
                  <el-input v-model="item.name" placeholder="请输入姓名" />
                </el-form-item>
                <el-form-item label="职称" :prop="`mentors.${index}.title`">
                  <el-input v-model="item.title" placeholder="请输入职称" />
                </el-form-item>
                <el-button
                  type="danger"
                  size="small"
                  @click="removeMentor(index)"
                >
                  删除
                </el-button>
              </el-card>
            </div>
          </div>
        </el-form>
      </div>
      
      <!-- 步骤2: 活动说明 -->
      <div v-show="currentStep === 1" class="step-content">
        <el-form
          ref="activityFormRef"
          :model="activityForm"
          :rules="activityRules"
          label-width="180px"
        >
          <el-form-item label="活动主题" prop="theme">
            <el-input v-model="activityForm.theme" placeholder="请输入活动主题" />
          </el-form-item>
          
          <el-form-item label="关键词" prop="keywords">
            <el-input
              v-model="activityForm.keywords"
              placeholder="请输入关键词，多个关键词用逗号分隔"
            />
          </el-form-item>
          
          <el-form-item label="主题类型" prop="subjectTypeCode">
            <el-radio-group v-model="activityForm.subjectTypeCode">
              <el-radio
                v-for="item in dictionaries.subjectTypes"
                :key="item.code"
                :label="item.code"
              >
                {{ item.label }}
              </el-radio>
            </el-radio-group>
            <el-input
              v-if="activityForm.subjectTypeCode === 'other'"
              v-model="activityForm.subjectTypeOther"
              placeholder="请说明"
              style="margin-top: 8px"
            />
          </el-form-item>
          
          <el-form-item label="运用手法" prop="methodCode">
            <el-radio-group v-model="activityForm.methodCode">
              <el-radio
                v-for="item in dictionaries.methods"
                :key="item.code"
                :label="item.code"
              >
                {{ item.label }}
              </el-radio>
            </el-radio-group>
            <el-input
              v-if="activityForm.methodCode === 'other'"
              v-model="activityForm.methodOther"
              placeholder="请说明"
              style="margin-top: 8px"
            />
          </el-form-item>
          
          <el-form-item label="改善就医感受" prop="experienceImproveCode">
            <el-checkbox-group v-model="activityForm.experienceImproveCodes">
              <el-checkbox
                v-for="item in dictionaries.experienceImproves"
                :key="item.code"
                :label="item.code"
              >
                {{ item.label }}
              </el-checkbox>
            </el-checkbox-group>
            <el-input
              v-if="activityForm.experienceImproveCodes.includes('other')"
              v-model="activityForm.experienceImproveOther"
              placeholder="请说明"
              style="margin-top: 8px"
            />
          </el-form-item>
          
          <el-form-item label="医疗质量安全相关主题" prop="qualityTopicCode">
            <el-radio-group v-model="activityForm.qualityTopicCode">
              <el-radio
                v-for="item in dictionaries.qualityTopics"
                :key="item.code"
                :label="item.code"
              >
                {{ item.label }}
              </el-radio>
            </el-radio-group>
            <el-input
              v-if="activityForm.qualityTopicCode === 'other'"
              v-model="activityForm.qualityTopicOther"
              placeholder="请说明"
              style="margin-top: 8px"
            />
          </el-form-item>
          
          <el-form-item label="平均工作年限" prop="avgWorkYears">
            <el-input-number
              v-model="activityForm.avgWorkYears"
              :min="0"
              :max="50"
            />
            <span style="margin-left: 8px">年</span>
          </el-form-item>
          
          <el-form-item label="平均年龄" prop="avgAge">
            <el-input-number
              v-model="activityForm.avgAge"
              :min="18"
              :max="100"
            />
            <span style="margin-left: 8px">岁</span>
          </el-form-item>
          
          <el-form-item label="跨部门" prop="crossDepartment">
            <el-radio-group v-model="activityForm.crossDepartment">
              <el-radio :value="true">是</el-radio>
              <el-radio :value="false">否</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 步骤3: 项目摘要 -->
      <div v-show="currentStep === 2" class="step-content">
        <el-form
          ref="summaryFormRef"
          :model="summaryForm"
          :rules="summaryRules"
          label-width="200px"
        >
          <el-form-item label="参赛活动主题">
            <span>{{ activityForm.theme || '-' }}</span>
          </el-form-item>
          
          <el-form-item label="1. 计划" prop="plan">
            <el-input
              v-model="summaryForm.plan"
              type="textarea"
              :rows="4"
              placeholder="请输入计划内容"
            />
          </el-form-item>
          
          <el-form-item label="2. 问题结构与对策措施探讨" prop="problem">
            <el-input
              v-model="summaryForm.problem"
              type="textarea"
              :rows="4"
              placeholder="请输入问题结构与对策措施探讨"
            />
          </el-form-item>
          
          <el-form-item label="3. 对策行动过程" prop="action">
            <el-input
              v-model="summaryForm.action"
              type="textarea"
              :rows="4"
              placeholder="请输入对策行动过程"
            />
          </el-form-item>
          
          <el-form-item label="4. 成果表现" prop="success">
            <el-input
              v-model="summaryForm.success"
              type="textarea"
              :rows="4"
              placeholder="请输入成果表现"
            />
          </el-form-item>
          
          <el-form-item label="5. 讨论总结" prop="discussion">
            <el-input
              v-model="summaryForm.discussion"
              type="textarea"
              :rows="4"
              placeholder="请输入讨论总结"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 步骤4: 提交资料 -->
      <div v-show="currentStep === 3" class="step-content">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 12px;"
        >
          <template #default>
            报名表要求Word文档形式，请单位盖章后另上传PDF扫描件一份。
          </template>
        </el-alert>
        <el-table :data="materialsList" border>
          <el-table-column prop="type" label="类型" width="200">
            <template #default="{ row }">
              {{ getMaterialTypeText(row.type) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.fileName ? 'success' : 'info'" size="small">
                {{ row.fileName ? '已上传' : '未上传' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="fileName" label="文件名称" />
          <el-table-column prop="uploadedAt" label="上传时间" width="160" />
          <el-table-column label="操作" width="260">
            <template #default="{ row }">
              <el-upload
                :action="`/api/registrations/${registrationId}/materials?type=${row.type}`"
                :headers="{ Authorization: `Bearer ${token}` }"
                :show-file-list="false"
                :on-success="(res) => handleUploadSuccess(res, row.type)"
                :before-upload="(file) => beforeUpload(file, row.maxSize)"
                :accept="row.accept"
              >
                <el-button type="primary" size="small">上传</el-button>
              </el-upload>
              <el-button
                v-if="row.hasTemplate"
                type="success"
                size="small"
                @click="downloadTemplate(row.type)"
              >
                下载模板
              </el-button>
              <el-button
                v-if="row.fileName"
                type="danger"
                size="small"
                @click="deleteMaterial(row.type)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 操作按钮 -->
      <div class="actions">
        <el-button v-if="currentStep > 0" @click="prevStep">
          上一步
        </el-button>
        <el-button v-if="currentStep < 3" type="primary" @click="nextStep">
          下一步
        </el-button>
        <el-button
          v-if="currentStep === 3"
          type="success"
          :loading="submitting"
          @click="submitRegistration"
        >
          提交报名
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import {
  createRegistration,
  updateRegistrationMembers,
  updateRegistrationActivity,
  updateRegistrationSummary,
  submitRegistration as submitRegistrationApi,
  getRegistrationCountByInstitution
} from '@/api/registration'
import { getInstitution } from '@/api/institution'
import { getDictionaryByType } from '@/api/dictionary'
import { getCompetitionTemplates, downloadCompetitionTemplate } from '@/api/competition'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const competitionId = ref(route.params.competitionId)
const registrationId = ref(null)
const currentStep = ref(0)
const submitting = ref(false)

const token = computed(() => userStore.token)

// 机构信息
const institutionInfo = reactive({
  name: '',
  code: '',
  uscc: '',
  level: ''
})

// 三级机构不可选基层组
const isThirdLevel = computed(() => institutionInfo.level?.startsWith('三级'))

watch(isThirdLevel, (val) => {
  if (val && basicForm.groupType === 'BASIC') {
    basicForm.groupType = 'COMPREHENSIVE'
  }
})

// 字典数据
const dictionaries = reactive({
  subjectTypes: [],
  methods: [],
  experienceImproves: [],
  qualityTopics: []
})

// 报名表
const basicFormRef = ref(null)
const basicForm = reactive({
  projectName: '',
  groupType: 'ADVANCED'
})
const basicRules = {
  projectName: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { max: 100, message: '项目名称不能超过100字', trigger: 'blur' }
  ],
  groupType: [
    { required: true, message: '请选择竞赛组别', trigger: 'change' }
  ]
}

// 参与人员
const participants = ref([])
const mentors = ref([])

// 活动说明
const activityFormRef = ref(null)
const activityForm = reactive({
  theme: '',
  keywords: '',
  subjectTypeCode: '',
  subjectTypeOther: '',
  methodCode: '',
  methodOther: '',
  experienceImproveCodes: [],
  experienceImproveOther: '',
  qualityTopicCode: '',
  qualityTopicOther: '',
  avgWorkYears: 0,
  avgAge: 0,
  crossDepartment: false
})
const activityRules = {
  theme: [{ required: true, message: '请输入活动主题', trigger: 'blur' }],
  keywords: [{ required: true, message: '请输入关键词', trigger: 'blur' }]
}

// 项目摘要
const summaryFormRef = ref(null)
const summaryForm = reactive({
  theme: '',
  plan: '',
  problem: '',
  action: '',
  success: '',
  discussion: ''
})
const summaryRules = {
  plan: [{ required: true, message: '请输入计划', trigger: 'blur' }],
  problem: [{ required: true, message: '请输入问题结构与对策措施探讨', trigger: 'blur' }],
  action: [{ required: true, message: '请输入对策行动过程', trigger: 'blur' }],
  success: [{ required: true, message: '请输入成果表现', trigger: 'blur' }],
  discussion: [{ required: true, message: '请输入讨论总结', trigger: 'blur' }]
}

// 提交资料
const materialsList = ref([
  { type: 'REGISTRATION_FORM_DOC', accept: '.doc,.docx', maxSize: 30,  fileName: '', uploadedAt: '', hasTemplate: true },
  { type: 'REGISTRATION_FORM_PDF', accept: '.pdf',       maxSize: 30,  fileName: '', uploadedAt: '', hasTemplate: false },
  { type: 'REPORT',                accept: '',           maxSize: 30,  fileName: '', uploadedAt: '', hasTemplate: true },
  { type: 'EVIDENCE',              accept: '',           maxSize: 100, fileName: '', uploadedAt: '', hasTemplate: false }
])

const getMaterialTypeText = (type) => {
  const map = {
    'REGISTRATION_FORM_DOC': '报名表 Word',
    'REGISTRATION_FORM_PDF': '报名表 PDF（盖章扫描件）',
    'REPORT':                '成果汇报书',
    'EVIDENCE':              '佐证材料（≤100MB，视频请打包成压缩包）'
  }
  return map[type] || type
}

// 加载机构信息
const loadInstitutionInfo = async () => {
  try {
    const res = await getInstitution(userStore.institutionId)
    if (res.success && res.data) {
      institutionInfo.name = res.data.name
      institutionInfo.code = res.data.code
      institutionInfo.uscc = res.data.uscc
      institutionInfo.level = res.data.level || ''
    }
  } catch (error) {
    console.error('加载机构信息失败:', error)
  }
}

// 加载字典数据
const loadDictionaries = async () => {
  try {
    const [subjectTypes, methods, experienceImproves, qualityTopics] = await Promise.all([
      getDictionaryByType('subject_type'),
      getDictionaryByType('method'),
      getDictionaryByType('experience_improve'),
      getDictionaryByType('quality_topic')
    ])
    
    dictionaries.subjectTypes = subjectTypes.data || []
    dictionaries.methods = methods.data || []
    dictionaries.experienceImproves = experienceImproves.data || []
    dictionaries.qualityTopics = qualityTopics.data || []
  } catch (error) {
    console.error('加载字典数据失败:', error)
  }
}

// 添加参与人员
const addParticipant = () => {
  if (participants.value.length >= 20) {
    ElMessage.warning('参与人员不能超过20人')
    return
  }
  participants.value.push({
    name: '',
    title: '',
    department: ''
  })
}

const removeParticipant = (index) => {
  participants.value.splice(index, 1)
}

// 添加辅导员
const addMentor = () => {
  if (mentors.value.length >= 20) {
    ElMessage.warning('辅导员不能超过20人')
    return
  }
  mentors.value.push({
    name: '',
    title: ''
  })
}

const removeMentor = (index) => {
  mentors.value.splice(index, 1)
}

// 上一步
const prevStep = () => {
  currentStep.value--
}

// 下一步
const nextStep = async () => {
  try {
    if (currentStep.value === 0) {
      await basicFormRef.value.validate()
      await saveBasicInfo()
    } else if (currentStep.value === 1) {
      await activityFormRef.value.validate()
      await saveActivityInfo()
    } else if (currentStep.value === 2) {
      await summaryFormRef.value.validate()
      await saveSummaryInfo()
    }
    
    currentStep.value++
  } catch (error) {
    console.error('验证失败:', error)
  }
}

// 保存基本信息
const saveBasicInfo = async () => {
  try {
    // 创建报名
    if (!registrationId.value) {
      const res = await createRegistration({
        competitionId: competitionId.value,
        institutionId: userStore.institutionId,
        applicantId: userStore.userId,
        projectName: basicForm.projectName,
        groupType: basicForm.groupType
      })
      
      if (res.success && res.data) {
        registrationId.value = res.data.id
      }
    }
    
    // 更新成员信息
    const items = [
      ...participants.value.map(p => ({ ...p, role: 'PARTICIPANT' })),
      ...mentors.value.map(m => ({ ...m, role: 'MENTOR', department: '' }))
    ]
    
    await updateRegistrationMembers(registrationId.value, { items })
    
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存基本信息失败:', error)
    throw error
  }
}

// 保存活动说明
const saveActivityInfo = async () => {
  try {
    await updateRegistrationActivity(registrationId.value, {
      ...activityForm,
      experienceImproveCode: activityForm.experienceImproveCodes[0] || null
    })
    
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存活动说明失败:', error)
    throw error
  }
}

// 保存项目摘要
const saveSummaryInfo = async () => {
  try {
    await updateRegistrationSummary(registrationId.value, {
      ...summaryForm,
      theme: activityForm.theme
    })
    
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存项目摘要失败:', error)
    throw error
  }
}

// 文件上传
const beforeUpload = (file, maxSize = 30) => {
  const ok = file.size / 1024 / 1024 < maxSize
  if (!ok) {
    ElMessage.error(`文件大小不能超过 ${maxSize}MB!`)
  }
  return ok
}

const handleUploadSuccess = (res, type) => {
  if (res.success) {
    ElMessage.success('上传成功')
    const item = materialsList.value.find(m => m.type === type)
    if (item) {
      item.fileName = res.data.fileName
      item.uploadedAt = res.data.uploadedAt
        ? res.data.uploadedAt.replace('T', ' ').substring(0, 16)
        : ''
    }
  } else {
    ElMessage.error(res.message || '上传失败')
  }
}

const downloadTemplate = async (type) => {
  try {
    const templates = await getCompetitionTemplates(competitionId.value)
    const template = templates.data?.find(t => t.type === type)
    if (template) {
      const blob = await downloadCompetitionTemplate(competitionId.value, template.id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = template.fileName
      a.click()
      window.URL.revokeObjectURL(url)
    }
  } catch (error) {
    console.error('下载模板失败:', error)
  }
}

const deleteMaterial = (type) => {
  const item = materialsList.value.find(m => m.type === type)
  if (item) {
    item.fileName = ''
  }
  ElMessage.success('删除成功')
}

// 提交报名
const submitRegistration = async () => {
  try {
    submitting.value = true
    // 提交前检查机构项目数量上限
    const countRes = await getRegistrationCountByInstitution(competitionId.value)
    if (countRes.success && countRes.data >= 8) {
      ElMessage.error('您所在机构在本次赛事中已提交 8 个项目，已达上限，无法继续提交')
      return
    }
    await submitRegistrationApi(registrationId.value)
    ElMessage.success('提交成功')
    router.push('/contestant/dashboard')
  } catch (error) {
    console.error('提交报名失败:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadInstitutionInfo()
  loadDictionaries()
})
</script>

<style scoped lang="scss">
.register-page {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
  
  .steps-container {
    margin-bottom: 32px;
    padding: 0 40px;
  }
  
  .step-content {
    min-height: 400px;
    padding: 20px 0;
    
    .members-section {
      margin-bottom: 20px;
      
      .members-list {
        margin-top: 16px;
        
        .member-card {
          margin-bottom: 16px;
        }
      }
    }
  }
  
  .actions {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-top: 32px;
    padding-top: 32px;
    border-top: 1px solid #e8e8e8;
  }
}
</style>
