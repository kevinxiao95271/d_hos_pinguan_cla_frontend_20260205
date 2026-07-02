<template>
  <div class="historical-data-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>历史数据</span>
        </div>
      </template>

      <!-- 筛选表单 -->
      <el-form :model="filters" :inline="true" class="filter-form">
        <el-form-item label="地区">
          <el-input v-model="filters.region" placeholder="请输入地区" clearable style="width: 150px" />
        </el-form-item>
        
        <el-form-item label="组别">
          <el-select v-model="filters.competitionGroup" placeholder="请选择组别" clearable style="width: 150px">
            <el-option label="基层组" value="基层组" />
            <el-option label="综合组" value="综合组" />
            <el-option label="进阶组" value="进阶组" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="品管工具">
          <el-input v-model="filters.circleName" placeholder="请输入品管工具" clearable style="width: 150px" />
        </el-form-item>
        
        <el-form-item label="医院名称">
          <el-input v-model="filters.institutionName" placeholder="请输入医院名称" clearable style="width: 200px" />
        </el-form-item>
        
        <el-form-item label="项目名称">
          <el-input v-model="filters.projectName" placeholder="请输入项目名称" clearable style="width: 200px" />
        </el-form-item>
        
        <el-form-item label="年份">
          <el-select v-model="filters.year" placeholder="请选择年份" clearable style="width: 120px">
            <el-option label="2025" :value="2025" />
            <el-option label="2024" :value="2024" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">
            查询
          </el-button>
          <el-button @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table 
        :data="tableData" 
        border 
        v-loading="loading"
        style="margin-top: 20px"
      >
        <el-table-column prop="region" label="地区" width="120" />
        <el-table-column prop="competitionGroup" label="组别" width="100" />
        <el-table-column prop="circleName" label="品管工具" width="150" />
        <el-table-column prop="institutionName" label="医院名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="projectName" label="项目名称" min-width="250" show-overflow-tooltip />
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="rank" label="排名" width="80" />
        <el-table-column prop="score" label="得分" width="100" />
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getHistoricalData } from '@/api/admin'

const loading = ref(false)
const tableData = ref([])

const filters = reactive({
  region: '',
  competitionGroup: '',
  circleName: '',
  institutionName: '',
  projectName: '',
  year: null
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const loadData = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page - 1, // 后端从0开始
      size: pagination.size
    }
    
    // 只添加非空的筛选条件
    if (filters.region) params.region = filters.region
    if (filters.competitionGroup) params.competitionGroup = filters.competitionGroup
    if (filters.circleName) params.circleName = filters.circleName
    if (filters.institutionName) params.institutionName = filters.institutionName
    if (filters.projectName) params.projectName = filters.projectName
    if (filters.year) params.year = filters.year
    
    const res = await getHistoricalData(params)
    if (res.success && res.data) {
      tableData.value = res.data.content || res.data.items || []
      pagination.total = res.data.totalElements || res.data.total || 0
    }
  } catch (error) {
    console.error('加载历史数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  filters.region = ''
  filters.competitionGroup = ''
  filters.circleName = ''
  filters.institutionName = ''
  filters.projectName = ''
  filters.year = null
  pagination.page = 1
  loadData()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadData()
}

const handleCurrentChange = () => {
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.historical-data-page {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
  
  .filter-form {
    :deep(.el-form-item) {
      margin-bottom: 15px;
    }
  }
}
</style>
