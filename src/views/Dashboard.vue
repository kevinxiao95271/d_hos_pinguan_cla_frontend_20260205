<template>
  <div class="dashboard">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>欢迎使用浙江省医院品管大赛平台</span>
        </div>
      </template>
      
      <el-result
        icon="success"
        title="登录成功"
        :sub-title="`欢迎您，${userStore.userName}（${roleText}）`"
      >
        <template #extra>
          <el-button type="primary" @click="goToHome">
            进入系统
          </el-button>
        </template>
      </el-result>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const roleText = computed(() => {
  const roleMap = {
    'CONTESTANT': '参赛者',
    'REVIEWER': '评审专家',
    'COMMITTEE_ADMIN': '赛事组委会',
    'OPS': '系统运维',
    'OPERATOR': '会场监督员'
  }
  return roleMap[userStore.role] || ''
})

const goToHome = () => {
  const role = userStore.role
  if (role === 'CONTESTANT') {
    router.push('/contestant/dashboard')
  } else if (role === 'REVIEWER') {
    router.push('/reviewer/dashboard')
  } else if (role === 'COMMITTEE_ADMIN') {
    router.push('/committee/statistics')
  } else if (role === 'OPS') {
    router.push('/committee/statistics')
  } else if (role === 'OPERATOR') {
    router.push('/operator/scores')
  }
}
</script>

<style scoped lang="scss">
.dashboard {
  padding: 20px;
  
  .card-header {
    font-size: 18px;
    font-weight: 600;
  }
}
</style>
