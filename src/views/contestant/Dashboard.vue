<template>
  <div class="contestant-dashboard">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的赛事</span>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      
      <div v-else-if="registrations.length === 0" class="empty-container">
        <el-empty description="暂无报名记录">
          <el-button type="primary" @click="goToCompetitions">
            去报名
          </el-button>
        </el-empty>
      </div>
      
      <div v-else class="registrations-list">
        <el-card
          v-for="item in registrations"
          :key="item.id"
          class="registration-card"
          shadow="hover"
        >
          <div class="card-content">
            <div class="project-info">
              <h3>{{ item.projectName }}</h3>
              <el-tag :type="getStatusType(item.status)">
                {{ getStatusText(item.status) }}
              </el-tag>
            </div>
            
            <div class="meta-info">
              <div class="meta-item">
                <span class="label">赛事名称：</span>
                <span>{{ item.competitionName }}</span>
              </div>
              <div class="meta-item">
                <span class="label">竞赛组别：</span>
                <span>{{ getGroupTypeText(item.groupType) }}</span>
              </div>
              <div class="meta-item">
                <span class="label">报名时间：</span>
                <span>{{ formatDate(item.createdAt) }}</span>
              </div>
            </div>
            
            <div class="actions">
              <el-button type="primary" @click="viewDetail(item.id)">
                查看详情
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
import { useUserStore } from '@/stores/user'
import { getRegistrationsByApplicant } from '@/api/registration'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const registrations = ref([])

const loadData = async () => {
  try {
    loading.value = true
    const res = await getRegistrationsByApplicant(userStore.userId)
    if (res.success) {
      registrations.value = res.data || []
    }
  } catch (error) {
    console.error('加载报名列表失败:', error)
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const map = {
    'DRAFT': 'info',
    'SUBMITTED': 'success',
    'APPROVED': 'success',
    'REJECTED': 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'DRAFT': '草稿',
    'SUBMITTED': '已提交',
    'APPROVED': '已通过',
    'REJECTED': '已驳回'
  }
  return map[status] || status
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

const viewDetail = (id) => {
  router.push(`/contestant/registration/${id}`)  // ✅ 修复路径，匹配路由配置
}

const goToCompetitions = () => {
  router.push('/contestant/competitions')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.contestant-dashboard {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
  
  .loading-container,
  .empty-container {
    padding: 40px 0;
  }
  
  .registrations-list {
    .registration-card {
      margin-bottom: 16px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .card-content {
        .project-info {
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
