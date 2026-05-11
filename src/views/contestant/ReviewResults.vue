<template>
  <div class="review-results-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>已发布反馈</span>
          <el-tag type="info">{{ projectName }}</el-tag>
        </div>
      </template>
      
      <div v-loading="loading">
        <el-empty v-if="!loading && results.length === 0" description="暂无已发布反馈" />
        
        <div v-else>
          <div v-for="(result, index) in results" :key="index" style="margin-bottom: 30px;">
            <el-card shadow="hover">
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-weight: 600;">{{ getStageText(result.stage) }}反馈</span>
                  <el-tag type="success">已发布</el-tag>
                </div>
              </template>

              <el-descriptions :column="1" border>
                <el-descriptions-item label="亮点">
                  <div style="white-space: pre-wrap;">{{ result.finalHighlight || '-' }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="不足之处">
                  <div style="white-space: pre-wrap;">{{ result.finalWeakness || '-' }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="发布时间">
                  {{ formatDate(result.publishedAt) }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
          <el-button @click="goBack">返回</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPublishedFeedback, getRegistrationDetail } from '@/api/registration'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const registrationId = ref(route.params.id)
const projectName = ref('')
const results = ref([])
const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    // 加载项目信息
    const detailRes = await getRegistrationDetail(registrationId.value)
    if (detailRes.success && detailRes.data) {
      projectName.value = detailRes.data.projectName
    }
    
    // 加载已发布反馈（只读最终稿）
    const resultsRes = await getPublishedFeedback(registrationId.value)
    if (resultsRes.success) {
      results.value = resultsRes.data || []
    } else {
      ElMessage.error(resultsRes.message || '加载失败')
    }
  } catch (error) {
    console.error('加载已发布反馈失败:', error)
    ElMessage.error('加载已发布反馈失败')
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
  return map[stage] || stage
}

const formatDate = (value) => {
  if (!value) return '-'
  return dayjs(value).format('YYYY-MM-DD HH:mm:ss')
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.review-results-page {
  padding: 20px;
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 600;
  }
}
</style>
