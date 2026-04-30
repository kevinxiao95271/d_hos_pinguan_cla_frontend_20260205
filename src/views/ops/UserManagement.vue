<template>
  <div class="user-management">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalUsers || 0 }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value text-primary">{{ stats.contestants || 0 }}</div>
            <div class="stat-label">参赛者</div>
            <div class="stat-sub">({{ stats.contestantsEnabled || 0 }} 启用)</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value text-warning">{{ stats.reviewers || 0 }}</div>
            <div class="stat-label">评委</div>
            <div class="stat-sub">({{ stats.reviewersEnabled || 0 }} 启用)</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value text-danger">{{ stats.disabledUsers || 0 }}</div>
            <div class="stat-label">已禁用</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索和操作栏 -->
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="手机号">
          <el-input
            v-model="searchForm.phone"
            placeholder="手机号"
            clearable
            style="width: 180px"
          />
        </el-form-item>

        <el-form-item label="姓名">
          <el-input
            v-model="searchForm.name"
            placeholder="姓名"
            clearable
            style="width: 150px"
          />
        </el-form-item>

        <el-form-item label="角色">
          <el-select
            v-model="searchForm.role"
            placeholder="全部"
            clearable
            style="width: 150px"
          >
            <el-option label="参赛者" value="CONTESTANT" />
            <el-option label="评委" value="REVIEWER" />
            <el-option label="组委会管理员" value="COMMITTEE_ADMIN" />
            <el-option label="系统运维" value="OPS" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="searchForm.enabled"
            placeholder="全部"
            clearable
            style="width: 120px"
          >
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" icon="Plus" @click="showCreateReviewerDialog">
            创建评委
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card shadow="never" class="table-card">
      <el-table
        :data="users"
        border
        stripe
        v-loading="tableLoading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="phone" label="手机号" width="120" align="center" />
        <el-table-column prop="name" label="姓名" width="100" align="center" />
        <el-table-column prop="title" label="职称" width="120" align="center" show-overflow-tooltip />
        <el-table-column prop="role" label="角色" width="130" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.role === 'CONTESTANT'" type="info">参赛者</el-tag>
            <el-tag v-else-if="row.role === 'REVIEWER'" type="warning">评委</el-tag>
            <el-tag v-else-if="row.role === 'COMMITTEE_ADMIN'" type="danger">组委会管理员</el-tag>
            <el-tag v-else-if="row.role === 'OPS'" type="danger">系统运维</el-tag>
            <el-tag v-else>{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="institutionName" label="所属机构" min-width="200" show-overflow-tooltip />
        <el-table-column prop="region" label="地区" width="100" align="center" />
        <el-table-column prop="enabled" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.enabled" type="success">启用</el-tag>
            <el-tag v-else type="danger">禁用</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastLoginAt" label="最后登录" width="170" align="center">
          <template #default="{ row }">
            {{ row.lastLoginAt ? formatDate(row.lastLoginAt) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.enabled"
              size="small"
              type="warning"
              @click="handleDisable(row)"
            >
              禁用
            </el-button>
            <el-button
              v-else
              size="small"
              type="success"
              @click="handleEnable(row)"
            >
              启用
            </el-button>
            <el-button
              size="small"
              type="primary"
              @click="handleResetPassword(row)"
            >
              重置密码
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @current-change="loadUsers"
        @size-change="handleSizeChange"
      />
    </el-card>

    <!-- 创建评委对话框 -->
    <el-dialog
      v-model="createReviewerVisible"
      title="创建评委账号"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="reviewerFormRef"
        :model="reviewerForm"
        :rules="reviewerRules"
        label-width="100px"
      >
        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="reviewerForm.phone"
            placeholder="请输入手机号"
            maxlength="11"
          />
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="reviewerForm.name"
            placeholder="请输入姓名"
            maxlength="50"
          />
        </el-form-item>

        <el-form-item label="职称">
          <el-input
            v-model="reviewerForm.title"
            placeholder="如：主任医师"
            maxlength="50"
          />
        </el-form-item>

        <el-form-item label="所属机构" prop="institutionId">
          <div v-if="selectedReviewerInstitution" class="selected-inst">
            <el-tag type="success" closable @close="selectedReviewerInstitution = null">
              {{ selectedReviewerInstitution.displayText || selectedReviewerInstitution.name }}
            </el-tag>
          </div>
          <el-button v-else @click="showInstitutionDialog = true" style="width: 100%">
            选择机构
          </el-button>
        </el-form-item>

        <el-form-item label="专家背景">
          <el-input
            v-model="reviewerForm.expertBackground"
            placeholder="如：心内科"
            maxlength="100"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createReviewerVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreateReviewer">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 机构选择对话框 -->
    <el-dialog
      v-model="showInstitutionDialog"
      title="选择所属机构"
      width="800px"
      :close-on-click-modal="false"
    >
      <InstitutionSelector @select="handleReviewerInstitutionSelect" />
      <template #footer>
        <el-button @click="showInstitutionDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 初始密码对话框 -->
    <el-dialog
      v-model="passwordVisible"
      :title="createdReviewer.institutionName === '-' ? '密码重置成功' : '评委账号创建成功'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-alert
        type="success"
        :closable="false"
        :description="createdReviewer.institutionName === '-' ? '新密码已生成，请立即记录' : '请立即记录以下信息并通知评委'"
        style="margin-bottom: 20px"
      />

      <div class="password-info">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="手机号">
            {{ createdReviewer.phone }}
          </el-descriptions-item>
          <el-descriptions-item label="姓名">
            {{ createdReviewer.name }}
          </el-descriptions-item>
          <el-descriptions-item :label="createdReviewer.institutionName === '-' ? '新密码' : '初始密码'">
            <span class="initial-password">{{ createdReviewer.initialPassword }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="所属机构" v-if="createdReviewer.institutionName !== '-'">
            {{ createdReviewer.institutionName }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <el-alert
        type="warning"
        :closable="false"
        :description="createdReviewer.institutionName === '-' ? '请及时通知用户新密码' : '请提醒评委首次登录后尽快修改密码'"
        style="margin-top: 20px"
      />

      <template #footer>
        <el-button type="primary" @click="passwordVisible = false">
          已记录
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import InstitutionSelector from '@/components/InstitutionSelector.vue'
import { queryUsers, createReviewer, disableUser, enableUser, getUserStatistics } from '@/api/user'
import { resetUserPassword } from '@/api/admin'

// 统计数据
const stats = reactive({
  totalUsers: 0,
  enabledUsers: 0,
  disabledUsers: 0,
  contestants: 0,
  contestantsEnabled: 0,
  reviewers: 0,
  reviewersEnabled: 0,
  committeeAdmins: 0,
  opsAdmins: 0
})

// 搜索表单
const searchForm = reactive({
  phone: '',
  name: '',
  role: '',
  institutionId: null,
  enabled: null
})

// 用户列表
const users = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableLoading = ref(false)

// 创建评委对话框
const createReviewerVisible = ref(false)
const creating = ref(false)
const reviewerFormRef = ref(null)
const selectedReviewerInstitution = ref(null)
const showInstitutionDialog = ref(false)
const reviewerForm = reactive({
  phone: '',
  name: '',
  title: '',
  institutionId: null,
  expertBackground: ''
})

const reviewerRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  institutionId: [
    { required: true, message: '请选择所属机构', trigger: 'change' }
  ]
}

// 初始密码对话框
const passwordVisible = ref(false)
const createdReviewer = reactive({
  phone: '',
  name: '',
  initialPassword: '',
  institutionName: ''
})

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 加载统计数据
const loadStats = async () => {
  try {
    const res = await getUserStatistics()
    if (res.success && res.data) {
      Object.assign(stats, res.data)
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 加载用户列表
const loadUsers = async () => {
  tableLoading.value = true
  try {
    // 构建参数，过滤空字符串（后端不接受空字符串，但接受null或不传）
    const params = {
      page: currentPage.value - 1,
      size: pageSize.value
    }
    
    // 只添加非空的搜索条件
    if (searchForm.phone) params.phone = searchForm.phone
    if (searchForm.name) params.name = searchForm.name
    if (searchForm.role) params.role = searchForm.role
    if (searchForm.institutionId) params.institutionId = searchForm.institutionId
    if (searchForm.enabled !== null && searchForm.enabled !== undefined) {
      params.enabled = searchForm.enabled
    }

    const res = await queryUsers(params)
    if (res.success && res.data) {
      users.value = res.data.content
      total.value = res.data.totalElements
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    tableLoading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadUsers()
}

// 重置
const handleReset = () => {
  Object.assign(searchForm, {
    phone: '',
    name: '',
    role: '',
    institutionId: null,
    enabled: null
  })
  currentPage.value = 1
  loadUsers()
}

// 分页大小变化
const handleSizeChange = () => {
  currentPage.value = 1
  loadUsers()
}

// 显示创建评委对话框
const showCreateReviewerDialog = () => {
  Object.assign(reviewerForm, {
    phone: '',
    name: '',
    title: '',
    institutionId: null,
    expertBackground: ''
  })
  selectedReviewerInstitution.value = null
  createReviewerVisible.value = true
}

// 评委机构选择回调
const handleReviewerInstitutionSelect = (institution) => {
  if (institution) {
    selectedReviewerInstitution.value = institution
    reviewerForm.institutionId = institution.id
    showInstitutionDialog.value = false
  }
}

// 创建评委
const handleCreateReviewer = async () => {
  try {
    await reviewerFormRef.value.validate()

    creating.value = true

    const data = {
      phone: reviewerForm.phone,
      name: reviewerForm.name,
      title: reviewerForm.title || null,
      institutionId: reviewerForm.institutionId,
      expertBackground: reviewerForm.expertBackground || null
    }

    const res = await createReviewer(data)

    if (res.success && res.data) {
      ElMessage.success('评委账号创建成功')

      // 显示初始密码
      Object.assign(createdReviewer, res.data)
      createReviewerVisible.value = false
      passwordVisible.value = true

      // 刷新列表和统计
      loadUsers()
      loadStats()
    } else {
      ElMessage.error(res.message || '创建失败')
    }
  } catch (error) {
    console.error('创建评委失败:', error)
    const message = error.response?.data?.message || error.message || '创建失败'
    ElMessage.error(message)
  } finally {
    creating.value = false
  }
}

// 禁用用户
const handleDisable = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确认禁用用户 ${user.name}（${user.phone}）？`,
      '提示',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res = await disableUser(user.id)

    if (res.success) {
      ElMessage.success('已禁用')
      loadUsers()
      loadStats()
    } else {
      ElMessage.error(res.message || '禁用失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('禁用用户失败:', error)
      const message = error.response?.data?.message || error.message || '禁用失败'
      ElMessage.error(message)
    }
  }
}

// 启用用户
const handleEnable = async (user) => {
  try {
    const res = await enableUser(user.id)

    if (res.success) {
      ElMessage.success('已启用')
      loadUsers()
      loadStats()
    } else {
      ElMessage.error(res.message || '启用失败')
    }
  } catch (error) {
    console.error('启用用户失败:', error)
    const message = error.response?.data?.message || error.message || '启用失败'
    ElMessage.error(message)
  }
}

// 重置密码
const handleResetPassword = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确认重置用户 ${user.name}（${user.phone}）的密码？将生成6位随机密码。`,
      '重置密码',
      {
        confirmButtonText: '确认重置',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res = await resetUserPassword(user.id)

    if (res.success) {
      // 显示新密码
      createdReviewer.phone = user.phone
      createdReviewer.name = user.name
      createdReviewer.initialPassword = res.data.newPassword
      createdReviewer.institutionName = user.institutionName || '-'
      passwordVisible.value = true
      
      ElMessage.success('密码重置成功')
    } else {
      ElMessage.error(res.message || '密码重置失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重置密码失败:', error)
      const message = error.response?.data?.message || error.message || '密码重置失败'
      ElMessage.error(message)
    }
  }
}

// 初始化
onMounted(() => {
  loadStats()
  loadUsers()
})
</script>

<style scoped lang="scss">
.user-management {
  padding: 20px;

  .stats-row {
    margin-bottom: 20px;

    .stat-card {
      .stat-content {
        text-align: center;

        .stat-value {
          font-size: 32px;
          font-weight: 600;
          color: #333;
          margin-bottom: 8px;

          &.text-primary {
            color: #409eff;
          }

          &.text-warning {
            color: #e6a23c;
          }

          &.text-danger {
            color: #f56c6c;
          }
        }

        .stat-label {
          font-size: 14px;
          color: #666;
          margin-bottom: 4px;
        }

        .stat-sub {
          font-size: 12px;
          color: #999;
        }
      }
    }
  }

  .search-card {
    margin-bottom: 20px;

    .search-form {
      margin: 0;
    }
  }

  .table-card {
    .pagination {
      margin-top: 20px;
      display: flex;
      justify-content: center;
    }
  }

  .password-info {
    .initial-password {
      font-size: 24px;
      font-weight: 600;
      color: #e6a23c;
      font-family: 'Courier New', monospace;
    }
  }
}
</style>
