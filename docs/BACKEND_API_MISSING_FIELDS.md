# 后端 API 缺失字段说明

## 🔴 问题描述

前端需要在报名列表中显示以下字段，但当前后端接口 **未返回** 这些数据：

1. **项目编号** (registrationId)
2. **医疗机构名称** (institutionName)  
3. **品管工具** (methodLabel) - 中文标签
4. **报名人** (applicantName)

---

## 📊 当前接口返回的数据

### 接口: `GET /api/registrations?competitionId=21`

**当前返回字段（仅 7 个）**：

```json
{
  "success": true,
  "data": [
    {
      "id": 106,
      "projectName": "项目名称",
      "groupType": "BASIC",
      "groupCode": "A1",
      "status": "APPROVED",
      "submittedAt": "2026-02-04T15:38:52.604359",
      "createdAt": "2026-02-05T23:38:52.604359"
    }
  ]
}
```

---

## ✅ 需要添加的字段

### 方案 1: 扩展列表接口（推荐）⭐

在 `GET /api/registrations` 接口返回的数据中**添加**以下字段：

```json
{
  "success": true,
  "data": [
    {
      // === 现有字段 ===
      "id": 106,
      "projectName": "改善就医体验规范流程-1",
      "groupType": "BASIC",
      "groupCode": "A1",
      "status": "APPROVED",
      "submittedAt": "2026-02-04T15:38:52.604359",
      "createdAt": "2026-02-05T23:38:52.604359",
      
      // === 需要添加的字段 ===
      "registrationId": "BM20260106",         // 项目编号（格式化）
      "institutionId": 1,                     // 医疗机构 ID
      "institutionName": "浙江省人民医院",     // 医疗机构名称 ⭐
      "institutionCode": "330000001",         // 机构代码
      "methodCode": "qc_topic",               // 品管工具代码
      "methodLabel": "品管圈-课题达成",         // 品管工具（中文）⭐
      "subjectTypeCode": "education",         // 主题类型代码
      "subjectTypeLabel": "教育训练",          // 主题类型（中文）⭐
      "applicantId": 10,                      // 报名人 ID
      "applicantName": "张三"                  // 报名人姓名 ⭐
    }
  ]
}
```

---

## 🔧 后端实现建议

### Java 示例（假设使用 Spring Boot）

#### 1. 创建/修改 DTO

```java
@Data
public class RegistrationListDTO {
    // 现有字段
    private Long id;
    private String projectName;
    private String groupType;
    private String groupCode;
    private String status;
    private LocalDateTime submittedAt;
    private LocalDateTime createdAt;
    
    // 新增字段
    private String registrationId;          // 格式化的项目编号
    private Long institutionId;             // 机构 ID
    private String institutionName;         // 机构名称 ⭐
    private String institutionCode;         // 机构代码
    private String methodCode;              // 品管工具代码
    private String methodLabel;             // 品管工具中文 ⭐
    private String subjectTypeCode;         // 主题类型代码
    private String subjectTypeLabel;        // 主题类型中文 ⭐
    private Long applicantId;               // 报名人 ID
    private String applicantName;           // 报名人姓名 ⭐
}
```

#### 2. 修改查询逻辑

```java
@Service
public class RegistrationService {
    
    public List<RegistrationListDTO> getRegistrations(Long competitionId) {
        // 查询报名信息（需要 JOIN 相关表）
        String sql = """
            SELECT 
                r.id,
                r.project_name,
                r.group_type,
                r.group_code,
                r.status,
                r.submitted_at,
                r.created_at,
                
                -- 新增字段
                CONCAT('BM', LPAD(r.id, 8, '0')) as registration_id,  -- 格式化编号
                i.id as institution_id,
                i.name as institution_name,                            -- 机构名称
                i.code as institution_code,
                a.method_code,
                dm.label as method_label,                              -- 品管工具中文
                a.subject_type_code,
                ds.label as subject_type_label,                        -- 主题类型中文
                u.id as applicant_id,
                u.name as applicant_name                               -- 报名人姓名
                
            FROM registrations r
            LEFT JOIN institutions i ON r.institution_id = i.id
            LEFT JOIN activity_info a ON r.id = a.registration_id
            LEFT JOIN dictionaries dm ON a.method_code = dm.code AND dm.type = 'method'
            LEFT JOIN dictionaries ds ON a.subject_type_code = ds.code AND ds.type = 'subject_type'
            LEFT JOIN users u ON r.applicant_id = u.id
            WHERE r.competition_id = ?
            ORDER BY r.created_at DESC
        """;
        
        // 执行查询并映射到 DTO
        return jdbcTemplate.query(sql, new BeanPropertyRowMapper<>(RegistrationListDTO.class), competitionId);
    }
}
```

---

## 📋 数据关系说明

根据数据库表结构，这些字段应该来自：

| 字段 | 来源表 | 说明 |
|------|--------|------|
| `registrationId` | 格式化 `registrations.id` | 例如: `BM20260106` |
| `institutionName` | `institutions.name` | 通过 `registrations.institution_id` 关联 |
| `methodLabel` | `dictionaries.label` | 通过 `activity_info.method_code` 关联，type='method' |
| `subjectTypeLabel` | `dictionaries.label` | 通过 `activity_info.subject_type_code` 关联，type='subject_type' |
| `applicantName` | `users.name` | 通过 `registrations.applicant_id` 关联 |

---

## 🧪 验证方法

修改后，使用以下请求验证：

```bash
curl -X GET "http://localhost:6031/api/registrations?competitionId=21" \
  -H "Authorization: Bearer {token}"
```

**预期响应**应包含新增的字段：

```json
{
  "success": true,
  "data": [
    {
      "id": 106,
      "registrationId": "BM20260106",         // ✓
      "projectName": "...",
      "institutionName": "浙江省人民医院",     // ✓
      "methodLabel": "品管圈-课题达成",         // ✓
      "subjectTypeLabel": "教育训练",          // ✓
      "applicantName": "张三",                 // ✓
      "groupType": "BASIC",
      ...
    }
  ]
}
```

---

## 🎯 前端需求优先级

| 字段 | 优先级 | 说明 |
|------|--------|------|
| `institutionName` | ⭐⭐⭐ 高 | 用户必须看到是哪家医院 |
| `methodLabel` | ⭐⭐⭐ 高 | 筛选和展示都需要 |
| `applicantName` | ⭐⭐ 中 | 联系人信息 |
| `registrationId` | ⭐⭐ 中 | 方便引用和查找 |
| `subjectTypeLabel` | ⭐⭐ 中 | 筛选和展示都需要 |

---

## 📝 其他相关接口

以下接口也建议同步修改：

### 1. Admin 筛选接口（如果要修复 401 问题）

```
GET /api/admin/registrations/filter?competitionId=21&methodCode=xxx
```

返回格式应与 `/api/registrations` 一致。

### 2. 详情接口（可选优化）

```
GET /api/registrations/{id}
```

当前详情接口返回的 `registration` 对象中也缺少这些字段，建议同步添加。

---

## ✅ 预期效果

后端修改完成后，前端列表将能正常显示：

| ID | 项目名称 | 项目编号 | 医疗机构名称 | 品管工具 | 报名人 | 竞赛组别 | 分组 |
|----|---------|---------|-------------|---------|--------|---------|------|
| 106 | 改善就医体验... | BM20260106 | 浙江省人民医院 | 品管圈-课题达成 | 张三 | 基层组 | A1 |

---

## 🆘 需要帮助？

如有疑问，请参考：
- 前端代码: `src/views/committee/BookStage.vue`
- 测试脚本: `test_different_endpoints.py`
- 前端文档: `FRONTEND_COMPLETE_FLOW_GUIDE.md`

---

**创建时间**: 2026-02-06  
**优先级**: 🔴 高（影响核心功能）  
**预计工作量**: 2-4 小时（包括测试）
