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

</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { loginWithPassword } from '@/api/auth'
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

const handleLogin = async () => {
  try {
    await formRef.value.validate()
    loading.value = true

    const loginData = {
      phone: form.phone,
      password: form.password
    }

    const res = await loginWithPassword(loginData)

    if (res.success && res.data) {
      userStore.setUserInfo(res.data)
      ElMessage.success('登录成功')

      // 根据角色跳转到对应页面
      const role = userStore.role
      if (role === 'CONTESTANT') {
        router.push('/contestant/dashboard')
      } else if (role === 'REVIEWER') {
        router.push('/reviewer/dashboard')
      } else if (role === 'COMMITTEE_ADMIN') {
        // 赛事管理者：自动初始化当前赛事
        await initializeCompetitionForAdmin()
        router.push('/committee/book-stage/registration')
      } else if (role === 'OPS') {
        router.push('/ops/institutions')
      } else {
        router.push('/dashboard')
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
