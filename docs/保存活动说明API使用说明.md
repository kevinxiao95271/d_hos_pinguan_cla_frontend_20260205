# 保存活动说明 API 使用说明

## 📍 触发时机

**用户操作**：
1. 在报名表单第3步（活动说明）填写内容
2. 点击"下一步"按钮

**代码位置**：
- 文件：`src/views/contestant/RegisterForm.vue`
- 函数：`nextStep()` → `saveActivity()`
- 行号：约第666-683行

---

## 🔗 使用的API

### API端点

```
PUT /api/registrations/{id}/activity
```

### 实现代码

**API定义**（`src/api/registration.js`）：
```javascript
export function updateRegistrationActivity(id, data) {
  return request({
    url: `/registrations/${id}/activity`,
    method: 'put',
    data
  })
}
```

**调用代码**（`src/views/contestant/RegisterForm.vue`）：
```javascript
const saveActivity = async () => {
  if (!registrationId.value) {
    ElMessage.warning('请先保存基本信息')
    return false
  }
  
  try {
    // 调用API，传入报名ID和活动说明数据
    const res = await updateRegistrationActivity(registrationId.value, form.activity)
    if (res.success) {
      ElMessage.success('保存成功')
      return true
    }
  } catch (error) {
    console.error('保存活动说明失败:', error)
    ElMessage.error('保存活动说明失败')
    return false
  }
}
```

---

## 📦 发送的参数

### URL参数

| 参数名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| `id` | Number | 报名ID | `123` |

**完整URL示例**：
```
PUT http://localhost:6031/api/registrations/123/activity
```

### 请求体（Body）参数

**数据来源**：`form.activity` 对象

| 字段名 | 类型 | 说明 | 必填 | 默认值 | 示例值 |
|--------|------|------|------|--------|--------|
| `theme` | String | 活动主题 | ✅ 是 | `''` | `"提升门诊就诊效率"` |
| `keywords` | String | 关键词 | ❌ 否 | `''` | `"效率,流程,优化"` |
| `subjectTypeCode` | String | 主题类型代码 | ✅ 是 | `''` | `"time_efficiency"` |
| `methodCode` | String | 运用手法代码 | ✅ 是 | `''` | `"pdca"` |
| `experienceImproveCode` | String | 改善就医感受代码 | ❌ 否 | `''` | `"appointment"` |
| `qualityTopicCode` | String | 医疗质量安全主题代码 | ❌ 否 | `''` | `"emergency_surgery_time"` |
| `avgWorkYears` | Number | 平均工作年限 | ❌ 否 | `0` | `5.5` |
| `avgAge` | Number | 平均年龄 | ❌ 否 | `0` | `35` |
| `crossDepartment` | Boolean | 是否跨科室 | ❌ 否 | `false` | `true` |

### 完整请求示例

**HTTP请求**：
```http
PUT /api/registrations/123/activity HTTP/1.1
Host: localhost:6031
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "theme": "提升门诊就诊效率",
  "keywords": "效率,流程,优化",
  "subjectTypeCode": "time_efficiency",
  "methodCode": "pdca",
  "experienceImproveCode": "appointment",
  "qualityTopicCode": "emergency_surgery_time",
  "avgWorkYears": 5.5,
  "avgAge": 35,
  "crossDepartment": true
}
```

**JavaScript代码**：
```javascript
await updateRegistrationActivity(123, {
  theme: '提升门诊就诊效率',
  keywords: '效率,流程,优化',
  subjectTypeCode: 'time_efficiency',
  methodCode: 'pdca',
  experienceImproveCode: 'appointment',
  qualityTopicCode: 'emergency_surgery_time',
  avgWorkYears: 5.5,
  avgAge: 35,
  crossDepartment: true
})
```

---

## 📋 前端表单验证规则

**定义位置**：`RegisterForm.vue` 第420-424行

```javascript
const activityRules = {
  theme: [{ required: true, message: '请输入活动主题', trigger: 'blur' }],
  subjectTypeCode: [{ required: true, message: '请选择主题类型', trigger: 'change' }],
  methodCode: [{ required: true, message: '请选择运用手法', trigger: 'change' }]
}
```

**必填字段**：
- ✅ `theme` - 活动主题
- ✅ `subjectTypeCode` - 主题类型
- ✅ `methodCode` - 运用手法

**可选字段**：
- ❌ `keywords` - 关键词
- ❌ `experienceImproveCode` - 改善就医感受
- ❌ `qualityTopicCode` - 医疗质量安全主题
- ❌ `avgWorkYears` - 平均工作年限
- ❌ `avgAge` - 平均年龄
- ❌ `crossDepartment` - 是否跨科室

---

## 🔄 完整执行流程

### 1. 用户点击"下一步"

```javascript
// nextStep 函数（第575-608行）
const nextStep = async () => {
  let valid = false
  
  // 当前在第3步（活动说明，索引为2）
  if (currentStep.value === 2) {
    // 1. 先进行表单验证
    valid = await activityFormRef.value.validate().catch(() => false)
    
    // 2. 验证通过后，调用保存函数
    if (valid) {
      await saveActivity()
    }
  }
  
  // 3. 验证通过且保存成功，进入下一步
  if (valid && currentStep.value < 4) {
    currentStep.value++
  }
}
```

### 2. 表单验证

**验证规则**：
```javascript
✅ theme: 必填，失去焦点时验证
✅ subjectTypeCode: 必填，值改变时验证
✅ methodCode: 必填，值改变时验证
```

**验证失败**：
- 阻止保存
- 显示错误提示
- 不进入下一步

**验证成功**：
- 继续执行 `saveActivity()`

### 3. 调用保存API

```javascript
// saveActivity 函数（第666-683行）
const saveActivity = async () => {
  // 前置检查：必须先有报名ID
  if (!registrationId.value) {
    ElMessage.warning('请先保存基本信息')
    return false
  }
  
  try {
    // 发起PUT请求
    const res = await updateRegistrationActivity(
      registrationId.value,  // URL参数：报名ID
      form.activity          // Body参数：活动说明全部字段
    )
    
    // 处理响应
    if (res.success) {
      ElMessage.success('保存成功')
      return true
    }
  } catch (error) {
    // ❌ 当前400错误会在这里被捕获
    console.error('保存活动说明失败:', error)
    ElMessage.error('保存活动说明失败')
    return false
  }
}
```

### 4. 后端处理

**期望的后端行为**：
1. 接收 `PUT /api/registrations/{id}/activity` 请求
2. 验证用户权限（是否是报名的创建者）
3. 验证报名ID是否存在
4. 验证必填字段（theme, subjectTypeCode, methodCode）
5. 验证字典代码是否有效
6. 更新数据库中的活动说明数据
7. 返回成功响应

**成功响应**（期望）：
```json
{
  "success": true,
  "data": null,
  "message": "保存成功"
}
```

**失败响应**（当前400错误）：
```json
{
  "success": false,
  "message": "参数验证失败：xxxx",
  "data": null
}
```

---

## 📊 数据流向图

```
用户填写表单
    ↓
点击"下一步"
    ↓
nextStep() 函数
    ↓
表单验证（activityFormRef.validate()）
    ↓
验证通过 → saveActivity() 函数
    ↓
检查 registrationId 存在
    ↓
调用 updateRegistrationActivity(id, form.activity)
    ↓
发起 HTTP 请求
    ↓
PUT /api/registrations/{id}/activity
    ↓
请求头: Authorization: Bearer {token}
请求体: {theme, keywords, subjectTypeCode, ...}
    ↓
后端处理
    ↓
返回响应
    ↓
前端处理响应
    ↓
成功 → 显示"保存成功" → 进入下一步
失败 → 显示"保存活动说明失败" → 停留当前步骤
```

---

## 🔍 当前400错误说明

### 错误捕获位置

```javascript
// 第679行
console.error('保存活动说明失败:', error)
```

### 错误类型

```
AxiosError: Request failed with status code 400
```

### 错误含义

**HTTP 400 Bad Request** 表示：
- ❌ 请求参数格式错误
- ❌ 必填字段缺失
- ❌ 字段值不符合后端验证规则
- ❌ 字典代码无效
- ❌ 数据类型不匹配

### 可能的原因（举例）

1. **字典代码无效**：
   ```javascript
   // 前端发送
   {
     "subjectTypeCode": "invalid_code"  // ❌ 后端字典中不存在
   }
   ```

2. **必填字段为空**（虽然前端已验证）：
   ```javascript
   {
     "theme": "",  // ❌ 后端要求非空
     "subjectTypeCode": "time_efficiency",
     "methodCode": "pdca"
   }
   ```

3. **数据类型不匹配**：
   ```javascript
   {
     "avgWorkYears": "abc",  // ❌ 应该是数字
     "avgAge": null,         // ❌ 后端不接受null
     "crossDepartment": "yes" // ❌ 应该是boolean
   }
   ```

4. **字段名拼写错误**：
   ```javascript
   {
     "thema": "主题",  // ❌ 拼写错误，应该是 theme
     "subjectTypeCode": "time_efficiency"
   }
   ```

---

## 📝 调试建议（仅供参考）

### 查看实际发送的数据

**在 `saveActivity` 函数中添加日志**：
```javascript
const saveActivity = async () => {
  if (!registrationId.value) {
    ElMessage.warning('请先保存基本信息')
    return false
  }
  
  // 添加调试日志
  console.log('📤 保存活动说明:', {
    registrationId: registrationId.value,
    activityData: form.activity
  })
  
  try {
    const res = await updateRegistrationActivity(registrationId.value, form.activity)
    if (res.success) {
      ElMessage.success('保存成功')
      return true
    }
  } catch (error) {
    console.error('保存活动说明失败:', error)
    // 添加更详细的错误信息
    console.error('❌ 错误详情:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        data: error.config?.data
      }
    })
    ElMessage.error('保存活动说明失败')
    return false
  }
}
```

### 后端日志检查

建议查看后端日志中的：
- 接收到的参数
- 验证失败的具体字段
- 详细的错误信息

---

## 📊 总结

### API调用信息

| 项目 | 值 |
|------|-----|
| **方法** | `PUT` |
| **端点** | `/api/registrations/{id}/activity` |
| **认证** | 需要（Bearer Token） |
| **Content-Type** | `application/json` |

### 发送参数

| 参数位置 | 参数来源 | 参数数量 |
|----------|----------|----------|
| URL路径 | `registrationId.value` | 1个 |
| 请求体 | `form.activity` 对象 | 9个字段 |

### 9个字段详情

**必填**：
1. `theme` (String) - 活动主题
2. `subjectTypeCode` (String) - 主题类型代码
3. `methodCode` (String) - 运用手法代码

**可选**：
4. `keywords` (String) - 关键词
5. `experienceImproveCode` (String) - 改善就医感受代码
6. `qualityTopicCode` (String) - 医疗质量安全主题代码
7. `avgWorkYears` (Number) - 平均工作年限
8. `avgAge` (Number) - 平均年龄
9. `crossDepartment` (Boolean) - 是否跨科室

### 当前状态

- ✅ 前端表单验证：通过
- ✅ API调用：成功发起
- ❌ 后端响应：400错误
- 📍 错误位置：`RegisterForm.vue:679`

---

**文档生成时间**: 2026-02-25  
**相关文件**: `src/views/contestant/RegisterForm.vue`, `src/api/registration.js`
