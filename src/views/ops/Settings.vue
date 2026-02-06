<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="200px" style="max-width: 800px">
        <el-divider content-position="left">评审设置</el-divider>
        
        <el-form-item label="评审专家最大负荷">
          <el-input-number v-model="form.reviewerMaxLoad" :min="1" :max="100" />
          <span style="margin-left: 8px">个项目</span>
        </el-form-item>
        
        <el-divider content-position="left">分组设置</el-divider>
        
        <el-form-item label="基层组分组数量">
          <el-input-number v-model="form.basicGroupCount" :min="1" :max="20" />
          <span style="margin-left: 8px">个</span>
        </el-form-item>
        
        <el-form-item label="综合组分组数量">
          <el-input-number v-model="form.comprehensiveGroupCount" :min="1" :max="20" />
          <span style="margin-left: 8px">个</span>
        </el-form-item>
        
        <el-form-item label="进阶组分组数量">
          <el-input-number v-model="form.advancedGroupCount" :min="1" :max="20" />
          <span style="margin-left: 8px">个</span>
        </el-form-item>
        
        <el-divider content-position="left">入围设置</el-divider>
        
        <el-form-item label="入围比例">
          <el-input-number v-model="form.shortlistRatio" :min="0" :max="100" :step="0.1" />
          <span style="margin-left: 8px">%</span>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="saveSettings">
            保存设置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSetting, saveSetting } from '@/api/admin'

const saving = ref(false)

const form = reactive({
  reviewerMaxLoad: 10,
  basicGroupCount: 5,
  comprehensiveGroupCount: 5,
  advancedGroupCount: 5,
  shortlistRatio: 30
})

const loadSettings = async () => {
  try {
    const keys = Object.keys(form)
    const promises = keys.map(key => getSetting(key))
    const results = await Promise.all(promises)
    
    results.forEach((res, index) => {
      if (res.success && res.data) {
        form[keys[index]] = res.data.value
      }
    })
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

const saveSettings = async () => {
  try {
    saving.value = true
    
    const promises = Object.entries(form).map(([key, value]) =>
      saveSetting({ key, value })
    )
    
    await Promise.all(promises)
    
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped lang="scss">
.settings-page {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
}
</style>
