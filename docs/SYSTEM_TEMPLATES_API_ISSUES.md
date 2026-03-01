# 系统模版管理API问题报告

## 测试时间
2026-03-01 12:54

## 测试账号
- 手机号: 13800000005
- 角色: OPS（系统运维）

---

## API测试结果总览

| API端点 | 方法 | 状态 | 问题描述 |
|---------|------|------|---------|
| /system-templates/active | GET | ✅ 正常 | 返回有效模版列表 |
| /system-templates | GET | ❌ 404 | **端点不存在** |
| /system-templates/upload | POST | ✅ 正常 | 上传端点存在 |
| /system-templates/{id} | DELETE | ✅ 正常 | 删除端点存在 |
| /system-templates/{id}/download | GET | ✅ 正常 | 下载端点存在 |

---

## 🔴 关键问题

### 问题1: 获取所有模版列表API不存在

**前端期望的API**:
```
GET /api/system-templates
```

**实际测试结果**:
```json
{
  "timestamp": "2026-03-01T04:54:09.502+00:00",
  "status": 404,
  "error": "Not Found",
  "path": "/api/system-templates"
}
```

**影响**:
- OPS用户无法在模版管理页面查看所有模版（包括历史版本和已停用的模版）
- 页面加载时会报错
- 无法管理模版的完整生命周期

**前端代码位置**:
- 文件: `src/views/ops/SystemTemplates.vue`
- 函数: `loadTemplates()`
- 调用: `getAllTemplates()`

**前端调用代码**:
```javascript
const loadTemplates = async () => {
  loading.value = true
  try {
    // 加载有效模版和所有模版
    const [activeRes, allRes] = await Promise.all([
      getActiveTemplates(),  // ✅ 这个API存在
      getAllTemplates()      // ❌ 这个API不存在
    ])
    
    if (activeRes.success) {
      activeTemplates.value = activeRes.data || []
    }
    
    if (allRes.success) {
      allTemplates.value = allRes.data || []
    }
  } catch (error) {
    console.error('加载模版列表失败:', error)
    ElMessage.error('加载模版列表失败')
  } finally {
    loading.value = false
  }
}
```

---

## ✅ 正常工作的API

### 1. 获取有效模版列表

**端点**: `GET /api/system-templates/active`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "templateType": "registration_form",
      "fileName": "2026年浙江省医院品管大赛报名表模版.docx",
      "fileSize": 16967,
      "version": 1,
      "isActive": true,
      "uploadedBy": null,
      "uploadedAt": "2026-02-27T16:53:27",
      "description": null
    },
    {
      "id": 2,
      "templateType": "result_report",
      "fileName": "成果报告书制作说明.docx",
      "fileSize": 17671,
      "version": 1,
      "isActive": true,
      "uploadedBy": null,
      "uploadedAt": "2026-02-27T16:53:27",
      "description": null
    }
  ],
  "message": null
}
```

**说明**: 
- 返回当前有效的模版列表
- 用于用户下载模版
- 数据结构完整

---

### 2. 上传模版

**端点**: `POST /api/system-templates/upload`

**测试结果**: 端点存在（返回400是因为测试时未上传文件）

**说明**: 
- 用于OPS上传新模版
- 需要 multipart/form-data 格式
- 应该支持 file 字段

---

### 3. 删除模版

**端点**: `DELETE /api/system-templates/{id}`

**测试结果**: 端点存在

**响应示例**（模版不存在时）:
```json
{
  "success": false,
  "data": null,
  "message": "模版不存在"
}
```

**说明**: 
- 用于删除或停用模版
- 可能是软删除（设置 isActive=false）

---

### 4. 下载模版

**端点**: `GET /api/system-templates/{id}/download`

**测试结果**: 端点存在

**说明**: 
- 返回文件流（Blob）
- 用于下载模版文件

---

## 🎯 需要后端实现的API

### API: 获取所有模版列表（包括历史版本）

**端点**: `GET /api/system-templates`

**用途**: OPS管理员查看和管理所有模版

**权限**: 仅OPS角色可访问

**请求参数**: 无

**期望响应格式**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "templateName": "报名表模版",
      "templateType": "registration_form",
      "fileName": "2026年浙江省医院品管大赛报名表模版.docx",
      "filePath": "/uploads/templates/xxx.docx",
      "fileSize": 16967,
      "version": 1,
      "active": true,
      "uploadedBy": "OPS User",
      "createdAt": "2026-02-27T16:53:27",
      "description": "报名表模版说明"
    },
    {
      "id": 3,
      "templateName": "报名表模版",
      "templateType": "registration_form",
      "fileName": "2025年浙江省医院品管大赛报名表模版.docx",
      "filePath": "/uploads/templates/yyy.docx",
      "fileSize": 15234,
      "version": 2,
      "active": false,
      "uploadedBy": "OPS User",
      "createdAt": "2025-12-01T10:00:00",
      "description": "旧版本，已停用"
    }
  ],
  "message": null
}
```

**字段说明**:
- `id`: 模版ID（必需）
- `templateName`: 模版名称（必需，前端显示用）
- `templateType`: 模版类型（可选，如 registration_form, result_report）
- `fileName`: 文件名（必需）
- `filePath`: 存储路径（可选，用于显示）
- `fileSize`: 文件大小（可选，字节数）
- `version`: 版本号（必需）
- `active`: 是否有效（必需，true=有效，false=已停用）
- `uploadedBy`: 上传人（可选）
- `createdAt`: 上传时间（必需）
- `description`: 描述（可选）

**与现有API的区别**:
- `/system-templates/active` - 只返回有效模版（active=true）
- `/system-templates` - 返回所有模版（包括已停用的）

**业务逻辑**:
1. 返回所有模版记录，不论 active 状态
2. 按上传时间倒序排列（最新的在前）
3. 包含历史版本
4. 仅OPS角色可访问

---

## 📋 前端字段映射

前端期望的字段与后端返回的字段对比：

| 前端字段 | 后端字段（active API） | 后端字段（all API需要） | 说明 |
|---------|---------------------|---------------------|------|
| id | id | id | 模版ID |
| templateName | ❌ 缺失 | templateName | **需要添加** |
| version | version | version | 版本号 |
| fileName | fileName | fileName | 文件名 |
| filePath | ❌ 缺失 | filePath | **需要添加** |
| active | isActive | active | 是否有效 |
| createdAt | uploadedAt | createdAt | 上传时间 |

**注意**: 
- 后端 `/system-templates/active` 返回的是 `isActive`
- 前端期望的是 `active`
- 建议统一使用 `active` 字段

---

## 🔧 后端实现建议

### Controller 层

```java
@RestController
@RequestMapping("/api/system-templates")
public class SystemTemplateController {
    
    /**
     * 获取所有模版（包括历史版本） - OPS专用
     */
    @GetMapping
    @PreAuthorize("hasRole('OPS')")
    public ResponseEntity<?> getAllTemplates() {
        List<SystemTemplate> templates = systemTemplateService.findAll();
        return ResponseEntity.ok(new ApiResponse(true, templates, null));
    }
    
    /**
     * 获取有效模版列表 - 公开接口
     */
    @GetMapping("/active")
    public ResponseEntity<?> getActiveTemplates() {
        List<SystemTemplate> templates = systemTemplateService.findActiveTemplates();
        return ResponseEntity.ok(new ApiResponse(true, templates, null));
    }
    
    // ... 其他方法
}
```

### Service 层

```java
@Service
public class SystemTemplateService {
    
    /**
     * 获取所有模版（包括已停用的）
     */
    public List<SystemTemplate> findAll() {
        return systemTemplateRepository.findAllByOrderByCreatedAtDesc();
    }
    
    /**
     * 获取有效模版
     */
    public List<SystemTemplate> findActiveTemplates() {
        return systemTemplateRepository.findByActiveTrue();
    }
}
```

### Repository 层

```java
public interface SystemTemplateRepository extends JpaRepository<SystemTemplate, Long> {
    
    List<SystemTemplate> findAllByOrderByCreatedAtDesc();
    
    List<SystemTemplate> findByActiveTrue();
}
```

---

## 🧪 测试验证

### 测试脚本
```bash
python scripts/test_system_templates_api.py
```

### 预期结果
所有API测试通过：
- ✅ 获取有效模版
- ✅ 获取所有模版
- ✅ 上传模版端点
- ✅ 删除模版端点
- ✅ 下载模版端点

---

## 📝 前端临时解决方案

在后端API实现之前，前端可以临时使用 `/system-templates/active` 的数据：

```javascript
const loadTemplates = async () => {
  loading.value = true
  try {
    // 临时方案：只加载有效模版
    const activeRes = await getActiveTemplates()
    
    if (activeRes.success) {
      activeTemplates.value = activeRes.data || []
      // 临时将有效模版也显示在所有模版列表中
      allTemplates.value = activeRes.data || []
    }
  } catch (error) {
    console.error('加载模版列表失败:', error)
    ElMessage.error('加载模版列表失败')
  } finally {
    loading.value = false
  }
}
```

**限制**:
- 无法查看历史版本
- 无法查看已停用的模版
- 无法完整管理模版生命周期

---

## 📊 优先级

**优先级**: 🔴 高

**原因**:
1. 影响OPS核心功能
2. 模版管理页面无法正常使用
3. 无法管理模版的完整生命周期

**建议处理时间**: 1-2天内完成

---

## 📞 联系方式

如有疑问，请联系前端开发团队。

**相关文档**:
- 前端代码: `src/views/ops/SystemTemplates.vue`
- API定义: `src/api/systemTemplate.js`
- 测试脚本: `scripts/test_system_templates_api.py`

---

**报告生成时间**: 2026-03-01  
**报告生成人**: Kiro AI Assistant
