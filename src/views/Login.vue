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
    <div class="pdf-scroll-wrap">
      <div v-if="guidePdfLoading" class="pdf-loading">加载中...</div>
      <VuePdfEmbed
        :source="guidePdfUrl"
        @loaded="guidePdfLoading = false"
        @loading-failed="guidePdfLoading = false"
      />
    </div>
  </el-dialog>

  <!-- 移动端扫码入口弹窗 -->
  <el-dialog v-model="showQrDialog" title="面谈评审专家请扫码登录" width="340px" align-center>
    <div style="display:flex; flex-direction:column; align-items:center; gap:16px; padding:8px 0;">
      <qrcode-vue :value="mobileLoginUrl" :size="220" level="H" />
      <div style="font-size:13px; color:#909399;">扫码后使用专家账号登录即可打分</div>
      <el-button size="small" @click="openFullscreen">全屏投屏</el-button>
    </div>
  </el-dialog>

  <!-- 决赛须知强制阅读弹窗 -->
  <el-dialog
    v-model="showNoticeDialog"
    title="2026年专家评审纪律及评审要求"
    width="760px"
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    align-center
  >
    <div class="notice-pdf-wrap">
      <iframe
        :src="noticePdfUrl"
        class="notice-pdf-frame"
        title="专家评审纪律及评审要求"
      />
    </div>
    <template #footer>
      <div class="notice-footer">
        <span class="notice-hint">请仔细阅读以上内容，阅读完毕后点击确认</span>
        <el-button type="primary" :loading="confirmingNotice" @click="handleConfirmNotice">
          我已阅读并同意遵守
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
import QrcodeVue from 'qrcode.vue'
import { loginWithPassword, confirmIntegrityNotice } from '@/api/auth'
import { ensureCurrentCompetition } from '@/utils/competition'

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

// ── 决赛须知 ──────────────────────────────────────────────────────
const showNoticeDialog = ref(false)
const confirmingNotice = ref(false)
const noticePdfUrl = `${import.meta.env.BASE_URL}reviewer_discipline.pdf`

const handleConfirmNotice = async () => {
  confirmingNotice.value = true
  try {
    await confirmIntegrityNotice({ noticeKey: 'FINAL' })
  } catch {
    // 幂等，忽略错误
  } finally {
    confirmingNotice.value = false
  }
  showNoticeDialog.value = false
  await navigateAfterLogin(userStore.role)
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

const handleLogin = async () => {
  try {
    await formRef.value.validate()
    loading.value = true

    const res = await loginWithPassword({ phone: form.phone, password: form.password })

    if (res.success && res.data) {
      userStore.setUserInfo(res.data)
      ElMessage.success('登录成功')

      const pendingKeys = res.data?.pendingIntegrityNoticeKeys || []
      if (userStore.role === 'REVIEWER' && pendingKeys.includes('FINAL')) {
        showNoticeDialog.value = true
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

// 移动端扫码二维码
const showQrDialog = ref(false)
const mobileLoginUrl = `${window.location.origin}${import.meta.env.BASE_URL}login`
const openFullscreen = () => {
  window.open(`${import.meta.env.BASE_URL}mobile-qr`, '_blank')
}

// 报名系统操作说明 PDF
const showGuidePdf = ref(false)
const guidePdfLoading = ref(true)
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
  padding: 16px;
  box-sizing: border-box;

  .login-box {
    width: 420px;
    max-width: 100%;
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

.pdf-scroll-wrap {
  max-height: 72vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.pdf-loading {
  text-align: center;
  padding: 40px 0;
  color: #909399;
  font-size: 14px;
}

@media (max-width: 480px) {
  .login-container {
    align-items: flex-start;
    padding-top: 40px;

    .login-box {
      padding: 28px 20px;

      .login-header {
        margin-bottom: 24px;

        h1 {
          font-size: 20px;
        }
      }
    }
  }
}

.notice-pdf-wrap {
  height: 500px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.notice-pdf-frame {
  width: 100%;
  height: 100%;
  border: none;
}

.notice-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;

  .notice-hint {
    font-size: 13px;
    color: #909399;
  }
}
</style>
