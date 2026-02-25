<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h1>用户注册</h1>
        <p>Quality Competition Management System</p>
      </div>

      <!-- 步骤指示器 -->
      <el-steps :active="step - 1" align-center class="steps">
        <el-step title="选择机构" />
        <el-step title="填写信息" />
      </el-steps>

      <!-- 步骤1: 选择机构 -->
      <div v-show="step === 1" class="step-content">
        <InstitutionSelector @select="handleInstitutionSelect" />
        
        <div class="step-actions">
          <el-button @click="goToLogin">返回登录</el-button>
          <el-button 
            type="primary" 
            :disabled="!selectedInstitution"
            @click="goToStep2"
          >
            下一步
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 填写注册信息 -->
      <div v-show="step === 2" class="step-content">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          class="register-form"
        >
          <!-- 所属机构（只读） -->
          <el-form-item label="所属机构">
            <el-input
              :value="selectedInstitution?.displayText || selectedInstitution?.name"
              disabled
            />
          </el-form-item>

          <!-- 手机号 -->
          <el-form-item label="手机号" prop="phone">
            <el-input
              v-model="form.phone"
              placeholder="请输入手机号"
              maxlength="11"
            />
          </el-form-item>

          <!-- 密码 -->
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="6-20位密码"
              show-password
              maxlength="20"
            />
          </el-form-item>

          <!-- 确认密码 -->
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="再次输入密码"
              show-password
              maxlength="20"
            />
          </el-form-item>

          <!-- 姓名 -->
          <el-form-item label="姓名" prop="name">
            <el-input
              v-model="form.name"
              placeholder="请输入真实姓名"
              maxlength="50"
            />
          </el-form-item>

          <!-- 职称 -->
          <el-form-item label="职称">
            <el-input
              v-model="form.title"
              placeholder="如：主任医师"
              maxlength="50"
            />
          </el-form-item>

          <el-form-item>
            <el-button @click="step = 1">上一步</el-button>
            <el-button
              type="primary"
              :loading="loading"
              @click="handleRegister"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import InstitutionSelector from '@/components/InstitutionSelector.vue'
import { register } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const step = ref(1)
const selectedInstitution = ref(null)
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  phone: '',
  password: '',
  confirmPassword: '',
  name: '',
  title: ''
})

// 自定义验证规则
const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6 || value.length > 20) {
    callback(new Error('密码长度必须在6-20位之间'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在2-50位之间', trigger: 'blur' }
  ]
}

// 机构选择回调
const handleInstitutionSelect = (institution) => {
  selectedInstitution.value = institution
}

// 进入第二步
const goToStep2 = () => {
  if (!selectedInstitution.value) {
    ElMessage.warning('请先选择所属机构')
    return
  }
  step.value = 2
}

// 返回登录
const goToLogin = () => {
  router.push('/login')
}

// 提交注册
const handleRegister = async () => {
  try {
    await formRef.value.validate()
    
    loading.value = true

    const registerData = {
      phone: form.phone,
      password: form.password,
      confirmPassword: form.confirmPassword,
      name: form.name,
      title: form.title || null,
      role: 'CONTESTANT',
      institutionId: selectedInstitution.value.id
    }

    const res = await register(registerData)

    if (res.success && res.data) {
      ElMessage.success('注册成功！')

      // 保存Token和用户信息
      userStore.setUserInfo(res.data)

      // 跳转到参赛者首页
      setTimeout(() => {
        router.push('/contestant/dashboard')
      }, 500)
    } else {
      ElMessage.error(res.message || '注册失败')
    }
  } catch (error) {
    console.error('注册失败:', error)
    const message = error.response?.data?.message || error.message || '注册失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;

  .register-box {
    width: 100%;
    max-width: 900px;
    padding: 40px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);

    .register-header {
      text-align: center;
      margin-bottom: 32px;

      h1 {
        font-size: 28px;
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

    .steps {
      margin-bottom: 32px;
    }

    .step-content {
      .step-actions {
        margin-top: 24px;
        display: flex;
        justify-content: space-between;
      }

      .register-form {
        max-width: 500px;
        margin: 0 auto;
      }
    }
  }
}
</style>
