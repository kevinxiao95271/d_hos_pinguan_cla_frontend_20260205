<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>浙江省医院品管大赛平台</h1>
      </div>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        label-width="0"
      >
        <el-form-item prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="请输入手机号"
            size="large"
            prefix-icon="Phone"
            maxlength="11"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="login-footer">
          <el-link type="primary" @click="goToRegister">
            还没有账号？立即注册
          </el-link>
          <el-link type="info" @click="handleForgotPassword">
            忘记密码？
          </el-link>
        </div>

        <div class="login-extra">
          <el-link type="info" underline="never" style="color: #67b3e8;" @click="showGuidePdf = true">
            📄 报名系统操作说明
          </el-link>
        </div>
      </el-form>
    </div>
  </div>

  <!-- 报名系统操作说明 PDF 预览弹窗 -->
  <el-dialog
    v-model="showGuidePdf"
    title="报名系统操作说明"
    width="80%"
    top="5vh"
    destroy-on-close
  >
    <template #header>
      <div style="display:flex; align-items:center; justify-content:space-between; width:100%;">
        <span style="font-size:16px; font-weight:600;">报名系统操作说明</span>
        <el-button type="primary" size="small" :icon="Download" @click="downloadGuidePdf">
          下载 PDF
        </el-button>
      </div>
    </template>
    <iframe
      :src="guidePdfUrl"
      style="width:100%; height:75vh; border:none;"
    />
  </el-dialog>

  <!-- 诚信须知强制阅读弹窗（支持多份按队列阅读） -->
  <el-dialog
    v-model="showNoticeDialog"
    :title="currentNoticeTitle"
    width="82%"
    top="3vh"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
  >
    <div style="margin-bottom: 10px; color: #e6a23c; font-weight: 600;">
      请认真阅读以下专家须知，阅读完毕后方可继续使用系统。
    </div>
    <iframe
      v-if="currentNoticePdfUrl"
      :key="currentNoticeKey"
      :src="currentNoticePdfUrl"
      style="width:100%; height:72vh; border:none;"
    />
    <template #footer>
      <div style="display:flex; align-items:center; justify-content:flex-end;">
        <el-button
          type="primary"
          :disabled="noticeCountdown > 0"
          :loading="confirmingNotice"
          @click="confirmNotice"
        >
          {{ noticeCountdown > 0 ? `请阅读完毕（${noticeCountdown}s）` : '确认已阅读，进入系统' }}
        </el-button>
      </div>
    </template>
  </el-dialog>

</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { loginWithPassword, confirmIntegrityNotice } from '@/api/auth'
import { ensureCurrentCompetition } from '@/utils/competition'
import {
  getIntegrityNoticeMeta,
  resolvePendingIntegrityNoticeKeys
} from '@/config/integrityNotices'

const router = useRouter()
const userStore = useUserStore()

// 页面加载时检查token是否过期
onMounted(() => {
  if (userStore.isLoggedIn && userStore.isTokenExpired()) {
    console.warn('⚠️ 检测到token已过期，清除登录状态')
    userStore.logout()
    ElMessage.warning('登录已过期，请重新登录')
  }
})

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  phone: '',
  password: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

// 诚信须知（pendingIntegrityQueue 顺序即阅读顺序）
const showNoticeDialog = ref(false)
const pendingIntegrityQueue = ref([])
const noticeCountdown = ref(0)
const confirmingNotice = ref(false)
const baseUrl = import.meta.env.BASE_URL
let noticeTimer = null

const currentNoticeKey = computed(() => pendingIntegrityQueue.value[0] || '')
const currentNoticeMeta = computed(() =>
  currentNoticeKey.value ? getIntegrityNoticeMeta(currentNoticeKey.value) : null
)
const currentNoticeTitle = computed(
  () => currentNoticeMeta.value?.title || '浙江省医院品管大赛专家须知'
)
const currentNoticePdfUrl = computed(() => {
  const file = currentNoticeMeta.value?.pdfFile
  return file ? `${baseUrl}${file}` : ''
})

const startNoticeCountdown = () => {
  noticeCountdown.value = 5
  if (noticeTimer) clearInterval(noticeTimer)
  noticeTimer = setInterval(() => {
    noticeCountdown.value--
    if (noticeCountdown.value <= 0) clearInterval(noticeTimer)
  }, 1000)
}
const navigateAfterLogin = async (role) => {
  if (role === 'CONTESTANT') {
    router.push('/contestant/dashboard')
  } else if (role === 'REVIEWER') {
    router.push('/reviewer/dashboard')
  } else if (role === 'COMMITTEE_ADMIN') {
    await initializeCompetitionForAdmin()
    router.push('/committee/book-stage/registration')
  } else if (role === 'OPS') {
    router.push('/ops/institutions')
  } else {
    router.push('/dashboard')
  }
}

const confirmNotice = async () => {
  const key = currentNoticeKey.value
  if (!key) return
  confirmingNotice.value = true
  try {
    await confirmIntegrityNotice({ noticeKey: key })
  } catch {
    // 后端未实现时忽略错误，不阻塞流程
  } finally {
    confirmingNotice.value = false
  }
  pendingIntegrityQueue.value.shift()
  if (pendingIntegrityQueue.value.length > 0) {
    startNoticeCountdown()
    return
  }
  showNoticeDialog.value = false
  await navigateAfterLogin(userStore.role)
}

const handleLogin = async () => {
  try {
    await formRef.value.validate()
    loading.value = true

    const res = await loginWithPassword({ phone: form.phone, password: form.password })

    if (res.success && res.data) {
      userStore.setUserInfo(res.data)
      ElMessage.success('登录成功')

      // 评审专家：新字段 pendingIntegrityNoticeKeys 优先；否则回退旧 noticeConfirmed
      const pendingKeys = resolvePendingIntegrityNoticeKeys(res.data)
      if (userStore.role === 'REVIEWER' && pendingKeys.length > 0) {
        pendingIntegrityQueue.value = [...pendingKeys]
        showNoticeDialog.value = true
        startNoticeCountdown()
      } else {
        await navigateAfterLogin(userStore.role)
      }
    } else {
      ElMessage.error(res.message || '手机号或密码错误')
    }
  } catch (error) {
    console.error('登录失败:', error)
    const message = error.response?.data?.message || error.message || '登录失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

// 为赛事管理者自动初始化当前赛事
const initializeCompetitionForAdmin = async () => {
  console.log('⏳ 正在为赛事管理者初始化赛事...')
  await ensureCurrentCompetition()
}

const goToRegister = () => {
  router.push('/register')
}

const handleForgotPassword = () => {
  ElMessage.info('密码重置功能开发中，请联系管理员')
}

// 报名系统操作说明 PDF
const showGuidePdf = ref(false)
const guidePdfUrl = `${import.meta.env.BASE_URL}registration_guide.pdf`
const downloadGuidePdf = () => {
  const a = document.createElement('a')
  a.href = guidePdfUrl
  a.download = '报名系统操作说明.pdf'
  a.click()
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  .login-box {
    width: 420px;
    padding: 40px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    
    .login-header {
      text-align: center;
      margin-bottom: 32px;
      
      h1 {
        font-size: 24px;
        font-weight: 600;
        color: #333;
        margin: 0;
      }
    }
    
    .login-form {
      .login-footer {
        display: flex;
        justify-content: space-between;
        margin-top: 16px;
      }
      .login-extra {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
        margin-top: 12px;
      }
    }
  }
}
</style>
