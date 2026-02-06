<template>
  <div class="review-results-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>评审结果</span>
          <el-tag type="info">{{ projectName }}</el-tag>
        </div>
      </template>
      
      <div v-loading="loading">
        <el-empty v-if="!loading && results.length === 0" description="暂无评审结果" />
        
        <div v-else>
          <!-- 书审结果 -->
          <div v-for="(result, index) in results" :key="index" style="margin-bottom: 30px;">
            <el-card shadow="hover">
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-weight: 600;">
                    {{ getStageText(result.stage) }} - 评委：{{ result.reviewerName || '匿名' }}
                  </span>
                  <el-tag type="success">总分: {{ result.totalScore || 0 }}</el-tag>
                </div>
              </template>
              
              <el-descriptions :column="2" border>
                <el-descriptions-item label="计划">
                  {{ result.planScore || 0 }} 分
                </el-descriptions-item>
                <el-descriptions-item label="问题结构与对策措施探讨">
                  {{ result.problemAnalysisScore || 0 }} 分
                </el-descriptions-item>
                <el-descriptions-item label="对策实施">
                  {{ result.implementationScore || 0 }} 分
                </el-descriptions-item>
                <el-descriptions-item label="成功表现">
                  {{ result.resultScore || 0 }} 分
                </el-descriptions-item>
                <el-descriptions-item label="检讨">
                  {{ result.reviewScore || 0 }} 分
                </el-descriptions-item>
                <el-descriptions-item label="整体运作">
                  {{ result.operationScore || 0 }} 分
                </el-descriptions-item>
                <el-descriptions-item label="资料呈现" :span="2">
                  {{ result.presentationScore || 0 }} 分
                </el-descriptions-item>
              </el-descriptions>
              
              <el-divider />
              
              <el-descriptions :column="1" border>
                <el-descriptions-item label="亮点">
                  <div style="white-space: pre-wrap;">{{ result.highlights || '-' }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="不足之处">
                  <div style="white-space: pre-wrap;">{{ result.shortcomings || '-' }}</div>
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
import { getRegistrationReviewResults, getRegistrationDetail } from '@/api/registration'

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
    
    // 加载评审结果
    const resultsRes = await getRegistrationReviewResults(registrationId.value)
    if (resultsRes.success) {
      results.value = resultsRes.data || []
    } else {
      ElMessage.error(resultsRes.message || '加载失败')
    }
  } catch (error) {
    console.error('加载评审结果失败:', error)
    ElMessage.error('加载评审结果失败')
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
