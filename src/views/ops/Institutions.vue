<template>
  <div class="institutions-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>机构管理</span>
          <el-space>
            <el-upload
              :action="`/api/institutions/import`"
              :headers="{ Authorization: `Bearer ${token}` }"
              :show-file-list="false"
              :on-success="handleImportSuccess"
              accept=".xlsx,.xls"
            >
              <el-button type="success">导入机构</el-button>
            </el-upload>
            <el-button type="primary" @click="createInstitution">
              新建机构
            </el-button>
          </el-space>
        </div>
      </template>
      
      <el-table :data="institutions" border>
        <el-table-column prop="name" label="机构名称" />
        <el-table-column prop="code" label="机构编号" />
        <el-table-column prop="level" label="机构等级" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.level" type="success" size="small">
              {{ row.level }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="uscc" label="统一社会信用代码" />
        <el-table-column prop="createdAt" label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editInstitution(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deleteInstitution(row)">
              删除
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
    
    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="140px"
      >
        <el-form-item label="机构名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入机构名称" />
        </el-form-item>
        
        <el-form-item label="机构编号" prop="code">
          <el-input v-model="form.code" placeholder="请输入机构编号" />
        </el-form-item>
        
        <el-form-item label="统一社会信用代码" prop="uscc">
          <el-input v-model="form.uscc" placeholder="请输入统一社会信用代码" />
        </el-form-item>
        
        <el-form-item label="机构等级" prop="level">
          <el-select v-model="form.level" placeholder="请选择机构等级" clearable>
            <el-option label="三级甲等" value="三级甲等" />
            <el-option label="三级乙等" value="三级乙等" />
            <el-option label="二级甲等" value="二级甲等" />
            <el-option label="二级乙等" value="二级乙等" />
            <el-option label="一级甲等" value="一级甲等" />
            <el-option label="一级乙等" value="一级乙等" />
            <el-option label="未定级" value="未定级" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import {
  getInstitutions,
  createInstitution as createInstitutionApi,
  updateInstitution,
  deleteInstitution as deleteInstitutionApi
} from '@/api/institution'
import { usePagination } from '@/composables/usePagination'
import dayjs from 'dayjs'

const userStore = useUserStore()
const token = computed(() => userStore.token)

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

const institutions = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新建机构')
const formRef = ref(null)
const submitting = ref(false)
const editingId = ref(null)

const form = reactive({
  name: '',
  code: '',
  uscc: '',
  level: ''
})

const rules = {
  name: [{ required: true, message: '请输入机构名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入机构编号', trigger: 'blur' }],
  uscc: [{ required: true, message: '请输入统一社会信用代码', trigger: 'blur' }]
}

const loadData = async () => {
  try {
    const res = await getInstitutions(getPaginationParams())
    if (res.success) {
      institutions.value = extractDataList(res.data)
    }
  } catch (error) {
    console.error('加载机构列表失败:', error)
  }
}

const createInstitution = () => {
  dialogTitle.value = '新建机构'
  editingId.value = null
  Object.keys(form).forEach(key => {
    form[key] = ''
  })
  dialogVisible.value = true
}

const editInstitution = (row) => {
  dialogTitle.value = '编辑机构'
  editingId.value = row.id
  Object.assign(form, row)
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (editingId.value) {
      await updateInstitution(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createInstitutionApi(form)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

const deleteInstitution = (row) => {
  ElMessageBox.confirm('确定要删除该机构吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteInstitutionApi(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  })
}

const handleImportSuccess = (res) => {
  if (res.success) {
    ElMessage.success('导入成功')
    loadData()
  }
}

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.institutions-page {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
