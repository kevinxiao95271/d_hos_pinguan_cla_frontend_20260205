<template>
  <div class="reviewers-container">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">评审专家管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增评委
          </el-button>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :model="filters" :inline="true" style="margin-bottom: 20px">
        <el-form-item label="机构">
          <el-select v-model="filters.institutionId" placeholder="请选择机构" clearable style="width: 200px">
            <el-option
              v-for="inst in institutions"
              :key="inst.id"
              :label="inst.name"
              :value="inst.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="专家背景">
          <el-input v-model="filters.expertBackground" placeholder="请输入专家背景" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 评委列表 -->
      <el-table :data="reviewers" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="phone" label="手机号" width="130" align="center" />
        <el-table-column prop="name" label="姓名" width="120" align="center" />
        <el-table-column prop="title" label="职称" width="150" align="center" />
        <el-table-column prop="institutionName" label="所属机构" min-width="200" />
        <el-table-column prop="expertBackground" label="专家背景" width="150">
          <template #default="{ row }">
            {{ row.expertBackground || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="currentLoad" label="当前负荷" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.currentLoad > 10 ? 'danger' : row.currentLoad > 5 ? 'warning' : 'success'">
              {{ row.currentLoad || 0 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 统计信息 -->
      <div style="margin-top: 20px; color: #666; font-size: 14px">
        共 {{ reviewers.length }} 位评审专家
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" maxlength="50" />
        </el-form-item>
        <el-form-item label="职称" prop="title">
          <el-input v-model="form.title" placeholder="请输入职称" maxlength="50" />
        </el-form-item>
        <el-form-item label="所属机构" prop="institutionId">
          <el-select v-model="form.institutionId" placeholder="请选择所属机构" style="width: 100%">
            <el-option
              v-for="inst in institutions"
              :key="inst.id"
              :label="inst.name"
              :value="inst.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="专家背景">
          <el-input
            v-model="form.expertBackground"
            type="textarea"
            :rows="3"
            placeholder="请输入专家背景（选填）"
            maxlength="500"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getReviewers, createReviewer, updateReviewer, deleteReviewer } from '@/api/review'
import { getInstitutions } from '@/api/institution'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增评委')
const isEdit = ref(false)
const currentId = ref(null)
const formRef = ref(null)

const reviewers = ref([])
const institutions = ref([])

const filters = reactive({
  institutionId: null,
  expertBackground: ''
})

const form = reactive({
  phone: '',
  name: '',
  title: '',
  institutionId: null,
  expertBackground: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在2-50个字符', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入职称', trigger: 'blur' }
  ],
  institutionId: [
    { required: true, message: '请选择所属机构', trigger: 'change' }
  ]
}

// 加载机构列表
const loadInstitutions = async () => {
  try {
    const res = await getInstitutions()
    if (res.success && res.data) {
      institutions.value = res.data
    }
  } catch (error) {
    console.error('加载机构列表失败:', error)
  }
}

// 加载评委列表
const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.institutionId) params.institutionId = filters.institutionId
    if (filters.expertBackground) params.expertBackground = filters.expertBackground

    const res = await getReviewers(params)
    if (res.success) {
      // 处理返回数据，可能是数组或者包含content的对象
      if (Array.isArray(res.data)) {
        reviewers.value = res.data
      } else if (res.data && Array.isArray(res.data.content)) {
        reviewers.value = res.data.content
      } else {
        reviewers.value = []
      }
      ElMessage.success('加载成功')
    }
  } catch (error) {
    console.error('加载评委列表失败:', error)
    ElMessage.error('加载失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 重置筛选条件
const resetFilters = () => {
  filters.institutionId = null
  filters.expertBackground = ''
  loadData()
}

// 新增评委
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增评委'
  dialogVisible.value = true
}

// 编辑评委
const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.id
  dialogTitle.value = '编辑评委'
  
  form.phone = row.phone
  form.name = row.name
  form.title = row.title
  form.institutionId = row.institutionId
  form.expertBackground = row.expertBackground || ''
  
  dialogVisible.value = true
}

// 删除评委
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除评委 "${row.name}" 吗？删除后将无法恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await deleteReviewer(row.id)
    if (res.success) {
      ElMessage.success('删除成功')
      loadData()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除评委失败:', error)
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    const data = {
      phone: form.phone,
      name: form.name,
      title: form.title,
      institutionId: form.institutionId,
      expertBackground: form.expertBackground || null
    }
    
    let res
    if (isEdit.value) {
      res = await updateReviewer(currentId.value, data)
    } else {
      res = await createReviewer(data)
    }
    
    if (res.success) {
      ElMessage.success(isEdit.value ? '更新成功' : '新增成功')
      dialogVisible.value = false
      loadData()
    }
  } catch (error) {
    if (error !== false) {
      console.error('提交表单失败:', error)
      ElMessage.error('操作失败: ' + (error.message || '未知错误'))
    }
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  form.phone = ''
  form.name = ''
  form.title = ''
  form.institutionId = null
  form.expertBackground = ''
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

onMounted(() => {
  loadInstitutions()
  loadData()
})
</script>

<style scoped lang="scss">
.reviewers-container {
  padding: 20px;
  
  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;
  }
  
  :deep(.el-card__body) {
    padding: 20px;
  }
}
</style>
