# Label字段缺失 - 给后端

## 🎯 问题

详情页显示的是代码而不是中文标签：
- 显示 `subject_type_3` 而不是"医疗质量安全"
- 显示 `method_9` 而不是"PDCA循环法"
- 显示 `outpatient_process` 而不是"门诊流程改善"

---

## 📍 需要修复的API

### API地址
```
GET /api/registrations/{id}
```

### 缺失的字段（在 data.activityInfo 对象中）

| 字段名 | 当前状态 | 应该返回 |
|--------|---------|---------|
| `subjectTypeLabel` | ❌ null 或不存在 | ✅ "医疗质量安全" |
| `methodLabel` | ❌ null 或不存在 | ✅ "PDCA循环法" |
| `experienceImproveLabel` | ❌ null 或不存在 | ✅ "门诊流程改善" |
| `qualityTopicLabel` | ❌ null 或不存在 | ✅ "患者安全" |

---

## 📦 当前返回（错误）

```json
{
  "success": true,
  "data": {
    "activityInfo": {
      "subjectTypeCode": "subject_type_3",
      "subjectTypeLabel": null,  // ❌ 缺失
      
      "methodCode": "method_9",
      "methodLabel": null,  // ❌ 缺失
      
      "experienceImproveCode": "outpatient_process",
      "experienceImproveLabel": null,  // ❌ 缺失
      
      "qualityTopicCode": "quality_1",
      "qualityTopicLabel": null  // ❌ 缺失
    }
  }
}
```

## 📦 应该返回（正确）

```json
{
  "success": true,
  "data": {
    "activityInfo": {
      "subjectTypeCode": "subject_type_3",
      "subjectTypeLabel": "医疗质量安全",  // ✅ 需要返回
      
      "methodCode": "method_9",
      "methodLabel": "PDCA循环法",  // ✅ 需要返回
      
      "experienceImproveCode": "outpatient_process",
      "experienceImproveLabel": "门诊流程改善",  // ✅ 需要返回
      
      "qualityTopicCode": "quality_1",
      "qualityTopicLabel": "患者安全"  // ✅ 需要返回
    }
  }
}
```

---

## 🔍 数据来源

这些 Label 应该从字典表关联查询：

| Code字段 | 字典类型 | Label字段 |
|---------|---------|----------|
| `subjectTypeCode` | `subject_type` | `subjectTypeLabel` |
| `methodCode` | `method` | `methodLabel` |
| `experienceImproveCode` | `experience_improve` | `experienceImproveLabel` |
| `qualityTopicCode` | `quality_topic` | `qualityTopicLabel` |

---

## ✅ 修复建议

在后端查询报名详情时，关联查询字典表，返回完整的 Label 字段。

---

**API**: `GET /api/registrations/{id}`  
**问题**: `activityInfo` 对象中的所有 `xxxLabel` 字段为空  
**修复**: 关联字典表查询，返回中文标签
