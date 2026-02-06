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
          />
        </el-form-item>
        
        <el-form-item prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入姓名"
            size="large"
            prefix-icon="User"
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  phone: '',
  name: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ]
}

const testAccounts = [
  // 推荐参赛者账号（有报名数据）⭐
  { phone: '13966000011', name: '参赛者11', label: '参赛者11⭐', role: 'CONTESTANT', institutionId: null },
  { phone: '13966000012', name: '参赛者12', label: '参赛者12⭐', role: 'CONTESTANT', institutionId: null },
  { phone: '13966000013', name: '参赛者13', label: '参赛者13⭐', role: 'CONTESTANT', institutionId: null },
  { phone: '13966000014', name: '参赛者14', label: '参赛者14⭐', role: 'CONTESTANT', institutionId: null },
  { phone: '13966000015', name: '参赛者15', label: '参赛者15⭐', role: 'CONTESTANT', institutionId: null },
  // 测试参赛者账号
  { phone: '13800000011', name: 'Contestant A', label: '参赛者A', role: 'CONTESTANT', institutionId: 1 },
  { phone: '13800000012', name: 'Contestant B', label: '参赛者B', role: 'CONTESTANT', institutionId: 2 },
  // 推荐评审专家账号（有任务数据）⭐
  { phone: '13800000021', name: '李明华', label: '李明华⭐', role: 'REVIEWER', institutionId: null },
  { phone: '13800002004', name: '孙丽娟', label: '孙丽娟⭐', role: 'REVIEWER', institutionId: null },
  // 测试评审专家账号
  { phone: '13800000022', name: 'Reviewer B', label: '评审专家B', role: 'REVIEWER', institutionId: 1 },
  // 组委会账号
  { phone: '13800000041', name: 'CommitteeAdmin A', label: '组委会A', role: 'COMMITTEE_ADMIN', institutionId: null },
  { phone: '13800000042', name: 'CommitteeAdmin B', label: '组委会B', role: 'COMMITTEE_ADMIN', institutionId: null },
  // 运维账号
  { phone: '13800000051', name: 'Ops A', label: '运维A', role: 'OPS', institutionId: null },
  { phone: '13800000052', name: 'Ops B', label: '运维B', role: 'OPS', institutionId: null }
]

const fillAccount = (account) => {
  form.phone = account.phone
  form.name = account.name
}

const handleLogin = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 查找测试账号信息
    const account = testAccounts.find(acc => acc.phone === form.phone)
    
    const loginData = {
      phone: form.phone,
      name: form.name,
      title: 'Test Title',
      role: account?.role || 'CONTESTANT',
      institutionId: account?.institutionId || null,
      reviewerGroupCode: account?.role === 'REVIEWER' ? 'A1' : null,
      interviewGroupCode: account?.role === 'REVIEWER' ? 'A1' : null,
      expertBackground: account?.role === 'REVIEWER' ? 'MEDICAL' : null
    }
    
    const res = await userStore.login(loginData)
    
    if (res.success) {
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
        router.push('/committee/book-stage/registration')
      } else {
        router.push('/dashboard')
      }
    }
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
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
