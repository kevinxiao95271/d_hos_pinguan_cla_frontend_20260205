# 我的报名API - 项目ID字段确认

**API：** `GET /api/registrations/my`

**问题：** 用户报告项目编号129在"我的报名"列表中，需要确认API返回的列表数据外层是否包含项目ID字段。

---

## ❓ 需要确认的问题

**请确认 `GET /api/registrations/my` 返回的数据结构：**

列表数据的每一项（外层）是否包含以下字段之一：
- `id` - 报名记录主键（项目ID）
- `registrationId` - 报名ID
- `projectId` - 项目ID

---

## ✅ 预期的返回结构

```json
{
  "success": true,
  "data": [
    {
      "id": 129,  // ← 这个字段必须存在！
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
      "submittedAt": "2026-02-25T15:30:00"
    },
    {
      "id": 130,  // ← 另一条记录
      // ... 其他字段
    }
  ]
}
```

---

## 🚨 如果缺少 `id` 字段会导致

### 前端功能失效

**代码位置：** `src/views/contestant/MyRegistrations.vue`

```javascript
// 编辑按钮
<el-button @click="editRegistration(row.id)">编辑</el-button>

// 查看详情按钮
<el-button @click="viewDetail(row.id)">查看详情</el-button>

// 提交按钮
<el-button @click="submitRegistration(row.id)">提交</el-button>
```

**如果 `row.id` 为 `undefined`：**
- ❌ 编辑跳转到：`/contestant/register/undefined` → 404错误
- ❌ 查看详情跳转到：`/contestant/registration/undefined` → 404错误
- ❌ 提交调用：`POST /registrations/undefined/submit` → 400/404错误

---

## 🔍 对比其他API

### 组委会分组列表API

**API：** `GET /api/admin/registrations/filter`

**返回结构（参考）：**
```json
{
  "success": true,
  "data": [
    {
      "id": 129,  // ✅ 或 "registrationId": 129
      "projectName": "...",
      // ... 其他字段
    }
  ]
}
```

**前端处理（有兼容逻辑）：**
```javascript
// src/views/committee/book/Registration.vue
const detailId = row.registrationId || row.id  // 兼容两种字段名

// src/views/committee/interview/Group.vue
const id = row.registrationId || row.id
if (!id) {
  ElMessage.error('无法获取项目ID')
  return
}
```

**建议：**
- 统一所有API，都返回 `id` 字段作为报名记录主键
- 或者统一使用 `registrationId`

---

## 🎯 修复建议

### 方案1：添加 `id` 字段（推荐）

```java
// 在DTO中添加id字段
public class RegistrationListDTO {
    private Long id;  // ← 报名记录主键，必需！
    private String projectName;
    private Long competitionId;
    private String competitionName;
    // ... 其他字段
}

// Controller返回时确保包含id
@GetMapping("/registrations/my")
public ApiResponse<List<RegistrationListDTO>> getMyRegistrations() {
    // ... 查询逻辑
    List<RegistrationListDTO> list = registrations.stream()
        .map(reg -> {
            RegistrationListDTO dto = new RegistrationListDTO();
            dto.setId(reg.getId());  // ✅ 设置主键ID
            dto.setProjectName(reg.getProjectName());
            // ... 其他字段映射
            return dto;
        })
        .collect(Collectors.toList());
    
    return ApiResponse.success(list);
}
```

---

### 方案2：使用 `registrationId` 字段

如果已经返回了 `registrationId`，请确保：
- 该字段的值是报名记录的主键
- 前端需要做兼容处理（已记录到前端TODO）

---

## 📋 验证方法

### 1. SQL查询验证

```sql
-- 查找项目编号129
SELECT id, project_name, status, applicant_id
FROM registrations
WHERE id = 129;

-- 查询该用户的所有报名
SELECT id, project_name, competition_id, status
FROM registrations
WHERE applicant_id = (SELECT id FROM users WHERE username = 'wangkexin')
ORDER BY created_at DESC;
```

### 2. API测试验证

```bash
# 1. 登录
curl -X POST http://localhost:6031/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"wangkexin","password":"123456"}'

# 2. 调用我的报名API
curl -X GET http://localhost:6031/api/registrations/my \
  -H "Authorization: Bearer {token}"

# 3. 检查返回的data数组中，每一项是否有id字段
```

### 3. 前端Console验证（最快）

1. 浏览器登录参赛者账号
2. 进入"我的报名"页面
3. F12打开Console
4. 查看输出：`📊 我的报名接口返回:` 和 `📝 原始数据:`
5. 检查第一条数据中是否有 `id` 字段

---

## 🔧 修复优先级

**P0（高优先级）：**
- ✅ 确认API是否返回 `id` 或 `registrationId` 字段
- ✅ 如果没有，后端必须添加

**P1（建议优化）：**
- 统一所有报名相关API的字段命名
- 添加更详细的API文档说明

---

## 📞 联系方式

**前端分析文档：** `docs/我的报名API-项目ID字段分析.md`  
**测试脚本：** `scripts/test_my_registrations_id.py`

**验证后请反馈：**
- API是否返回了项目ID字段？
- 字段名是什么？（`id` 还是 `registrationId`？）
- 项目编号129是否能正常查询到？

---

**分析时间：** 2026-02-27  
**状态：** ❓ 待后端确认
