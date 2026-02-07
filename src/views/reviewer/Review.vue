<template>
  <div class="review-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isViewMode ? '查看评分' : '评分' }}</span>
          <el-tag v-if="taskInfo.projectName" type="info" style="margin-left: 10px">
            {{ taskInfo.projectName }}
          </el-tag>
        </div>
      </template>
      
      <div v-loading="loading">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="200px"
          :disabled="isViewMode"
        >
          <el-divider content-position="left">项目信息</el-divider>
          
          <el-form-item label="项目名称">
            <span>{{ taskInfo.projectName || route.query.projectName || '-' }}</span>
          </el-form-item>
          
          <el-form-item label="医疗机构">
            <span>{{ taskInfo.institutionName || '-' }}</span>
          </el-form-item>
          
          <el-form-item label="机构等级">
            <el-tag v-if="taskInfo.institutionLevel" type="success">
              {{ taskInfo.institutionLevel }}
            </el-tag>
            <span v-else>-</span>
          </el-form-item>
          
          <el-form-item label="评审阶段">
            <span>{{ getStageText(taskInfo.stage) }}</span>
          </el-form-item>
          
          <el-form-item label="竞赛组别">
            <span>{{ getGroupTypeText(taskInfo.groupType) }}</span>
          </el-form-item>
          
          <!-- 项目详情折叠面板 -->
          <el-collapse v-if="projectDetail" v-model="activeCollapse" style="margin-bottom: 20px;">
            <el-collapse-item title="查看项目详情" name="detail">
              <!-- 成员信息 -->
              <div v-if="projectDetail.members && projectDetail.members.length > 0" style="margin-bottom: 20px;">
                <h4>项目成员</h4>
                <el-table :data="projectDetail.members" border size="small">
                  <el-table-column prop="name" label="姓名" width="120" />
                  <el-table-column prop="title" label="职称" width="150" />
                  <el-table-column prop="department" label="科室" />
                  <el-table-column prop="role" label="角色" width="100">
                    <template #default="{ row }">
                      {{ row.role === 'PARTICIPANT' ? '参与人员' : '辅导员' }}
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              
              <!-- 活动说明 -->
              <div v-if="projectDetail.activityInfo" style="margin-bottom: 20px;">
                <h4>活动说明</h4>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="活动主题">{{ projectDetail.activityInfo.theme }}</el-descriptions-item>
                  <el-descriptions-item label="关键词">{{ projectDetail.activityInfo.keywords }}</el-descriptions-item>
                  <el-descriptions-item label="主题类型">{{ projectDetail.activityInfo.subjectTypeLabel }}</el-descriptions-item>
                  <el-descriptions-item label="运用手法">{{ projectDetail.activityInfo.methodLabel }}</el-descriptions-item>
                  <el-descriptions-item label="平均工作年限">{{ projectDetail.activityInfo.avgWorkYears }} 年</el-descriptions-item>
                  <el-descriptions-item label="平均年龄">{{ projectDetail.activityInfo.avgAge }} 岁</el-descriptions-item>
                </el-descriptions>
              </div>
              
              <!-- 项目总结 -->
              <div v-if="projectDetail.summary" style="margin-bottom: 20px;">
                <h4>项目总结</h4>
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="计划">
                    <div style="white-space: pre-wrap;">{{ projectDetail.summary.plan || '-' }}</div>
                  </el-descriptions-item>
                  <el-descriptions-item label="问题分析">
                    <div style="white-space: pre-wrap;">{{ projectDetail.summary.problemAnalysis || '-' }}</div>
                  </el-descriptions-item>
                  <el-descriptions-item label="实施过程">
                    <div style="white-space: pre-wrap;">{{ projectDetail.summary.implementation || '-' }}</div>
                  </el-descriptions-item>
                  <el-descriptions-item label="成果表现">
                    <div style="white-space: pre-wrap;">{{ projectDetail.summary.result || '-' }}</div>
                  </el-descriptions-item>
                  <el-descriptions-item label="讨论总结">
                    <div style="white-space: pre-wrap;">{{ projectDetail.summary.review || '-' }}</div>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </el-collapse-item>
          </el-collapse>
          
          <el-divider content-position="left">评分</el-divider>
          
          <el-form-item label="计划" prop="planScore">
            <el-input-number v-model="form.planScore" :min="0" :max="100" />
            <span style="margin-left: 10px; color: #909399;">满分100分</span>
          </el-form-item>
          
          <el-form-item label="问题结构与对策措施探讨" prop="problemAnalysisScore">
            <el-input-number v-model="form.problemAnalysisScore" :min="0" :max="100" />
            <span style="margin-left: 10px; color: #909399;">满分100分</span>
          </el-form-item>
          
          <el-form-item label="对策实施" prop="implementationScore">
            <el-input-number v-model="form.implementationScore" :min="0" :max="100" />
            <span style="margin-left: 10px; color: #909399;">满分100分</span>
          </el-form-item>
          
          <el-form-item label="成功表现" prop="resultScore">
            <el-input-number v-model="form.resultScore" :min="0" :max="100" />
            <span style="margin-left: 10px; color: #909399;">满分100分</span>
          </el-form-item>
          
          <el-form-item label="检讨" prop="reviewScore">
            <el-input-number v-model="form.reviewScore" :min="0" :max="100" />
            <span style="margin-left: 10px; color: #909399;">满分100分</span>
          </el-form-item>
          
          <el-form-item label="整体运作" prop="operationScore">
            <el-input-number v-model="form.operationScore" :min="0" :max="100" />
            <span style="margin-left: 10px; color: #909399;">满分100分</span>
          </el-form-item>
          
          <el-form-item label="资料呈现" prop="presentationScore">
            <el-input-number v-model="form.presentationScore" :min="0" :max="100" />
            <span style="margin-left: 10px; color: #909399;">满分100分</span>
          </el-form-item>
          
          <el-form-item label="总分">
            <el-tag type="success" size="large">{{ totalScore }}</el-tag>
          </el-form-item>
          
          <el-divider content-position="left">评价</el-divider>
          
          <el-form-item label="亮点" prop="highlights">
            <el-input
              v-model="form.highlights"
              type="textarea"
              :rows="4"
              placeholder="请输入亮点，不超过500字"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="不足之处" prop="shortcomings">
            <el-input
              v-model="form.shortcomings"
              type="textarea"
              :rows="4"
              placeholder="请输入不足之处，不超过500字"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item v-if="!isViewMode">
            <el-button type="primary" :loading="submitting" @click="submitReview">
              提交评分
            </el-button>
          </el-form-item>
        </el-form>
        
        <!-- 返回按钮移到表单外，避免被表单的 disabled 影响 -->
        <div style="margin-top: 20px; text-align: left; padding-left: 200px;">
          <el-button @click="goBack">
            返回
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { submitReviewScore, getReviewScore } from '@/api/review'
import { getRegistrationDetail } from '@/api/registration'

const route = useRoute()
const router = useRouter()

const taskId = computed(() => route.params.taskId)
const registrationId = computed(() => route.query.registrationId)  // ✅ 改为 computed，自动响应路由变化
const isViewMode = computed(() => route.query.view === 'score' || route.query.isViewMode === 'true')
const formRef = ref(null)
const submitting = ref(false)
const loading = ref(false)

const taskInfo = reactive({
  projectName: '',
  institutionName: '',
  institutionLevel: '',
  stage: '',
  groupType: ''
})

const projectDetail = ref(null)
const activeCollapse = ref(['detail']) // 默认展开项目详情

const form = reactive({
  planScore: 0,
  problemAnalysisScore: 0,
  implementationScore: 0,
  resultScore: 0,
  reviewScore: 0,
  operationScore: 0,
  presentationScore: 0,
  highlights: '',
  shortcomings: ''
})

const totalScore = computed(() => {
  return form.planScore + 
         form.problemAnalysisScore + 
         form.implementationScore + 
         form.resultScore + 
         form.reviewScore + 
         form.operationScore + 
         form.presentationScore
})

const rules = {
  planScore: [{ required: true, message: '请输入计划得分', trigger: 'blur' }],
  problemAnalysisScore: [{ required: true, message: '请输入问题分析得分', trigger: 'blur' }],
  implementationScore: [{ required: true, message: '请输入实施得分', trigger: 'blur' }],
  resultScore: [{ required: true, message: '请输入成果得分', trigger: 'blur' }],
  reviewScore: [{ required: true, message: '请输入检讨得分', trigger: 'blur' }],
  operationScore: [{ required: true, message: '请输入整体运作得分', trigger: 'blur' }],
  presentationScore: [{ required: true, message: '请输入资料呈现得分', trigger: 'blur' }],
  highlights: [
    { required: true, message: '请输入亮点', trigger: 'blur' },
    { max: 500, message: '亮点不能超过500字', trigger: 'blur' }
  ],
  shortcomings: [
    { required: true, message: '请输入不足之处', trigger: 'blur' },
    { max: 500, message: '不足之处不能超过500字', trigger: 'blur' }
  ]
}

const loadData = async () => {
  loading.value = true
  try {
    // 先从 query 中获取基本信息
    taskInfo.projectName = route.query.projectName || ''
    taskInfo.institutionName = route.query.institutionName || ''
    taskInfo.institutionLevel = route.query.institutionLevel || ''
    taskInfo.stage = route.query.stage || 'BOOK'
    
    // 加载项目详情
    if (registrationId.value) {
      try {
        const detailRes = await getRegistrationDetail(registrationId.value)
        if (detailRes.success && detailRes.data) {
          const data = detailRes.data
          
          // 保存完整项目详情
          projectDetail.value = {
            registration: data.registration,
            members: data.members || [],
            activityInfo: data.activityInfo,
            summary: data.projectSummary  // 注意：后端返回的是 projectSummary
          }
          
          // 更新任务基本信息（从 registration 对象中提取，优先使用详情接口返回的数据）
          const reg = data.registration || {}
          if (reg.projectName) {
            taskInfo.projectName = reg.projectName
          }
          if (reg.groupType) {
            taskInfo.groupType = reg.groupType
          }
          if (reg.status) {
            taskInfo.status = reg.status
          }
          
          console.log('项目详情加载成功:', {
            projectName: taskInfo.projectName,
            institutionName: taskInfo.institutionName,
            groupType: reg.groupType,
            members: data.members?.length,
            hasActivity: !!data.activityInfo,
            hasSummary: !!data.projectSummary
          })
        }
      } catch (error) {
        console.error('加载项目详情失败:', error)
        ElMessage.error('加载项目详情失败')
      }
    } else {
      console.warn('缺少 registrationId，无法加载项目详情')
      ElMessage.warning('缺少项目ID，无法加载详情')
    }
    
    // 如果是查看模式或已经评分，加载评分数据
    if (isViewMode.value || taskId.value) {
      try {
        const scoreRes = await getReviewScore(taskId.value)
        if (scoreRes.success && scoreRes.data) {
          Object.assign(form, scoreRes.data)
        }
      } catch (error) {
        // 未评分，忽略错误
        console.log('未找到已有评分')
      }
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const getStageText = (stage) => {
  const map = {
    'BOOK': '书审',
    'INTERVIEW': '面谈',
    'FINAL': '决赛'
  }
  return map[stage] || stage || '-'
}

const getGroupTypeText = (type) => {
  const map = {
    'BASIC': '基层组',
    'COMPREHENSIVE': '综合组',
    'ADVANCED': '进阶组'
  }
  return map[type] || type || '-'
}

const submitReview = async () => {
  try {
    await formRef.value.validate()
    
    // 确认提交
    await ElMessageBox.confirm(
      `确认提交评分？总分为 ${totalScore.value} 分`,
      '确认提交',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    submitting.value = true
    
    // ✅ 使用正确的字段名
    const submitData = {
      reviewTaskId: parseInt(taskId.value),  // ✅ 任务ID（不是 taskId）
      plan: form.planScore,                  // ✅ 计划（不是 planScore）
      problem: form.problemAnalysisScore,    // ✅ 问题（不是 problemAnalysisScore）
      action: form.implementationScore,      // ✅ 措施（不是 implementationScore）
      success: form.resultScore,             // ✅ 成效（不是 resultScore）
      review: form.reviewScore,              // ✅ 回顾（不是 reviewScore）
      operation: form.operationScore,        // ✅ 操作（不是 operationScore）
      presentation: form.presentationScore,  // ✅ 展示（不是 presentationScore）
      highlight: form.highlights || '',      // ✅ 亮点（单数，必填）
      weakness: form.shortcomings || ''      // ✅ 不足（不是 shortcomings，必填）
    }
    
    console.log('📤 提交评分参数:', submitData)
    console.log('  reviewTaskId:', submitData.reviewTaskId)
    console.log('  总分:', submitData.plan + submitData.problem + submitData.action + submitData.success + submitData.review + submitData.operation + submitData.presentation)
    
    const res = await submitReviewScore(submitData)
    
    if (res.success) {
      ElMessage.success('提交成功')
      router.push('/reviewer/tasks')
    } else {
      ElMessage.error(res.message || '提交失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交评分失败:', error)
      ElMessage.error('提交评分失败')
    }
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadData()
})

// 监听路由变化，重新加载数据
watch(() => route.query.registrationId, (newId, oldId) => {
  if (newId && newId !== oldId) {
    console.log('路由变化，重新加载数据:', newId)
    loadData()
  }
})
</script>

<style scoped lang="scss">
.review-page {
  padding: 20px;
  
  .card-header {
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
  }
  
  :deep(.el-input-number) {
    width: 150px;
  }
}
</style>
