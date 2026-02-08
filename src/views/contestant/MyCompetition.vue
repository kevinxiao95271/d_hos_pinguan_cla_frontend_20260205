<template>
  <div class="my-competition-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ registration.projectName || '我的赛事' }}</span>
        </div>
      </template>
      
      <!-- 阶段进度 -->
      <stage-progress
        :current-stage="competition.currentStage"
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
                {{ registration.institutionName }}
              </el-descriptions-item>
              <el-descriptions-item label="机构等级">
                <el-tag v-if="institutionInfo.level" type="success">
                  {{ institutionInfo.level }}
                </el-tag>
                <span v-else>-</span>
              </el-descriptions-item>
              <el-descriptions-item label="机构编号">
                {{ institutionInfo.code }}
              </el-descriptions-item>
              <el-descriptions-item label="统一社会信用代码">
                {{ institutionInfo.uscc }}
              </el-descriptions-item>
            </el-descriptions>
            
            <el-descriptions title="项目信息" :column="2" border style="margin-top: 20px">
              <el-descriptions-item label="参赛项目名称" :span="2">
                {{ registration.projectName }}
              </el-descriptions-item>
              <el-descriptions-item label="竞赛组别">
                {{ getGroupTypeText(registration.groupType) }}
              </el-descriptions-item>
              <el-descriptions-item label="分组">
                {{ registration.groupCode || '未分组' }}
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
                <el-table-column prop="fileName" label="文件名" />
                <el-table-column prop="fileType" label="类型" width="100" />
                <el-table-column label="操作" width="120">
                  <template #default="{ row }">
                    <el-button type="primary" size="small" @click="downloadFile(row)">
                      下载
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
          
          <!-- 书审结果 -->
          <div v-if="activeTab === 'book'" class="tab-content">
            <div v-if="bookReview">
              <el-descriptions title="书审得分" :column="2" border>
                <el-descriptions-item label="计划">
                  {{ bookReview.planScore || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="问题结构与对策措施探讨">
                  {{ bookReview.problemScore || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="对策实施">
                  {{ bookReview.actionScore || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="成功表现">
                  {{ bookReview.successScore || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="检讨">
                  {{ bookReview.discussionScore || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="整体运作">
                  {{ bookReview.operationScore || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="资料呈现">
                  {{ bookReview.presentationScore || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="总分">
                  <el-tag type="success" size="large">
                    {{ bookReview.totalScore || '-' }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
              
              <el-divider content-position="left">亮点</el-divider>
              <div class="feedback-text">
                {{ bookReview.highlights || '暂无' }}
              </div>
              
              <el-divider content-position="left">不足之处</el-divider>
              <div class="feedback-text">
                {{ bookReview.improvements || '暂无' }}
              </div>
            </div>
            <el-empty v-else description="暂无书审结果" />
          </div>
          
          <!-- 面谈结果 -->
          <div v-if="activeTab === 'interview'" class="tab-content">
            <div v-if="interviewReview">
              <el-descriptions title="面谈得分" :column="1" border>
                <el-descriptions-item label="总分">
                  <el-tag type="success" size="large">
                    {{ interviewReview.totalScore || '-' }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
              
              <el-divider content-position="left">亮点</el-divider>
              <div class="feedback-text">
                {{ interviewReview.highlights || '暂无' }}
              </div>
              
              <el-divider content-position="left">不足之处</el-divider>
              <div class="feedback-text">
                {{ interviewReview.improvements || '暂无' }}
              </div>
            </div>
            <el-empty v-else description="暂无面谈结果" />
          </div>
          
          <!-- 决赛成绩 -->
          <div v-if="activeTab === 'final'" class="tab-content">
            <div v-if="finalReview">
              <el-descriptions title="决赛得分" :column="1" border>
                <el-descriptions-item label="总分">
                  <el-tag type="success" size="large">
                    {{ finalReview.totalScore || '-' }}
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getRegistration, getRegistrationReviewDetails } from '@/api/registration'
import { getCompetition } from '@/api/competition'
import StageProgress from '@/components/StageProgress.vue'
import dayjs from 'dayjs'

const route = useRoute()
const registrationId = ref(route.params.id)  // ✅ 修复：路由参数名是 'id'，不是 'registrationId'
const activeTab = ref('registration')

const registration = ref({})
const competition = ref({})
const institutionInfo = reactive({
  code: '',
  uscc: '',
  region: '',  // 地区信息
  level: ''    // 机构等级
})

const participants = computed(() => {
  return registration.value.members?.filter(m => m.role === 'PARTICIPANT') || []
})

const mentors = computed(() => {
  return registration.value.members?.filter(m => m.role === 'MENTOR') || []
})

const bookReview = ref(null)
const interviewReview = ref(null)
const finalReview = ref(null)

const stagesList = computed(() => {
  return [
    {
      key: 'REGISTRATION',
      title: '报名',
      description: formatDateRange(competition.value.registrationStartTime, competition.value.registrationEndTime)
    },
    {
      key: 'BOOK',
      title: '书审',
      description: formatDateRange(competition.value.bookStartTime, competition.value.bookEndTime)
    },
    {
      key: 'INTERVIEW',
      title: '面谈',
      description: formatDateRange(competition.value.interviewStartTime, competition.value.interviewEndTime)
    },
    {
      key: 'FINAL',
      title: '决赛',
      description: formatDateRange(competition.value.finalStartTime, competition.value.finalEndTime)
    }
  ]
})

const loadData = async () => {
  try {
    // 加载报名详情
    const regRes = await getRegistration(registrationId.value)
    console.log('📊 报名详情API返回:', regRes)
    
    if (regRes.success && regRes.data) {
      const data = regRes.data
      console.log('📦 完整数据结构:', data)
      console.log('📝 registration 对象:', data.registration)
      console.log('🔍 关键字段检查:')
      console.log('  - subjectType:', data.registration?.subjectType)
      console.log('  - qualityTools:', data.registration?.qualityTools)
      console.log('  - activityInfo:', data.activityInfo)
      console.log('  - projectSummary:', data.projectSummary)
      
      // ✅ 处理嵌套数据结构
      registration.value = {
        ...data.registration,  // 基本信息在 registration 对象中
        members: data.members || [],  // 成员列表
        activityInfo: data.activityInfo,  // 活动说明
        summary: data.projectSummary  // 项目总结
      }
      
      // 加载赛事信息
      if (data.registration?.competitionId) {
        const compRes = await getCompetition(data.registration.competitionId)
        if (compRes.success && compRes.data) {
          competition.value = compRes.data
        }
      }
      
      // ✅ 直接从响应中获取机构信息（后端已优化，不需要单独请求）
      if (data.institution) {
        registration.value.institutionName = data.institution.name
        institutionInfo.code = data.institution.code
        institutionInfo.uscc = data.institution.uscc
        institutionInfo.region = data.institution.region  // 地区信息
        institutionInfo.level = data.institution.level    // 机构等级
      }
    }
    
    // 加载评审详情
    const reviewRes = await getRegistrationReviewDetails(registrationId.value)
    if (reviewRes.success && reviewRes.data) {
      bookReview.value = reviewRes.data.BOOK
      interviewReview.value = reviewRes.data.INTERVIEW
      finalReview.value = reviewRes.data.FINAL
    }
  } catch (error) {
    console.error('加载数据失败:', error)
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

// 下载文件
const downloadFile = (file) => {
  if (file.fileUrl) {
    window.open(file.fileUrl, '_blank')
  } else {
    ElMessage.warning('文件链接不存在')
  }
}

const formatDateRange = (start, end) => {
  if (!start || !end) return ''
  return `${dayjs(start).format('MM-DD')} ~ ${dayjs(end).format('MM-DD')}`
}

const handleTabChange = (key) => {
  activeTab.value = key
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.my-competition-page {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
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
