<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>
      
      <el-alert
        title="提示"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        系统配置修改后立即生效，请谨慎操作
      </el-alert>
      
      <el-form :model="form" label-width="200px" style="max-width: 800px">
        <el-divider content-position="left">报名限制</el-divider>
        
        <el-form-item label="机构报名配额限制">
          <el-input-number 
            v-model="form.maxRegistrationsPerInstitution" 
            :min="1" 
            :max="50" 
          />
          <span style="margin-left: 8px; color: #606266">
            个项目/机构（当前生效：{{ form.maxRegistrationsPerInstitution }}）
          </span>
        </el-form-item>
        
        <el-form-item label="">
          <el-text type="info" size="small">
            限制单个医疗机构在同一赛事中可报名的最大项目数量
          </el-text>
        </el-form-item>
        
        <el-divider content-position="left">评审设置</el-divider>
        
        <el-form-item label="评审专家最大负荷">
          <el-input-number v-model="form.reviewerMaxLoad" :min="1" :max="100" />
          <span style="margin-left: 8px; color: #909399">个项目（暂未实现）</span>
        </el-form-item>
        
        <el-divider content-position="left">分组设置</el-divider>
        
        <el-form-item label="基层组分组数量">
          <el-input-number v-model="form.basicGroupCount" :min="1" :max="20" />
          <span style="margin-left: 8px; color: #909399">个（暂未实现）</span>
        </el-form-item>
        
        <el-form-item label="综合组分组数量">
          <el-input-number v-model="form.comprehensiveGroupCount" :min="1" :max="20" />
          <span style="margin-left: 8px; color: #909399">个（暂未实现）</span>
        </el-form-item>
        
        <el-form-item label="进阶组分组数量">
          <el-input-number v-model="form.advancedGroupCount" :min="1" :max="20" />
          <span style="margin-left: 8px; color: #909399">个（暂未实现）</span>
        </el-form-item>
        
        <el-divider content-position="left">入围设置</el-divider>
        
        <el-form-item label="入围比例">
          <el-input-number v-model="form.shortlistRatio" :min="0" :max="100" :step="0.1" />
          <span style="margin-left: 8px; color: #909399">%（暂未实现）</span>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="saveSettings">
            保存设置
          </el-button>
          <el-button @click="loadSettings">刷新</el-button>
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
  maxRegistrationsPerInstitution: 8,  // 机构报名配额限制（已实现）
  reviewerMaxLoad: 10,                 // 评审专家最大负荷（未实现）
  basicGroupCount: 5,                  // 基层组分组数量（未实现）
  comprehensiveGroupCount: 5,          // 综合组分组数量（未实现）
  advancedGroupCount: 5,               // 进阶组分组数量（未实现）
  shortlistRatio: 30                   // 入围比例（未实现）
})

const loadSettings = async () => {
  try {
    const keys = Object.keys(form)
    
    // 逐个查询配置项，忽略不存在的配置项
    for (const key of keys) {
      try {
        const res = await getSetting(key)
        if (res.success && res.data) {
          // 后端返回的是 settingValue 字段，需要转换为数字
          const value = res.data.settingValue || res.data.value
          if (value !== undefined && value !== null) {
            form[key] = Number(value)
          }
        }
      } catch (error) {
        // 配置项不存在或查询失败，使用默认值
        console.log(`配置项 ${key} 不存在或查询失败，使用默认值 ${form[key]}`)
      }
    }
    
    console.log('✅ 配置加载完成:', form)
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.warning('部分配置加载失败，使用默认值')
  }
}

const saveSettings = async () => {
  try {
    saving.value = true
    
    // 只保存已实现的配置项
    const implementedKeys = ['maxRegistrationsPerInstitution']
    let successCount = 0
    let failCount = 0
    
    for (const [key, value] of Object.entries(form)) {
      try {
        const res = await saveSetting({ 
          key, 
          value: String(value)  // 后端需要字符串格式
        })
        
        if (res.success) {
          successCount++
          console.log(`✅ ${key} 保存成功:`, value)
        } else {
          failCount++
          console.warn(`⚠️ ${key} 保存失败:`, res.message)
        }
      } catch (error) {
        failCount++
        console.error(`❌ ${key} 保存异常:`, error)
      }
    }
    
    if (successCount > 0) {
      ElMessage.success(`保存成功 (${successCount}/${Object.keys(form).length})`)
      
      // 重新加载配置确认
      await loadSettings()
    } else {
      ElMessage.error('保存失败，请检查权限')
    }
    
    if (failCount > 0 && successCount > 0) {
      ElMessage.warning(`部分配置保存失败 (${failCount} 个)`)
    }
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存失败')
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
