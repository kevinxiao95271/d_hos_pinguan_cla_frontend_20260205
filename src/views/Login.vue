<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>浙江省品管大赛管理系统</h1>
        <p>Quality Competition Management System</p>
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
      </el-form>
      
      <div class="test-accounts">
        <el-divider>测试账号</el-divider>
        <div class="account-grid">
          <el-button
            v-for="account in testAccounts"
            :key="account.phone"
            size="small"
            @click="fillAccount(account)"
          >
            {{ account.label }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { loginWithPassword } from '@/api/auth'

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

const testAccounts = [
  // 旧系统测试账号（使用旧登录方式）
  { phone: '13799999112', name: '王建国', label: '测试-王建国', password: '（旧账号）' },
  { phone: '13800000127', name: 'CommitteeAdmin A', label: '组委会A', password: '（旧账号）' },
  { phone: '13800000005', name: 'OPS User 1', label: '运维1', password: '（旧账号）' }
]

const fillAccount = (account) => {
  form.phone = account.phone
  if (account.password && account.password !== '（旧账号）') {
    form.password = account.password
  } else {
    form.password = ''
  }
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

const goToRegister = () => {
  router.push('/register')
}

const handleForgotPassword = () => {
  ElMessage.info('密码重置功能开发中，请联系管理员')
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
        margin: 0 0 8px 0;
      }
      
      p {
        font-size: 14px;
        color: #999;
        margin: 0;
      }
    }
    
    .login-form {
      margin-bottom: 24px;

      .login-footer {
        display: flex;
        justify-content: space-between;
        margin-top: 16px;
      }
    }
    
    .test-accounts {
      .account-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        margin-top: 16px;
      }
    }
  }
}
</style>
