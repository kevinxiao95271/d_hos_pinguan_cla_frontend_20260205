# 我的报名API - 项目ID字段分析

**分析时间：** 2026-02-27  
**用户需求：** 检查"我的报名"列表数据外层是否返回项目ID（如项目编号129）  
**分析方式：** 代码分析 + API探测（待后端运行）

---

## 📋 API基本信息

### 使用的API

**API路径：** `GET /api/registrations/my`

**API定义位置：** `src/api/registration.js` 第6-11行

```javascript
/**
 * 获取我的报名列表 (从token获取申请人ID)
 */
export function getMyRegistrations() {
  return request({
    url: '/registrations/my',
    method: 'get'
  })
}
```

**使用页面：** `src/views/contestant/MyRegistrations.vue`

---

## 🔍 前端代码分析

### 1. 前端如何使用数据

**代码位置：** `src/views/contestant/MyRegistrations.vue` 第107-130行

```javascript
const loadData = async () => {
  loading.value = true
  try {
    const res = await getMyRegistrations()
    console.log('📊 我的报名接口返回:', res)
    
    if (res.success) {
      const rawData = res.data || []
      console.log('📝 原始数据:', rawData)
      
      if (rawData.length > 0) {
        console.log('🔍 第一条数据字段检查:')
        console.log('  - institutionId:', rawData[0].institutionId)
        console.log('  - institutionName:', rawData[0].institutionName)
        console.log('  - institutionLevel:', rawData[0].institutionLevel)
        console.log('  - competitionId:', rawData[0].competitionId)
        console.log('  - competitionName:', rawData[0].competitionName)
      }
      
      registrations.value = rawData
    }
  } catch (error) {
    console.error('加载报名列表失败:', error)
    ElMessage.error('加载报名列表失败')
  } finally {
    loading.value = false
  }
}
```

**观察：**
- ✅ 前端有 console.log 输出第一条数据的字段
- ⚠️ **没有打印 `id` 或 `registrationId` 字段**
- ✅ 前端直接将 `res.data` 赋值给 `registrations.value`

---

### 2. 表格如何显示项目ID

**代码位置：** `src/views/contestant/MyRegistrations.vue` 第13-90行

```vue
<el-table :data="registrations" v-loading="loading" border>
  <el-table-column prop="projectName" label="项目名称" min-width="200" />
  <el-table-column prop="institutionName" label="医疗机构" width="180" />
  <el-table-column prop="institutionLevel" label="机构等级" width="120">
    <!-- ... -->
  </el-table-column>
  <el-table-column prop="groupType" label="竞赛组别" width="120">
    <!-- ... -->
  </el-table-column>
  <el-table-column prop="status" label="状态" width="100">
    <!-- ... -->
  </el-table-column>
  <el-table-column prop="createdAt" label="创建时间" width="160">
    <!-- ... -->
  </el-table-column>
  <el-table-column prop="submittedAt" label="提交时间" width="160">
    <!-- ... -->
  </el-table-column>
  <el-table-column label="操作" width="200" fixed="right">
    <!-- ... -->
  </el-table-column>
</el-table>
```

**观察：**
- ❌ **表格中没有显示"项目编号"列**
- ✅ 只显示了：项目名称、医疗机构、机构等级、竞赛组别、状态、创建时间、提交时间、操作

---

### 3. 操作按钮如何使用项目ID

**代码位置：** `src/views/contestant/MyRegistrations.vue` 第180-190行

```javascript
const editRegistration = (id) => {
  router.push(`/contestant/register/${id}`)
}

const viewDetail = (id) => {
  router.push(`/contestant/registration/${id}`)
}

const viewResults = (id) => {
  router.push(`/contestant/registration/${id}/results`)
}
```

**调用方式：** `@click="editRegistration(row.id)"`

**观察：**
- ✅ 前端通过 `row.id` 获取项目ID
- ⚠️ **假设API返回的数据中有 `id` 字段**

---

## 🎯 关键问题分析

### 问题：外层是否返回项目ID？

**前端代码的假设：**
```javascript
// 前端假设数据结构
{
  "success": true,
  "data": [
    {
      "id": 129,  // ← 前端期望这个字段存在！
      "projectName": "项目名称",
      "institutionName": "医院名称",
      "institutionLevel": "三级甲等",
      "groupType": "ADVANCED",
      "status": "DRAFT",
      "createdAt": "2026-02-27T10:00:00",
      "submittedAt": null,
      "competitionId": 1,
      "competitionName": "2026年浙江省品管大赛",
      "institutionId": 100
    },
    // ... 更多记录
  ]
}
```

**前端依赖 `row.id` 的地方：**
1. 编辑按钮：`@click="editRegistration(row.id)"`
2. 查看详情按钮：`@click="viewDetail(row.id)"`
3. 查看评审结果按钮：`@click="viewResults(row.id)"`
4. 提交按钮：`@click="submitRegistration(row.id)"`

**如果外层没有 `id` 字段，会导致：**
- ❌ 点击"编辑"跳转路径错误：`/contestant/register/undefined`
- ❌ 点击"查看详情"跳转路径错误：`/contestant/registration/undefined`
- ❌ 提交操作调用API失败：`/registrations/undefined/submit`

---

## 📊 对比其他类似API

### 书审分组列表 API

**API：** `GET /api/admin/registrations/filter`

**使用位置：** `src/views/committee/book/Registration.vue`

**前端代码：**
```javascript
// 第215-234行
const viewDetail = (row) => {
  console.log('🔍 查看详情 - 原始数据:', row)
  console.log('📋 可用ID字段:', {
    id: row.id,
    registrationId: row.registrationId,
    projectId: row.projectId
  })
  
  const detailId = row.registrationId || row.id
  // ...
}
```

**观察：**
- ✅ 前端做了兼容处理：`row.registrationId || row.id`
- ✅ 说明这个API可能返回 `registrationId` 或 `id`

---

### 面谈分组列表 API

**API：** `GET /api/admin/registrations/filter`（同书审）

**使用位置：** `src/views/committee/interview/Group.vue`

**前端代码：**
```javascript
// 第506-517行
const viewDetail = (row) => {
  console.log('🔍 查看详情，row数据:', row)
  
  const id = row.registrationId || row.id
  if (!id) {
    console.error('❌ 无法获取项目ID', row)
    ElMessage.error('无法获取项目ID')
    return
  }
  // ...
}
```

**观察：**
- ✅ 也做了兼容处理：`row.registrationId || row.id`
- ✅ 还增加了错误检查

---

## 🔬 验证方法（需要后端运行）

### 方法1：运行测试脚本（推荐）

**脚本位置：** `scripts/test_my_registrations_id.py`

**运行命令：**
```bash
python scripts/test_my_registrations_id.py
```

**功能：**
- 自动登录参赛者账号
- 调用 `GET /api/registrations/my`
- 检查返回数据的所有字段
- 重点检查 `id`、`registrationId`、`projectId` 字段
- 查找项目编号129

**输出示例：**
```
[Conclusion] Key Findings:

1. Project ID Field Existence:
   - id: [YES] or [NO]
   - registrationId: [YES] or [NO]
   - projectId: [YES] or [NO]

2. Available Fields for Project Identification:
   [OK] Can use 'id' field (value: 129)
   
3. Search for Project ID 129:
   [FOUND] Project 129 (item #1)
      - projectName: xxx
      - id: 129
      - status: SUBMITTED
```

---

### 方法2：浏览器Console查看（快速）

1. 打开浏览器，登录参赛者账号
2. 进入"我的报名"页面
3. 打开浏览器开发者工具（F12）→ Console
4. 查看 console.log 输出：

```javascript
📊 我的报名接口返回: { success: true, data: [...] }
📝 原始数据: [{...}, {...}]
🔍 第一条数据字段检查:
  - institutionId: 100
  - institutionName: xxx医院
  - institutionLevel: 三级甲等
  - competitionId: 1
  - competitionName: 2026年浙江省品管大赛
  // ⚠️ 注意看有没有 id 或 registrationId 字段
```

---

### 方法3：直接调用API（需要Token）

```bash
# 1. 先登录获取token
curl -X POST http://localhost:6031/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"wangkexin","password":"123456"}'

# 2. 使用token调用我的报名API
curl -X GET http://localhost:6031/api/registrations/my \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📋 预期的API返回结构

### 正确的返回（应该包含项目ID）

```json
{
  "success": true,
  "data": [
    {
      "id": 129,                           // ✅ 项目ID（主键）- 必需！
      "projectName": "改善门诊流程项目",
      "competitionId": 1,
      "competitionName": "2026年浙江省品管大赛",
      "institutionId": 100,
      "institutionName": "浙江省人民医院",
      "institutionLevel": "三级甲等",
      "groupType": "ADVANCED",
      "groupCode": "C1",
      "status": "SUBMITTED",
      "createdAt": "2026-02-20T10:00:00",
      "submittedAt": "2026-02-25T15:30:00",
      "applicantId": 50,
      "applicantName": "王可心"
    }
    // ... 更多报名记录
  ]
}
```

**必需字段（项目ID）：**
- ✅ `id` - 报名ID（项目ID），用于编辑、查看详情、提交等操作
- 或者 `registrationId` - 也可以（需要前端适配）

---

### 错误的返回（如果缺少项目ID）

```json
{
  "success": true,
  "data": [
    {
      // ❌ 没有 id 字段
      // ❌ 没有 registrationId 字段
      "projectName": "改善门诊流程项目",
      "competitionId": 1,
      "institutionName": "浙江省人民医院",
      // ... 其他字段
    }
  ]
}
```

**导致的问题：**
- ❌ 前端 `row.id` 为 `undefined`
- ❌ 编辑按钮点击后跳转到：`/contestant/register/undefined`
- ❌ 查看详情失败
- ❌ 提交操作失败

---

## 🔄 对比其他API的处理

### 组委会书审/面谈分组列表

**API：** `GET /api/admin/registrations/filter`

**前端处理（做了兼容）：**
```javascript
// src/views/committee/book/Registration.vue
const viewDetail = (row) => {
  const detailId = row.registrationId || row.id  // ✅ 兼容处理
  // ...
}

// src/views/committee/interview/Group.vue
const viewDetail = (row) => {
  const id = row.registrationId || row.id  // ✅ 兼容处理
  if (!id) {
    console.error('❌ 无法获取项目ID', row)
    ElMessage.error('无法获取项目ID')
    return
  }
  // ...
}
```

**建议：**
- 如果后端可能返回 `registrationId` 或 `id`
- 前端也需要在 `MyRegistrations.vue` 中做兼容处理

---

## 📝 现状总结

### 前端代码当前状态

1. **表格列：**
   - ❌ 没有显示"项目编号"列
   - 只显示：项目名称、医疗机构、机构等级、竞赛组别、状态、创建时间、提交时间

2. **Console日志：**
   - ⚠️ 没有打印 `id` 或 `registrationId` 字段
   - 只打印了：institutionId、institutionName、institutionLevel、competitionId、competitionName

3. **操作按钮：**
   - ✅ 使用 `row.id` 作为参数
   - ⚠️ 没有兼容处理（不像组委会页面有 `row.registrationId || row.id`）

---

## 🎯 需要后端确认的问题

### 核心问题

**`GET /api/registrations/my` 返回的列表数据中，每一项是否包含以下字段之一：**

| 字段名 | 说明 | 是否存在 |
|-------|------|---------|
| `id` | 报名ID（项目ID） | ❓ 需确认 |
| `registrationId` | 报名ID（项目ID） | ❓ 需确认 |
| `projectId` | 项目ID | ❓ 需确认 |

### 推荐返回结构

**建议后端返回 `id` 字段（主键）：**

```json
{
  "success": true,
  "data": [
    {
      "id": 129,  // ← 报名ID（项目ID），必需！
      "projectName": "项目名称",
      "competitionId": 1,
      "competitionName": "赛事名称",
      "institutionId": 100,
      "institutionName": "医院名称",
      "institutionLevel": "三级甲等",
      "groupType": "ADVANCED",
      "groupCode": "C1",  // 如果已分组
      "status": "SUBMITTED",
      "createdAt": "2026-02-20T10:00:00",
      "submittedAt": "2026-02-25T15:30:00",
      "applicantId": 50,  // 申请人ID（可选）
      "applicantName": "王可心"  // 申请人姓名（可选）
    }
  ]
}
```

**关键字段说明：**
- ✅ **`id`** - 报名记录的主键，用于编辑、查看详情等操作（**必需**）
- ✅ `projectName` - 项目名称
- ✅ `competitionId` / `competitionName` - 所属赛事
- ✅ `institutionId` / `institutionName` / `institutionLevel` - 所属机构
- ✅ `groupType` / `groupCode` - 组别和分组
- ✅ `status` - 状态（DRAFT/SUBMITTED等）
- ✅ `createdAt` / `submittedAt` - 时间信息

---

## 🔧 如果API缺少项目ID字段

### 需要后端修复

**问题：** 如果外层没有 `id` 或 `registrationId` 字段

**修复方案：** 后端在返回列表数据时，添加 `id` 字段

**Java示例（伪代码）：**
```java
@GetMapping("/registrations/my")
public ResponseEntity<ApiResponse<List<RegistrationDTO>>> getMyRegistrations() {
    Long userId = getCurrentUserId();
    List<Registration> registrations = registrationService.findByApplicantId(userId);
    
    List<RegistrationDTO> dtoList = registrations.stream()
        .map(reg -> {
            RegistrationDTO dto = new RegistrationDTO();
            dto.setId(reg.getId());  // ✅ 必须返回主键ID
            dto.setProjectName(reg.getProjectName());
            dto.setCompetitionId(reg.getCompetitionId());
            // ... 其他字段
            return dto;
        })
        .collect(Collectors.toList());
    
    return ResponseEntity.ok(ApiResponse.success(dtoList));
}
```

---

## 🧪 验证清单（给后端）

### 1. 检查API返回数据

```sql
-- 查询用户的报名记录，确认ID字段
SELECT 
  id,  -- ← 这个是报名记录的主键（项目ID）
  project_name,
  competition_id,
  institution_id,
  applicant_id,
  status,
  created_at,
  submitted_at
FROM registrations
WHERE applicant_id = (SELECT id FROM users WHERE username = 'wangkexin');
```

### 2. 确认返回的JSON结构

**测试方式：**
```bash
# 使用Postman或curl测试
GET http://localhost:6031/api/registrations/my
Headers: Authorization: Bearer {token}
```

**检查重点：**
- ✅ data数组中每一项是否有 `id` 字段？
- ✅ `id` 的值是否是报名记录的主键？
- ✅ 是否能通过 `id` 找到项目编号129？

---

## 💡 前端需要的改进（如果API正常）

即使API返回正常，前端也建议做以下优化：

### 1. 添加项目编号列（可选）

```vue
<el-table-column prop="id" label="项目编号" width="100" />
```

### 2. 增强Console日志

```javascript
if (rawData.length > 0) {
  console.log('🔍 第一条数据字段检查:')
  console.log('  - id:', rawData[0].id)  // ← 添加这行
  console.log('  - registrationId:', rawData[0].registrationId)  // ← 添加这行
  console.log('  - institutionId:', rawData[0].institutionId)
  // ...
}
```

### 3. 添加兼容处理（推荐）

```javascript
const editRegistration = (row) => {
  const id = row.id || row.registrationId  // ← 兼容处理
  if (!id) {
    ElMessage.error('无法获取项目ID')
    return
  }
  router.push(`/contestant/register/${id}`)
}
```

---

## 🎯 结论和建议

### 当前状态（基于代码分析）

| 项目 | 状态 | 说明 |
|-----|------|------|
| API是否返回项目ID | ❓ 待验证 | 需要实际调用API确认 |
| 前端是否使用项目ID | ✅ 是 | `row.id` 用于编辑、查看详情等 |
| 前端是否显示项目编号 | ❌ 否 | 表格中没有"项目编号"列 |
| 前端是否有兼容处理 | ❌ 否 | 不像组委会页面有兼容 |

### 需要后端确认

**请后端检查 `GET /api/registrations/my` 的返回数据：**

1. ✅ 列表数据的外层是否有 `id` 字段？
2. ✅ 如果没有，是否有 `registrationId` 字段？
3. ✅ 该字段的值是否是报名记录的主键（项目ID）？
4. ✅ 能否通过该字段查询到项目编号129的数据？

**如果外层没有项目ID字段：**
- ⚠️ 需要后端在返回数据中添加 `id` 或 `registrationId` 字段
- ⚠️ 该字段应该是报名记录的主键

### 推荐前端优化（无论API是否正常）

1. **添加兼容处理**（防御性编程）
2. **增强日志输出**（便于调试）
3. **添加项目编号列**（用户体验）

---

## 📞 下一步行动

### 立即验证

**方式1：** 浏览器Console查看（最快）
- 登录 → 我的报名 → F12查看console输出

**方式2：** 运行测试脚本（需要后端运行）
- `python scripts/test_my_registrations_id.py`

### 确认后

- ✅ 如果API有项目ID → 前端建议做兼容优化
- ❌ 如果API没有项目ID → **通知后端添加**

---

**分析完成，等待API验证结果！**
