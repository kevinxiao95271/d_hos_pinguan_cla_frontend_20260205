# /api/admin/registrations/filter 返回 401 问题

## 🔴 问题描述

**症状：** 登录后立即提示"登录已过期"

**根本原因：** `/api/admin/registrations/filter` 接口返回 401（未授权）

## ⚠️ 复现步骤

1. 使用 `COMMITTEE_ADMIN` 账号登录（13800000041）
2. 登录成功，获取到 Token
3. 页面自动跳转到"报名统计"或"书审阶段"
4. 前端自动调用 `/api/admin/registrations/filter?competitionId=21`
5. **后端返回 401**
6. 前端拦截器触发"登录已过期"提示

## 🧪 API 测试结果

```bash
# 1. 登录成功
POST /api/auth/login
Body: {"phone":"13800000041","name":"CommitteeAdmin A","title":"Title","role":"COMMITTEE_ADMIN"}
Response: 200 OK, Token 正常返回

# 2. 使用 Token 调用 admin 接口
GET /api/admin/registrations/filter?competitionId=21
Header: Authorization: Bearer {token}
Response: 401 Unauthorized ❌

# 3. 使用同一 Token 调用普通接口
GET /api/registrations?competitionId=21
Header: Authorization: Bearer {token}
Response: 200 OK, 返回 33 条数据 ✅
```

## 📊 结论

- ✅ 登录功能正常
- ✅ Token 有效
- ✅ `/api/registrations` 接口正常
- ❌ `/api/admin/registrations/filter` **权限验证有问题**

## 🔧 临时解决方案（已实施）

**前端已切换回使用 `/api/registrations` 接口**，可以正常登录和查看数据。

**缺失字段：**
- ❌ `registrationId`（项目编号）
- ❌ `institutionName`（医疗机构名称）
- ❌ `methodLabel`（品管工具）
- ❌ `applicantName`（报名人）

**现有字段：**
- ✅ `id`（内部ID）
- ✅ `projectName`（项目名称）
- ✅ `groupType`（竞赛组别）
- ✅ `groupCode`（分组）
- ✅ `status`（状态）
- ✅ `submittedAt`（报名时间）

## 🎯 后端修复建议

### 1. 检查权限配置

`CompetitionAdminController.java` 中的 `/api/admin/registrations/filter` 接口：

```java
@PreAuthorize("hasAnyRole('COMMITTEE_ADMIN', 'OPS')")
@GetMapping("/admin/registrations/filter")
public Result<?> filterRegistrations(...) {
    // 实现
}
```

**检查项：**
- ✅ JWT Token 中的 `role` 字段是否正确设置为 `COMMITTEE_ADMIN`？
- ✅ Spring Security 的角色前缀是否一致（`ROLE_` vs 无前缀）？
- ✅ `@PreAuthorize` 注解是否生效？

### 2. 日志排查

在后端添加日志：

```java
@GetMapping("/admin/registrations/filter")
public Result<?> filterRegistrations(...) {
    log.info("🔍 [Admin API] 接收到请求，Token: {}, Role: {}", 
        SecurityContextHolder.getContext().getAuthentication().getName(),
        SecurityContextHolder.getContext().getAuthentication().getAuthorities());
    
    // 原有逻辑
}
```

### 3. 快速测试

使用以下脚本测试后端：

```python
import requests

# 1. 登录
login_url = "http://localhost:6031/api/auth/login"
login_data = {
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "title": "Title",
    "role": "COMMITTEE_ADMIN"
}
response = requests.post(login_url, json=login_data)
token = response.json()['data']['token']
print(f"✅ Token: {token}")

# 2. 测试 admin 接口
admin_url = "http://localhost:6031/api/admin/registrations/filter?competitionId=21"
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(admin_url, headers=headers)
print(f"📥 Admin API 响应: {response.status_code}")
if response.status_code != 200:
    print(f"❌ 错误: {response.text}")
else:
    print(f"✅ 成功: {len(response.json()['data'])} 条数据")
```

## 📝 前端恢复步骤（后端修复后）

修复后端后，前端需要：

1. 取消注释 `BookStage.vue` 中的字段列：
   - `registrationId`
   - `institutionName`
   - `methodLabel`
   - `applicantName`

2. 改回使用 `filterRegistrations`：
   ```javascript
   import { filterRegistrations } from '@/api/admin'
   const res = await filterRegistrations(registrationFilters)
   ```

3. 重启前端服务，硬刷新浏览器

## 🕐 更新日志

- **2026-02-06 22:00**: 发现问题，前端切换回 `/api/registrations`
- **待后端修复**: `/api/admin/registrations/filter` 权限问题
