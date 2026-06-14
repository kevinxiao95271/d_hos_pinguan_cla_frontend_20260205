<template>
  <el-container class="main-layout">
    <el-header class="header">
      <div class="header-left">
        <el-icon v-if="isMobile" class="hamburger" @click="drawerOpen = true"><Expand /></el-icon>
        <h1 class="title">浙江省医院品管大赛平台</h1>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            <span class="user-name">{{ userStore.userName }}</span>
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

    <!-- 移动端抽屉菜单 -->
    <el-drawer v-model="drawerOpen" direction="ltr" size="240px" :with-header="false">
      <el-menu
        :default-active="activeMenu"
        :router="true"
        @select="drawerOpen = false"
        class="drawer-menu"
      >
        <template v-for="item in menuItems" :key="item.path">
          <el-sub-menu v-if="item.children" :index="item.path" class="level-1-submenu">
            <template #title>
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </template>
            <template v-for="child in item.children" :key="child.path">
              <el-sub-menu v-if="child.children" :index="child.path" class="level-2-submenu">
                <template #title>
                  <el-icon v-if="child.icon"><component :is="child.icon" /></el-icon>
                  <span>{{ child.title }}</span>
                </template>
                <el-menu-item v-for="grandchild in child.children" :key="grandchild.path" :index="grandchild.path" class="level-3-item">
                  {{ grandchild.title }}
                </el-menu-item>
              </el-sub-menu>
              <el-menu-item v-else :index="child.path" class="level-2-item">
                <el-icon v-if="child.icon"><component :is="child.icon" /></el-icon>
                {{ child.title }}
              </el-menu-item>
            </template>
          </el-sub-menu>
          <el-menu-item v-else :index="item.path" class="level-1-item">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-drawer>

    <el-container class="content-container">
      <el-aside v-if="!isMobile" :width="sidebarWidth" class="sidebar">
        <el-menu
          :default-active="activeMenu"
          :router="true"
          :collapse="isCollapse"
        >
          <template v-for="item in menuItems" :key="item.path">
            <!-- 一级：有子项 → el-sub-menu -->
            <el-sub-menu v-if="item.children" :index="item.path" class="level-1-submenu">
              <template #title>
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ item.title }}</span>
              </template>
              <!-- 二级遍历 -->
              <template v-for="child in item.children" :key="child.path">
                <!-- 二级：有孙子项 → 嵌套 el-sub-menu -->
                <el-sub-menu v-if="child.children" :index="child.path" class="level-2-submenu">
                  <template #title>
                    <el-icon v-if="child.icon"><component :is="child.icon" /></el-icon>
                    <span>{{ child.title }}</span>
                  </template>
                  <!-- 三级菜单项 -->
                  <el-menu-item
                    v-for="grandchild in child.children"
                    :key="grandchild.path"
                    :index="grandchild.path"
                    class="level-3-item"
                  >
                    {{ grandchild.title }}
                  </el-menu-item>
                </el-sub-menu>
                <!-- 二级：无孙子项 → 普通 el-menu-item -->
                <el-menu-item v-else :index="child.path" class="level-2-item">
                  <el-icon v-if="child.icon"><component :is="child.icon" /></el-icon>
                  {{ child.title }}
                </el-menu-item>
              </template>
            </el-sub-menu>
            <!-- 一级：无子项 → 直接 el-menu-item -->
            <el-menu-item v-else :index="item.path" class="level-1-item">
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
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Expand } from '@element-plus/icons-vue'
import TokenDebugger from '@/components/TokenDebugger.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapse = ref(false)
const sidebarWidth = computed(() => isCollapse.value ? '64px' : '220px')

// 移动端检测
const isMobile = ref(window.innerWidth <= 768)
const drawerOpen = ref(false)
const onResize = () => { isMobile.value = window.innerWidth <= 768 }
onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))

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
      { path: '/reviewer/dashboard', title: '评审任务', icon: 'Document' },
      { path: '/reviewer/profile', title: '专家信息', icon: 'User' }
    ]
  }
  
  if (role === 'OPERATOR') {
    return [
      { path: '/operator/scores', title: '会场评分', icon: 'DataLine' }
    ]
  }

  if (role === 'COMMITTEE_ADMIN' || role === 'OPS') {
    const menu = [
      // 一级：报名情况（含二级子项）
      {
        path: '/committee/registration-overview',
        title: '报名情况',
        icon: 'DataAnalysis',
        children: [
          { path: '/committee/statistics', title: '报名统计' },
          { path: '/ops/registrations', title: '报名详情' }
        ]
      },
      // 一级：书审阶段
      {
        path: '/committee/book',
        title: '书审阶段',
        icon: 'Document',
        children: [
          { path: '/committee/book-stage/registration', title: '项目分组' },
          { path: '/committee/book-stage/reviewer', title: '评委分配' },
          { path: '/committee/book-stage/score', title: '书审标化得分' },
          { path: '/committee/book-stage/feedback', title: '专家意见反馈' }
        ]
      },
      // 一级：面谈阶段
      {
        path: '/committee/interview',
        title: '面谈阶段',
        icon: 'ChatDotRound',
        children: [
          { path: '/committee/interview-stage/group', title: '面谈分组' },
          { path: '/committee/interview-stage/reviewer', title: '评委分配' },
          { path: '/committee/interview-stage/score', title: '面谈标化得分' },
          { path: '/committee/interview-stage/interview-only-ranking', title: '纯面谈排名' }
        ]
      },
      // 一级：入围管理（无子项）
      { path: '/committee/interview-stage/shortlist', title: '入围管理', icon: 'Select' },
      // 一级：决赛阶段
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
      // 一级：系统管理（三级菜单）
      {
        path: '/system-mgmt',
        title: '系统管理',
        icon: 'Setting',
        children: [
          // 二级：账户管理 → 三级
          {
            path: '/system-mgmt/account',
            title: '账户管理',
            icon: 'UserFilled',
            children: [
              { path: '/ops/institutions', title: '医疗机构管理' },
              { path: '/ops/reviewers', title: '评审专家管理' },
              { path: '/ops/users', title: '用户登录管理' }
            ]
          },
          // 二级：赛事管理 → 三级
          {
            path: '/system-mgmt/competition',
            title: '赛事管理',
            icon: 'Management',
            children: [
              { path: '/ops/settings', title: '规则设置' },
              { path: '/committee/create-competition', title: '创建赛事' },
              { path: '/committee/switch-competition', title: '切换赛事' }
            ]
          },
          // 二级：历史数据（无三级）
          { path: '/committee/historical-data', title: '历史数据', icon: 'FolderOpened' }
        ]
      }
    ]

    // OPS 角色额外追加技术管理项
    if (role === 'OPS') {
      const sysMgmt = menu.find(m => m.path === '/system-mgmt')
      sysMgmt.children.push({
        path: '/system-mgmt/tech',
        title: '技术配置',
        icon: 'Tools',
        children: [
          { path: '/ops/templates', title: '系统模版管理' },
          { path: '/ops/dictionaries', title: '字典管理' },
          { path: '/ops/datasource', title: '数据源管理' }
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
      display: flex;
      align-items: center;
      gap: 10px;

      .hamburger {
        font-size: 22px;
        color: #1890ff;
        cursor: pointer;
        flex-shrink: 0;
      }

      .title {
        font-size: 20px;
        font-weight: 600;
        color: #1890ff;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }

    .header-right {
      flex-shrink: 0;

      .user-info {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;

        .user-name {
          white-space: nowrap;
        }

        .role-tag {
          padding: 2px 8px;
          background: #e6f7ff;
          border: 1px solid #91d5ff;
          border-radius: 4px;
          font-size: 12px;
          color: #1890ff;
          white-space: nowrap;
        }
      }
    }
  }

  @media (max-width: 768px) {
    .header {
      padding: 0 12px;

      .header-left .title {
        font-size: 15px;
      }

      .header-right .user-info {
        .user-name { display: none; }
        .role-tag  { display: none; }
      }
    }

    .main-content {
      padding: 12px 8px;
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
        // 侧边栏整体渐变背景
        background: linear-gradient(180deg, #001d3d 0%, #000e1f 100%);

        // ── 一级：sub-menu 标题（有子项的折叠组）──
        :deep(.level-1-submenu > .el-sub-menu__title) {
          font-size: 13.5px;
          font-weight: 700;
          color: #e8f4ff;
          letter-spacing: 0.6px;
          // 渐变左边框：用 background 模拟（蓝→青）
          background-image: linear-gradient(to bottom, #1890ff, #36cfc9),
                            linear-gradient(to right, rgba(24, 144, 255, 0.08), transparent);
          background-size: 3px 100%, 100% 100%;
          background-position: left center, left center;
          background-repeat: no-repeat, no-repeat;
          padding-left: 18px !important;

          .el-icon {
            // 图标也做渐变（用 filter 近似）
            color: #40c9ff;
            font-size: 15px;
            filter: drop-shadow(0 0 4px rgba(64, 201, 255, 0.5));
          }

          &:hover {
            background-image: linear-gradient(to bottom, #1890ff, #36cfc9),
                              linear-gradient(90deg, rgba(24, 144, 255, 0.18), transparent 80%);
            background-size: 3px 100%, 100% 100%;
            background-color: transparent !important;
          }
        }

        // ── 一级：直接菜单项（无子项，如"入围管理"）──
        :deep(.level-1-item) {
          font-size: 13.5px;
          font-weight: 700;
          color: #e8f4ff;
          letter-spacing: 0.6px;
          background-image: linear-gradient(to bottom, #1890ff, #36cfc9),
                            linear-gradient(to right, rgba(24, 144, 255, 0.08), transparent);
          background-size: 3px 100%, 100% 100%;
          background-position: left center, left center;
          background-repeat: no-repeat, no-repeat;
          padding-left: 18px !important;

          .el-icon {
            color: #40c9ff;
            font-size: 15px;
            filter: drop-shadow(0 0 4px rgba(64, 201, 255, 0.5));
          }

          &:hover {
            background-image: linear-gradient(to bottom, #1890ff, #36cfc9),
                              linear-gradient(90deg, rgba(24, 144, 255, 0.25), transparent 80%);
            background-size: 3px 100%, 100% 100%;
            background-color: transparent !important;
            color: #ffffff !important;
          }

          &.is-active {
            background-image: linear-gradient(to bottom, #1890ff, #36cfc9),
                              linear-gradient(90deg, rgba(24, 144, 255, 0.3), transparent 80%);
            background-size: 3px 100%, 100% 100%;
            background-color: transparent !important;
            color: #ffffff !important;
          }
        }

        // ── 二级 sub-menu 标题（有三级子项）──
        :deep(.level-2-submenu > .el-sub-menu__title) {
          font-size: 13px;
          font-weight: 500;
          color: #69b1ff;
          padding-left: 30px !important;

          .el-icon {
            color: #69b1ff;
            font-size: 13px;
          }

          &:hover {
            background: linear-gradient(90deg, rgba(105, 177, 255, 0.12), transparent 80%) !important;
            color: #91caff !important;
          }
        }

        // ── 二级菜单项（无三级子项，如"历史数据"）──
        :deep(.level-2-item) {
          font-size: 13px;
          font-weight: 400;
          color: #69b1ff;
          padding-left: 30px !important;

          &:hover {
            background: linear-gradient(90deg, rgba(24, 144, 255, 0.25), transparent 80%) !important;
            color: #ffffff !important;
          }

          &.is-active {
            background: linear-gradient(90deg, rgba(24, 144, 255, 0.35), transparent 85%) !important;
            color: #91caff !important;
            font-weight: 600;
          }
        }

        // ── 三级菜单项 ──
        :deep(.level-3-item) {
          font-size: 12.5px;
          font-weight: 400;
          color: #91caff;
          padding-left: 48px !important;

          &:hover {
            background: linear-gradient(90deg, rgba(54, 207, 201, 0.2), transparent 80%) !important;
            color: #ffffff !important;
          }

          &.is-active {
            background: linear-gradient(90deg, rgba(54, 207, 201, 0.28), transparent 85%) !important;
            color: #b5f5ec !important;
            font-weight: 600;
          }
        }

        // ── 箭头颜色 ──
        :deep(.el-sub-menu__icon-arrow) {
          color: #4d8fcc;
        }

        // ── 二级展开背景 ──
        :deep(.el-menu--inline) {
          background: linear-gradient(180deg, #001428 0%, #000b1a 100%);
        }

        // ── 三级展开背景 ──
        :deep(.el-menu--inline .el-menu--inline) {
          background: linear-gradient(180deg, #000a14 0%, #00060e 100%);
        }
      }
    }
    
    .main-content {
      background: #f0f2f5;
      overflow-y: auto;
    }
  }
}

// 抽屉菜单继承侧边栏深色风格
:global(.drawer-menu) {
  height: 100%;
  background: linear-gradient(180deg, #001d3d 0%, #000e1f 100%) !important;
  border-right: none;

  .el-menu-item,
  .el-sub-menu__title {
    color: #e8f4ff;

    &:hover {
      background: rgba(24, 144, 255, 0.15) !important;
      color: #fff !important;
    }

    &.is-active {
      background: rgba(24, 144, 255, 0.25) !important;
      color: #fff !important;
    }
  }

  .el-menu--inline {
    background: rgba(0, 0, 0, 0.2) !important;
  }
}
</style>
