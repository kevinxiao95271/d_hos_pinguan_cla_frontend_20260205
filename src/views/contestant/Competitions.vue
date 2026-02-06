<template>
  <div class="competitions-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>赛事列表</span>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      
      <div v-else-if="competitions.length === 0" class="empty-container">
        <el-empty description="暂无可报名的赛事" />
      </div>
      
      <div v-else class="competitions-list">
        <el-card
          v-for="item in competitions"
          :key="item.id"
          class="competition-card"
          shadow="hover"
        >
          <div class="card-content">
            <div class="competition-info">
              <h3>{{ item.name }}</h3>
              <el-tag :type="getStageType(item.currentStage)">
                {{ getStageText(item.currentStage) }}
              </el-tag>
            </div>
            
            <div class="meta-info">
              <div class="meta-item">
                <span class="label">报名时间：</span>
                <span>{{ formatDateRange(item.registrationStartTime, item.registrationEndTime) }}</span>
              </div>
              <div class="meta-item">
                <span class="label">当前阶段：</span>
                <span>{{ getStageText(item.currentStage) }}</span>
              </div>
            </div>
            
            <div class="actions">
              <el-button
                type="primary"
                :disabled="!canRegister(item)"
                @click="register(item.id)"
              >
                {{ getButtonText(item) }}
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCompetitions } from '@/api/competition'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const competitions = ref([])

const loadData = async () => {
  try {
    loading.value = true
    const res = await getCompetitions()
    if (res.success) {
      competitions.value = res.data || []
    }
  } catch (error) {
    console.error('加载赛事列表失败:', error)
  } finally {
    loading.value = false
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

const formatDateRange = (start, end) => {
  if (!start || !end) return '-'
  return `${dayjs(start).format('YYYY-MM-DD')} 至 ${dayjs(end).format('YYYY-MM-DD')}`
}

const canRegister = (item) => {
  return item.currentStage === 'REGISTRATION'
}

const getButtonText = (item) => {
  return canRegister(item) ? '立即报名' : '报名已结束'
}

const register = (competitionId) => {
  router.push(`/contestant/register/${competitionId}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.competitions-page {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
  
  .loading-container,
  .empty-container {
    padding: 40px 0;
  }
  
  .competitions-list {
    .competition-card {
      margin-bottom: 16px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .card-content {
        .competition-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          
          h3 {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
          }
        }
        
        .meta-info {
          margin-bottom: 16px;
          
          .meta-item {
            margin-bottom: 8px;
            color: #666;
            
            .label {
              color: #999;
            }
          }
        }
        
        .actions {
          display: flex;
          justify-content: flex-end;
        }
      }
    }
  }
}
</style>
