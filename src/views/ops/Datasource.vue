<template>
  <div class="datasource-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据源管理</span>
        </div>
      </template>
      
      <el-alert
        title="提示"
        type="info"
        description="切换数据源后系统将重启，请谨慎操作"
        :closable="false"
        style="margin-bottom: 20px"
      />
      
      <el-descriptions title="当前数据源" :column="1" border>
        <el-descriptions-item label="数据库名称">
          {{ datasource.currentDatabase }}
        </el-descriptions-item>
        <el-descriptions-item label="连接状态">
          <el-tag :type="datasource.connected ? 'success' : 'danger'">
            {{ datasource.connected ? '已连接' : '未连接' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider />
      
      <el-form :model="form" label-width="140px" style="max-width: 600px">
        <el-form-item label="目标数据库">
          <el-select v-model="form.targetDatabase" placeholder="请选择数据库">
            <el-option
              label="d_hos_pinguan_traegj_20260205"
              value="d_hos_pinguan_traegj_20260205"
            />
            <el-option
              label="d_hos_pinguan_traegj_20260205-2"
              value="d_hos_pinguan_traegj_20260205-2"
            />
            <el-option
              label="d_hos_pinguan_traegj_20260205-3"
              value="d_hos_pinguan_traegj_20260205-3"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="switching"
            @click="switchDatasource"
          >
            切换数据源
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDatasource, switchDatasource as switchDatasourceApi } from '@/api/admin'

const datasource = reactive({
  currentDatabase: '',
  connected: false
})

const form = reactive({
  targetDatabase: ''
})

const switching = ref(false)

const loadData = async () => {
  try {
    const res = await getDatasource()
    if (res.success && res.data) {
      Object.assign(datasource, res.data)
    }
  } catch (error) {
    console.error('加载数据源信息失败:', error)
  }
}

const switchDatasource = () => {
  if (!form.targetDatabase) {
    ElMessage.warning('请选择目标数据库')
    return
  }
  
  ElMessageBox.confirm(
    `确定要切换到数据库 ${form.targetDatabase} 吗？系统将重启。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      switching.value = true
      await switchDatasourceApi({
        targetDatabase: form.targetDatabase
      })
      ElMessage.success('切换成功，系统即将重启')
      
      // 延迟刷新页面
      setTimeout(() => {
        window.location.reload()
      }, 2000)
    } catch (error) {
      console.error('切换数据源失败:', error)
      switching.value = false
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.datasource-page {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
}
</style>
