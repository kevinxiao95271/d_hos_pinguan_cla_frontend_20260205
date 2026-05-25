import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录 - 浙江省品管大赛' }
  },
  {
    path: '/mobile-qr',
    name: 'MobileQr',
    component: () => import('@/views/MobileQr.vue'),
    meta: { title: '面谈评审专家扫码入口', public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '用户注册 - 浙江省品管大赛' }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  // 参赛者端
  {
    path: '/contestant',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true, roles: ['CONTESTANT'] },
    children: [
      {
        path: 'dashboard',
        name: 'ContestantDashboard',
        component: () => import('@/views/contestant/Dashboard.vue'),
        meta: { title: '我的赛事' }
      },
      {
        path: 'competitions',
        name: 'ContestantCompetitions',
        component: () => import('@/views/contestant/Competitions.vue'),
        meta: { title: '赛事列表' }
      },
      {
        path: 'registrations',
        name: 'MyRegistrations',
        component: () => import('@/views/contestant/MyRegistrations.vue'),
        meta: { title: '我的报名' }
      },
      {
        path: 'register/:id',
        name: 'RegisterForm',
        component: () => import('@/views/contestant/RegisterForm.vue'),
        meta: { title: '报名表单' }
      },
      {
        path: 'registration/:id',
        name: 'RegistrationDetail',
        component: () => import('@/views/contestant/MyCompetition.vue'),
        meta: { title: '报名详情' }
      },
      {
        path: 'registration/:id/results',
        name: 'ReviewResults',
        component: () => import('@/views/contestant/ReviewResults.vue'),
        meta: { title: '评审结果' }
      }
    ]
  },
  // 评审专家端
  {
    path: '/reviewer',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true, roles: ['REVIEWER'] },
    children: [
      {
        path: 'dashboard',
        name: 'ReviewerDashboard',
        component: () => import('@/views/reviewer/Tasks.vue'),
        meta: { title: '评审任务' }
      },
      {
        path: 'tasks',
        redirect: '/reviewer/dashboard'
      },
      {
        path: 'review/:taskId',
        name: 'Review',
        component: () => import('@/views/reviewer/Review.vue'),
        meta: { title: '评分' }
      },
      {
        path: 'final-review/:taskId',
        name: 'FinalReview',
        component: () => import('@/views/reviewer/FinalReview.vue'),
        meta: { title: '决赛评分' }
      },
      {
        path: 'profile',
        name: 'ReviewerProfile',
        component: () => import('@/views/reviewer/Profile.vue'),
        meta: { title: '专家信息' }
      }
    ]
  },
  // 赛事管理者端
  {
    path: '/committee',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true, roles: ['COMMITTEE_ADMIN', 'OPS'] },
    redirect: '/committee/book-stage/registration',
    children: [
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/committee/Statistics.vue'),
        meta: { title: '报名统计' }
      },
      // 书审阶段子路由
      {
        path: 'book-stage/registration',
        name: 'BookStageRegistration',
        component: () => import('@/views/committee/book/Registration.vue'),
        meta: { title: '项目分组', parent: '书审阶段' }
      },
      {
        path: 'book-stage/reviewer',
        name: 'BookStageReviewer',
        component: () => import('@/views/committee/book/Reviewer.vue'),
        meta: { title: '评委分配', parent: '书审阶段' }
      },
      {
        path: 'book-stage/score',
        name: 'BookStageScore',
        component: () => import('@/views/committee/book/Score.vue'),
        meta: { title: '书审得分', parent: '书审阶段' }
      },
      {
        path: 'book-stage/feedback',
        name: 'BookStageFeedback',
        component: () => import('@/views/committee/book/Feedback.vue'),
        meta: { title: '专家意见反馈', parent: '书审阶段' }
      },
      // 面谈阶段子路由
      {
        path: 'interview-stage/group',
        name: 'InterviewStageGroup',
        component: () => import('@/views/committee/interview/Group.vue'),
        meta: { title: '面谈分组', parent: '面谈阶段' }
      },
      {
        path: 'interview-stage/reviewer',
        name: 'InterviewStageReviewer',
        component: () => import('@/views/committee/interview/Reviewer.vue'),
        meta: { title: '评委分配', parent: '面谈阶段' }
      },
      {
        path: 'interview-stage/score',
        name: 'InterviewStageScore',
        component: () => import('@/views/committee/interview/Score.vue'),
        meta: { title: '面谈得分', parent: '面谈阶段' }
      },
      {
        path: 'interview-stage/shortlist',
        name: 'InterviewStageShortlist',
        component: () => import('@/views/committee/interview/Shortlist.vue'),
        meta: { title: '入围管理', parent: '面谈阶段' }
      },
      {
        path: 'interview-stage/interview-only-ranking',
        name: 'InterviewOnlyRanking',
        component: () => import('@/views/committee/interview/InterviewOnlyRanking.vue'),
        meta: { title: '纯面谈排名', parent: '面谈阶段' }
      },
      // 决赛阶段子路由
      {
        path: 'final-stage/group',
        name: 'FinalStageGroup',
        component: () => import('@/views/committee/final/Group.vue'),
        meta: { title: '决赛分组', parent: '决赛阶段' }
      },
      {
        path: 'final-stage/reviewer',
        name: 'FinalStageReviewer',
        component: () => import('@/views/committee/final/Reviewer.vue'),
        meta: { title: '评委分配', parent: '决赛阶段' }
      },
      {
        path: 'final-stage/score',
        name: 'FinalStageScore',
        component: () => import('@/views/committee/final/Score.vue'),
        meta: { title: '现场打分', parent: '决赛阶段' }
      },
      {
        path: 'final-stage/ranking',
        name: 'FinalStageRanking',
        component: () => import('@/views/committee/final/Ranking.vue'),
        meta: { title: '最终排名', parent: '决赛阶段' }
      },
      {
        path: 'create-competition',
        name: 'CreateCompetition',
        component: () => import('@/views/committee/CreateCompetition.vue'),
        meta: { title: '创建赛事' }
      },
      {
        path: 'switch-competition',
        name: 'SwitchCompetition',
        component: () => import('@/views/committee/SwitchCompetition.vue'),
        meta: { title: '切换赛事' }
      },
      {
        path: 'historical-data',
        name: 'HistoricalData',
        component: () => import('@/views/committee/HistoricalData.vue'),
        meta: { title: '历史数据' }
      }
    ]
  },
  // 系统运维端
  {
    path: '/ops',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true, roles: ['COMMITTEE_ADMIN', 'OPS'] },
    children: [
      {
        path: 'dashboard',
        name: 'OpsDashboard',
        component: () => import('@/views/ops/Dashboard.vue'),
        meta: { title: '系统管理' }
      },
      {
        path: 'institutions',
        name: 'Institutions',
        component: () => import('@/views/ops/Institutions.vue'),
        meta: { title: '机构管理' }
      },
      {
        path: 'reviewers',
        name: 'Reviewers',
        component: () => import('@/views/ops/Reviewers.vue'),
        meta: { title: '评审专家管理' }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/ops/UserManagement.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'registrations',
        name: 'OpsRegistrations',
        component: () => import('@/views/ops/Registrations.vue'),
        meta: { title: '报名列表' }
      },
      {
        path: 'dictionaries',
        name: 'Dictionaries',
        component: () => import('@/views/ops/Dictionaries.vue'),
        meta: { title: '字典管理' }
      },
      {
        path: 'templates',
        name: 'SystemTemplates',
        component: () => import('@/views/ops/SystemTemplates.vue'),
        meta: { title: '系统模版管理' }
      },
      {
        path: 'datasource',
        name: 'Datasource',
        component: () => import('@/views/ops/Datasource.vue'),
        meta: { title: '数据源管理' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/ops/Settings.vue'),
        meta: { title: '系统设置' }
      }
    ]
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true, title: '首页' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  document.title = to.meta.title || '浙江省品管大赛'
  
  // 检查token是否过期
  if (userStore.isLoggedIn && userStore.isTokenExpired()) {
    console.warn('⚠️ Token已过期，清除登录状态')
    userStore.logout()
    
    // 如果当前要访问需要登录的页面，跳转到登录页
    if (to.meta.requiresAuth) {
      next('/login')
      return
    }
  }
  
  // 如果需要登录
  if (to.meta.requiresAuth) {
    if (!userStore.isLoggedIn) {
      next('/login')
      return
    }
    
    // 检查角色权限
    if (to.meta.roles && to.meta.roles.length > 0) {
      if (!to.meta.roles.includes(userStore.role)) {
        next('/dashboard')
        return
      }
    }
  }
  
  // 如果已登录访问登录页，重定向到首页
  if (to.path === '/login' && userStore.isLoggedIn) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router
