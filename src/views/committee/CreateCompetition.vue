<template>
  <div class="create-competition-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>创建赛事</span>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="140px"
      >
        <el-form-item label="赛事名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入赛事名称，不多于100字"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-divider content-position="left">资料模板</el-divider>
        
        <el-form-item label="报名表模板">
          <el-upload
            :auto-upload="false"
            :on-change="(file) => handleFileChange(file, 'registration')"
            :file-list="fileList.registration"
            :limit="1"
          >
            <el-button type="primary">选择文件</el-button>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="成果汇报书模板">
          <el-upload
            :auto-upload="false"
            :on-change="(file) => handleFileChange(file, 'report')"
            :file-list="fileList.report"
            :limit="1"
          >
            <el-button type="primary">选择文件</el-button>
          </el-upload>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submit">
            创建赛事
          </el-button>
          <el-button @click="goBack">
            返回
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createCompetition, uploadCompetitionTemplate } from '@/api/competition'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  name: ''
})

const rules = {
  name: [
    { required: true, message: '请输入赛事名称', trigger: 'blur' },
    { max: 100, message: '赛事名称不能超过100字', trigger: 'blur' }
  ]
}

const fileList = reactive({
  registration: [],
  report: []
})

const files = reactive({
  registration: null,
  report: null
})

const handleFileChange = (file, type) => {
  files[type] = file.raw
  fileList[type] = [file]
}

const submit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 创建赛事
    const res = await createCompetition({
      name: form.name
    })
    
    if (res.success && res.data) {
      const competitionId = res.data.id
      
      // 上传模板
      const uploadPromises = []
      if (files.registration) {
        uploadPromises.push(
          uploadCompetitionTemplate(competitionId, files.registration, 'registration')
        )
      }
      if (files.report) {
        uploadPromises.push(
          uploadCompetitionTemplate(competitionId, files.report, 'report')
        )
      }
      
      await Promise.all(uploadPromises)
      
      ElMessage.success('创建成功')
      router.push(`/committee/competition/${competitionId}`)
    }
  } catch (error) {
    console.error('创建赛事失败:', error)
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.back()
}
</script>

<style scoped lang="scss">
.create-competition-page {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
}
</style>
