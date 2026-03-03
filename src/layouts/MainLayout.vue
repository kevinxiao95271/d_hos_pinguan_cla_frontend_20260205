<template>
  <el-container class="main-layout">
    <el-header class="header">
      <div class="header-left">
        <h1 class="title">浙江省医院品管大赛管理系统</h1>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            <span>{{ userStore.userName }}</span>
            <span class="role-tag">{{ roleText }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container class="content-container">
      <el-aside :width="sidebarWidth" class="sidebar">
        <el-menu
          :default-active="activeMenu"
          :router="true"
          :collapse="isCollapse"
        >
          <template v-for="item in menuItems" :key="item.path">
            <el-sub-menu v-if="item.children" :index="item.path">
              <template #title>
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ item.title }}</span>
              </template>
              <el-menu-item
                v-for="child in item.children"
                :key="child.path"
                :index="child.path"
              >
                {{ child.title }}
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item v-else :index="item.path">
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
    
    <!-- Token 调试器 (仅开发环境显示) -->
    <TokenDebugger />
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import TokenDebugger from '@/components/TokenDebugger.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapse = ref(false)
const sidebarWidth = computed(() => isCollapse.value ? '64px' : '200px')

const roleText = computed(() => {
  const roleMap = {
    'CONTESTANT': '参赛者',
    'REVIEWER': '评审专家',
    'COMMITTEE_ADMIN': '赛事组委会',
    'OPS': '系统运维'
  }
  return roleMap[userStore.role] || ''
})

// 根据角色生成菜单
const menuItems = computed(() => {
  const role = userStore.role
  
  if (role === 'CONTESTANT') {
    return [
      { path: '/contestant/dashboard', title: '我的赛事', icon: 'House' },
      { path: '/contestant/registrations', title: '我的报名', icon: 'Document' },
      { path: '/contestant/competitions', title: '赛事列表', icon: 'Trophy' }
    ]
  }
  
  if (role === 'REVIEWER') {
    return [
      { path: '/reviewer/dashboard', title: '评审首页', icon: 'House' },
      { path: '/reviewer/tasks', title: '评审任务', icon: 'Document' }
    ]
  }
  
  if (role === 'COMMITTEE_ADMIN' || role === 'OPS') {
    const menu = [
      { path: '/committee/statistics', title: '报名统计', icon: 'DataAnalysis' },
      {
        path: '/committee/book',
        title: '书审阶段',
        icon: 'Document',
        children: [
          { path: '/committee/book-stage/registration', title: '项目分组' },
          { path: '/committee/book-stage/reviewer', title: '评委分配' },
          { path: '/committee/book-stage/score', title: '书审得分' },
          { path: '/committee/book-stage/feedback', title: '专家意见反馈' }
        ]
      },
      {
        path: '/committee/interview',
        title: '面谈阶段',
        icon: 'ChatDotRound',
        children: [
          { path: '/committee/interview-stage/group', title: '面谈分组' },
          { path: '/committee/interview-stage/reviewer', title: '评委分配' },
          { path: '/committee/interview-stage/score', title: '面谈得分' }
        ]
      },
      { path: '/committee/interview-stage/shortlist', title: '入围管理', icon: 'Select' },
      {
        path: '/committee/final',
        title: '决赛阶段',
        icon: 'Trophy',
        children: [
          { path: '/committee/final-stage/group', title: '决赛分组' },
          { path: '/committee/final-stage/reviewer', title: '评委分配' },
          { path: '/committee/final-stage/score', title: '现场打分' },
          { path: '/committee/final-stage/ranking', title: '最终排名' }
        ]
      },
      { path: '/committee/create-competition', title: '创建赛事', icon: 'Plus' },
      { path: '/committee/switch-competition', title: '切换赛事', icon: 'Switch' },
      { path: '/committee/historical-data', title: '历史数据', icon: 'FolderOpened' }
    ]
    
    if (role === 'OPS') {
      menu.push({
        path: '/ops',
        title: '系统管理',
        icon: 'Setting',
        children: [
          { path: '/ops/institutions', title: '机构管理' },
          { path: '/ops/reviewers', title: '评审专家管理' },
          { path: '/ops/users', title: '用户管理' },
          { path: '/ops/registrations', title: '报名列表' },
          { path: '/ops/templates', title: '系统模版管理' },
          { path: '/ops/dictionaries', title: '字典管理' },
          { path: '/ops/datasource', title: '数据源管理' },
          { path: '/ops/settings', title: '系统设置' }
        ]
      })
    }
    
    return menu
  }
  
  return []
})

const activeMenu = computed(() => route.path)

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  }
}
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fff;
    border-bottom: 1px solid #e8e8e8;
    padding: 0 20px;
    
    .header-left {
      .title {
        font-size: 20px;
        font-weight: 600;
        color: #1890ff;
        margin: 0;
      }
    }
    
    .header-right {
      .user-info {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        
        .role-tag {
          padding: 2px 8px;
          background: #e6f7ff;
          border: 1px solid #91d5ff;
          border-radius: 4px;
          font-size: 12px;
          color: #1890ff;
        }
      }
    }
  }
  
  .content-container {
    height: calc(100vh - 60px);
    
    .sidebar {
      background: #fff;
      border-right: 1px solid #e8e8e8;
      overflow-y: auto;
      
      .el-menu {
        border-right: none;
        background-color: #001529;
        
        :deep(.el-sub-menu__title) {
          font-weight: bold;
          color: #ffffff;
          
          &:hover {
            background-color: #1890ff !important;
          }
        }
        
        :deep(.el-menu-item) {
          color: #ffffff;
          font-weight: 500;
          
          &:hover {
            background-color: #1890ff !important;
            color: #ffffff !important;
          }
          
          &.is-active {
            color: #ffffff !important;
            font-weight: bold;
            background-color: #1890ff !important;
          }
        }
        
        :deep(.el-sub-menu__icon-arrow) {
          color: #ffffff;
        }
        
        :deep(.el-menu--inline) {
          background-color: #000c17;
        }
      }
    }
    
    .main-content {
      background: #f0f2f5;
      overflow-y: auto;
    }
  }
}
</style>
