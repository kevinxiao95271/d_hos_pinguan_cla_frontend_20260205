<template>
  <div class="tasks-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>评审任务列表</span>
        </div>
      </template>
      
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="评审阶段">
          <el-select v-model="filters.stage" placeholder="全部" clearable>
            <el-option label="书审" value="BOOK" />
            <el-option label="面谈" value="INTERVIEW" />
            <el-option label="决赛" value="FINAL" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="待评审" value="PENDING" />
            <el-option label="评审中" value="IN_PROGRESS" />
            <el-option label="已评审" value="SCORED" />
            <el-option label="已完成" value="COMPLETED" />
            <el-option label="已退回" value="RETURNED" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadData">
            查询
          </el-button>
          <el-button @click="resetFilters">
            重置
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="filteredTasks" v-loading="loading" border>
        <el-table-column prop="projectName" label="项目名称" min-width="200" />
        <el-table-column prop="institutionName" label="医疗机构" min-width="150" />
        <el-table-column prop="institutionLevel" label="机构等级" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.institutionLevel" type="success" size="small">
              {{ row.institutionLevel }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="stage" label="评审阶段" width="100">
          <template #default="{ row }">
            {{ getStageText(row.stage) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignedAt" label="分配时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.assignedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewDetail(row)"
            >
              查看详情
            </el-button>
            <el-button
              v-if="row.status === 'PENDING'"
              type="success"
              size="small"
              @click="goToReview(row)"
            >
              评分
            </el-button>
            <el-button
              v-else-if="row.status === 'RETURNED'"
              type="warning"
              size="small"
              @click="goToReview(row)"
            >
              重新评分
            </el-button>
            <el-button
              v-else-if="row.status === 'SCORED' || row.status === 'COMPLETED'"
              size="small"
              @click="viewScore(row)"
            >
              查看评分
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页器 -->
      <div v-if="showPagination" class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalCount"
          :page-sizes="pageSizes"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getMyReviewTasks } from '@/api/review'
import { getRegistrationDetail } from '@/api/registration'
import { usePagination } from '@/composables/usePagination'
import dayjs from 'dayjs'

const router = useRouter()

// 分页
const {
  currentPage,
  pageSize,
  totalCount,
  pageSizes,
  showPagination,
  extractDataList,
  resetPagination,
  getPaginationParams
} = usePagination({ defaultPageSize: 50 })

const tasks = ref([])
const loading = ref(false)
const filters = reactive({
  stage: '',
  status: ''
})

const filteredTasks = computed(() => {
  let result = tasks.value
  
  if (filters.stage) {
    result = result.filter(t => t.stage === filters.stage)
  }
  
  if (filters.status) {
    result = result.filter(t => t.status === filters.status)
  }
  
  return result
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMyReviewTasks(getPaginationParams())
    if (res.success) {
      const dataList = extractDataList(res.data)
      // ✅ 字段映射：将 reviewTaskId 映射为 id，确保路由跳转正确
      tasks.value = dataList.map(task => ({
        ...task,
        id: task.reviewTaskId || task.id  // 兼容两种字段名
      }))
      console.log('✅ 加载任务成功:', tasks.value.length, '条', tasks.value[0])
      if (tasks.value.length === 0) {
        ElMessage.info('暂无评审任务')
      }
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('❌ 加载评审任务失败:', error)
    ElMessage.error('加载评审任务失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.stage = ''
  filters.status = ''
  resetPagination()
  loadData()
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
    'IN_PROGRESS': 'primary',
    'COMPLETED': 'success',
    'SCORED': 'success',
    'RETURNED': 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'PENDING': '待评审',
    'IN_PROGRESS': '评审中',
    'COMPLETED': '已完成',
    'SCORED': '已评审',
    'RETURNED': '已退回'
  }
  return map[status] || status
}

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}

const viewDetail = (row) => {
  // 跳转到评分页面（查看模式）
  router.push({
    path: `/reviewer/review/${row.id}`,
    query: {
      registrationId: row.registrationId,
      projectName: row.projectName,
      institutionName: row.institutionName,
      institutionLevel: row.institutionLevel,
      stage: row.stage,
      status: row.status,
      isViewMode: 'true'  // 标记为查看模式，不允许编辑
    }
  })
}

const goToReview = (row) => {
  router.push({
    path: `/reviewer/review/${row.id}`,
    query: {
      registrationId: row.registrationId,
      projectName: row.projectName,
      institutionName: row.institutionName,  // 传递医疗机构名称
      institutionLevel: row.institutionLevel,  // 传递机构等级
      stage: row.stage,  // 传递评审阶段
      status: row.status
    }
  })
}

const viewScore = (row) => {
  router.push({
    path: `/reviewer/review/${row.id}`,
    query: {
      view: 'score',
      registrationId: row.registrationId,
      projectName: row.projectName,
      institutionName: row.institutionName,  // 传递医疗机构名称
      stage: row.stage,  // 传递评审阶段
      status: row.status
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.tasks-page {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
  
  .filter-form {
    margin-bottom: 20px;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
