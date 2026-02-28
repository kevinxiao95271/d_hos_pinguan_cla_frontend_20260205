<template>
  <div class="switch-competition-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>切换赛事</span>
        </div>
      </template>
      
      <el-alert
        title="提示"
        type="info"
        description="选择要管理的赛事，切换后所有管理页面将切换到该赛事"
        :closable="false"
        style="margin-bottom: 20px"
      />
      
      <el-table
        :data="competitions"
        border
        highlight-current-row
        @current-change="handleCurrentChange"
      >
        <el-table-column type="index" width="55" label="序号" />
        <el-table-column prop="name" label="赛事名称" />
        <el-table-column prop="stage" label="当前阶段">
          <template #default="{ row }">
            <el-tag :type="getStageType(row.stage)">
              {{ getStageText(row.stage) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="registerStart" label="报名时间">
          <template #default="{ row }">
            {{ formatDateRange(row.registerStart, row.registerEnd) }}
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :disabled="row.id === currentCompetitionId"
              @click="switchCompetition(row)"
            >
              {{ row.id === currentCompetitionId ? '当前赛事' : '切换' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCompetitions } from '@/api/competition'
import { getCurrentCompetitionId, getCurrentCompetitionIdSync, setCurrentCompetitionId } from '@/utils/competition'
import dayjs from 'dayjs'

const router = useRouter()
const competitions = ref([])
const currentCompetitionId = ref(getCurrentCompetitionIdSync())

const loadData = async () => {
  try {
    // 加载赛事列表
    const res = await getCompetitions()
    if (res.success) {
      competitions.value = res.data || []
      console.log('✅ 加载赛事列表成功:', competitions.value.length, '个赛事')
    } else {
      console.warn('⚠️ 加载赛事列表失败:', res.message)
      ElMessage.warning('加载赛事列表失败：' + (res.message || '未知错误'))
    }
  } catch (error) {
    console.error('❌ 加载赛事列表异常:', error)
    ElMessage.error('加载赛事列表失败：' + error.message)
    return
  }
  
  // 从后端获取当前赛事ID（独立的try-catch，避免影响赛事列表显示）
  try {
    const currentId = await getCurrentCompetitionId()
    if (currentId) {
      currentCompetitionId.value = currentId
      console.log('✅ 当前赛事ID:', currentId)
    }
  } catch (error) {
    console.warn('⚠️ 获取当前赛事ID失败:', error)
  }
}

const handleCurrentChange = (row) => {
  // 可以高亮显示当前选中的行
}

const switchCompetition = async (row) => {
  try {
    const success = await setCurrentCompetitionId(row.id)
    if (success) {
      currentCompetitionId.value = row.id
      ElMessage.success(`已切换到赛事：${row.name}`)
      
      // 跳转到报名统计页面
      router.push('/committee/statistics')
    } else {
      ElMessage.error('切换赛事失败，请稍后重试')
    }
  } catch (error) {
    console.error('切换赛事异常:', error)
    ElMessage.error('切换赛事失败：' + error.message)
  }
}

const getStageType = (stage) => {
  const map = {
    'REGISTER': 'success',
    'BOOK_REVIEW': 'warning',
    'INTERVIEW': 'warning',
    'FINAL': 'danger'
  }
  return map[stage] || 'info'
}

const getStageText = (stage) => {
  const map = {
    'REGISTER': '报名中',
    'BOOK_REVIEW': '书审中',
    'INTERVIEW': '面谈中',
    'FINAL': '决赛中'
  }
  return map[stage] || stage
}

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}

const formatDateRange = (start, end) => {
  if (!start || !end) return '-'
  return `${dayjs(start).format('YYYY-MM-DD')} ~ ${dayjs(end).format('YYYY-MM-DD')}`
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.switch-competition-page {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
}
</style>
