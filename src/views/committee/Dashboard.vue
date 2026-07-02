<template>
  <div class="committee-dashboard">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>管理首页</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="进行中的赛事" :value="stats.activeCompetitions" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="总报名数" :value="stats.totalRegistrations" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="待评审任务" :value="stats.pendingReviews" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <el-statistic title="已完成评审" :value="stats.completedReviews" />
          </el-card>
        </el-col>
      </el-row>
      
      <el-card style="margin-top: 20px">
        <template #header>
          <span>快捷操作</span>
        </template>
        
        <el-space wrap>
          <el-button type="success" @click="goToCompetitions">
            赛事管理
          </el-button>
        </el-space>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStatsSummary } from '@/api/admin'

const router = useRouter()

const stats = reactive({
  activeCompetitions: 0,
  totalRegistrations: 0,
  pendingReviews: 0,
  completedReviews: 0
})

const loadData = async () => {
  try {
    const res = await getStatsSummary()
    if (res.success && res.data) {
      Object.assign(stats, res.data)
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const createCompetition = () => {
  router.push('/committee/competition/create')
}

const goToCompetitions = () => {
  router.push('/committee/competitions')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.committee-dashboard {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
}
</style>
