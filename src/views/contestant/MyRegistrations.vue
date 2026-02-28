<template>
  <div class="my-registrations-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的报名</span>
          <el-button type="primary" @click="goToCreate">
            新建报名
          </el-button>
        </div>
      </template>
      
      <el-table :data="registrations" v-loading="loading" border>
        <el-table-column prop="id" label="项目编号" width="100" />
        <el-table-column prop="projectName" label="项目名称" min-width="200" />
        <el-table-column prop="institutionName" label="医疗机构" width="180" />
        <el-table-column prop="institutionLevel" label="机构等级" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.institutionLevel" type="success" size="small">
              {{ row.institutionLevel }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="groupType" label="竞赛组别" width="120">
          <template #default="{ row }">
            {{ getGroupTypeText(row.groupType) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column prop="submittedAt" label="提交时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.submittedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="材料" width="120">
          <template #default="{ row }">
            <div v-if="row.materials && row.materials.length > 0">
              <el-tag type="success" size="small">{{ row.materials.length }}个文件</el-tag>
            </div>
            <el-tag v-else type="info" size="small">未上传</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-space :size="4" wrap>
              <template v-if="row.status === 'DRAFT'">
                <el-button
                  type="primary"
                  size="small"
                  @click="editRegistration(row.id)"
                >
                  编辑
                </el-button>
                <el-button
                  type="success"
                  size="small"
                  @click="submitRegistration(row.id)"
                >
                  提交
                </el-button>
              </template>
              <template v-else-if="row.status === 'SUBMITTED'">
                <el-button
                  size="small"
                  disabled
                  style="cursor: not-allowed; opacity: 0.6;"
                >
                  已提交
                </el-button>
              </template>
              <el-button
                size="small"
                @click="viewDetail(row.id)"
              >
                查看详情
              </el-button>
              <el-button
                v-if="row.status === 'SUBMITTED'"
                size="small"
                @click="viewResults(row.id)"
              >
                查看评审结果
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMyRegistrations, submitRegistration as submitReg } from '@/api/registration'
import dayjs from 'dayjs'

const router = useRouter()

const registrations = ref([])
const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMyRegistrations()
    console.log('📊 我的报名接口返回:', res)
    
    if (res.success) {
      const rawData = res.data || []
      console.log('📝 原始数据:', rawData)
      
      if (rawData.length > 0) {
        console.log('🔍 第一条数据字段检查:')
        console.log('  - institutionId:', rawData[0].institutionId)
        console.log('  - institutionName:', rawData[0].institutionName)
        console.log('  - institutionLevel:', rawData[0].institutionLevel)
        console.log('  - competitionId:', rawData[0].competitionId)
        console.log('  - competitionName:', rawData[0].competitionName)
      }
      
      // 后端已返回平铺字段，直接使用
      registrations.value = rawData
      
      if (registrations.value.length === 0) {
        ElMessage.info('暂无报名记录')
      }
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载报名列表失败:', error)
    ElMessage.error('加载报名列表失败')
  } finally {
    loading.value = false
  }
}

const getGroupTypeText = (type) => {
  const map = {
    'BASIC': '基层组',
    'COMPREHENSIVE': '综合组',
    'ADVANCED': '进阶组'
  }
  return map[type] || type
}

const getStatusType = (status) => {
  const map = {
    'DRAFT': 'info',
    'SUBMITTED': 'success',
    'APPROVED': 'success',
    'RETURNED': 'warning'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'DRAFT': '草稿',
    'SUBMITTED': '已提交',
    'APPROVED': '已通过',
    'RETURNED': '已退回'
  }
  return map[status] || status
}

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}

const goToCreate = () => {
  router.push('/contestant/register/new')
}

const editRegistration = (id) => {
  router.push(`/contestant/register/${id}`)
}

const viewDetail = (id) => {
  router.push(`/contestant/registration/${id}`)
}

const viewResults = (id) => {
  router.push(`/contestant/registration/${id}/results`)
}

const submitRegistration = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确认提交报名？提交后将无法修改。',
      '确认提交',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await submitReg(id)
    if (res.success) {
      ElMessage.success('提交成功')
      loadData()
    } else {
      ElMessage.error(res.message || '提交失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
      ElMessage.error('提交失败')
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.my-registrations-page {
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
