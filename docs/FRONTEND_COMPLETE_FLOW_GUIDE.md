# 前端完整流程指引

## 📋 目标

本指引用于排查"暂无报名数据"问题，以及正确获取列表、详情、筛选、成员信息的全过程。

按顺序执行即可验证整个流程。

---

## 🔄 完整流程（从登录到列表与详情）

### Step 1: 登录获取 Token

**API**: `POST /api/auth/login`

**请求体**:
```json
{
  "phone": "13800000041",
  "name": "CommitteeAdmin A",
  "title": "Committee Member",
  "role": "COMMITTEE_ADMIN",
  "institutionId": null,
  "reviewerGroupCode": null,
  "interviewGroupCode": null,
  "expertBackground": null
}
```

**返回**:
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "role": "COMMITTEE_ADMIN",
    ...
  }
}
```

**前端实现**: `src/stores/user.js` - `login()` 方法

**关键代码**:
```javascript
// 保存 token 到 localStorage
localStorage.setItem('token', res.data.token)
localStorage.setItem('userInfo', JSON.stringify(res.data))
```

---

### Step 2: 列表页拉取报名

#### 方案 A: Admin 接口（推荐，但可能返回 401）

**API**: `GET /api/admin/registrations/filter?competitionId=21`

**Headers**: `Authorization: Bearer {token}`

**参数**:
- `competitionId`: 赛事 ID（必填）
- `institutionName`: 机构名称（可选）
- `groupType`: 竞赛组别（可选）
- `groupCode`: 分组代码（可选）
- `projectName`: 项目名称（可选）
- `methodCode`: 品管工具代码（可选）

**返回**: `data` 为报名列表数组

**前端实现**: `src/api/admin.js` - `filterRegistrations()`

---

#### 方案 B: 通用接口（当前使用，推荐）

**API**: `GET /api/registrations?competitionId=21`

**Headers**: `Authorization: Bearer {token}`

**参数**: 同方案 A

**返回**: `data` 为报名列表数组

**前端实现**: `src/api/registration.js` - `getRegistrations()`

**当前使用位置**:
- `src/views/committee/BookStage.vue` - 书审阶段报名列表
- `src/views/committee/Statistics.vue` - 报名统计

**关键代码**:
```javascript
// BookStage.vue
const res = await getRegistrations({
  competitionId: registrationFilters.competitionId,
  institutionName: registrationFilters.institutionName,
  groupType: registrationFilters.groupType,
  // ... 其他筛选条件
})

if (res.success) {
  registrations.value = res.data || []
}
```

---

### Step 3: "暂无报名数据" 排查清单

#### ✅ 检查 1: Competition ID 是否正确

**位置**: `src/views/committee/BookStage.vue`

```javascript
// 从 localStorage 获取当前赛事 ID
const getCurrentCompetitionId = () => {
  const competitionId = localStorage.getItem('currentCompetitionId')
  return competitionId ? parseInt(competitionId) : 1
}

const registrationFilters = reactive({
  competitionId: getCurrentCompetitionId(),
  // ...
})
```

**排查方法**:
1. 打开浏览器控制台（F12）
2. 输入: `localStorage.getItem('currentCompetitionId')`
3. 确认返回的 ID 是否正确（当前样例用 `21`）

**修复方法**:
```javascript
// 在控制台中设置正确的 ID
localStorage.setItem('currentCompetitionId', '21')
// 刷新页面
```

---

#### ✅ 检查 2: Token 是否过期或未带

**现象**: 
- 请求返回 401
- 前端可能误判为空数据

**排查方法**:
1. 打开浏览器控制台（F12） → Network 标签
2. 刷新页面，查找 `/registrations` 请求
3. 检查 Request Headers 中是否有 `Authorization: Bearer xxx`
4. 检查 Response 状态码是否为 401

**修复方法**:
- 如果没有 Authorization header → 重新登录
- 如果返回 401 → Token 已过期，重新登录
- 查看控制台是否有红色错误日志

---

#### ✅ 检查 3: 是否请求了错误的接口

**正确的接口** (当前前端使用):
```
GET /api/registrations?competitionId=21
```

**错误的接口** (可能导致 401):
```
GET /api/admin/registrations/filter?competitionId=21
```

**排查方法**:
1. 打开控制台 → Network 标签
2. 查看实际请求的 URL
3. 如果是 `/admin/registrations/filter` 且返回 401，说明权限不足

**当前前端代码已修复**:
- ✅ `BookStage.vue` 使用 `getRegistrations()` → `/api/registrations`
- ✅ `Statistics.vue` 使用 `getRegistrations()` → `/api/registrations`

---

### Step 4: 详情页展示

#### 4.1 列表数据直接透传

列表接口已返回以下字段，可直接展示：
- `institutionName` - 机构名称
- `applicantName` - 报名人姓名
- `projectName` - 项目名称
- `methodLabel` - 品管工具（中文）
- `subjectTypeLabel` - 主题类型（中文）

**前端实现**: 表格直接绑定这些字段
```vue
<el-table-column prop="institutionName" label="医疗机构名称" />
<el-table-column prop="applicantName" label="报名人" />
<el-table-column prop="methodLabel" label="品管工具" />
<el-table-column prop="subjectTypeLabel" label="主题类型" />
```

---

#### 4.2 详情页获取完整数据

**API**: `GET /api/registrations/{id}`

**Headers**: `Authorization: Bearer {token}`

**返回示例**:
```json
{
  "success": true,
  "data": {
    "id": 106,
    "projectName": "项目名称",
    "institutionName": "浙江省人民医院",
    "applicantName": "张三",
    "members": [
      {
        "name": "李四",
        "title": "主任医师",
        "department": "内科",
        "role": "MENTOR"  // 辅导员
      },
      {
        "name": "王五",
        "title": "主治医师",
        "department": "外科",
        "role": "PARTICIPANT"  // 项目参与人员
      }
    ]
  }
}
```

**前端实现**: `src/views/contestant/MyCompetition.vue`

**关键代码**:
```javascript
// 过滤成员数据
const participants = computed(() => {
  return registration.value.members?.filter(m => m.role === 'PARTICIPANT') || []
})

const mentors = computed(() => {
  return registration.value.members?.filter(m => m.role === 'MENTOR') || []
})
```

**显示逻辑**:
- `members` 数组中 `role=MENTOR` → 辅导员
- `members` 数组中 `role=PARTICIPANT` → 项目参与人员

---

### Step 5: 下拉筛选

#### 5.1 获取主题类型字典

**API**: `GET /api/dictionaries/subject_type`

**Headers**: `Authorization: Bearer {token}`

**返回**:
```json
{
  "success": true,
  "data": [
    {
      "code": "subject_type_1",
      "label": "病人照护",
      "type": "subject_type"
    },
    ...
  ]
}
```

**前端实现**: `src/views/committee/BookStage.vue`

```javascript
// 加载字典
const dictionaries = reactive({
  subjectTypes: [],
  methods: []
})

const loadDictionaries = async () => {
  const res = await getDictionaryByType('subject_type')
  if (res.success) {
    dictionaries.subjectTypes = res.data || []
  }
}
```

---

#### 5.2 获取品管工具字典

**API**: `GET /api/dictionaries/method`

**Headers**: `Authorization: Bearer {token}`

**返回**: 格式同主题类型

**前端实现**: 同上，type 参数改为 `'method'`

---

#### 5.3 筛选报名列表

**API**: `GET /api/registrations?competitionId=21&subjectTypeCode=xxx&methodCode=yyy`

**前端实现**:
```vue
<!-- 下拉选择器 -->
<el-select v-model="registrationFilters.methodCode" clearable>
  <el-option
    v-for="item in dictionaries.methods"
    :key="item.code"
    :label="item.label"
    :value="item.code"
  />
</el-select>

<!-- 表格直接显示中文 -->
<el-table-column prop="methodLabel" label="品管工具" />
<el-table-column prop="subjectTypeLabel" label="主题类型" />
```

**重点**: 
- 筛选时使用 `code` 作为参数
- 列表显示时使用接口返回的 `Label` 字段（无需二次查字典）

---

## 🔧 前端代码检查清单

### ✅ 1. API 调用正确性

**文件**: `src/views/committee/BookStage.vue`

```javascript
// ✅ 正确：使用 getRegistrations
import { getRegistrations } from '@/api/registration'

// ❌ 错误：不要使用 filterRegistrations（会返回 401）
// import { filterRegistrations } from '@/api/admin'

const loadRegistrations = async () => {
  const res = await getRegistrations(params)
  // ...
}
```

---

### ✅ 2. Token 管理

**文件**: `src/utils/request.js`

```javascript
// 请求拦截器：自动添加 token
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：处理 401
if (status === 401) {
  ElMessage.error('登录已过期，请重新登录')
  localStorage.removeItem('token')
  router.push('/login')
}
```

---

### ✅ 3. Competition ID 管理

**文件**: `src/views/committee/BookStage.vue`

```javascript
// ✅ 从 localStorage 读取
const getCurrentCompetitionId = () => {
  const competitionId = localStorage.getItem('currentCompetitionId')
  return competitionId ? parseInt(competitionId) : 1
}

// ✅ 切换赛事时更新
// 文件: src/views/committee/SwitchCompetition.vue
const switchCompetition = (row) => {
  localStorage.setItem('currentCompetitionId', row.id)
  router.push('/committee/statistics')
}
```

---

### ✅ 4. 成员数据过滤

**文件**: `src/views/contestant/MyCompetition.vue`

```javascript
// ✅ 正确：使用 computed 过滤
const participants = computed(() => {
  return registration.value.members?.filter(m => m.role === 'PARTICIPANT') || []
})

const mentors = computed(() => {
  return registration.value.members?.filter(m => m.role === 'MENTOR') || []
})

// ❌ 错误：不要硬编码或假设所有成员都是参与者
```

---

### ✅ 5. 错误处理和加载状态

**文件**: `src/views/committee/BookStage.vue`

```javascript
const loading = ref(false)

const loadRegistrations = async () => {
  loading.value = true
  try {
    const res = await getRegistrations(params)
    
    if (res.success) {
      registrations.value = res.data || []
      
      if (registrations.value.length === 0) {
        ElMessage.info('暂无报名数据')
      } else {
        ElMessage.success(`加载成功，共 ${registrations.value.length} 条报名`)
      }
    } else {
      ElMessage.warning('加载失败: ' + (res.message || '未知错误'))
    }
  } catch (error) {
    console.error('加载报名列表失败:', error)
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error('加载失败，请检查网络或后端服务')
    }
  } finally {
    loading.value = false
  }
}
```

---

## 🐛 常见问题排查

### 问题 1: 列表一直显示"暂无报名数据"

**排查步骤**:
1. 打开浏览器控制台（F12） → Console 标签
2. 查看是否有日志输出：
   ```
   📥 正在加载报名列表...
   📥 报名列表响应: {...}
   ✅ 报名列表加载成功: X 条
   ```

3. 切换到 Network 标签：
   - 找到 `registrations` 请求
   - 检查 Status Code（应该是 200）
   - 检查 Response 内容

**可能原因和解决方案**:

| 原因 | 现象 | 解决方案 |
|------|------|----------|
| Competition ID 错误 | 返回空数组 `[]` | 设置正确的 `currentCompetitionId` |
| Token 过期 | 返回 401 | 重新登录 |
| 后端数据库无数据 | 返回空数组 `[]` | 后端创建测试数据 |
| 使用错误的 API | 返回 401 | 检查是否使用 `/api/registrations` |
| 网络问题 | 请求超时 | 检查后端服务是否运行 |

---

### 问题 2: 详情页看不到辅导员/参与人员

**排查步骤**:
1. 打开控制台，输入：
   ```javascript
   // 查看原始数据
   console.log(registration.value.members)
   ```

2. 检查 `members` 数组：
   ```javascript
   // 检查每个成员的 role 字段
   registration.value.members.forEach(m => {
     console.log(`${m.name}: role=${m.role}`)
   })
   ```

**可能原因**:
- `members` 数组为空 → 后端数据未填充
- `role` 字段值不对 → 检查是否为 `MENTOR` 或 `PARTICIPANT`
- 前端过滤逻辑错误 → 检查 computed 函数

---

### 问题 3: 筛选功能不工作

**排查步骤**:
1. 检查字典是否加载：
   ```javascript
   console.log(dictionaries.methods)
   console.log(dictionaries.subjectTypes)
   ```

2. 检查筛选参数：
   ```javascript
   console.log(registrationFilters)
   ```

3. 查看 Network 标签中的请求 URL：
   ```
   /api/registrations?competitionId=21&methodCode=xxx
   ```

---

## 📊 测试工具

### Python 测试脚本

```bash
# 快速登录测试
python test_login_simple.py

# 完整流程测试
python test_complete_flow.py

# 书审阶段 API 测试
python test_api_bookstage.py

# 报名 API 全面测试
python test_registrations_api.py
```

### 浏览器控制台快速测试

```javascript
// 1. 检查 token
localStorage.getItem('token')

// 2. 检查赛事 ID
localStorage.getItem('currentCompetitionId')

// 3. 手动设置赛事 ID
localStorage.setItem('currentCompetitionId', '21')

// 4. 查看用户信息
JSON.parse(localStorage.getItem('userInfo'))

// 5. 清除所有数据（重置）
localStorage.clear()
location.reload()
```

---

## 📝 总结

### 核心要点

1. ✅ **使用正确的 API**: `/api/registrations` 而不是 `/api/admin/registrations/filter`
2. ✅ **正确管理 Competition ID**: 从 localStorage 读取，切换赛事时更新
3. ✅ **Token 自动管理**: 请求拦截器自动添加，响应拦截器处理过期
4. ✅ **成员数据过滤**: 根据 `role` 字段区分辅导员和参与人员
5. ✅ **直接使用 Label 字段**: 列表中的 `methodLabel` 和 `subjectTypeLabel` 无需二次查询

### 已验证可用的端点

- ✅ `POST /api/auth/login` - 登录
- ✅ `GET /api/registrations?competitionId=21` - 报名列表
- ✅ `GET /api/registrations/{id}` - 报名详情
- ✅ `GET /api/dictionaries/method` - 品管工具字典
- ✅ `GET /api/dictionaries/subject_type` - 主题类型字典
- ✅ `GET /api/competitions` - 赛事列表

### 当前状态

所有前端代码已按此流程指引更新，应该能正常工作。如果仍然遇到问题，请按照本文档的排查清单逐项检查。
