<template>
  <div class="my-competition-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button type="primary" :icon="ArrowLeft" @click="goBack">返回</el-button>
          <span style="margin-left: 20px;">{{ registration.projectName || '项目详情' }}</span>
        </div>
      </template>
      
      <!-- 阶段进度 -->
      <stage-progress
        :current-stage="competition.stage"
        :stages="stagesList"
      />
      
      <!-- 左侧导航 -->
      <el-container class="content-container">
        <el-aside width="200px" class="sidebar">
          <el-menu :default-active="activeTab" @select="handleTabChange">
            <el-menu-item index="registration">报名管理</el-menu-item>
            <el-menu-item index="book">书审结果</el-menu-item>
            <el-menu-item index="interview">面谈结果</el-menu-item>
            <el-menu-item index="final">决赛成绩</el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main class="main-content">
          <!-- 报名管理 -->
          <div v-if="activeTab === 'registration'" class="tab-content">
            <el-descriptions title="机构基本信息" :column="2" border>
              <el-descriptions-item label="医疗机构名称">
                {{ institutionInfo.name || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="机构等级">
                <el-tag v-if="institutionInfo.level" type="success">
                  {{ institutionInfo.level }}
                </el-tag>
                <span v-else>-</span>
              </el-descriptions-item>
              <el-descriptions-item label="机构编号">
                {{ institutionInfo.code || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="统一社会信用代码">
                {{ institutionInfo.uscc || '-' }}
              </el-descriptions-item>
            </el-descriptions>
            
            <el-descriptions title="项目信息" :column="2" border style="margin-top: 20px">
              <el-descriptions-item label="项目编号">
                {{ registration.id || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="竞赛组别">
                {{ getGroupTypeText(registration.groupType) }}
              </el-descriptions-item>
              <el-descriptions-item label="参赛项目名称" :span="2">
                {{ registration.projectName }}
              </el-descriptions-item>
              <el-descriptions-item label="分组">
                {{ registration.groupCode || '未分组' }}
              </el-descriptions-item>
              <el-descriptions-item label="报名时间">
                {{ formatDate(registration.submittedAt) }}
              </el-descriptions-item>
            </el-descriptions>
            
            <el-descriptions 
              v-if="registration.activityInfo" 
              title="活动信息" 
              :column="2" 
              border 
              style="margin-top: 20px"
            >
              <el-descriptions-item label="活动主题" :span="2">
                {{ registration.activityInfo.theme || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="关键词" :span="2">
                {{ registration.activityInfo.keywords || '-' }}
              </el-descriptions-item>
              
              <!-- 4个Label字段 -->
              <el-descriptions-item label="主题类型">
                {{ registration.activityInfo.subjectTypeLabel || registration.activityInfo.subjectTypeCode || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="运用手法">
                {{ registration.activityInfo.methodLabel || registration.activityInfo.methodCode || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="改善就医环境">
                {{ getExperienceImproveDisplay(registration.activityInfo) }}
              </el-descriptions-item>
              <el-descriptions-item label="医疗质量相关主题">
                {{ getQualityTopicDisplay(registration.activityInfo) }}
              </el-descriptions-item>
              
              <el-descriptions-item label="平均工作年限">
                {{ registration.activityInfo.avgWorkYears || '-' }} 年
              </el-descriptions-item>
              <el-descriptions-item label="平均年龄">
                {{ registration.activityInfo.avgAge || '-' }} 岁
              </el-descriptions-item>
              <el-descriptions-item label="是否跨部门">
                <el-tag :type="registration.activityInfo.crossDepartment ? 'success' : 'info'">
                  {{ registration.activityInfo.crossDepartment ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="是否与数字化/AI相关">
                <el-tag :type="registration.activityInfo.relatedToDigitalAi ? 'success' : 'info'">
                  {{ registration.activityInfo.relatedToDigitalAi ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
            
            <el-card 
              v-if="registration.summary" 
              class="section" 
              style="margin-top: 20px"
            >
              <template #header>
                <h3>项目摘要</h3>
              </template>
              <div class="summary-content">
                <div class="summary-item" v-if="registration.summary.theme">
                  <h4>主题</h4>
                  <p>{{ registration.summary.theme }}</p>
                </div>
                <div class="summary-item" v-if="registration.summary.plan">
                  <h4>计划</h4>
                  <p>{{ registration.summary.plan }}</p>
                </div>
                <div class="summary-item" v-if="registration.summary.problem">
                  <h4>问题结构与对策措施探讨</h4>
                  <p>{{ registration.summary.problem }}</p>
                </div>
                <div class="summary-item" v-if="registration.summary.action">
                  <h4>对策行动过程</h4>
                  <p>{{ registration.summary.action }}</p>
                </div>
                <div class="summary-item" v-if="registration.summary.success">
                  <h4>成果表现</h4>
                  <p>{{ registration.summary.success }}</p>
                </div>
                <div class="summary-item" v-if="registration.summary.discussion">
                  <h4>讨论总结</h4>
                  <p>{{ registration.summary.discussion }}</p>
                </div>
                <div class="summary-item" v-if="registration.summary.operation">
                  <h4>运作</h4>
                  <p>{{ registration.summary.operation }}</p>
                </div>
                <div class="summary-item" v-if="registration.summary.presentation">
                  <h4>展示</h4>
                  <p>{{ registration.summary.presentation }}</p>
                </div>
              </div>
            </el-card>
            
            <el-divider content-position="left">项目参与人员</el-divider>
            <el-table :data="participants" border>
              <el-table-column prop="name" label="姓名" />
              <el-table-column prop="role" label="角色">
                <template #default="{ row }">
                  {{ getMemberRoleLabel(row.role) }}
                </template>
              </el-table-column>
              <el-table-column prop="title" label="职称" />
              <el-table-column prop="department" label="科室" />
            </el-table>
            
            <el-divider content-position="left">辅导员</el-divider>
            <el-table :data="mentors" border>
              <el-table-column prop="name" label="姓名" />
              <el-table-column prop="title" label="职称" />
            </el-table>
            
            <div v-if="registration.materials && registration.materials.length > 0" style="margin-top: 20px">
              <el-divider content-position="left">材料文件</el-divider>
              <el-table :data="registration.materials" border>
                <el-table-column prop="fileName" label="文件名" min-width="200" />
                <el-table-column prop="type" label="类型" width="180">
                  <template #default="{ row }">
                    {{ getMaterialTypeLabel(row.type) }}
                  </template>
                </el-table-column>
                <el-table-column prop="uploadedAt" label="上传时间" width="160">
                  <template #default="{ row }">
                    {{ formatDate(row.uploadedAt) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="160" align="center">
                  <template #default="{ row }">
                    <el-button
                      v-if="canPreview(row.fileName)"
                      type="success"
                      size="small"
                      link
                      @click="previewFile(row)"
                    >预览</el-button>
                    <el-button type="primary" size="small" link :loading="downloadingId === row.id" @click="downloadFile(row)">
                      下载
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
          
          <!-- 书审结果 -->
          <div v-if="activeTab === 'book'" class="tab-content">
            <template v-if="getPublishedFeedbackByStage('BOOK')">
              <el-divider content-position="left">组委会最终发布反馈</el-divider>
              <div class="feedback-text">
                <div><strong>亮点：</strong>{{ getPublishedFeedbackByStage('BOOK').finalHighlight || '暂无' }}</div>
                <div style="margin-top: 8px;"><strong>不足：</strong>{{ getPublishedFeedbackByStage('BOOK').finalWeakness || '暂无' }}</div>
                <div style="margin-top: 8px; color: #909399;">
                  发布时间：{{ formatDate(getPublishedFeedbackByStage('BOOK').publishedAt) }}
                </div>
              </div>
            </template>
            <el-empty v-else description="暂无已发布反馈" />
          </div>
          
          <!-- 面谈结果 -->
          <div v-if="activeTab === 'interview'" class="tab-content">
            <template v-if="getPublishedFeedbackByStage('INTERVIEW')">
              <el-divider content-position="left">组委会最终发布反馈</el-divider>
              <div class="feedback-text">
                <div><strong>亮点：</strong>{{ getPublishedFeedbackByStage('INTERVIEW').finalHighlight || '暂无' }}</div>
                <div style="margin-top: 8px;"><strong>不足：</strong>{{ getPublishedFeedbackByStage('INTERVIEW').finalWeakness || '暂无' }}</div>
                <div style="margin-top: 8px; color: #909399;">
                  发布时间：{{ formatDate(getPublishedFeedbackByStage('INTERVIEW').publishedAt) }}
                </div>
              </div>
            </template>
            <el-empty v-else description="暂无已发布反馈" />
          </div>
          
          <!-- 决赛成绩 -->
          <div v-if="activeTab === 'final'" class="tab-content">
            <div v-if="finalReview">
              <el-descriptions title="决赛得分" :column="1" border>
                <el-descriptions-item label="总分">
                  <el-tag type="success" size="large">
                    {{ typeof finalReview.totalScore === 'number' ? finalReview.totalScore.toFixed(1) : '-' }} 分
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="最终排名">
                  <el-tag type="danger" size="large">
                    第 {{ finalReview.ranking || '-' }} 名
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
            <el-empty v-else description="暂无决赛成绩" />
          </div>
        </el-main>
      </el-container>
    </el-card>

    <FilePreviewDialog
      v-model="filePreviewVisible"
      :material-id="previewMaterialId"
      :file-url="previewFileUrl"
      :file-name="previewFileName"
      :show-download="false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getRegistration, getRegistrationReviewDetails, getPublishedFeedback } from '@/api/registration'
import { getCompetition } from '@/api/competition'
import { getCurrentCompetitionId } from '@/utils/competition'
import { downloadMaterial } from '@/api/material'
import StageProgress from '@/components/StageProgress.vue'
import FilePreviewDialog from '@/components/FilePreviewDialog.vue'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const registrationId = ref(route.params.id)  // ✅ 修复：路由参数名是 'id'，不是 'registrationId'
const activeTab = ref('registration')

const registration = reactive({
  projectName: '',
  institutionName: '',
  groupType: '',
  groupCode: '',
  submittedAt: '',
  registrationId: '',
  id: '',
  members: [],
  activityInfo: null,
  summary: null
})
const competition = ref({})
const institutionInfo = reactive({
  name: '',    // 机构名称
  code: '',
  uscc: '',
  region: '',  // 地区信息
  level: ''    // 机构等级
})

const participants = computed(() => {
  return registration.members?.filter(m => m.role === 'PARTICIPANT') || []
})

const mentors = computed(() => {
  return registration.members?.filter(m => m.role === 'MENTOR') || []
})

const finalReview = ref(null)
const publishedFeedback = ref([])

const stagesList = computed(() => {
  return [
    {
      key: 'REGISTRATION',
      title: '报名',
      startDate: competition.value.registerStart,
      endDate: competition.value.registerEnd
    },
    {
      key: 'BOOK',
      title: '书审',
      startDate: competition.value.bookReviewStart,
      endDate: competition.value.bookReviewEnd
    },
    {
      key: 'INTERVIEW',
      title: '面谈',
      startDate: competition.value.interviewStart,
      endDate: competition.value.interviewEnd
    },
    {
      key: 'FINAL',
      title: '决赛',
      startDate: competition.value.finalStart,
      endDate: competition.value.finalEnd
    }
  ]
})

const loadData = async () => {
  try {
    // 加载报名详情
    const regRes = await getRegistration(registrationId.value)
    
    if (regRes.success && regRes.data) {
      const data = regRes.data
      
      // 处理嵌套数据结构
      const rawMaterials = data.materials ?? data.registration?.materials ?? []
      Object.assign(registration, {
        ...data.registration,
        members: data.members || [],
        activityInfo: data.activityInfo,
        summary: data.projectSummary,
        materials: Array.isArray(rawMaterials) ? rawMaterials : []
      })
      
      // 加载赛事信息（优先使用API返回的competitionId，否则使用后端全局当前赛事）
      const competitionId = data.registration?.competitionId || await getCurrentCompetitionId()
      
      if (competitionId) {
        try {
          const compRes = await getCompetition(competitionId)
          if (compRes.success && compRes.data) {
            competition.value = compRes.data
            console.log('✅ 赛事信息已加载:', {
              registerStart: compRes.data.registerStart,
              registerEnd: compRes.data.registerEnd,
              bookReviewStart: compRes.data.bookReviewStart,
              bookReviewEnd: compRes.data.bookReviewEnd
            })
          } else {
            console.warn('⚠️ 赛事信息加载失败')
          }
        } catch (err) {
          console.error('❌ 加载赛事信息异常:', err)
        }
      } else {
        console.warn('⚠️ 未找到赛事ID，跳过赛事信息加载')
      }
      
      // 获取机构信息
      if (data.institution) {
        institutionInfo.name = data.institution.name
        institutionInfo.code = data.institution.code
        institutionInfo.uscc = data.institution.uscc
        institutionInfo.region = data.institution.region
        institutionInfo.level = data.institution.level
      }
    } else {
      ElMessage.error('加载报名详情失败: ' + (regRes.message || '未知错误'))
    }
    
    // 加载评审详情
    const reviewRes = await getRegistrationReviewDetails(registrationId.value)
    if (reviewRes.success && reviewRes.data) {
      finalReview.value = reviewRes.data.FINAL
    }

    // 加载已发布反馈（参赛者只读）
    const feedbackRes = await getPublishedFeedback(registrationId.value)
    if (feedbackRes.success) {
      publishedFeedback.value = feedbackRes.data || []
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
  }
}

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

// 成员角色标签
const getMemberRoleLabel = (role) => {
  const labels = {
    'LEADER': '圈长',
    'PARTICIPANT': '圈员',
    'MENTOR': '辅导员'
  }
  return labels[role] || role
}

const downloadingId = ref(null)
const filePreviewVisible = ref(false)
const previewMaterialId = ref(null)
const previewFileName = ref('')
const previewFileUrl = ref(null)

const canPreview = (fileName) => {
  if (!fileName) return false
  const ext = fileName.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'docx', 'xlsx', 'xls'].includes(ext)
}

const previewFile = (file) => {
  previewMaterialId.value = file.id || null
  previewFileUrl.value = null
  previewFileName.value = file.fileName || '文件预览'
  filePreviewVisible.value = true
}

const getMaterialTypeLabel = (type) => {
  const map = {
    REGISTRATION_FORM_DOC: '报名表 Word',
    REGISTRATION_FORM_PDF: '报名表 PDF',
    REPORT: '成果报告书',
    EVIDENCE: '佐证材料',
    PAYMENT_PROOF: '缴费凭证'
  }
  return map[type] || type || '-'
}

const downloadFile = async (file) => {
  if (!file.id) {
    ElMessage.warning('文件暂无法下载')
    return
  }
  downloadingId.value = file.id
  try {
    const blob = await downloadMaterial(file.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.fileName || '下载文件'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('下载失败，请重试')
  } finally {
    downloadingId.value = null
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const formatDateRange = (start, end) => {
  if (!start || !end) return ''
  return `${dayjs(start).format('MM-DD')} ~ ${dayjs(end).format('MM-DD')}`
}

const getPublishedFeedbackByStage = (stage) => {
  return publishedFeedback.value.find(item => item.stage === stage) || null
}

const handleTabChange = (key) => {
  activeTab.value = key
}

const goBack = () => {
  router.push('/contestant/registrations')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.my-competition-page {
  padding: 20px;
  
  .card-header {
    display: flex;
    align-items: center;
    
    span {
      font-size: 18px;
      font-weight: 600;
    }
  }
  
  .content-container {
    margin-top: 20px;
    
    .sidebar {
      border-right: 1px solid #e8e8e8;
    }
    
    .main-content {
      .tab-content {
        .feedback-text {
          padding: 16px;
          background: #f5f5f5;
          border-radius: 4px;
          line-height: 1.8;
          white-space: pre-wrap;
        }
        
        .section {
          margin-bottom: 20px;
        }
        
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
  }
}
</style>
