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
            <el-tag :type="getStageType(item.stage)">
              {{ getStageText(item.stage) }}
            </el-tag>
          </div>
          
          <div class="meta-info">
            <div class="meta-item">
              <span class="label">报名时间：</span>
              <span>{{ formatDateRange(item.registerStart, item.registerEnd) }}</span>
            </div>
            <div class="meta-item">
              <span class="label">当前阶段：</span>
              <span>{{ getStageText(item.stage) }}</span>
            </div>
          </div>
            
            <div class="actions">
              <el-button
                :type="isRegistered(item.id) ? 'default' : 'primary'"
                :disabled="!canRegister(item) && !isRegistered(item.id)"
                @click="handleButtonClick(item)"
              >
                {{ getButtonText(item) }}
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 历年积分参考入口 -->
        <div class="score-history-link">
          <el-link :underline="false" style="color: #67b3e8;" @click="showScorePdf = true">
            📄 浙江省医院品管大赛历年积分汇总情况
          </el-link>
        </div>
      </div>
    </el-card>
  </div>

  <!-- 历年积分 PDF 预览弹窗 -->
  <el-dialog
    v-model="showScorePdf"
    width="80%"
    top="5vh"
    destroy-on-close
  >
    <template #header>
      <div style="display:flex; align-items:center; justify-content:space-between; width:100%;">
        <span style="font-size:16px; font-weight:600;">浙江省医院品管大赛历年积分汇总情况</span>
        <el-button type="primary" size="small" :icon="Download" @click="downloadScorePdf">
          下载 PDF
        </el-button>
      </div>
    </template>
    <iframe :src="scorePdfUrl" style="width:100%; height:75vh; border:none;" />
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCompetitions } from '@/api/competition'
import { getMyRegistrations } from '@/api/registration'
import { Download } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const competitions = ref([])
const myRegistrations = ref([])  // 我的报名列表

const loadData = async () => {
  try {
    loading.value = true
    
    // 并行加载赛事列表和我的报名
    const [competitionsRes, myRegsRes] = await Promise.all([
      getCompetitions(),
      getMyRegistrations()
    ])
    
    if (competitionsRes.success) {
      competitions.value = competitionsRes.data || []
    }
    
    if (myRegsRes.success) {
      myRegistrations.value = myRegsRes.data || []
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const getStageType = (stage) => {
  const map = {
    'REGISTER': 'success',  // 修复：后端返回 REGISTER 而不是 REGISTRATION
    'BOOK': 'warning',
    'INTERVIEW': 'warning',
    'FINAL': 'danger'
  }
  return map[stage] || 'info'
}

const getStageText = (stage) => {
  const map = {
    'REGISTER': '报名中',  // 修复：后端返回 REGISTER 而不是 REGISTRATION
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

// 判断是否已报名该赛事
const isRegistered = (competitionId) => {
  return myRegistrations.value.some(
    reg => reg.competitionId === competitionId
  )
}

// 获取已报名的记录
const getMyRegistration = (competitionId) => {
  return myRegistrations.value.find(
    reg => reg.competitionId === competitionId
  )
}

const canRegister = (item) => {
  // 只有报名阶段且未报名的才能报名
  return item.stage === 'REGISTER' && !isRegistered(item.id)
}

const getButtonText = (item) => {
  if (isRegistered(item.id)) {
    return '查看报名'
  }
  return canRegister(item) ? '立即报名' : '报名已结束'
}

const handleButtonClick = (item) => {
  if (isRegistered(item.id)) {
    // 跳转到报名详情
    const myReg = getMyRegistration(item.id)
    if (myReg) {
      router.push(`/contestant/registration/${myReg.id}`)
    }
  } else {
    // 跳转到新建报名页面，通过query参数传递赛事ID
    router.push({
      path: '/contestant/register/new',
      query: { competitionId: item.id }
    })
  }
}

// 历年积分 PDF
const showScorePdf = ref(false)
const scorePdfUrl = `${import.meta.env.BASE_URL}historical_score.pdf`
const downloadScorePdf = () => {
  const a = document.createElement('a')
  a.href = scorePdfUrl
  a.download = '浙江省医院品管大赛历年积分汇总表.pdf'
  a.click()
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

    .score-history-link {
      margin-top: 12px;
      text-align: center;
    }
  }
}
</style>
