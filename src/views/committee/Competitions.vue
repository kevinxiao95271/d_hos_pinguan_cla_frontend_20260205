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

      <el-table :data="competitions" border v-loading="loading">
        <el-table-column prop="name" label="赛事名称" min-width="200" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'info'">
              {{ row.status === 'ACTIVE' ? '已激活' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="当前阶段" width="100">
          <template #default="{ row }">
            <el-tag :type="getStageType(row.stage || row.currentStage)">
              {{ getStageText(row.stage || row.currentStage) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="分组前缀" width="130">
          <template #default="{ row }">
            <span class="prefix-tags">
              <el-tag size="small" type="primary">基层:{{ row.basicGroupPrefix || 'A' }}</el-tag>
              <el-tag size="small" type="warning">综合:{{ row.comprehensiveGroupPrefix || 'B' }}</el-tag>
              <el-tag size="small" type="success">进阶:{{ row.advancedGroupPrefix || 'C' }}</el-tag>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-space :size="4" wrap>
              <el-button type="primary" size="small" @click="viewDetail(row.id)">管理</el-button>
              <el-button
                v-if="row.status === 'DRAFT'"
                type="success"
                size="small"
                @click="handleActivate(row)"
              >激活</el-button>
              <el-button
                v-if="row.status === 'ACTIVE'"
                type="warning"
                size="small"
                @click="handleDeactivate(row)"
              >撤回激活</el-button>
              <el-button
                v-if="row.status === 'DRAFT'"
                type="danger"
                size="small"
                @click="handleDelete(row)"
              >删除</el-button>
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
import {
  getCompetitions,
  activateCompetition,
  deactivateCompetition,
  deleteCompetition
} from '@/api/competition'
import dayjs from 'dayjs'

const router = useRouter()
const competitions = ref([])
const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
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

const handleActivate = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定激活赛事「${row.name}」？激活后参赛者可报名，同年只允许一个激活赛事。`,
      '确认激活',
      { type: 'warning', confirmButtonText: '激活', cancelButtonText: '取消' }
    )
    const res = await activateCompetition(row.id)
    if (res.success) {
      ElMessage.success('激活成功')
      loadData()
    } else {
      ElMessage.error(res.message || '激活失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.message || '激活失败')
  }
}

const handleDeactivate = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定撤回赛事「${row.name}」的激活状态？仅在无报名记录时可撤回。`,
      '确认撤回',
      { type: 'warning', confirmButtonText: '撤回', cancelButtonText: '取消' }
    )
    const res = await deactivateCompetition(row.id)
    if (res.success) {
      ElMessage.success('撤回成功')
      loadData()
    } else {
      ElMessage.error(res.message || '撤回失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.message || '撤回失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定删除赛事「${row.name}」？此操作不可恢复，仅草稿且无报名记录时可删除。`,
      '确认删除',
      { type: 'error', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    const res = await deleteCompetition(row.id)
    if (res.success !== false) {
      ElMessage.success('删除成功')
      loadData()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.message || '删除失败')
  }
}

const getStageType = (stage) => {
  const map = { REGISTRATION: 'success', BOOK: 'warning', INTERVIEW: 'warning', FINAL: 'danger' }
  return map[stage] || 'info'
}

const getStageText = (stage) => {
  const map = { REGISTRATION: '报名中', BOOK: '书审中', INTERVIEW: '面谈中', FINAL: '决赛中' }
  return map[stage] || (stage || '-')
}

const formatDate = (date) => date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'

const createCompetition = () => router.push('/committee/competition/create')
const viewDetail = (id) => router.push(`/committee/competition/${id}`)

onMounted(() => loadData())
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

  .prefix-tags {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
}
</style>
