<template>
  <div class="competitions-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>赛事管理</span>
          <el-button type="primary" @click="createCompetition">
            创建赛事
          </el-button>
        </div>
      </template>
      
      <el-table :data="competitions" border>
        <el-table-column prop="name" label="赛事名称" />
        <el-table-column prop="currentStage" label="当前阶段">
          <template #default="{ row }">
            <el-tag :type="getStageType(row.currentStage)">
              {{ getStageText(row.currentStage) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="registrationStartTime" label="报名时间">
          <template #default="{ row }">
            {{ formatDateRange(row.registrationStartTime, row.registrationEndTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row.id)">
              管理
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
import { getCompetitions } from '@/api/competition'
import dayjs from 'dayjs'

const router = useRouter()
const competitions = ref([])

const loadData = async () => {
  try {
    const res = await getCompetitions()
    if (res.success) {
      competitions.value = res.data || []
    }
  } catch (error) {
    console.error('加载赛事列表失败:', error)
  }
}

const getStageType = (stage) => {
  const map = {
    'REGISTRATION': 'success',
    'BOOK': 'warning',
    'INTERVIEW': 'warning',
    'FINAL': 'danger'
  }
  return map[stage] || 'info'
}

const getStageText = (stage) => {
  const map = {
    'REGISTRATION': '报名中',
    'BOOK': '书审中',
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

const createCompetition = () => {
  router.push('/committee/competition/create')
}

const viewDetail = (id) => {
  router.push(`/committee/competition/${id}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.competitions-page {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
  }
}
</style>
