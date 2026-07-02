<template>
  <div class="reviewer-dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <el-statistic title="待评审任务" :value="stats.pending" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="已评审" :value="stats.completed" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="总任务数" :value="stats.total" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="完成率" :value="stats.completionRate" suffix="%" />
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>最近任务</span>
          <el-button type="primary" @click="goToTasks">
            查看全部
          </el-button>
        </div>
      </template>
      
      <el-table v-top-scrollbar :data="recentTasks" border>
        <el-table-column prop="projectName" label="项目名称" />
        <el-table-column prop="institutionName" label="医疗机构" />
        <el-table-column prop="institutionLevel" label="机构等级" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.institutionLevel" type="success" size="small">
              {{ row.institutionLevel }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="stage" label="评审阶段">
          <template #default="{ row }">
            {{ getStageText(row.stage) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button
              v-if="['PENDING','CONFIRMED','DRAFT'].includes(row.status)"
              type="primary"
              size="small"
              @click="goToReview(row)"
            >
              {{ row.status === 'DRAFT' ? '继续评分' : '开始评审' }}
            </el-button>
            <el-button
              v-else-if="row.status === 'RETURNED'"
              type="danger"
              size="small"
              @click="goToReview(row)"
            >
              重新评分
            </el-button>
            <el-button
              v-else-if="row.status === 'SCORED' || row.status === 'COMPLETED'"
              type="success"
              size="small"
              @click="viewReview(row)"
            >
              查看评分
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onActivated, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getMyReviewTasks } from '@/api/review'  // ✅ 使用新API

const router = useRouter()
const userStore = useUserStore()

const tasks = ref([])

const stats = computed(() => {
  const total = tasks.value.length
  const completed = tasks.value.filter(t => t.status === 'SCORED' || t.status === 'COMPLETED').length
  const pending = tasks.value.filter(t => ['PENDING','CONFIRMED','DRAFT','RETURNED'].includes(t.status)).length
  const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0
  return { total, completed, pending, completionRate }
})

const recentTasks = computed(() => {
  return tasks.value.slice(0, 5)
})

const loadData = async () => {
  try {
    const res = await getMyReviewTasks()  // ✅ 使用新API，自动从token获取评委ID
    if (res.success) {
      const dataList = res.data || []
      // ✅ 字段映射：将 reviewTaskId 映射为 id，确保路由跳转正确
      tasks.value = dataList.map(task => ({
        ...task,
        id: task.reviewTaskId || task.id  // 兼容两种字段名
      }))
      console.log('✅ Dashboard加载任务成功:', tasks.value.length, '条')
    }
  } catch (error) {
    console.error('❌ 加载评审任务失败:', error)
  }
}

const getStageText = (stage) => {
  const map = {
    'BOOK': '书审',
    'INTERVIEW': '面谈',
    'FINAL': '决赛'
  }
  return map[stage] || stage
}

const getStatusType = (status) => {
  const map = {
    'PENDING': 'warning',
    'CONFIRMED': 'warning',
    'DRAFT': 'primary',
    'IN_PROGRESS': 'primary',
    'SCORED': 'success',
    'COMPLETED': 'success',
    'RETURNED': 'danger',
    'RECUSED': 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'PENDING': '待评审',
    'CONFIRMED': '已确认',
    'DRAFT': '草稿',
    'IN_PROGRESS': '评审中',
    'SCORED': '已评分',
    'COMPLETED': '已完成',
    'RETURNED': '已退回',
    'RECUSED': '已规避'
  }
  return map[status] || status
}

const goToTasks = () => {
  router.push('/reviewer/tasks')
}

const goToReview = (row) => {
  // ✅ 传递完整参数
  router.push({
    path: `/reviewer/review/${row.id}`,
    query: {
      registrationId: row.registrationId,
      projectName: row.projectName,
      institutionName: row.institutionName,
      institutionLevel: row.institutionLevel,
      stage: row.stage
    }
  })
}

const viewReview = (row) => {
  // ✅ 传递完整参数
  router.push({
    path: `/reviewer/review/${row.id}`,
    query: {
      registrationId: row.registrationId,
      projectName: row.projectName,
      institutionName: row.institutionName,
      institutionLevel: row.institutionLevel,
      stage: row.stage,
      isViewMode: 'true'  // 查看模式
    }
  })
}

onMounted(() => {
  loadData()
})

// ✅ 当组件重新激活时（例如从评分页面返回）自动刷新数据
onActivated(() => {
  console.log('Dashboard activated, 重新加载数据')
  loadData()
})
</script>

<style scoped lang="scss">
.reviewer-dashboard {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
