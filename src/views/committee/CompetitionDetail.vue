<template>
  <div class="competition-detail-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ competition.name }}</span>
        </div>
      </template>
      
      <!-- 阶段进度 -->
      <stage-progress
        :current-stage="competition.currentStage"
        :stages="stagesList"
      />
      
      <!-- 左侧导航 + 右侧内容 -->
      <el-container class="content-container">
        <el-aside width="200px" class="sidebar">
          <el-menu :default-active="activeTab" @select="handleTabChange">
            <el-sub-menu index="book">
              <template #title>书审阶段</template>
              <el-menu-item index="book-registration">报名与分组</el-menu-item>
              <el-menu-item index="book-reviewer">评委分配</el-menu-item>
              <el-menu-item index="book-score">书审得分</el-menu-item>
              <el-menu-item index="book-feedback">专家意见反馈</el-menu-item>
            </el-sub-menu>
            
            <el-sub-menu index="interview">
              <template #title>面谈阶段</template>
              <el-menu-item index="interview-group">面谈分组</el-menu-item>
              <el-menu-item index="interview-reviewer">评委分配</el-menu-item>
              <el-menu-item index="interview-score">面谈得分</el-menu-item>
              <el-menu-item index="interview-shortlist">入围管理</el-menu-item>
            </el-sub-menu>
            
            <el-sub-menu index="final">
              <template #title>决赛阶段</template>
              <el-menu-item index="final-group">决赛分组</el-menu-item>
              <el-menu-item index="final-reviewer">评委分配</el-menu-item>
              <el-menu-item index="final-score">现场打分</el-menu-item>
              <el-menu-item index="final-ranking">最终排名</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </el-aside>
        
        <el-main class="main-content">
          <!-- 报名与分组 -->
          <div v-if="activeTab === 'book-registration'" class="tab-content">
            <el-form :inline="true" :model="registrationFilters" class="filter-form">
              <el-form-item label="医疗机构">
                <el-input
                  v-model="registrationFilters.institutionName"
                  placeholder="请输入机构名称"
                  clearable
                />
              </el-form-item>
              
              <el-form-item label="竞赛组别">
                <el-select v-model="registrationFilters.groupType" placeholder="全部" clearable>
                  <el-option label="基层组" value="BASIC" />
                  <el-option label="综合组" value="COMPREHENSIVE" />
                  <el-option label="进阶组" value="ADVANCED" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="分组">
                <el-select v-model="registrationFilters.groupCode" placeholder="全部" clearable>
                  <el-option
                    v-for="code in groupCodes"
                    :key="code"
                    :label="code"
                    :value="code"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="项目名称">
                <el-input
                  v-model="registrationFilters.projectName"
                  placeholder="请输入项目名称"
                  clearable
                />
              </el-form-item>
              
              <el-form-item label="品管工具">
                <el-select v-model="registrationFilters.methodCode" placeholder="全部" clearable>
                  <el-option
                    v-for="item in dictionaries.methods"
                    :key="item.code"
                    :label="item.label"
                    :value="item.code"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="loadRegistrations">
                  查询
                </el-button>
                <el-button @click="resetRegistrationFilters">
                  重置
                </el-button>
                <el-button type="success" @click="autoGroup">
                  自动分组
                </el-button>
                <el-button type="warning" @click="batchClassify">
                  批量分类
                </el-button>
              </el-form-item>
            </el-form>
            
            <el-table
              :data="registrations"
              border
              @selection-change="handleSelectionChange"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="projectName" label="项目名称" />
              <el-table-column prop="registrationId" label="项目编号" />
              <el-table-column prop="institutionName" label="医疗机构名称" />
              <el-table-column prop="groupType" label="竞赛组别">
                <template #default="{ row }">
                  {{ getGroupTypeText(row.groupType) }}
                </template>
              </el-table-column>
              <el-table-column prop="groupCode" label="分组" />
              <el-table-column prop="methodLabel" label="品管工具" />
              <el-table-column prop="applicantName" label="报名人" />
              <el-table-column prop="submittedAt" label="报名时间">
                <template #default="{ row }">
                  {{ formatDate(row.submittedAt) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="viewRegistrationDetail(row)">
                    详情
                  </el-button>
                  <el-button type="warning" size="small" @click="changeGroup(row)">
                    变更分组
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <!-- 评委分配 -->
          <div v-if="activeTab === 'book-reviewer'" class="tab-content">
            <el-button type="primary" @click="autoAssignReviewers">
              自动分配
            </el-button>
            
            <el-table :data="reviewerAssignments" border style="margin-top: 20px">
              <el-table-column prop="groupCode" label="分组" />
              <el-table-column prop="projectCount" label="报名项目数量" />
              <el-table-column prop="reviewers" label="评审人员">
                <template #default="{ row }">
                  <el-tag
                    v-for="(reviewer, index) in row.reviewers"
                    :key="index"
                    style="margin-right: 8px"
                  >
                    {{ reviewer.name }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="assignReviewer(row)">
                    评委设置
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <!-- 书审得分 -->
          <div v-if="activeTab === 'book-score'" class="tab-content">
            <el-form :inline="true" :model="scoreFilters" class="filter-form">
              <el-form-item label="竞赛组别">
                <el-select v-model="scoreFilters.groupType" placeholder="全部" clearable>
                  <el-option label="基层组" value="BASIC" />
                  <el-option label="综合组" value="COMPREHENSIVE" />
                  <el-option label="进阶组" value="ADVANCED" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="分组">
                <el-select v-model="scoreFilters.groupCode" placeholder="全部" clearable>
                  <el-option
                    v-for="code in groupCodes"
                    :key="code"
                    :label="code"
                    :value="code"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="评审状态">
                <el-select v-model="scoreFilters.status" placeholder="全部" clearable>
                  <el-option label="待评审" value="PENDING" />
                  <el-option label="已评审" value="COMPLETED" />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="loadScores">
                  查询
                </el-button>
              </el-form-item>
            </el-form>
            
            <el-table :data="scores" border>
              <el-table-column prop="projectName" label="项目名称" />
              <el-table-column prop="projectCode" label="项目编号" />
              <el-table-column prop="groupType" label="竞赛组别">
                <template #default="{ row }">
                  {{ getGroupTypeText(row.groupType) }}
                </template>
              </el-table-column>
              <el-table-column prop="groupCode" label="分组" />
              <el-table-column prop="reviewerName" label="评审专家" />
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'COMPLETED' ? 'success' : 'warning'">
                    {{ row.status === 'COMPLETED' ? '已评审' : '待评审' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="totalScore" label="总得分" />
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="viewScoreDetail(row)">
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <!-- 其他标签页内容 -->
          <div v-if="!['book-registration', 'book-reviewer', 'book-score'].includes(activeTab)" class="tab-content">
            <el-empty description="功能开发中" />
          </div>
        </el-main>
      </el-container>
    </el-card>
    
    <!-- 变更分组对话框 -->
    <el-dialog v-model="changeGroupDialogVisible" title="变更分组" width="400px">
      <el-form :model="changeGroupForm" label-width="100px">
        <el-form-item label="竞赛组别">
          <el-select v-model="changeGroupForm.groupType" @change="handleGroupTypeChange">
            <el-option label="基层组" value="BASIC" />
            <el-option label="综合组" value="COMPREHENSIVE" />
            <el-option label="进阶组" value="ADVANCED" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="分组">
          <el-select v-model="changeGroupForm.groupCode">
            <el-option
              v-for="code in availableGroupCodes"
              :key="code"
              :label="code"
              :value="code"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="changeGroupDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmChangeGroup">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCompetition } from '@/api/competition'
import {
  filterRegistrations,
  batchClassifyRegistrations,
  autoGroupRegistrations,
  autoAssignReview,
  getAdminReviewSummary
} from '@/api/admin'
import { getDictionaryByType } from '@/api/dictionary'
import StageProgress from '@/components/StageProgress.vue'
import dayjs from 'dayjs'

const route = useRoute()
const competitionId = ref(route.params.competitionId)
const activeTab = ref('book-registration')

const competition = ref({})
const registrations = ref([])
const selectedRegistrations = ref([])
const reviewerAssignments = ref([])
const scores = ref([])

const dictionaries = reactive({
  methods: []
})

const registrationFilters = reactive({
  institutionName: '',
  groupType: '',
  groupCode: '',
  projectName: '',
  methodCode: ''
})

const scoreFilters = reactive({
  groupType: '',
  groupCode: '',
  status: ''
})

const changeGroupDialogVisible = ref(false)
const changeGroupForm = reactive({
  registrationIds: [],
  groupType: '',
  groupCode: ''
})

const stagesList = computed(() => {
  return [
    { key: 'REGISTRATION', title: '报名', description: '' },
    { key: 'BOOK', title: '书审', description: '' },
    { key: 'INTERVIEW', title: '面谈', description: '' },
    { key: 'FINAL', title: '决赛', description: '' }
  ]
})

const groupCodes = computed(() => {
  const codes = []
  if (registrationFilters.groupType === 'BASIC') {
    for (let i = 1; i <= 10; i++) {
      codes.push(`A${i}`)
    }
  } else if (registrationFilters.groupType === 'COMPREHENSIVE') {
    for (let i = 1; i <= 10; i++) {
      codes.push(`B${i}`)
    }
  } else if (registrationFilters.groupType === 'ADVANCED') {
    for (let i = 1; i <= 10; i++) {
      codes.push(`C${i}`)
    }
  }
  return codes
})

const availableGroupCodes = computed(() => {
  const codes = []
  if (changeGroupForm.groupType === 'BASIC') {
    for (let i = 1; i <= 10; i++) {
      codes.push(`A${i}`)
    }
  } else if (changeGroupForm.groupType === 'COMPREHENSIVE') {
    for (let i = 1; i <= 10; i++) {
      codes.push(`B${i}`)
    }
  } else if (changeGroupForm.groupType === 'ADVANCED') {
    for (let i = 1; i <= 10; i++) {
      codes.push(`C${i}`)
    }
  }
  return codes
})

const loadCompetition = async () => {
  try {
    const res = await getCompetition(competitionId.value)
    if (res.success && res.data) {
      competition.value = res.data
    }
  } catch (error) {
    console.error('加载赛事信息失败:', error)
  }
}

const loadDictionaries = async () => {
  try {
    const res = await getDictionaryByType('method')
    if (res.success) {
      dictionaries.methods = res.data || []
    }
  } catch (error) {
    console.error('加载字典失败:', error)
  }
}

const loadRegistrations = async () => {
  try {
    const res = await filterRegistrations({
      competitionId: competitionId.value,
      ...registrationFilters
    })
    if (res.success) {
      registrations.value = res.data || []
    }
  } catch (error) {
    console.error('加载报名列表失败:', error)
  }
}

const loadScores = async () => {
  try {
    const res = await getAdminReviewSummary({
      competitionId: competitionId.value,
      stage: 'BOOK',
      ...scoreFilters
    })
    if (res.success) {
      scores.value = res.data || []
    }
  } catch (error) {
    console.error('加载评分列表失败:', error)
  }
}

const resetRegistrationFilters = () => {
  Object.keys(registrationFilters).forEach(key => {
    registrationFilters[key] = ''
  })
}

const handleSelectionChange = (selection) => {
  selectedRegistrations.value = selection
}

const autoGroup = async () => {
  try {
    await autoGroupRegistrations({
      competitionId: competitionId.value
    })
    ElMessage.success('自动分组成功')
    loadRegistrations()
  } catch (error) {
    console.error('自动分组失败:', error)
  }
}

const batchClassify = () => {
  if (selectedRegistrations.value.length === 0) {
    ElMessage.warning('请先选择要分类的项目')
    return
  }
  
  changeGroupForm.registrationIds = selectedRegistrations.value.map(r => r.registrationId)
  changeGroupDialogVisible.value = true
}

const changeGroup = (row) => {
  changeGroupForm.registrationIds = [row.registrationId]
  changeGroupForm.groupType = row.groupType
  changeGroupForm.groupCode = row.groupCode
  changeGroupDialogVisible.value = true
}

const handleGroupTypeChange = () => {
  changeGroupForm.groupCode = ''
}

const confirmChangeGroup = async () => {
  try {
    await batchClassifyRegistrations({
      registrationIds: changeGroupForm.registrationIds,
      groupCode: changeGroupForm.groupCode
    })
    ElMessage.success('变更分组成功')
    changeGroupDialogVisible.value = false
    loadRegistrations()
  } catch (error) {
    console.error('变更分组失败:', error)
  }
}

const autoAssignReviewers = async () => {
  try {
    await autoAssignReview({
      competitionId: competitionId.value,
      stage: 'BOOK'
    })
    ElMessage.success('自动分配成功')
  } catch (error) {
    console.error('自动分配失败:', error)
  }
}

const assignReviewer = (row) => {
  ElMessage.info('评委设置功能开发中')
}

const viewRegistrationDetail = (row) => {
  ElMessage.info('查看详情功能开发中')
}

const viewScoreDetail = (row) => {
  ElMessage.info('查看评分详情功能开发中')
}

const getGroupTypeText = (type) => {
  const map = {
    'BASIC': '基层组',
    'COMPREHENSIVE': '综合组',
    'ADVANCED': '进阶组'
  }
  return map[type] || type
}

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}

const handleTabChange = (key) => {
  activeTab.value = key
  
  if (key === 'book-registration') {
    loadRegistrations()
  } else if (key === 'book-score') {
    loadScores()
  }
}

onMounted(() => {
  loadCompetition()
  loadDictionaries()
  loadRegistrations()
})
</script>

<style scoped lang="scss">
.competition-detail-page {
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
        .filter-form {
          margin-bottom: 20px;
        }
      }
    }
  }
}
</style>
