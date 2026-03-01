# OPS新增功能：密码重置 & 报名删除

## 功能概述

为系统运维（OPS）角色新增两个管理功能：
1. **密码重置** - 重置任何用户的密码
2. **报名删除** - 删除报名记录及其所有相关数据

---

## 功能一：密码重置

### 后端API

**接口：** `POST /api/admin/users/{userId}/reset-password`

**权限：** 仅OPS角色可用

**功能：**
- 生成6位随机密码
- BCrypt加密后保存到数据库
- 返回明文密码供管理员通知用户

**响应格式：**
```json
{
  "success": true,
  "data": {
    "newPassword": "a7Bc2k"
  },
  "message": null
}
```

**非OPS角色响应：**
```json
{
  "success": false,
  "message": "仅系统运维可操作"
}
```

---

### 前端实现

#### 1. API封装（`src/api/admin.js`）

```javascript
/**
 * 重置用户密码（OPS专用）
 * @param {number} userId - 用户ID
 * @returns {Promise} 返回新密码 { newPassword: "XXXXXX" }
 */
export function resetUserPassword(userId) {
  return request({
    url: `/admin/users/${userId}/reset-password`,
    method: 'post'
  })
}
```

#### 2. 用户管理页面（`src/views/ops/UserManagement.vue`）

**UI修改：**
- 操作列宽度：`150px` → `200px`
- 新增"重置密码"按钮（蓝色，primary类型）

**功能实现：**
```javascript
const handleResetPassword = async (user) => {
  try {
    // 1. 二次确认
    await ElMessageBox.confirm(
      `确认重置用户 ${user.name}（${user.phone}）的密码？将生成6位随机密码。`,
      '重置密码',
      {
        confirmButtonText: '确认重置',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 2. 调用API
    const res = await resetUserPassword(user.id)

    if (res.success) {
      // 3. 显示新密码（复用创建评委的密码弹窗）
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
      const message = error.response?.data?.message || error.message || '密码重置失败'
      ElMessage.error(message)
    }
  }
}
```

**用户体验：**
1. 点击"重置密码"按钮
2. 弹出确认对话框（包含用户姓名和手机号）
3. 确认后调用API
4. 成功后显示新密码（6位随机密码）
5. 管理员需要立即记录并通知用户

---

## 功能二：报名删除

### 后端API

**接口：** `DELETE /api/admin/registrations/{id}`

**权限：** 仅OPS角色可用

**功能：**
- 级联删除所有相关数据
- MinIO文件清理（失败容忍）
- 事务保证数据一致性

**级联删除顺序：**
```
ReviewScore（评审评分）
  ↓
ReviewTask（评审任务）
  ↓
MaterialFile（材料文件记录 + MinIO实际文件清理）
  ↓
RegistrationMember（团队成员）
  ↓
ActivityInfo（活动信息）
  ↓
ProjectSummary（项目总结）
  ↓
Registration（报名记录）
```

**响应格式：**
```json
{
  "success": true,
  "data": null,
  "message": "删除成功"
}
```

**非OPS角色响应：**
```json
{
  "success": false,
  "message": "仅系统运维可操作"
}
```

---

### 前端实现

#### 1. API封装（`src/api/admin.js`）

```javascript
/**
 * 删除报名记录（OPS专用）
 * @param {number} registrationId - 报名ID
 * @returns {Promise}
 */
export function deleteRegistration(registrationId) {
  return request({
    url: `/admin/registrations/${registrationId}`,
    method: 'delete'
  })
}
```

#### 2. OPS报名列表页面（`src/views/ops/Registrations.vue`）

**UI修改：**
- 操作列宽度：`100px` → `160px`
- 新增"删除"按钮（红色，danger类型）

**功能实现：**
```javascript
const handleDelete = async (row) => {
  try {
    // 1. 危险操作确认（红色警告）
    await ElMessageBox.confirm(
      `确认删除报名【${row.projectName}】？此操作将级联删除所有相关数据（评审任务、评分、材料文件等），且不可恢复！`,
      '危险操作',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'error',
        confirmButtonClass: 'el-button--danger'
      }
    )

    // 2. 调用API
    const registrationId = row.registrationId || row.id
    const res = await deleteRegistration(registrationId)

    if (res.success) {
      ElMessage.success('删除成功')
      loadRegistrations()  // 刷新列表
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      const message = error.response?.data?.message || error.message || '删除失败'
      ElMessage.error(message)
    }
  }
}
```

**用户体验：**
1. 点击"删除"按钮（红色）
2. 弹出危险操作确认框（红色警告，明确说明级联删除范围）
3. 确认后调用API
4. 成功后刷新列表，删除的记录消失
5. 显示成功提示

---

## 权限控制

### 角色权限矩阵

| 功能 | OPS | COMMITTEE_ADMIN | REVIEWER | CONTESTANT |
|---|---|---|---|---|
| 密码重置 | ✅ | ❌ | ❌ | ❌ |
| 报名删除 | ✅ | ❌ | ❌ | ❌ |

**非OPS角色尝试操作时：**
- 后端返回：`"仅系统运维可操作"`
- 前端显示：错误提示消息

---

## 安全措施

### 密码重置
1. ✅ 二次确认对话框
2. ✅ 显示用户信息（姓名、手机号）
3. ✅ 新密码仅显示一次，提示管理员立即记录
4. ✅ 密码随机生成（6位）
5. ✅ BCrypt加密存储

### 报名删除
1. ✅ 危险操作确认（红色错误类型）
2. ✅ 明确提示级联删除范围
3. ✅ 强调不可恢复
4. ✅ 显示项目名称便于确认
5. ✅ 事务保证数据一致性
6. ✅ MinIO文件清理失败容忍（不影响数据库删除）

---

## 使用场景

### 密码重置
- 用户忘记密码
- 账号被锁定
- 初始化测试账号
- 应急重置访问

### 报名删除
- 测试数据清理
- 错误报名记录移除
- 数据维护和整理
- 用户明确要求删除（如退赛）

---

## 测试建议

### 前端测试步骤

#### 测试密码重置
1. 使用OPS账号登录系统
2. 进入"用户管理"页面
3. 找到任意用户，点击"重置密码"按钮
4. 确认操作
5. 验证弹窗显示新密码（6位）
6. 记录新密码
7. 尝试使用新密码登录该用户账号

#### 测试报名删除
1. 使用OPS账号登录系统
2. 进入"报名列表"页面
3. 选择一个测试报名（建议选择草稿状态）
4. 点击"详情"查看完整信息（评审任务、材料等）
5. 点击"删除"按钮
6. 确认危险操作
7. 验证报名从列表中消失
8. 尝试再次查询该报名（应该404）

---

## 技术细节

### 密码生成规则
- 长度：6位
- 字符集：数字、大小写字母
- 随机生成
- BCrypt加密（强度10）

### 级联删除说明
```
1. ReviewScore - 该报名的所有评分记录
2. ReviewTask - 该报名的所有评审任务
3. MaterialFile - 该报名的所有材料文件
   - 数据库记录删除
   - MinIO实际文件清理（失败不影响事务）
4. RegistrationMember - 团队成员信息
5. ActivityInfo - 活动详细信息
6. ProjectSummary - 项目总结信息
7. Registration - 报名主记录
```

**事务保证：** 使用`@Transactional`，任何步骤失败都会回滚（MinIO清理除外）

---

## 前端文件修改

1. ✅ `src/api/admin.js` - 新增2个API函数
2. ✅ `src/views/ops/UserManagement.vue` - 添加密码重置按钮和处理函数
3. ✅ `src/views/ops/Registrations.vue` - 添加删除按钮和处理函数

---

## 注意事项

### 密码重置
- ⚠️ 新密码仅显示一次，务必立即记录
- ⚠️ 及时通知用户新密码
- ⚠️ 提醒用户登录后修改密码

### 报名删除
- 🔴 操作不可恢复！
- 🔴 会删除所有关联数据（评分、任务、文件等）
- 🔴 建议只删除草稿或测试数据
- 🔴 删除已提交/已审核的报名需谨慎
- ⚠️ MinIO文件清理失败不会阻止删除（日志中会记录）

---

## 界面截图说明

### 用户管理页面
```
操作列：
  [禁用/启用]  [重置密码]  ← 新增
```

### 报名列表页面
```
操作列：
  [详情]  [删除]  ← 新增
```
