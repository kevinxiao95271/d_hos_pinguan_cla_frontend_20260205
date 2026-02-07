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
            
            <el-descriptions title="项目信息" :column="1" border style="margin-top: 20px">
              <el-descriptions-item label="参赛项目名称">
                {{ registration.projectName }}
              </el-descriptions-item>
              <el-descriptions-item label="竞赛组别">
                {{ getGroupTypeText(registration.groupType) }}
              </el-descriptions-item>
            </el-descriptions>
            
            <el-divider content-position="left">项目参与人员</el-divider>
            <el-table :data="participants" border>
              <el-table-column prop="name" label="姓名" />
              <el-table-column prop="title" label="职称" />
              <el-table-column prop="department" label="科室" />
            </el-table>
            
            <el-divider content-position="left">辅导员</el-divider>
            <el-table :data="mentors" border>
              <el-table-column prop="name" label="姓名" />
              <el-table-column prop="title" label="职称" />
            </el-table>
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
    if (regRes.success && regRes.data) {
      const data = regRes.data
      
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
      }
    }
  }
}
</style>
