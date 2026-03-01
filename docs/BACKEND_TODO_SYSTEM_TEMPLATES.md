# 后端待处理 - 系统模版管理API

## 🔴 紧急问题

### 缺失的API端点

**端点**: `GET /api/system-templates`

**问题**: 404 Not Found - 端点不存在

**影响**: OPS用户无法查看所有模版列表，模版管理页面报错

---

## 需要实现的功能

### API: 获取所有模版列表

```
GET /api/system-templates
```

**权限**: 仅OPS角色

**功能**: 返回所有模版（包括历史版本和已停用的模版）

**请求参数**: 无

**响应格式**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "templateName": "报名表模版",
      "version": 1,
      "fileName": "2026年浙江省医院品管大赛报名表模版.docx",
      "filePath": "/uploads/templates/xxx.docx",
      "active": true,
      "createdAt": "2026-02-27T16:53:27"
    }
  ],
  "message": null
}
```

**必需字段**:
- `id` - 模版ID
- `templateName` - 模版名称（用于前端显示）
- `version` - 版本号
- `fileName` - 文件名
- `active` - 是否有效（true/false）
- `createdAt` - 创建时间

**可选字段**:
- `filePath` - 存储路径
- `fileSize` - 文件大小
- `uploadedBy` - 上传人
- `description` - 描述

---

## 与现有API的区别

| API | 用途 | 返回数据 |
|-----|------|---------|
| GET /system-templates/active | 用户下载模版 | 只返回 active=true 的模版 |
| GET /system-templates | OPS管理模版 | 返回所有模版（包括 active=false） |

---

## 实现参考

### Controller
```java
@GetMapping
@PreAuthorize("hasRole('OPS')")
public ResponseEntity<?> getAllTemplates() {
    List<SystemTemplate> templates = systemTemplateService.findAll();
    return ResponseEntity.ok(new ApiResponse(true, templates, null));
}
```

### Service
```java
public List<SystemTemplate> findAll() {
    return systemTemplateRepository.findAllByOrderByCreatedAtDesc();
}
```

### Repository
```java
List<SystemTemplate> findAllByOrderByCreatedAtDesc();
```

---

## 测试验证

运行测试脚本：
```bash
python scripts/test_system_templates_api.py
```

预期结果：
```
✅ 获取有效模版: 正常
✅ 获取所有模版: 正常  ← 目前是 ❌
✅ 上传模版端点: 正常
✅ 删除模版端点: 正常
✅ 下载模版端点: 正常
```

---

## 优先级

🔴 **高优先级** - 影响OPS核心功能

建议处理时间: 1-2天

---

## 相关文件

- 详细报告: `docs/SYSTEM_TEMPLATES_API_ISSUES.md`
- 测试脚本: `scripts/test_system_templates_api.py`
- 前端代码: `src/views/ops/SystemTemplates.vue`

---

**创建时间**: 2026-03-01
