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
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-space :size="4" wrap>
              <el-button type="primary" size="small" @click="viewDetail(row.id)">管理</el-button>
              <el-button
                v-if="row.status === 'DRAFT'"
                size="small"
                @click="handleEdit(row)"
              >编辑</el-button>
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

    <!-- 编辑赛事弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑赛事" width="480px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="赛事名称">
          <el-input v-model="editForm.name" placeholder="请输入赛事名称" />
        </el-form-item>
        <el-form-item label="基层组前缀" :error="prefixError.basic">
          <el-input
            v-model="editForm.basicGroupPrefix"
            placeholder="默认 A"
            maxlength="1"
            style="width: 80px"
            @input="val => editForm.basicGroupPrefix = sanitizePrefixInput(val)"
          />
          <span style="margin-left: 8px; color: #909399; font-size: 13px">
            生成 {{ editForm.basicGroupPrefix || 'A' }}1、{{ editForm.basicGroupPrefix || 'A' }}2…
          </span>
        </el-form-item>
        <el-form-item label="综合组前缀" :error="prefixError.comprehensive">
          <el-input
            v-model="editForm.comprehensiveGroupPrefix"
            placeholder="默认 B"
            maxlength="1"
            style="width: 80px"
            @input="val => editForm.comprehensiveGroupPrefix = sanitizePrefixInput(val)"
          />
          <span style="margin-left: 8px; color: #909399; font-size: 13px">
            生成 {{ editForm.comprehensiveGroupPrefix || 'B' }}1、{{ editForm.comprehensiveGroupPrefix || 'B' }}2…
          </span>
        </el-form-item>
        <el-form-item label="进阶组前缀" :error="prefixError.advanced">
          <el-input
            v-model="editForm.advancedGroupPrefix"
            placeholder="默认 C"
            maxlength="1"
            style="width: 80px"
            @input="val => editForm.advancedGroupPrefix = sanitizePrefixInput(val)"
          />
          <span style="margin-left: 8px; color: #909399; font-size: 13px">
            生成 {{ editForm.advancedGroupPrefix || 'C' }}1、{{ editForm.advancedGroupPrefix || 'C' }}2…
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computePrefixErrors, hasPrefixError, sanitizePrefixInput } from '@/utils/groupPrefix'
import {
  getCompetitions,
  activateCompetition,
  deactivateCompetition,
  deleteCompetition,
  updateCompetitionConfig
} from '@/api/competition'
import dayjs from 'dayjs'

const router = useRouter()
const competitions = ref([])
const loading = ref(false)

// 编辑弹窗
const editDialogVisible = ref(false)
const saving = ref(false)
const editingId = ref(null)
const editForm = ref({ name: '', basicGroupPrefix: '', comprehensiveGroupPrefix: '', advancedGroupPrefix: '' })

const prefixError = computed(() => {
  const f = editForm.value
  return computePrefixErrors(f.basicGroupPrefix, f.comprehensiveGroupPrefix, f.advancedGroupPrefix)
})

const handleEdit = (row) => {
  editingId.value = row.id
  editForm.value = {
    name: row.name,
    basicGroupPrefix: row.basicGroupPrefix || '',
    comprehensiveGroupPrefix: row.comprehensiveGroupPrefix || '',
    advancedGroupPrefix: row.advancedGroupPrefix || ''
  }
  editDialogVisible.value = true
}

const handleSaveEdit = async () => {
  if (!editForm.value.name?.trim()) {
    ElMessage.warning('赛事名称不能为空')
    return
  }
  if (hasPrefixError(prefixError.value)) {
    ElMessage.warning('请修正前缀配置后再保存')
    return
  }
  saving.value = true
  try {
    const res = await updateCompetitionConfig(editingId.value, {
      name: editForm.value.name.trim(),
      basicGroupPrefix: editForm.value.basicGroupPrefix || undefined,
      comprehensiveGroupPrefix: editForm.value.comprehensiveGroupPrefix || undefined,
      advancedGroupPrefix: editForm.value.advancedGroupPrefix || undefined
    })
    // res 可能是 { success, data, message } 或空（204）
    if (res && res.success === false) {
      // 后端返回 HTTP 200 但 success=false（如 PREFIX_LOCKED_BY_GROUPING）
      ElMessage.error(res.message || '保存失败')
      return
    }
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    loadData()
  } catch {
    // HTTP 4xx/5xx 错误由 request 拦截器统一弹窗处理，此处无需重复
  } finally {
    saving.value = false
  }
}

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
  } catch {
    return // 用户取消
  }
  try {
    const res = await activateCompetition(row.id)
    if (res && res.success === false) {
      ElMessage.error(res.message || '激活失败')
      return
    }
    ElMessage.success('激活成功')
    loadData()
  } catch {
    // 拦截器已处理
  }
}

const handleDeactivate = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定撤回赛事「${row.name}」的激活状态？仅在无报名记录时可撤回。`,
      '确认撤回',
      { type: 'warning', confirmButtonText: '撤回', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  try {
    const res = await deactivateCompetition(row.id)
    if (res && res.success === false) {
      ElMessage.error(res.message || '撤回失败')
      return
    }
    ElMessage.success('撤回成功')
    loadData()
  } catch {
    // 拦截器已处理
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定删除赛事「${row.name}」？此操作不可恢复，仅草稿且无报名记录时可删除。`,
      '确认删除',
      { type: 'error', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  try {
    const res = await deleteCompetition(row.id)
    if (res && res.success === false) {
      ElMessage.error(res.message || '删除失败')
      return
    }
    ElMessage.success('删除成功')
    loadData()
  } catch {
    // 拦截器已处理
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
