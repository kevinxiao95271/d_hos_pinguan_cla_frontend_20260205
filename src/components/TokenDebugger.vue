<template>
  <div v-if="isDev" class="token-debugger">
    <el-button
      circle
      size="small"
      type="info"
      @click="visible = !visible"
    >
      <el-icon><InfoFilled /></el-icon>
    </el-button>
    
    <el-dialog
      v-model="visible"
      title="Token 调试信息"
      width="600px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="Token 状态">
          <el-tag :type="hasToken ? 'success' : 'danger'">
            {{ hasToken ? '已登录' : '未登录' }}
          </el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="Token">
          <el-text class="token-text" truncated>
            {{ tokenPreview }}
          </el-text>
          <el-button
            v-if="hasToken"
            size="small"
            text
            @click="copyToken"
          >
            复制
          </el-button>
        </el-descriptions-item>
        
        <el-descriptions-item label="用户信息">
          <pre>{{ userInfoText }}</pre>
        </el-descriptions-item>
        
        <el-descriptions-item label="当前路由">
          {{ currentRoute }}
        </el-descriptions-item>
        
        <el-descriptions-item label="登录时间">
          {{ loginTime }}
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <el-button @click="refreshToken">刷新 Token</el-button>
        <el-button type="danger" @click="clearToken">清除 Token</el-button>
        <el-button type="primary" @click="visible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'

const route = useRoute()
const visible = ref(false)

const isDev = import.meta.env.DEV

const hasToken = computed(() => {
  return !!localStorage.getItem('token')
})

const tokenPreview = computed(() => {
  const token = localStorage.getItem('token')
  if (!token) return '无'
  if (token.length > 50) {
    return token.substring(0, 30) + '...' + token.substring(token.length - 10)
  }
  return token
})

const userInfoText = computed(() => {
  const userInfo = localStorage.getItem('userInfo')
  if (!userInfo) return '无'
  try {
    return JSON.stringify(JSON.parse(userInfo), null, 2)
  } catch {
    return userInfo
  }
})

const currentRoute = computed(() => route.path)

const loginTime = computed(() => {
  const time = localStorage.getItem('loginTime')
  return time || '未知'
})

const copyToken = () => {
  const token = localStorage.getItem('token')
  if (token) {
    navigator.clipboard.writeText(token)
    ElMessage.success('Token 已复制到剪贴板')
  }
}

const refreshToken = () => {
  ElMessage.info('Token 刷新功能待实现')
}

const clearToken = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  localStorage.removeItem('loginTime')
  localStorage.removeItem('currentCompetitionId')
  ElMessage.success('Token 已清除')
  visible.value = false
  setTimeout(() => {
    window.location.reload()
  }, 500)
}
</script>

<style scoped lang="scss">
.token-debugger {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
}

.token-text {
  max-width: 300px;
  font-family: monospace;
  font-size: 12px;
}

pre {
  margin: 0;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}
</style>
