<template>
  <div class="system-templates-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统模版管理</span>
          <el-button type="primary" @click="uploadDialogVisible = true">
            上传新模版
          </el-button>
        </div>
      </template>
      
      <!-- 当前有效模版 -->
      <el-alert
        title="当前有效模版"
        type="success"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <div v-if="activeTemplates.length > 0">
          <p style="margin: 10px 0;">以下模版当前对用户可见：</p>
          <el-space wrap>
            <el-tag
              v-for="template in activeTemplates"
              :key="template.id"
              type="success"
              size="large"
            >
              {{ getTemplateTypeName(template.templateType) }} (v{{ template.version }})
            </el-tag>
          </el-space>
        </div>
        <div v-else>
          <p>暂无有效模版</p>
        </div>
      </el-alert>
      
      <!-- 所有模版列表 -->
      <el-table v-top-scrollbar :data="allTemplates" v-loading="loading" border>
        <el-table-column prop="id" label="模版ID" width="100" />
        <el-table-column prop="templateType" label="模版类型" min-width="180">
          <template #default="{ row }">
            {{ getTemplateTypeName(row.templateType) }}
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本号" width="100" />
        <el-table-column prop="fileName" label="文件名" min-width="200" />
        <el-table-column prop="fileSize" label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.fileSize) }}
          </template>
        </el-table-column>
        <el-table-column prop="isActive" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isActive ? 'success' : 'info'">
              {{ row.isActive ? '有效' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uploadedAt" label="上传时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.uploadedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-space :size="4" wrap>
              <el-button
                type="primary"
                size="small"
                @click="downloadTemplateFile(row)"
              >
                下载
              </el-button>
              <!-- 当前激活的模版不显示停用/删除按钮 -->
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 上传模版对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传新模版"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="uploadForm" label-width="120px">
        <el-form-item label="模版类型" required>
          <el-select v-model="uploadForm.templateType" placeholder="请选择模版类型" style="width:100%">
            <el-option label="报名表模版" value="registration_form" />
            <el-option label="成果报告书模版" value="result_report" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".doc,.docx,.pdf"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持Word、PDF格式，文件大小不超过30MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item v-if="uploadForm.file">
          <el-tag type="success">
            已选择：{{ uploadForm.file.name }}
          </el-tag>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="uploading"
          :disabled="!uploadForm.templateType || !uploadForm.file"
          @click="handleUpload"
        >
          确认上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAllTemplates,
  getActiveTemplates,
  uploadTemplate,
  downloadTemplate,
  deleteTemplate as deleteTemplateApi
} from '@/api/systemTemplate'
import dayjs from 'dayjs'

const loading = ref(false)
const uploading = ref(false)
const uploadDialogVisible = ref(false)
const activeTemplates = ref([])
const allTemplates = ref([])

const uploadForm = ref({
  templateType: '',
  file: null
})

const uploadRef = ref(null)

onMounted(() => {
  loadTemplates()
})

const loadTemplates = async () => {
  loading.value = true
  try {
    // 只加载有效模版（当前激活的模版）
    const activeRes = await getActiveTemplates()
    
    if (activeRes.success) {
      activeTemplates.value = activeRes.data || []
      // OPS管理页面也只显示当前激活的模版
      allTemplates.value = activeRes.data || []
    }
  } catch (error) {
    console.error('加载模版列表失败:', error)
    ElMessage.error('加载模版列表失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const getTemplateTypeName = (type) => {
  const typeMap = {
    'registration_form': '报名表模版',
    'result_report': '成果报告书模版'
  }
  return typeMap[type] || type
}

const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

const handleFileChange = (file) => {
  if (file.size > 30 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过30MB')
    return false
  }
  uploadForm.value.file = file.raw
}

const handleUpload = async () => {
  if (!uploadForm.value.templateType || !uploadForm.value.file) {
    ElMessage.warning('请选择模版类型并选择文件')
    return
  }
  
  try {
    uploading.value = true
    
    const formData = new FormData()
    formData.append('file', uploadForm.value.file)
    formData.append('templateType', uploadForm.value.templateType)
    
    const res = await uploadTemplate(formData)
    
    if (res.success) {
      ElMessage.success('上传成功')
      uploadDialogVisible.value = false
      uploadForm.value = {
        templateType: '',
        file: null
      }
      // 清空upload组件
      uploadRef.value?.clearFiles()
      // 重新加载模版列表
      loadTemplates()
    } else {
      ElMessage.error(res.message || '上传失败')
    }
  } catch (error) {
    console.error('上传模版失败:', error)
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const downloadTemplateFile = async (template) => {
  try {
    const blob = await downloadTemplate(template.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = template.fileName || `${template.templateName}_v${template.version}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载模版失败:', error)
    ElMessage.error('下载失败')
  }
}

const deactivateTemplate = async (template) => {
  try {
    await ElMessageBox.confirm(
      `确认停用模版"${template.templateName}"（版本${template.version}）？停用后用户将无法下载此模版。`,
      '确认停用',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用删除API（软删除，会变为停用状态）
    const res = await deleteTemplateApi(template.id)
    
    if (res.success) {
      ElMessage.success('停用成功')
      loadTemplates()
    } else {
      ElMessage.error(res.message || '停用失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('停用模版失败:', error)
      ElMessage.error('停用失败')
    }
  }
}

const deleteTemplate = async (template) => {
  try {
    await ElMessageBox.confirm(
      `确认删除模版"${template.templateName}"（版本${template.version}）？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    const res = await deleteTemplateApi(template.id)
    
    if (res.success) {
      ElMessage.success('删除成功')
      loadTemplates()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除模版失败:', error)
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.system-templates-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-upload__tip {
  font-size: 12px;
  color: #909399;
  margin-top: 7px;
}
</style>
