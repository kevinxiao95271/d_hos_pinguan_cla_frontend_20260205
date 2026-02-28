# 全局当前赛事API集成

## 概述

后端实现了全局当前赛事管理功能，由系统运维或赛事组委会统一设置当前赛事，所有用户共享同一个当前赛事ID。前端已完成API集成，替换了原有的localStorage方案。

---

## 后端API

### 1️⃣ 获取当前活跃赛事ID

**接口地址**: `GET /api/admin/current-competition`  
**权限要求**: ✅ 所有已登录用户（需要有效token）

**请求示例**:
```javascript
const response = await axios.get('/api/admin/current-competition', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

**响应示例（成功）**:
```json
{
  "code": 0,
  "message": "success",
  "data": 123
}
```

### 2️⃣ 设置当前活跃赛事

**接口地址**: `POST /api/admin/current-competition`  
**权限要求**: 🔒 仅限以下角色
- `COMMITTEE_ADMIN` - 评委会管理员
- `COMMITTEE` - 评委会成员
- `OPS` - 运维管理员

**请求示例**:
```javascript
await axios.post('/api/admin/current-competition', null, {
  params: {
    competitionId: 123
  },
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

**响应示例（成功）**:
```json
{
  "code": 0,
  "message": "success",
  "data": "已设置当前赛事ID: 123"
}
```

**响应示例（权限不足）**:
```json
{
  "code": -1,
  "message": "权限不足",
  "data": null
}
```

---

## 前端实现

### 1. API封装 (`src/api/competition.js`)

新增两个API方法：

```javascript
/**
 * 获取当前活跃赛事ID
 * 所有已登录用户可调用
 */
export function getCurrentCompetition() {
  return request({
    url: '/admin/current-competition',
    method: 'get'
  })
}

/**
 * 设置当前活跃赛事
 * 仅管理员角色可调用 (COMMITTEE_ADMIN, COMMITTEE, OPS)
 */
export function setCurrentCompetition(competitionId) {
  return request({
    url: '/admin/current-competition',
    method: 'post',
    params: { competitionId }
  })
}
```

### 2. 工具函数重构 (`src/utils/competition.js`)

#### 核心改动

**原方案**: 所有赛事ID存储和读取都依赖localStorage  
**新方案**: 使用后端API作为主要来源，localStorage仅作缓存

#### 关键函数

**`getCurrentCompetitionId()` - 异步版本**
```javascript
export async function getCurrentCompetitionId() {
  try {
    const res = await getCurrentCompetition()
    if (res.code === 0 && res.data) {
      // 同步到localStorage作为缓存
      localStorage.setItem('currentCompetitionId', res.data)
      return res.data
    }
  } catch (error) {
    console.warn('⚠️ 获取当前赛事失败，使用本地缓存:', error.message)
  }
  
  // Fallback到localStorage
  const id = localStorage.getItem('currentCompetitionId')
  return id ? parseInt(id) : null
}
```

**`getCurrentCompetitionIdSync()` - 同步版本**
```javascript
export function getCurrentCompetitionIdSync() {
  const id = localStorage.getItem('currentCompetitionId')
  return id ? parseInt(id) : null
}
```
- 用于reactive初始化等需要同步值的场景
- 读取localStorage缓存
- 实际值会在onMounted中异步更新

**`setCurrentCompetitionId()` - 设置赛事**
```javascript
export async function setCurrentCompetitionId(competitionId) {
  try {
    const res = await setCurrentCompetition(competitionId)
    if (res.code === 0) {
      // 同步到localStorage
      localStorage.setItem('currentCompetitionId', competitionId)
      return true
    } else {
      console.error('❌ 设置当前赛事失败:', res.message)
      return false
    }
  } catch (error) {
    console.error('❌ 设置当前赛事异常:', error)
    return false
  }
}
```

### 3. 页面改动

#### 所有相关页面统一改动模式

**初始化模式** (用于reactive初始化):
```javascript
// 修改前
const competitionId = ref(localStorage.getItem('currentCompetitionId') || '21')
const filters = reactive({
  competitionId: getCurrentCompetitionId()  // 调用本地函数
})

// 修改后
import { getCurrentCompetitionId, getCurrentCompetitionIdSync } from '@/utils/competition'

const competitionId = ref(getCurrentCompetitionIdSync())
const filters = reactive({
  competitionId: getCurrentCompetitionIdSync()
})
```

**onMounted加载真实值**:
```javascript
// 修改前
onMounted(() => {
  loadData()
})

// 修改后
onMounted(async () => {
  // 加载当前赛事ID
  const currentCompetitionId = await getCurrentCompetitionId()
  if (currentCompetitionId) {
    competitionId.value = currentCompetitionId
    // 或 filters.competitionId = currentCompetitionId
  }
  
  loadData()
})
```

#### 已修改的文件列表

1. **组委会页面** (8个):
   - `src/views/committee/SwitchCompetition.vue` - 赛事切换页面
   - `src/views/committee/Statistics.vue` - 统计页面
   - `src/views/committee/book/Registration.vue` - 书审报名列表
   - `src/views/committee/book/Score.vue` - 书审评分管理
   - `src/views/committee/book/Reviewer.vue` - 书审评委分配
   - `src/views/committee/interview/Group.vue` - 面谈分组
   - `src/views/committee/interview/Shortlist.vue` - 面谈入围名单
   - `src/views/committee/interview/Reviewer.vue` - 面谈评委分配
   - `src/views/committee/final/Reviewer.vue` - 决赛评委分配

2. **参赛者页面** (1个):
   - `src/views/contestant/MyCompetition.vue` - 我的竞赛

3. **运维页面** (1个):
   - `src/views/ops/Registrations.vue` - 报名列表

4. **Composable** (1个):
   - `src/composables/useCompetitionStages.js` - 赛事阶段信息

### 4. 切换赛事流程 (`SwitchCompetition.vue`)

**修改前**:
```javascript
const switchCompetition = (row) => {
  currentCompetitionId.value = row.id
  setCurrentCompetitionId(row.id)  // 仅写localStorage
  ElMessage.success(`已切换到赛事：${row.name}`)
  router.push('/committee/statistics')
}
```

**修改后**:
```javascript
const switchCompetition = async (row) => {
  try {
    const success = await setCurrentCompetitionId(row.id)  // 调用后端API
    if (success) {
      currentCompetitionId.value = row.id
      ElMessage.success(`已切换到赛事：${row.name}`)
      router.push('/committee/statistics')
    } else {
      ElMessage.error('切换赛事失败，请稍后重试')
    }
  } catch (error) {
    console.error('切换赛事异常:', error)
    ElMessage.error('切换赛事失败：' + error.message)
  }
}
```

---

## 关键改进

### ✅ 移除硬编码默认值

**修改前**: 多处使用硬编码 `|| 21` 或 `|| '21'` 作为默认赛事ID
```javascript
const competitionId = localStorage.getItem('currentCompetitionId') || 21
```

**修改后**: 使用后端API，无默认值
```javascript
const competitionId = await getCurrentCompetitionId()
if (!competitionId) {
  ElMessage.warning('未找到当前赛事，请先切换赛事')
  return
}
```

**优点**:
- ✅ 避免访问不存在赛事导致的400错误
- ✅ 强制用户/管理员明确选择赛事
- ✅ 更清晰的错误提示

### ✅ 统一的全局状态

**原方案问题**:
- 每个用户的localStorage独立，没有全局状态
- 组委会切换赛事，参赛者看不到
- 多tab/浏览器不同步

**新方案优势**:
- ✅ 后端数据库存储，全局唯一
- ✅ 所有用户共享同一个当前赛事
- ✅ 管理员切换后，全系统生效
- ✅ 跨浏览器、跨设备同步

### ✅ 权限分离

- **读取**: 所有已登录用户
- **设置**: 仅 `COMMITTEE_ADMIN`、`COMMITTEE`、`OPS` 角色

---

## 使用场景

### 场景1: 组委会管理员切换赛事

1. 登录后访问"切换赛事"页面
2. 点击某个赛事的"切换"按钮
3. 后端API设置全局当前赛事ID
4. 成功后跳转到统计页面

### 场景2: 参赛者访问竞赛信息

1. 参赛者登录后进入"我的竞赛"
2. 前端调用 `getCurrentCompetitionId()` 获取全局当前赛事
3. 如果报名表中有competitionId，优先使用报名表的
4. 否则使用全局当前赛事ID
5. 加载对应赛事的时间线和规则

### 场景3: OPS查看报名列表

1. OPS登录后访问"报名列表"
2. 页面加载时调用 `getCurrentCompetitionId()`
3. 自动选择全局当前赛事
4. 加载该赛事的报名数据

---

## localStorage缓存策略

### 为什么保留localStorage？

虽然后端提供了全局当前赛事API，但localStorage仍然作为**客户端缓存**存在：

1. **性能优化**: 避免每次页面刷新都调用API
2. **Fallback**: 网络失败时的备用方案
3. **同步初始化**: reactive初始化需要同步值

### 缓存更新时机

- ✅ 调用 `getCurrentCompetitionId()` 成功后自动同步到localStorage
- ✅ 调用 `setCurrentCompetitionId()` 成功后自动同步到localStorage
- ✅ 用户登出时清除localStorage（已有逻辑）

---

## 向后兼容性

### ✅ 平滑迁移

1. **初次访问**: 
   - 如果后端没有当前赛事，系统自动选择第一个赛事
   - 管理员角色会尝试调用后端API设置

2. **旧localStorage数据**:
   - 作为fallback继续有效
   - 下次成功API调用后会被更新

3. **无破坏性变更**:
   - 所有页面功能保持正常
   - 仅改进了数据来源和同步机制

---

## 测试验证

### 手动测试步骤

#### 1. 测试管理员切换赛事

1. 以`OPS`或`COMMITTEE_ADMIN`身份登录
2. 访问"切换赛事"页面
3. 选择一个赛事并点击"切换"
4. 验证成功提示
5. 在其他页面验证赛事ID已更新

#### 2. 测试参赛者读取当前赛事

1. 以`CONTESTANT`身份登录
2. 访问"我的竞赛"页面
3. 验证加载了正确的赛事信息
4. 不应出现"赛事不存在"错误

#### 3. 测试OPS报名列表

1. 以`OPS`身份登录
2. 访问"报名列表"页面
3. 验证自动选择了当前赛事
4. 验证报名数据正常显示

#### 4. 测试权限控制

1. 以`CONTESTANT`身份尝试调用设置API（通过浏览器console）
2. 应该返回权限不足错误

---

## 技术细节

### 响应格式差异

**注意**: 此API使用不同的响应格式

**标准API响应**:
```json
{
  "success": true,
  "data": {...}
}
```

**当前赛事API响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": 123
}
```

**判断成功的方法**:
```javascript
// 标准API
if (res.success && res.data) { ... }

// 当前赛事API
if (res.code === 0 && res.data) { ... }
```

### 数据类型

- `GET` 返回的 `data` 是**数字**类型（赛事ID）
- `POST` 返回的 `data` 是**字符串**类型（成功消息）

### 异步处理

所有 `getCurrentCompetitionId()` 调用现在返回Promise：

```javascript
// ❌ 错误用法
const id = getCurrentCompetitionId()  // 返回Promise，不是数字

// ✅ 正确用法（async context）
const id = await getCurrentCompetitionId()

// ✅ 正确用法（非async context，如reactive初始化）
const id = getCurrentCompetitionIdSync()  // 读取localStorage缓存
```

---

## 已修改文件清单

### API层
- ✅ `src/api/competition.js` - 新增2个API方法

### 工具层
- ✅ `src/utils/competition.js` - 重构为API驱动

### 组委会页面 (9个)
- ✅ `src/views/committee/SwitchCompetition.vue`
- ✅ `src/views/committee/Statistics.vue`
- ✅ `src/views/committee/book/Registration.vue`
- ✅ `src/views/committee/book/Score.vue`
- ✅ `src/views/committee/book/Reviewer.vue`
- ✅ `src/views/committee/interview/Group.vue`
- ✅ `src/views/committee/interview/Shortlist.vue`
- ✅ `src/views/committee/interview/Reviewer.vue`
- ✅ `src/views/committee/final/Reviewer.vue`

### 参赛者页面 (1个)
- ✅ `src/views/contestant/MyCompetition.vue`

### 运维页面 (1个)
- ✅ `src/views/ops/Registrations.vue`

### Composables (1个)
- ✅ `src/composables/useCompetitionStages.js`

**总计**: 14个文件

---

## 影响分析

### ✅ 优点

1. **全局统一**: 所有用户看到同一个当前赛事
2. **集中管理**: 管理员可统一切换，无需每个用户手动选择
3. **避免错误**: 不再出现"赛事不存在"的400错误
4. **数据一致**: 后端数据库持久化，避免浏览器本地数据不一致

### ⚠️ 注意事项

1. **性能**: 每次页面加载会多1次API调用（已通过localStorage缓存优化）
2. **网络依赖**: 需要后端服务正常运行
3. **权限**: 设置API有权限限制，普通用户无法切换

### ✅ 向后兼容

- localStorage作为缓存保留，旧代码仍可工作
- 所有页面逻辑保持不变，仅数据来源改变
- 渐进式升级，无破坏性变更

---

## 后续优化建议

1. **增强缓存策略**: 
   - 添加缓存时间戳
   - 定期（如5分钟）刷新缓存

2. **实时同步**:
   - 使用WebSocket推送赛事切换事件
   - 所有在线用户实时收到更新

3. **用户提示**:
   - 赛事切换时，弹窗通知所有在线用户
   - 提示"赛事已切换，是否刷新页面？"

4. **权限细化**:
   - OPS可设置全局当前赛事
   - COMMITTEE仅可切换自己可见的赛事

---

## 开发时间

**完成时间**: 2026-02-28

**修改内容**:
- API集成
- 工具函数重构
- 14个页面适配
- 文档和测试脚本

---

## 测试脚本

**文件**: `scripts/test_current_competition_api.py`

**功能**:
- 测试不同角色的API访问权限
- 验证GET和POST接口
- 检查响应格式和数据类型

**运行方法**:
```bash
python scripts/test_current_competition_api.py
```
