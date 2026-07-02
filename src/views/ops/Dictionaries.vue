<template>
  <div class="dictionaries-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>字典管理</span>
          <el-button type="primary" @click="createDictionary">
            新建字典
          </el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeType" @tab-change="loadData">
        <el-tab-pane label="主题类型" name="subject_type" />
        <el-tab-pane label="运用手法" name="method" />
        <el-tab-pane label="改善就医感受" name="experience_improve" />
        <el-tab-pane label="医疗质量安全" name="quality_topic" />
      </el-tabs>
      
      <el-table :data="dictionaries" border>
        <el-table-column prop="code" label="编码" />
        <el-table-column prop="label" label="名称" />
        <el-table-column prop="type" label="类型" />
        <el-table-column prop="sortOrder" label="排序" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editDictionary(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deleteDictionary(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
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
        label-width="100px"
      >
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" :disabled="!!editingId">
            <el-option label="主题类型" value="subject_type" />
            <el-option label="运用手法" value="method" />
            <el-option label="改善就医感受" value="experience_improve" />
            <el-option label="医疗质量安全" value="quality_topic" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入编码" />
        </el-form-item>
        
        <el-form-item label="名称" prop="label">
          <el-input v-model="form.label" placeholder="请输入名称" />
        </el-form-item>
        
        <el-form-item label="排序" prop="sortOrder">
          <el-input-number v-model="form.sortOrder" :min="0" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getDictionaryByType,
  createDictionary as createDictionaryApi,
  updateDictionary,
  deleteDictionary as deleteDictionaryApi
} from '@/api/dictionary'

const activeType = ref('subject_type')
const dictionaries = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新建字典')
const formRef = ref(null)
const submitting = ref(false)
const editingId = ref(null)

const form = reactive({
  type: 'subject_type',
  code: '',
  label: '',
  sortOrder: 0
})

const rules = {
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
  label: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

const loadData = async () => {
  try {
    const res = await getDictionaryByType(activeType.value)
    if (res.success) {
      dictionaries.value = res.data || []
    }
  } catch (error) {
    console.error('加载字典失败:', error)
  }
}

const createDictionary = () => {
  dialogTitle.value = '新建字典'
  editingId.value = null
  form.type = activeType.value
  form.code = ''
  form.label = ''
  form.sortOrder = 0
  dialogVisible.value = true
}

const editDictionary = (row) => {
  dialogTitle.value = '编辑字典'
  editingId.value = row.id
  Object.assign(form, row)
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (editingId.value) {
      await updateDictionary(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createDictionaryApi(form)
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

const deleteDictionary = (row) => {
  ElMessageBox.confirm('确定要删除该字典吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteDictionaryApi(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.dictionaries-page {
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
