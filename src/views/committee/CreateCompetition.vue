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
        label-width="160px"
      >
        <el-form-item label="赛事名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入赛事名称，不多于100字"
            maxlength="100"
            show-word-limit
            style="width: 400px"
          />
        </el-form-item>

        <el-divider content-position="left">赛事时间段</el-divider>

        <el-form-item label="报名时间" prop="registerStart">
          <el-date-picker
            v-model="form.registerStart"
            type="datetime"
            placeholder="报名开始"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 200px"
          />
          <span style="margin: 0 8px; color: #909399;">至</span>
          <el-date-picker
            v-model="form.registerEnd"
            type="datetime"
            placeholder="报名结束"
            value-format="YYYY-MM-DDTHH:mm:ss"
            :default-time="new Date(2000, 0, 1, 23, 59, 59)"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="书审时间" prop="bookReviewStart">
          <el-date-picker
            v-model="form.bookReviewStart"
            type="datetime"
            placeholder="书审开始"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 200px"
          />
          <span style="margin: 0 8px; color: #909399;">至</span>
          <el-date-picker
            v-model="form.bookReviewEnd"
            type="datetime"
            placeholder="书审结束"
            value-format="YYYY-MM-DDTHH:mm:ss"
            :default-time="new Date(2000, 0, 1, 23, 59, 59)"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="面谈时间" prop="interviewStart">
          <el-date-picker
            v-model="form.interviewStart"
            type="datetime"
            placeholder="面谈开始"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 200px"
          />
          <span style="margin: 0 8px; color: #909399;">至</span>
          <el-date-picker
            v-model="form.interviewEnd"
            type="datetime"
            placeholder="面谈结束"
            value-format="YYYY-MM-DDTHH:mm:ss"
            :default-time="new Date(2000, 0, 1, 23, 59, 59)"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="决赛时间" prop="finalStart">
          <el-date-picker
            v-model="form.finalStart"
            type="datetime"
            placeholder="决赛开始"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 200px"
          />
          <span style="margin: 0 8px; color: #909399;">至</span>
          <el-date-picker
            v-model="form.finalEnd"
            type="datetime"
            placeholder="决赛结束"
            value-format="YYYY-MM-DDTHH:mm:ss"
            :default-time="new Date(2000, 0, 1, 23, 59, 59)"
            style="width: 200px"
          />
        </el-form-item>

        <el-divider content-position="left">分组前缀配置（选填，默认 A / B / C）</el-divider>

        <el-alert
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 16px; max-width: 600px"
        >
          <template #default>
            前缀用于生成分组编号，如 A1、A2、B1、C1。一旦赛事开始分组，前缀将锁定不可修改。
          </template>
        </el-alert>

        <el-form-item label="基层组前缀">
          <el-input
            v-model="form.basicGroupPrefix"
            placeholder="默认 A"
            maxlength="5"
            style="width: 120px"
          />
          <span style="margin-left: 8px; color: #909399; font-size: 13px">生成 {{ (form.basicGroupPrefix || 'A') }}1、{{ (form.basicGroupPrefix || 'A') }}2…</span>
        </el-form-item>

        <el-form-item label="综合组前缀">
          <el-input
            v-model="form.comprehensiveGroupPrefix"
            placeholder="默认 B"
            maxlength="5"
            style="width: 120px"
          />
          <span style="margin-left: 8px; color: #909399; font-size: 13px">生成 {{ (form.comprehensiveGroupPrefix || 'B') }}1、{{ (form.comprehensiveGroupPrefix || 'B') }}2…</span>
        </el-form-item>

        <el-form-item label="进阶组前缀">
          <el-input
            v-model="form.advancedGroupPrefix"
            placeholder="默认 C"
            maxlength="5"
            style="width: 120px"
          />
          <span style="margin-left: 8px; color: #909399; font-size: 13px">生成 {{ (form.advancedGroupPrefix || 'C') }}1、{{ (form.advancedGroupPrefix || 'C') }}2…</span>
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
          <el-button @click="goBack">返回</el-button>
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
  name: '',
  registerStart: '',
  registerEnd: '',
  bookReviewStart: '',
  bookReviewEnd: '',
  interviewStart: '',
  interviewEnd: '',
  finalStart: '',
  finalEnd: '',
  basicGroupPrefix: '',
  comprehensiveGroupPrefix: '',
  advancedGroupPrefix: ''
})

const rules = {
  name: [
    { required: true, message: '请输入赛事名称', trigger: 'blur' },
    { max: 100, message: '赛事名称不能超过100字', trigger: 'blur' }
  ]
}

const fileList = reactive({ registration: [], report: [] })
const files = reactive({ registration: null, report: null })

const handleFileChange = (file, type) => {
  files[type] = file.raw
  fileList[type] = [file]
}

const submit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    const payload = { name: form.name }
    if (form.registerStart) payload.registerStart = form.registerStart
    if (form.registerEnd) payload.registerEnd = form.registerEnd
    if (form.bookReviewStart) payload.bookReviewStart = form.bookReviewStart
    if (form.bookReviewEnd) payload.bookReviewEnd = form.bookReviewEnd
    if (form.interviewStart) payload.interviewStart = form.interviewStart
    if (form.interviewEnd) payload.interviewEnd = form.interviewEnd
    if (form.finalStart) payload.finalStart = form.finalStart
    if (form.finalEnd) payload.finalEnd = form.finalEnd
    if (form.basicGroupPrefix) payload.basicGroupPrefix = form.basicGroupPrefix
    if (form.comprehensiveGroupPrefix) payload.comprehensiveGroupPrefix = form.comprehensiveGroupPrefix
    if (form.advancedGroupPrefix) payload.advancedGroupPrefix = form.advancedGroupPrefix

    const res = await createCompetition(payload)

    if (res.success && res.data) {
      const competitionId = res.data.id
      const uploadPromises = []
      if (files.registration) uploadPromises.push(uploadCompetitionTemplate(competitionId, files.registration, 'registration'))
      if (files.report) uploadPromises.push(uploadCompetitionTemplate(competitionId, files.report, 'report'))
      await Promise.all(uploadPromises)

      ElMessage.success('创建成功，赛事状态为草稿，激活后参赛者可报名')
      router.push('/committee/competitions')
    } else {
      ElMessage.error(res.message || '创建失败')
    }
  } catch (error) {
    if (error?.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    }
    console.error('创建赛事失败:', error)
  } finally {
    submitting.value = false
  }
}

const goBack = () => router.back()
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
