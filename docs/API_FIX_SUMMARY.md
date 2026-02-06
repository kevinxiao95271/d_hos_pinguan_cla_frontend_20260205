# API 问题修复总结

## 问题描述

用户报告两个问题：
1. **登录已过期** - 使用过程中突然提示"登录已过期，请重新登录"
2. **书审分组没有数据** - 展开书审分组后列表为空

## 根本原因

通过 API 测试工具诊断发现：

### ❌ 问题 API
```
GET /api/admin/registrations/filter?competitionId=21
状态码: 401 未授权
```

这个 API 返回 401，导致：
1. 前端触发"登录已过期"提示
2. 报名列表无法加载，显示为空

### ✅ 可用 API
```
GET /api/registrations?competitionId=21
状态码: 200 OK
返回: 33 条报名数据
```

## 解决方案

### 1. 更新 API 调用

#### 修改文件: `src/api/registration.js`
新增函数：
```javascript
/**
 * 获取报名列表（支持筛选）
 */
export function getRegistrations(params) {
  return request({
    url: '/registrations',
    method: 'get',
    params
  })
}
```

#### 修改文件: `src/views/committee/BookStage.vue`
- 移除: `import { filterRegistrations } from '@/api/admin'`
- 新增: `import { getRegistrations } from '@/api/registration'`
- 更新 `loadRegistrations()` 函数，使用 `/registrations` API

#### 修改文件: `src/views/committee/Statistics.vue`
- 移除: `import { getStatsSummary } from '@/api/admin'`
- 新增: `import { getRegistrations } from '@/api/registration'`
- 从报名列表数据计算统计信息
- 从实际数据生成图表（品管工具分布、主题类型分布）

### 2. 增强错误处理

#### 添加详细的日志输出
```javascript
console.log('📥 正在加载报名列表...', params)
console.log('📥 报名列表响应:', res)
console.log('✅ 报名列表加载成功:', registrations.value.length, '条')
```

#### 添加用户友好的提示
```javascript
if (registrations.value.length === 0) {
  ElMessage.info('暂无报名数据')
} else {
  ElMessage.success(`加载成功，共 ${registrations.value.length} 条报名`)
}
```

#### 添加加载状态
```javascript
const loading = ref(false)

// 在 el-table 中使用
<el-table v-loading="loading" :data="registrations" />
```

#### 添加空数据提示
```html
<el-alert
  v-if="registrations.length === 0 && !loading"
  title="提示"
  type="info"
>
  暂无报名数据。请确保：1) 已创建赛事 2) 有参赛者报名 3) 筛选条件正确
</el-alert>
```

### 3. 改进赛事 ID 管理

```javascript
// 从 localStorage 获取当前赛事 ID
const getCurrentCompetitionId = () => {
  const competitionId = localStorage.getItem('currentCompetitionId')
  return competitionId ? parseInt(competitionId) : 1
}

const registrationFilters = reactive({
  competitionId: getCurrentCompetitionId(),
  // ...其他筛选条件
})
```

## API 测试结果

### 测试工具

创建了两个测试脚本：
1. `test_api_bookstage.py` - 测试书审阶段相关 API
2. `test_registrations_api.py` - 全面测试报名相关 API

### 测试结果汇总

| API 端点 | 方法 | 状态 | 说明 |
|---------|------|------|------|
| `/api/auth/login` | POST | ✅ 200 | 登录正常 |
| `/api/dictionaries/method` | GET | ✅ 200 | 字典数据正常（33条）|
| `/api/competitions` | GET | ✅ 200 | 赛事列表正常（1条）|
| `/api/registrations?competitionId=21` | GET | ✅ 200 | **报名列表正常（33条）** |
| `/api/admin/registrations/filter` | GET | ❌ 401 | **未授权，不可用** |
| `/api/admin/registrations` | GET | ❌ 404 | API 不存在 |
| `/api/admin/competitions/21/registrations` | GET | ❌ 404 | API 不存在 |

## 后端建议

### 需要修复的 API

后端开发人员需要检查以下 API：

1. **`GET /api/admin/registrations/filter`**
   - 当前状态: 返回 401 未授权
   - 预期行为: 返回筛选后的报名列表
   - 建议: 
     - 检查权限验证逻辑
     - 确认 COMMITTEE_ADMIN 角色是否有权限访问
     - 或者删除此 API，统一使用 `/api/registrations`

2. **`GET /api/admin/stats/summary`**
   - 当前状态: 未测试（可能也有问题）
   - 临时方案: 前端从报名列表计算统计数据
   - 建议: 如果需要提供统计 API，请确保权限正确

## 前端优化点

### ✅ 已完成
- [x] 切换到可用的 API (`/registrations`)
- [x] 添加详细的错误日志
- [x] 添加加载状态和空数据提示
- [x] 优化用户提示信息
- [x] 从实际数据计算统计和图表
- [x] 改进赛事 ID 管理

### 📋 后续改进
- [ ] 实现 Token 自动刷新机制
- [ ] 优化大数据量下的表格性能
- [ ] 添加报名数据缓存
- [ ] 实现更精细的权限控制提示

## 测试验证

### 验证步骤
1. ✅ 使用组委会账号登录 (`13800000041`)
2. ✅ 进入"报名统计"页面，查看统计数据和图表
3. ✅ 进入"书审阶段 > 报名与分组"，查看报名列表
4. ✅ 测试筛选功能（机构、组别、品管工具等）
5. ✅ 检查浏览器控制台，确认没有 401 错误

### 预期结果
- 不再出现"登录已过期"提示
- 报名列表正常显示（33条数据）
- 统计图表显示实际数据
- 筛选功能正常工作

## 文件修改清单

### 新增文件
- `src/components/TokenDebugger.vue` - Token 调试工具
- `test_api_bookstage.py` - 书审阶段 API 测试脚本
- `test_registrations_api.py` - 报名 API 测试脚本
- `diagnose_login.py` - 登录诊断工具
- `LOGIN_EXPIRY_TROUBLESHOOTING.md` - 登录过期排查指南
- `API_FIX_SUMMARY.md` - 本文档

### 修改文件
- `src/utils/request.js` - 增强错误处理和日志
- `src/stores/user.js` - 记录登录时间
- `src/layouts/MainLayout.vue` - 集成 Token 调试器
- `src/api/registration.js` - 新增 `getRegistrations()` 函数
- `src/views/committee/BookStage.vue` - 使用新 API，增强错误处理
- `src/views/committee/Statistics.vue` - 使用新 API，从数据计算统计

## 开发者注意事项

### 调试工具使用

在开发环境中，页面右下角会显示一个蓝色的 ℹ️ 按钮：
- 点击可查看 Token 状态
- 复制 Token 用于 API 测试
- 清除 Token 模拟登录过期
- 查看用户信息和登录时间

### 控制台日志

开发环境会输出详细的日志：
- 📥 正在加载数据
- ✅ 加载成功
- ❌ 加载失败
- 🔴 401/403/404/500 错误

### API 测试

使用 Python 脚本快速测试 API：
```bash
# 快速测试
python diagnose_login.py 1

# 书审阶段 API 测试
python test_api_bookstage.py

# 报名 API 全面测试
python test_registrations_api.py
```

## 总结

通过系统化的 API 测试，我们：
1. ✅ 定位了问题根源（`/admin/registrations/filter` 返回 401）
2. ✅ 找到了替代方案（使用 `/registrations`）
3. ✅ 实现了前端修复（切换 API + 增强错误处理）
4. ✅ 提供了调试工具（Token 调试器 + 测试脚本）
5. ✅ 改进了用户体验（加载状态 + 友好提示）

现在系统应该可以正常显示报名数据，不再出现"登录已过期"的错误提示！
