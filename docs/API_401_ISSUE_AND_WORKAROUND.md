# `/api/admin/registrations/filter` 返回 401 问题及临时方案

## 🔴 当前问题

**接口:** `GET /api/admin/registrations/filter`  
**状态:** 返回 **401 Unauthorized**  
**测试时间:** 2026-02-06 23:30  

```bash
$ python test_list_api_now.py

✅ 登录成功
❌ /api/admin/registrations/filter 返回 401
```

## 🔧 临时解决方案（已实施）

### 方案概述

由于完整接口不可用，前端采用**"批量获取详情 + 客户端筛选"**的方案：

```
1. 调用 /api/registrations?competitionId=21
   → 获取基础数据（33条）

2. 对每条数据并行调用 /api/registrations/{id}
   → 获取详情，提取 methodCode / subjectTypeCode

3. 从字典查找对应的 label
   → methodCode → methodLabel
   → subjectTypeCode → subjectTypeLabel

4. 客户端筛选
   → 支持按 methodCode 筛选
```

### 代码实现

**加载数据:**
```javascript
const loadRegistrations = async () => {
  // 1. 获取基础列表
  const res = await getRegistrations({ competitionId: 21 })
  const baseData = res.data
  
  // 2. 批量获取详情补充字段
  const enrichedData = await Promise.all(
    baseData.map(async (item) => {
      const detailRes = await getRegistration(item.id)
      if (detailRes.success) {
        item.methodCode = detailRes.data.activityInfo.methodCode
        item.methodLabel = getMethodLabel(detailRes.data.activityInfo.methodCode)
        item.subjectTypeCode = detailRes.data.activityInfo.subjectTypeCode
        item.subjectTypeLabel = getSubjectTypeLabel(detailRes.data.activityInfo.subjectTypeCode)
      }
      return item
    })
  )
  
  allRegistrations.value = enrichedData
  applyClientFilters()
}
```

**客户端筛选:**
```javascript
const applyClientFilters = () => {
  let filtered = [...allRegistrations.value]
  
  if (registrationFilters.groupType) {
    filtered = filtered.filter(item => item.groupType === registrationFilters.groupType)
  }
  
  if (registrationFilters.methodCode) {
    filtered = filtered.filter(item => item.methodCode === registrationFilters.methodCode)
  }
  
  registrations.value = filtered
}
```

## ✅ 当前功能状态

### 可用功能 ✅

| 功能 | 实现方式 | 性能 |
|------|---------|------|
| 查看列表 | 批量获取详情 | ⚠️ 较慢（33个请求） |
| 详情-品管工具 | 字典查找 | ✅ 快 |
| 详情-主题类型 | 字典查找 | ✅ 快 |
| 筛选-组别 | 客户端筛选 | ✅ 快 |
| 筛选-分组 | 客户端筛选 | ✅ 快 |
| **筛选-品管工具** | **客户端筛选** | ✅ **已实现** |
| 筛选-项目名称 | 客户端筛选 | ✅ 快 |

### 暂不可用 ❌

| 功能 | 原因 |
|------|------|
| 列表显示机构名称 | 基础接口不返回 |
| 列表显示项目编号 | 基础接口不返回 |
| 列表显示报名人 | 基础接口不返回 |
| 筛选-机构名称 | 基础接口不返回 |

## 🎯 使用指南

### 筛选品管工具

**步骤:**
1. 进入"书审阶段" → "报名与分组"
2. 等待数据加载完成（约2-3秒）
3. 在"品管工具"下拉框中选择（如"品管圈-课题达成"）
4. 点击"查询"按钮
5. ✅ 列表显示筛选后的结果

**控制台日志:**
```
📥 正在加载报名列表...
✅ 获取到基础数据: 33 条
📥 正在批量获取详情以补充品管工具信息...
✅ 数据补充完成，支持品管工具筛选
🔍 按品管工具筛选: qc_topic，结果 5 条
✅ 加载成功，共 5 条报名
```

## ⚠️ 性能说明

### 当前性能

- **首次加载**: 约 **2-3 秒**（33个并行详情请求）
- **筛选操作**: < 100ms（客户端筛选）
- **切换筛选**: < 100ms（客户端筛选）

### 性能瓶颈

批量获取详情需要发起 **33 个 HTTP 请求**，虽然是并行的，但仍比单次请求慢。

## 🚀 后端修复后的改进

### 需要后端修复

**优先级 P0:** 修复 `/api/admin/registrations/filter` 的 401 问题

**期望接口行为:**
```javascript
// 请求
GET /api/admin/registrations/filter?competitionId=21&methodCode=qcc_topic

// 响应（200 OK）
{
  "success": true,
  "data": [
    {
      "id": 106,
      "registrationId": "2024-ZJ-001",
      "projectName": "护理交接班规范化-1",
      "institutionName": "浙江大学医学院附属第二医院",
      "methodCode": "qc_topic",
      "methodLabel": "品管圈-课题达成",    ← 后端返回
      "subjectTypeCode": "education",
      "subjectTypeLabel": "教育训练",      ← 后端返回
      "applicantName": "张三",
      "groupType": "BASIC",
      "groupCode": "A1",
      "submittedAt": "2026-02-04T15:38:52"
    }
  ]
}
```

### 修复后的前端优化

```javascript
// 简化后的代码
const loadRegistrations = async () => {
  // 直接调用完整接口，无需批量获取详情
  const res = await filterRegistrations(registrationFilters)
  registrations.value = res.data
  
  // 直接显示 methodLabel，无需字典查找
}
```

**性能提升:**
- 加载时间: 2-3秒 → **< 500ms** ⚡
- HTTP 请求: 33个 → **1个** ⚡
- 无需字典映射
- 无需客户端筛选

## 📝 后端修复检查清单

### 1. 权限验证

检查 `@PreAuthorize` 注解：
```java
@PreAuthorize("hasAnyRole('COMMITTEE_ADMIN', 'OPS')")
@GetMapping("/admin/registrations/filter")
public Result<?> filterRegistrations(...) {
    // ...
}
```

**检查项:**
- [ ] Token 中的 role 字段是否正确
- [ ] Role 前缀是否一致（ROLE_ vs 无前缀）
- [ ] Security 配置是否生效

### 2. 返回字段完整性

确保返回 DTO 包含所有字段：
```java
public class RegistrationFilterItem {
    private Long id;
    private String registrationId;        // ← 必需
    private String institutionName;       // ← 必需
    private String methodCode;
    private String methodLabel;           // ← 必需（后端查字典）
    private String subjectTypeCode;
    private String subjectTypeLabel;      // ← 必需（后端查字典）
    private String applicantName;         // ← 必需
    // ... 其他字段
}
```

### 3. 筛选参数支持

确保支持以下参数：
```java
@GetMapping("/admin/registrations/filter")
public Result<?> filterRegistrations(
    @RequestParam Long competitionId,
    @RequestParam(required = false) String institutionName,
    @RequestParam(required = false) String methodCode,      // ← 必需
    @RequestParam(required = false) String subjectTypeCode, // ← 必需
    @RequestParam(required = false) String groupType,
    @RequestParam(required = false) String groupCode,
    @RequestParam(required = false) String projectName
) {
    // 实现筛选逻辑
}
```

## 🧪 测试脚本

**快速测试:**
```bash
python test_list_api_now.py
```

**预期输出（修复后）:**
```
✅ 登录成功
✅ /api/admin/registrations/filter 返回 200
✅ registrationId: 2024-ZJ-001
✅ institutionName: 浙江大学医学院附属第二医院
✅ methodLabel: 品管圈-课题达成
✅ subjectTypeLabel: 教育训练
✅ applicantName: 张三
✅ 筛选成功，共 5 条

✅ 后端已完全优化！
```

## 📊 总结

### 当前状态

- ✅ **品管工具筛选已实现**（客户端筛选）
- ⚠️ 性能一般（需批量请求详情）
- ⚠️ 部分字段缺失（机构名称、项目编号、报名人）

### 后端修复后

- ⚡ 性能大幅提升（单次请求）
- ✅ 完整字段支持
- ✅ 后端筛选（更高效）
- ✅ 代码更简洁

---

**创建时间:** 2026-02-06 23:35  
**当前方案:** 临时可用，等待后端修复优化
