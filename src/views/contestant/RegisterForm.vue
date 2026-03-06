<template>
  <div class="register-form-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ registrationId ? '编辑报名' : '新建报名' }}</span>
          <el-tag v-if="form.status === 'DRAFT'" type="warning">草稿</el-tag>
          <el-tag v-else-if="form.status === 'RETURNED'" type="danger">已被驳回，请修改后重新提交</el-tag>
          <el-tag v-else-if="form.status === 'SUBMITTED'" type="success">已提交</el-tag>
        </div>
      </template>
      
      <!-- 步骤条 -->
      <el-steps :active="currentStep" align-center finish-status="success" style="margin-bottom: 30px;">
        <el-step title="基本信息" />
        <el-step title="成员信息" />
        <el-step title="活动说明" />
        <el-step title="项目总结" />
        <el-step title="材料上传" />
      </el-steps>
      
      <div v-loading="loading">
        <!-- 步骤1: 基本信息 -->
        <div v-show="currentStep === 0">
          <el-form
            ref="basicFormRef"
            :model="form.basic"
            :rules="basicRules"
            label-width="120px"
            :disabled="isDisabled"
          >
            <el-form-item label="赛事" prop="competitionId">
              <el-select v-model="form.basic.competitionId" placeholder="请选择赛事" style="width: 100%;">
                <el-option
                  v-for="comp in competitions"
                  :key="comp.id"
                  :label="comp.name"
                  :value="comp.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="医疗机构">
              <el-input 
                :value="userStore.institutionName" 
                readonly 
                disabled
                style="width: 100%;"
              />
              <div style="color: #909399; font-size: 12px; margin-top: 4px;">
                您的报名将自动关联到您注册时绑定的机构，无需选择
              </div>
            </el-form-item>
            
            <el-form-item label="项目名称" prop="projectName">
              <el-input
                v-model="form.basic.projectName"
                placeholder="请输入项目名称，不超过100字"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
            
            <el-form-item label="竞赛组别" prop="groupType">
              <el-radio-group v-model="form.basic.groupType">
                <el-tooltip
                  :disabled="!isThirdLevel"
                  content="基层组仅限二级及以下医疗机构报名，三级机构不可选"
                  placement="top"
                >
                  <el-radio value="BASIC" :disabled="isThirdLevel">基层组</el-radio>
                </el-tooltip>
                <el-radio value="COMPREHENSIVE">综合组</el-radio>
                <el-radio value="ADVANCED">进阶组</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 步骤2: 成员信息 -->
        <div v-show="currentStep === 1">
          <el-form
            ref="membersFormRef"
            :model="form.members"
            label-width="120px"
            :disabled="isDisabled"
          >
            <el-divider content-position="left">项目参与人员</el-divider>
            <el-button v-if="!isDisabled" type="primary" size="small" @click="addParticipant" style="margin-bottom: 10px;">
              添加参与人员
            </el-button>
            
            <div v-for="(member, index) in form.members.participants" :key="index" class="member-item">
              <el-card shadow="hover" style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                  <div style="flex: 1;">
                    <el-form-item :label="`姓名`" :prop="`participants.${index}.name`" :rules="[{ required: true, message: '请输入姓名' }]">
                      <el-input v-model="member.name" placeholder="请输入姓名" style="width: 200px;" />
                    </el-form-item>
                    <el-form-item :label="`职称`" :prop="`participants.${index}.title`">
                      <el-input v-model="member.title" placeholder="请输入职称" style="width: 200px;" />
                    </el-form-item>
                    <el-form-item :label="`科室`" :prop="`participants.${index}.department`">
                      <el-input v-model="member.department" placeholder="请输入科室" style="width: 200px;" />
                    </el-form-item>
                  </div>
                  <el-button v-if="!isDisabled" type="danger" size="small" @click="removeParticipant(index)">删除</el-button>
                </div>
              </el-card>
            </div>
            
            <el-divider content-position="left">辅导员</el-divider>
            <el-button v-if="!isDisabled" type="primary" size="small" @click="addMentor" style="margin-bottom: 10px;">
              添加辅导员
            </el-button>
            
            <div v-for="(mentor, index) in form.members.mentors" :key="index" class="member-item">
              <el-card shadow="hover" style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                  <div style="flex: 1;">
                    <el-form-item :label="`姓名`" :prop="`mentors.${index}.name`" :rules="[{ required: true, message: '请输入姓名' }]">
                      <el-input v-model="mentor.name" placeholder="请输入姓名" style="width: 200px;" />
                    </el-form-item>
                    <el-form-item :label="`职称`" :prop="`mentors.${index}.title`">
                      <el-input v-model="mentor.title" placeholder="请输入职称" style="width: 200px;" />
                    </el-form-item>
                  </div>
                  <el-button v-if="!isDisabled" type="danger" size="small" @click="removeMentor(index)">删除</el-button>
                </div>
              </el-card>
            </div>
          </el-form>
        </div>
        
        <!-- 步骤3: 活动说明 -->
        <div v-show="currentStep === 2">
          <el-form
            ref="activityFormRef"
            :model="form.activity"
            :rules="activityRules"
            label-width="150px"
            :disabled="isDisabled"
          >
            <el-form-item label="活动主题" prop="theme">
              <el-input v-model="form.activity.theme" placeholder="请输入活动主题" />
            </el-form-item>
            
            <el-form-item label="关键词" prop="keywords">
              <el-input v-model="form.activity.keywords" placeholder="多个关键词用逗号分隔" />
            </el-form-item>
            
            <el-form-item label="主题类型" prop="subjectTypeCode">
              <el-select v-model="form.activity.subjectTypeCode" placeholder="请选择" style="width: 100%;">
                <el-option
                  v-for="item in subjectTypes"
                  :key="item.code"
                  :label="item.label"
                  :value="item.code"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item v-if="form.activity.subjectTypeCode === 'other'" label="其他主题类型说明" prop="subjectTypeOther">
              <el-input v-model="form.activity.subjectTypeOther" placeholder="请输入其他主题类型的具体说明" />
            </el-form-item>
            
            <el-form-item label="运用手法" prop="methodCode">
              <el-select v-model="form.activity.methodCode" placeholder="请选择" style="width: 100%;">
                <el-option
                  v-for="item in methods"
                  :key="item.code"
                  :label="item.label"
                  :value="item.code"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item v-if="form.activity.methodCode === 'other'" label="其他运用手法说明" prop="methodOther">
              <el-input v-model="form.activity.methodOther" placeholder="请输入其他运用手法的具体说明" />
            </el-form-item>
            
            <el-form-item label="改善就医感受" prop="experienceImproveCode">
              <el-select v-model="form.activity.experienceImproveCode" placeholder="请选择" style="width: 100%;">
                <el-option
                  v-for="item in experienceImproves"
                  :key="item.code"
                  :label="item.label"
                  :value="item.code"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item v-if="form.activity.experienceImproveCode === 'other'" label="其他改善就医感受说明" prop="experienceImproveOther">
              <el-input v-model="form.activity.experienceImproveOther" placeholder="请输入其他改善就医感受的具体说明" />
            </el-form-item>
            
            <el-form-item label="医疗质量安全主题" prop="qualityTopicCode">
              <el-select v-model="form.activity.qualityTopicCode" placeholder="请选择" style="width: 100%;">
                <el-option
                  v-for="item in qualityTopics"
                  :key="item.code"
                  :label="item.label"
                  :value="item.code"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item v-if="form.activity.qualityTopicCode === 'other'" label="其他质量主题说明" prop="qualityTopicOther">
              <el-input v-model="form.activity.qualityTopicOther" placeholder="请输入其他质量主题的具体说明" />
            </el-form-item>
            
            <el-form-item label="平均工作年限" prop="avgWorkYears">
              <el-input-number v-model="form.activity.avgWorkYears" :min="0" :max="50" />
              <span style="margin-left: 10px;">年</span>
            </el-form-item>
            
            <el-form-item label="平均年龄" prop="avgAge">
              <el-input-number v-model="form.activity.avgAge" :min="18" :max="70" />
              <span style="margin-left: 10px;">岁</span>
            </el-form-item>
            
            <el-form-item label="跨部门" prop="crossDepartment">
              <el-radio-group v-model="form.activity.crossDepartment">
                <el-radio :value="true">是</el-radio>
                <el-radio :value="false">否</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="是否与数字化/人工智能应用相关" prop="relatedToDigitalAi">
              <el-radio-group v-model="form.activity.relatedToDigitalAi">
                <el-radio :value="true">是</el-radio>
                <el-radio :value="false">否</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 步骤4: 项目总结 -->
        <div v-show="currentStep === 3">
          <el-form
            ref="summaryFormRef"
            :model="form.summary"
            :rules="summaryRules"
            label-width="200px"
            :disabled="isDisabled"
          >
            <el-form-item label="主题" prop="theme">
              <el-input
                v-model="form.summary.theme"
                placeholder="请输入项目主题"
              />
            </el-form-item>
            
            <el-form-item label="计划" prop="plan">
              <el-input
                v-model="form.summary.plan"
                type="textarea"
                :rows="4"
                placeholder="请输入计划内容"
              />
            </el-form-item>
            
            <el-form-item label="问题结构与对策措施探讨" prop="problem">
              <el-input
                v-model="form.summary.problem"
                type="textarea"
                :rows="4"
                placeholder="请输入问题分析"
              />
            </el-form-item>
            
            <el-form-item label="对策行动过程" prop="action">
              <el-input
                v-model="form.summary.action"
                type="textarea"
                :rows="4"
                placeholder="请输入对策行动过程"
              />
            </el-form-item>
            
            <el-form-item label="成果表现" prop="success">
              <el-input
                v-model="form.summary.success"
                type="textarea"
                :rows="4"
                placeholder="请输入成果表现"
              />
            </el-form-item>
            
            <el-form-item label="讨论总结" prop="discussion">
              <el-input
                v-model="form.summary.discussion"
                type="textarea"
                :rows="4"
                placeholder="请输入讨论总结"
              />
            </el-form-item>
            
            <el-form-item label="操作说明">
              <el-input
                v-model="form.summary.operation"
                type="textarea"
                :rows="3"
                placeholder="请输入操作说明（可选）"
              />
            </el-form-item>
            
            <el-form-item label="成果展示">
              <el-input
                v-model="form.summary.presentation"
                type="textarea"
                :rows="3"
                placeholder="请输入成果展示说明（可选）"
              />
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 步骤5: 材料上传 -->
        <div v-show="currentStep === 4">
          <el-form label-width="150px" :disabled="isDisabled">
            <el-form-item label="报名表 Word" required>
              <div style="display: flex; flex-direction: column; gap: 12px;">
                <el-alert
                  type="info"
                  :closable="false"
                  show-icon
                  style="padding: 6px 12px;"
                >
                  <template #default>
                    报名表要求Word文档形式，请单位盖章后另上传PDF扫描件一份。
                  </template>
                </el-alert>
                <el-upload
                  :auto-upload="false"
                  :on-change="handleRegistrationFormDocChange"
                  :on-remove="handleRegistrationFormDocRemove"
                  :file-list="form.materials.registrationFormDoc"
                  :limit="1"
                  accept=".doc,.docx"
                >
                  <el-button type="primary" :disabled="isDisabled">选择 Word 文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      仅支持 doc/docx 格式，文件大小不超过30MB
                    </div>
                  </template>
                </el-upload>
                <div v-if="registrationFormTemplate" class="template-download-hint">
                  <span style="color: #606266;">请先下载模版：</span>
                  <el-link 
                    type="primary" 
                    underline="never"
                    @click="downloadTemplateFile(registrationFormTemplate)"
                    :icon="Download"
                  >
                    {{ registrationFormTemplate.fileName }}
                  </el-link>
                </div>
              </div>
            </el-form-item>

            <el-form-item label="报名表 PDF" required>
              <div style="display: flex; flex-direction: column; gap: 12px;">
                <el-upload
                  :auto-upload="false"
                  :on-change="handleRegistrationFormPdfChange"
                  :on-remove="handleRegistrationFormPdfRemove"
                  :file-list="form.materials.registrationFormPdf"
                  :limit="1"
                  accept=".pdf"
                >
                  <el-button type="primary" :disabled="isDisabled">选择 PDF 文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      仅支持 pdf 格式（盖章扫描件），文件大小不超过30MB
                    </div>
                  </template>
                </el-upload>
              </div>
            </el-form-item>
            
            <el-form-item label="成果报告书" required>
              <div style="display: flex; flex-direction: column; gap: 12px;">
                <el-upload
                  :auto-upload="false"
                  :on-change="handleReportChange"
                  :on-remove="handleReportRemove"
                  :file-list="form.materials.report"
                  :limit="1"
                  accept=".pdf,.doc,.docx"
                >
                  <el-button type="primary" :disabled="isDisabled">选择文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持PDF、Word格式，文件大小不超过30MB
                    </div>
                  </template>
                </el-upload>
                <div v-if="resultReportTemplate" class="template-download-hint">
                  <span style="color: #606266;">请先下载模版：</span>
                  <el-link 
                    type="primary" 
                    underline="never"
                    @click="downloadTemplateFile(resultReportTemplate)"
                    :icon="Download"
                  >
                    {{ resultReportTemplate.fileName }}
                  </el-link>
                </div>
              </div>
            </el-form-item>
            
            <el-form-item label="佐证材料">
              <el-upload
                :auto-upload="false"
                :on-change="handleEvidenceChange"
                :on-remove="handleEvidenceRemove"
                :file-list="form.materials.evidence"
                :limit="5"
                multiple
                accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.zip,.rar"
              >
                <el-button type="primary" :disabled="isDisabled">选择文件</el-button>
                <template #tip>
                  <div class="el-upload__tip">
                    支持格式：PDF (.pdf)、Word (.doc/.docx)、Excel (.xls/.xlsx)、PPT (.ppt/.pptx)、图片 (.jpg/.jpeg/.png)、压缩包 (.zip/.rar)<br>
                    限制：最多5个文件，单个文件不超过100MB<br>
                    <span style="color:#E6A23C;">视频文件请先打包成压缩包（.zip/.rar）再上传</span>
                  </div>
                </template>
              </el-upload>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 按钮组 -->
        <div class="button-group">
          <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
          <el-button v-if="!isDisabled && currentStep < 4" type="primary" @click="nextStep">
            下一步
          </el-button>
          <el-button v-if="!isDisabled" @click="saveDraft" :loading="saving">
            保存草稿
          </el-button>
          <el-button v-if="!isDisabled && currentStep === 4" type="success" @click="submitForm" :loading="submitting">
            提交报名
          </el-button>
          <el-button @click="goBack">返回</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import {
  createRegistration,
  updateRegistration,
  updateRegistrationMembers,
  updateRegistrationActivity,
  updateRegistrationSummary,
  uploadRegistrationMaterial,
  submitRegistration,
  getRegistrationDetail,
  getRegistrationCountByInstitution
} from '@/api/registration'
import { getCompetitions } from '@/api/competition'
import { getDictionaries } from '@/api/dictionary'
import { getActiveTemplates, downloadTemplate } from '@/api/systemTemplate'
import { uploadMaterial } from '@/api/material'
import { getInstitution } from '@/api/institution'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const registrationId = ref(route.params.id !== 'new' ? route.params.id : null)
const currentStep = ref(0)
const loading = ref(false)
const saving = ref(false)
const submitting = ref(false)

const competitions = ref([])
const subjectTypes = ref([])
const methods = ref([])
const experienceImproves = ref([])
const qualityTopics = ref([])
const templates = ref([])

const basicFormRef = ref(null)
const membersFormRef = ref(null)
const activityFormRef = ref(null)
const summaryFormRef = ref(null)

const form = reactive({
  status: 'DRAFT',
  basic: {
    competitionId: null,
    projectName: '',
    groupType: 'BASIC'
  },
  members: {
    participants: [],
    mentors: []
  },
  activity: {
    theme: '',
    keywords: '',
    subjectTypeCode: '',
    subjectTypeOther: '',
    methodCode: '',
    methodOther: '',
    experienceImproveCode: '',
    experienceImproveOther: '',
    qualityTopicCode: '',
    qualityTopicOther: '',
    avgWorkYears: 0,
    avgAge: 0,
    crossDepartment: false,
    relatedToDigitalAi: false
  },
  summary: {
    theme: '',
    plan: '',
    problem: '',
    action: '',
    success: '',
    discussion: '',
    operation: '',
    presentation: ''
  },
  materials: {
    registrationFormDoc: [],
    registrationFormPdf: [],
    report: [],
    evidence: []
  }
})

const isDisabled = computed(() => form.status === 'SUBMITTED')

// 三级机构不可选基层组
const institutionLevel = ref('')
const isThirdLevel = computed(() => institutionLevel.value?.startsWith('三级'))

watch(isThirdLevel, (val) => {
  if (val && form.basic.groupType === 'BASIC') {
    form.basic.groupType = 'COMPREHENSIVE'
  }
})

// 获取报名表模版
const registrationFormTemplate = computed(() => {
  return templates.value.find(t => t.templateType === 'registration_form')
})

// 获取成果报告书模版
const resultReportTemplate = computed(() => {
  return templates.value.find(t => t.templateType === 'result_report')
})

const basicRules = {
  competitionId: [{ required: true, message: '请选择赛事', trigger: 'change' }],
  projectName: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  groupType: [{ required: true, message: '请选择竞赛组别', trigger: 'change' }]
}

const activityRules = {
  theme: [{ required: true, message: '请输入活动主题', trigger: 'blur' }],
  keywords: [{ required: true, message: '请输入关键词', trigger: 'blur' }],
  subjectTypeCode: [{ required: true, message: '请选择主题类型', trigger: 'change' }],
  methodCode: [{ required: true, message: '请选择运用手法', trigger: 'change' }],
  experienceImproveCode: [{ required: true, message: '请选择改善就医感受', trigger: 'change' }],
  qualityTopicCode: [{ required: true, message: '请选择医疗质量安全主题', trigger: 'change' }],
  relatedToDigitalAi: [{ required: true, message: '请选择是否与数字化/AI相关', trigger: 'change' }]
}

const summaryRules = {
  theme: [{ required: true, message: '请输入项目主题', trigger: 'blur' }],
  plan: [{ required: true, message: '请输入计划内容', trigger: 'blur' }],
  problem: [{ required: true, message: '请输入问题分析', trigger: 'blur' }],
  action: [{ required: true, message: '请输入对策行动过程', trigger: 'blur' }],
  success: [{ required: true, message: '请输入成果表现', trigger: 'blur' }],
  discussion: [{ required: true, message: '请输入讨论总结', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    // 加载下拉选项
    await Promise.all([
      loadCompetitions(),
      loadDictionaries()
    ])
    
    // 异步加载模版（不阻塞主流程）
    loadTemplates().catch(err => {
      console.warn('模版加载失败（不影响其他功能）:', err)
    })
    
    // 如果是编辑模式，加载报名详情
    if (registrationId.value) {
      await loadRegistrationDetail()
    } else {
      // 新建模式：检查query参数，如果有competitionId则自动预选
      const competitionIdFromQuery = route.query.competitionId
      if (competitionIdFromQuery) {
        form.basic.competitionId = parseInt(competitionIdFromQuery)
        console.log('📋 从赛事列表跳转，自动预选赛事ID:', form.basic.competitionId)
      }
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadCompetitions = async () => {
  try {
    const res = await getCompetitions()
    if (res.success) {
      competitions.value = res.data || []
    }
  } catch (error) {
    console.error('加载赛事失败:', error)
  }
}

const loadDictionaries = async () => {
  try {
    const [subjectTypesRes, methodsRes, experienceRes, qualityRes] = await Promise.all([
      getDictionaries('subject_type'),
      getDictionaries('method'),
      getDictionaries('experience_improve'),
      getDictionaries('quality_topic')
    ])
    
    // 兼容两种响应格式：
    // 1. 标准格式: {success: true, data: [...]}
    // 2. 直接返回列表: [{code, label}, ...]
    subjectTypes.value = Array.isArray(subjectTypesRes) ? subjectTypesRes : (subjectTypesRes.data || [])
    methods.value = Array.isArray(methodsRes) ? methodsRes : (methodsRes.data || [])
    experienceImproves.value = Array.isArray(experienceRes) ? experienceRes : (experienceRes.data || [])
    qualityTopics.value = Array.isArray(qualityRes) ? qualityRes : (qualityRes.data || [])
    
    console.log('📚 字典数据加载:', {
      subjectTypes: subjectTypes.value.length,
      methods: methods.value.length,
      experienceImproves: experienceImproves.value.length,
      qualityTopics: qualityTopics.value.length
    })
  } catch (error) {
    console.error('加载字典失败:', error)
  }
}

const loadTemplates = async () => {
  try {
    const res = await getActiveTemplates()
    if (res.success) {
      templates.value = res.data || []
      console.log('✅ 加载模版列表:', templates.value.length, '个模版')
    }
  } catch (error) {
    console.error('❌ 加载模版失败:', error)
    // 模版加载失败不影响其他功能，只记录错误
  }
}

const downloadTemplateFile = async (template) => {
  try {
    const blob = await downloadTemplate(template.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = template.fileName || `${template.templateName}_v${template.version}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('模版下载成功')
  } catch (error) {
    console.error('下载模版失败:', error)
    ElMessage.error('下载模版失败')
  }
}

const loadRegistrationDetail = async () => {
  try {
    const res = await getRegistrationDetail(registrationId.value)
    if (res.success && res.data) {
      // 适配后端响应结构
      const data = res.data
      const registration = data.registration || data
      
      // 状态
      form.status = registration.status
      
      // 基本信息
      // competitionId 可能在顶层或在registration中
      form.basic.competitionId = data.competitionId || registration.competitionId
      form.basic.projectName = registration.projectName
      form.basic.groupType = registration.groupType
      
      console.log('📝 加载报名详情:', {
        competitionId: form.basic.competitionId,
        projectName: form.basic.projectName,
        groupType: form.basic.groupType
      })
      
      // 成员信息
      if (data.members && data.members.length > 0) {
        form.members.participants = data.members.filter(m => m.role === 'PARTICIPANT')
        form.members.mentors = data.members.filter(m => m.role === 'MENTOR')
      }
      
      // 活动说明
      if (data.activityInfo) {
        Object.assign(form.activity, data.activityInfo)
      }
      
      // 项目总结
      if (data.projectSummary) {
        Object.assign(form.summary, data.projectSummary)
        console.log('📄 项目总结数据加载:', form.summary)
      }
    }
  } catch (error) {
    console.error('加载报名详情失败:', error)
    ElMessage.error('加载报名详情失败')
  }
}

const addParticipant = () => {
  form.members.participants.push({
    name: '',
    title: '',
    department: '',
    role: 'PARTICIPANT'
  })
}

const removeParticipant = (index) => {
  form.members.participants.splice(index, 1)
}

const addMentor = () => {
  form.members.mentors.push({
    name: '',
    title: '',
    role: 'MENTOR'
  })
}

const removeMentor = (index) => {
  form.members.mentors.splice(index, 1)
}

const handleRegistrationFormDocChange = (file, fileList) => {
  if (file.size > 30 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过30MB')
    return false
  }
  form.materials.registrationFormDoc = fileList
}

const handleRegistrationFormDocRemove = (file, fileList) => {
  form.materials.registrationFormDoc = fileList
}

const handleRegistrationFormPdfChange = (file, fileList) => {
  if (file.size > 30 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过30MB')
    return false
  }
  form.materials.registrationFormPdf = fileList
}

const handleRegistrationFormPdfRemove = (file, fileList) => {
  form.materials.registrationFormPdf = fileList
}

const handleReportChange = (file, fileList) => {
  if (file.size > 30 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过30MB')
    return false
  }
  form.materials.report = fileList
}

const handleReportRemove = (file, fileList) => {
  form.materials.report = fileList
}

const handleEvidenceChange = (file, fileList) => {
  if (file.size > 100 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过100MB')
    return false
  }
  form.materials.evidence = fileList
}

const handleEvidenceRemove = (file, fileList) => {
  form.materials.evidence = fileList
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const nextStep = async () => {
  // 验证当前步骤
  let valid = false
  if (currentStep.value === 0) {
    valid = await basicFormRef.value.validate().catch(() => false)
    if (valid) {
      await saveBasicInfo()
    }
  } else if (currentStep.value === 1) {
    await saveMembers()
    valid = true
  } else if (currentStep.value === 2) {
    valid = await activityFormRef.value.validate().catch(() => false)
    if (valid) {
      await saveActivity()
    }
  } else if (currentStep.value === 3) {
    valid = await summaryFormRef.value.validate().catch(() => false)
    if (valid) {
      await saveSummary()
    }
  }
  
  if (valid && currentStep.value < 4) {
    currentStep.value++
  }
}

const saveBasicInfo = async () => {
  try {
    if (!registrationId.value) {
      // 创建报名
      const res = await createRegistration(form.basic)
      if (res.success && res.data) {
        registrationId.value = res.data.id
        ElMessage.success('创建成功')
        
        // 创建成功后，更新URL为编辑模式，避免刷新后丢失ID
        router.replace({
          name: 'RegisterForm',
          params: { id: res.data.id }
        })
        
        return true
      }
    } else {
      // 更新基本信息
      const res = await updateRegistration(registrationId.value, form.basic)
      if (res.success) {
        ElMessage.success('保存成功')
        return true
      }
    }
  } catch (error) {
    console.error('保存基本信息失败:', error)
    ElMessage.error('保存基本信息失败')
    return false
  }
}

const saveMembers = async () => {
  if (!registrationId.value) {
    ElMessage.warning('请先保存基本信息')
    return false
  }
  
  try {
    const members = [
      ...form.members.participants,
      ...form.members.mentors
    ]
    
    const res = await updateRegistrationMembers(registrationId.value, { members })
    if (res.success) {
      ElMessage.success('保存成功')
      return true
    }
  } catch (error) {
    console.error('保存成员信息失败:', error)
    ElMessage.error('保存成员信息失败')
    return false
  }
}

const saveActivity = async () => {
  if (!registrationId.value) {
    ElMessage.warning('请先保存基本信息')
    return false
  }
  
  try {
    const res = await updateRegistrationActivity(registrationId.value, form.activity)
    if (res.success) {
      ElMessage.success('保存成功')
      return true
    }
  } catch (error) {
    console.error('保存活动说明失败:', error)
    ElMessage.error('保存活动说明失败')
    return false
  }
}

const saveSummary = async () => {
  if (!registrationId.value) {
    ElMessage.warning('请先保存基本信息')
    return false
  }
  
  console.log('📤 保存项目总结:', {
    registrationId: registrationId.value,
    summaryData: form.summary
  })
  
  try {
    const res = await updateRegistrationSummary(registrationId.value, form.summary)
    if (res.success) {
      ElMessage.success('保存成功')
      return true
    }
  } catch (error) {
    console.error('保存项目总结失败:', error)
    console.error('❌ 错误详情:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data
    })
    ElMessage.error('保存项目总结失败')
    return false
  }
}

const saveDraft = async () => {
  saving.value = true
  try {
    // 根据当前步骤保存相应内容
    if (currentStep.value === 0) {
      await saveBasicInfo()
    } else if (currentStep.value === 1) {
      await saveMembers()
    } else if (currentStep.value === 2) {
      await saveActivity()
    } else if (currentStep.value === 3) {
      await saveSummary()
    }
  } finally {
    saving.value = false
  }
}

const submitForm = async () => {
  try {
    // 验证必填材料
    if (form.materials.registrationFormDoc.length === 0) {
      ElMessage.warning('请上传报名表 Word 文件')
      return
    }
    if (form.materials.registrationFormPdf.length === 0) {
      ElMessage.warning('请上传报名表 PDF 文件（盖章扫描件）')
      return
    }
    if (form.materials.report.length === 0) {
      ElMessage.warning('请上传成果报告书')
      return
    }
    
    // 提交前检查机构项目数量上限
    const countRes = await getRegistrationCountByInstitution(form.basic.competitionId)
    if (countRes.success && countRes.data >= 8) {
      ElMessage.error('您所在机构在本次赛事中已提交 8 个项目，已达上限，无法继续提交')
      return
    }

    // 确认提交
    await ElMessageBox.confirm(
      '确认提交报名？提交后将无法修改。',
      '确认提交',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    submitting.value = true
    
    // 上传材料文件
    try {
      // 上传报名表 Word
      if (form.materials.registrationFormDoc.length > 0 && form.materials.registrationFormDoc[0].raw) {
        const file = form.materials.registrationFormDoc[0].raw
        const formData = new FormData()
        formData.append('file', file)
        formData.append('type', 'REGISTRATION_FORM_DOC')
        await uploadMaterial(registrationId.value, formData)
      }

      // 上传报名表 PDF
      if (form.materials.registrationFormPdf.length > 0 && form.materials.registrationFormPdf[0].raw) {
        const file = form.materials.registrationFormPdf[0].raw
        const formData = new FormData()
        formData.append('file', file)
        formData.append('type', 'REGISTRATION_FORM_PDF')
        await uploadMaterial(registrationId.value, formData)
      }
      
      // 上传成果报告书
      if (form.materials.report.length > 0 && form.materials.report[0].raw) {
        const file = form.materials.report[0].raw
        const formData = new FormData()
        formData.append('file', file)
        formData.append('type', 'REPORT')
        formData.append('contentType', file.type || 'application/octet-stream')
        await uploadMaterial(registrationId.value, formData)
        console.log('✅ 成果报告书上传成功')
      }
      
      // 上传佐证材料
      for (const evidence of form.materials.evidence) {
        if (evidence.raw) {
          const file = evidence.raw
          const formData = new FormData()
          formData.append('file', file)
          formData.append('type', 'EVIDENCE')
          formData.append('contentType', file.type || 'application/octet-stream')
          await uploadMaterial(registrationId.value, formData)
        }
      }
      console.log('✅ 佐证材料上传成功')
    } catch (uploadError) {
      console.error('材料上传失败:', uploadError)
      ElMessage.error('材料上传失败，请重试')
      return
    }
    
    // 提交报名
    const res = await submitRegistration(registrationId.value)
    if (res.success) {
      ElMessage.success('提交成功')
      router.push('/contestant/registrations')
    } else {
      ElMessage.error(res.message || '提交失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
      ElMessage.error('提交失败')
    }
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(async () => {
  loadData()
  // 加载机构等级，用于基层组限制
  if (userStore.institutionId) {
    try {
      const res = await getInstitution(userStore.institutionId)
      if (res.success && res.data) {
        institutionLevel.value = res.data.level || ''
      }
    } catch (e) {
      console.error('加载机构等级失败:', e)
    }
  }
})
</script>

<style scoped lang="scss">
.register-form-page {
  padding: 20px;
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 600;
  }
  
  .member-item {
    margin-bottom: 15px;
  }
  
  .template-download-hint {
    padding: 8px 12px;
    background-color: #f0f9ff;
    border: 1px solid #d1e7fd;
    border-radius: 4px;
    font-size: 13px;
    
    .el-link {
      margin-left: 4px;
      font-weight: 500;
    }
  }
  
  .button-group {
    margin-top: 30px;
    text-align: center;
    padding-top: 20px;
    border-top: 1px solid #eee;
    
    .el-button {
      margin: 0 10px;
    }
  }
}
</style>
