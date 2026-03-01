# 系统设置页面API分析报告

## 页面位置
`src/views/ops/Settings.vue`

---

## 调用的API

### 1. 获取配置项
**端点**: `GET /api/admin/settings?key={key}`

**前端调用**:
```javascript
const res = await getSetting(key)
```

**前端尝试获取的配置项**:
1. `maxRegistrationsPerInstitution` - 机构报名配额限制（已实现）
2. `reviewerMaxLoad` - 评审专家最大负荷（未实现）
3. `basicGroupCount` - 基层组分组数量（未实现）
4. `comprehensiveGroupCount` - 综合组分组数量（未实现）
5. `advancedGroupCount` - 进阶组分组数量（未实现）
6. `shortlistRatio` - 入围比例（未实现）

---

### 2. 保存配置项
**端点**: `POST /api/admin/settings`

**请求体**:
```json
{
  "key": "maxRegistrationsPerInstitution",
  "value": "8"
}
```

**前端调用**:
```javascript
const res = await saveSetting({ 
  key, 
  value: String(value)
})
```

---

## 前端逻辑

### 页面加载时 (onMounted)
```javascript
const loadSettings = async () => {
  try {
    const keys = Object.keys(form)  // 6个配置项
    
    // 逐个查询配置项
    for (const key of keys) {
      try {
        const res = await getSetting(key)
        if (res.success && res.data) {
          const value = res.data.settingValue || res.data.value
          if (value !== undefined && value !== null) {
            form[key] = Number(value)
          }
        }
      } catch (error) {
        // 配置项不存在或查询失败，使用默认值
        console.log(`配置项 ${key} 不存在或查询失败，使用默认值`)
      }
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.warning('部分配置加载失败，使用默认值')
  }
}
```

### 保存设置时
```javascript
const saveSettings = async () => {
  try {
    saving.value = true
    
    let successCount = 0
    let failCount = 0
    
    // 逐个保存所有配置项
    for (const [key, value] of Object.entries(form)) {
      try {
        const res = await saveSetting({ 
          key, 
          value: String(value)
        })
        
        if (res.success) {
          successCount++
        } else {
          failCount++
        }
      } catch (error) {
        failCount++
      }
    }
    
    if (successCount > 0) {
      ElMessage.success(`保存成功 (${successCount}/${Object.keys(form).length})`)
    }
  } finally {
    saving.value = false
  }
}
```

---

## 可能的报错原因

### 1. 配置项不存在
如果后端某些配置项不存在，可能返回：
- 404 Not Found
- 或 `{ success: false, message: "配置项不存在" }`

**影响**: 
- 前端会在控制台输出错误日志
- 但页面会使用默认值，不影响显示

### 2. 权限问题
如果OPS角色没有权限访问某些配置项：
- 401 Unauthorized
- 403 Forbidden

### 3. 参数格式问题
如果后端对参数格式有要求：
- 400 Bad Request

### 4. 后端未实现
如果后端完全没有实现这些API：
- 404 Not Found

---

## 前端容错处理

前端代码已经做了容错处理：

1. **获取配置时**: 使用 try-catch，失败时使用默认值
2. **保存配置时**: 统计成功和失败数量，部分成功也会提示
3. **错误提示**: 只在必要时弹出提示，不会阻塞用户操作

---

## 默认值

```javascript
const form = reactive({
  maxRegistrationsPerInstitution: 8,   // 机构报名配额限制
  reviewerMaxLoad: 10,                  // 评审专家最大负荷
  basicGroupCount: 5,                   // 基层组分组数量
  comprehensiveGroupCount: 5,           // 综合组分组数量
  advancedGroupCount: 5,                // 进阶组分组数量
  shortlistRatio: 30                    // 入围比例
})
```

---

## 后端需要实现的功能

### 方案1: 实现所有配置项（推荐）

为所有6个配置项提供存储和查询功能：

```java
@GetMapping("/admin/settings")
public ResponseEntity<?> getSetting(@RequestParam String key) {
    Setting setting = settingService.findByKey(key);
    if (setting == null) {
        // 返回默认值
        setting = getDefaultSetting(key);
    }
    return ResponseEntity.ok(new ApiResponse(true, setting, null));
}

@PostMapping("/admin/settings")
public ResponseEntity<?> saveSetting(@RequestBody SettingRequest request) {
    Setting setting = settingService.saveOrUpdate(request.getKey(), request.getValue());
    return ResponseEntity.ok(new ApiResponse(true, setting, null));
}
```

### 方案2: 只实现已使用的配置项

只实现 `maxRegistrationsPerInstitution`，其他配置项返回默认值或404。

前端已经做了容错，这种方案也可以工作。

### 方案3: 批量查询接口

提供一个批量查询接口，减少请求次数：

```java
@PostMapping("/admin/settings/batch")
public ResponseEntity<?> getSettings(@RequestBody List<String> keys) {
    Map<String, String> settings = settingService.findByKeys(keys);
    return ResponseEntity.ok(new ApiResponse(true, settings, null));
}
```

---

## 测试建议

### 手动测试步骤

1. 登录OPS账号
2. 访问"系统管理" → "系统设置"
3. 打开浏览器开发者工具 (F12)
4. 查看 Network 标签
5. 观察以下请求：
   - 6个 GET /admin/settings?key=xxx 请求
   - 保存时的 POST /admin/settings 请求

### 预期结果

**正常情况**:
- 所有请求返回 200 OK
- 页面正常显示配置值
- 保存成功

**部分配置不存在**:
- 部分请求返回 404 或 success=false
- 控制台有警告日志
- 页面使用默认值
- 保存时部分成功

---

## 控制台可能的错误信息

```javascript
配置项 reviewerMaxLoad 不存在或查询失败，使用默认值 10
配置项 basicGroupCount 不存在或查询失败，使用默认值 5
配置项 comprehensiveGroupCount 不存在或查询失败，使用默认值 5
配置项 advancedGroupCount 不存在或查询失败，使用默认值 5
配置项 shortlistRatio 不存在或查询失败，使用默认值 30
```

这些是正常的日志，表示后端未实现这些配置项，前端使用默认值。

---

## 建议

### 短期方案
1. 确认后端实现了 `maxRegistrationsPerInstitution` 配置项
2. 其他配置项可以暂时不实现，前端会使用默认值
3. 前端已经做了容错，不会影响用户使用

### 长期方案
1. 后端实现所有6个配置项的存储
2. 提供批量查询接口，优化性能
3. 添加配置项的验证和权限控制

---

**报告生成时间**: 2026-03-01  
**分析人员**: Kiro AI Assistant
