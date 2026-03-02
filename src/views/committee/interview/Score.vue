<template>
  <div class="score-page">
    <stage-progress current-stage="INTERVIEW" :stages="stagesList" />
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>面谈得分列表</span>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <el-form :model="filters" inline style="margin-bottom: 20px">
        <el-form-item label="评委姓名">
          <el-input v-model="filters.reviewerName" clearable placeholder="输入评委姓名" style="width: 150px" @clear="loadData" @keyup.enter="loadData" />
        </el-form-item>
        
        <el-form-item label="医疗机构">
          <el-input v-model="filters.institutionName" clearable placeholder="输入机构名称" style="width: 200px" @clear="loadData" @keyup.enter="loadData" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 统计信息 -->
      <el-alert
        v-if="scores.length > 0"
        :title="`共 ${scores.length} 条评分记录`"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      />
      
      <!-- 评分列表 -->
      <el-table
        v-loading="loading"
        :data="scores"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        
        <el-table-column prop="projectName" label="项目名称" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="institutionName" label="医疗机构" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="institutionLevel" label="机构等级" width="110" align="center" />
        
        <el-table-column prop="groupCode" label="分组" width="80" align="center" />
        
        <el-table-column prop="reviewerName" label="评委姓名" width="100" align="center" />
        
        <el-table-column prop="reviewerInstitutionName" label="评委机构" min-width="180" show-overflow-tooltip />
        
        <el-table-column label="评分详情" width="400">
          <template #default="{ row }">
            <div class="score-details">
              <div class="score-item">
                <span class="label">计划:</span>
                <span class="value">{{ row.plan.toFixed(1) }}</span>
              </div>
              <div class="score-item">
                <span class="label">问题:</span>
                <span class="value">{{ row.problem.toFixed(1) }}</span>
              </div>
              <div class="score-item">
                <span class="label">行动:</span>
                <span class="value">{{ row.action.toFixed(1) }}</span>
              </div>
              <div class="score-item">
                <span class="label">成效:</span>
                <span class="value">{{ row.success.toFixed(1) }}</span>
              </div>
              <div class="score-item">
                <span class="label">回顾:</span>
                <span class="value">{{ row.review.toFixed(1) }}</span>
              </div>
              <div class="score-item">
                <span class="label">运作:</span>
                <span class="value">{{ row.operation.toFixed(1) }}</span>
              </div>
              <div class="score-item">
                <span class="label">展示:</span>
                <span class="value">{{ row.presentation.toFixed(1) }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="total" label="总分" width="90" align="center">
          <template #default="{ row }">
            <el-tag type="success" size="large">
              {{ row.total.toFixed(1) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="submittedAt" label="提交时间" width="160" align="center">
          <template #default="{ row }">
            {{ formatDate(row.submittedAt) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="danger"
              size="small"
              @click="handleReturn(row)"
            >
              驳回
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 空状态 -->
      <el-empty v-if="!loading && scores.length === 0" description="暂无评分记录" />
    </el-card>
    
    <!-- 驳回对话框 -->
    <el-dialog
      v-model="returnDialogVisible"
      title="驳回评分"
      width="500px"
    >
      <el-form :model="returnForm" :rules="returnRules" ref="returnFormRef" label-width="80px">
        <el-form-item label="项目名称">
          <span>{{ currentScore?.projectName }}</span>
        </el-form-item>
        
        <el-form-item label="评委">
          <span>{{ currentScore?.reviewerName }}</span>
        </el-form-item>
        
        <el-form-item label="总分">
          <el-tag type="success">{{ currentScore?.total.toFixed(1) }} 分</el-tag>
        </el-form-item>
        
        <el-form-item label="驳回原因" prop="reason">
          <el-input
            v-model="returnForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入驳回原因"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="returnDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="returning" @click="confirmReturn">
          确认驳回
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getInterviewScores, returnScore } from '@/api/review'
import StageProgress from '@/components/StageProgress.vue'
import { useCompetitionStages } from '@/composables/useCompetitionStages'
import { getCurrentCompetitionId } from '@/utils/competition'
import dayjs from 'dayjs'

const { stagesList } = useCompetitionStages()

const loading = ref(false)
const scores = ref([])

const filters = reactive({
  reviewerName: '',
  institutionName: ''
})

const returnDialogVisible = ref(false)
const returning = ref(false)
const currentScore = ref(null)
const returnFormRef = ref(null)

const returnForm = reactive({
  reason: ''
})

const returnRules = {
  reason: [
    { required: true, message: '请输入驳回原因', trigger: 'blur' },
    { min: 5, message: '驳回原因至少5个字符', trigger: 'blur' }
  ]
}

const loadData = async () => {
  const competitionId = await getCurrentCompetitionId()
  if (!competitionId) {
    ElMessage.warning('请先选择赛事')
    return
  }
  
  loading.value = true
  try {
    const params = {
      competitionId,
      groupType: 'ADVANCED',
      ...filters
    }
    
    Object.keys(params).forEach(key => {
      if (!params[key]) delete params[key]
    })
    
    const res = await getInterviewScores(params)
    
    if (res.success) {
      scores.value = res.data || []
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载面谈得分失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.reviewerName = ''
  filters.institutionName = ''
  loadData()
}

const handleReturn = (score) => {
  currentScore.value = score
  returnForm.reason = ''
  returnDialogVisible.value = true
}

const confirmReturn = async () => {
  try {
    await returnFormRef.value.validate()
    
    await ElMessageBox.confirm(
      `确认驳回【${currentScore.value.projectName}】的评分？评分记录将被删除，任务状态将变为"待重评"。`,
      '确认驳回',
      {
        confirmButtonText: '确认驳回',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    returning.value = true
    
    const res = await returnScore({
      scoreId: currentScore.value.scoreId,
      reason: returnForm.reason
    })
    
    if (res.success) {
      ElMessage.success('驳回成功')
      returnDialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.message || '驳回失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('驳回失败:', error)
      ElMessage.error('驳回失败')
    }
  } finally {
    returning.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.score-page {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
  
  .score-details {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    
    .score-item {
      display: flex;
      align-items: center;
      font-size: 13px;
      
      .label {
        color: #909399;
        margin-right: 4px;
      }
      
      .value {
        color: #409eff;
        font-weight: 500;
      }
    }
  }
}
</style>
